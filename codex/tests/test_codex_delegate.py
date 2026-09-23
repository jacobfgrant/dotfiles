"""Unit tests for codex-delegate. No Codex or model calls; `codex-delegate doctor` is the integration test."""

import json
import subprocess
import sys
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / ".local" / "bin" / "codex-delegate"


def load_script():
    """Import the extensionless script as a module."""
    spec = spec_from_loader("codex_delegate", SourceFileLoader("codex_delegate", str(SCRIPT)))
    module = module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclasses resolve annotations through sys.modules
    spec.loader.exec_module(module)
    return module


cd = load_script()
OUT = Path("/tmp/out.txt")
SCHEMA = Path("/tmp/schema.json")


def request(**overrides):
    base = {"intent": "consult", "cwd": Path("/repo"), "model": "gpt-6-sol", "effort": "high"}
    return cd.Request(**{**base, **overrides})


# --- command construction: the security contract ---


def test_review_uses_native_reviewer_with_review_profile():
    argv = cd.build_command(request(intent="review", base="master"), OUT)
    assert argv[:5] == ["codex", "exec", "review", "--base", "master"]
    assert 'default_permissions="review"' in argv
    assert 'model_reasoning_effort="high"' in argv
    assert argv[argv.index("--model") + 1] == "gpt-6-sol"
    assert "--json" in argv and str(OUT) in argv
    assert argv[-1] != "-", "review takes no prompt"
    assert "--uncommitted" in cd.build_command(request(intent="review"), OUT)


def test_adversarial_reads_prompt_from_stdin_and_uses_schema():
    argv = cd.build_command(request(intent="adversarial", base="main"), OUT, SCHEMA)
    assert argv[:2] == ["codex", "exec"] and "review" not in argv
    assert argv[argv.index("--output-schema") + 1] == str(SCHEMA)
    assert argv[-1] == "-"
    assert 'default_permissions="review"' in argv


def test_implement_uses_development_profile_and_worktree():
    argv = cd.build_command(request(intent="implement", worktree=True), OUT)
    assert 'default_permissions="development"' in argv
    assert "--worktree" in argv


def test_resume_profile_follows_write_flag_and_inherits_settings():
    inherited = cd.build_command(request(intent="resume", session_id="abc", model=None, effort=None), OUT)
    assert inherited[1:4] == ["exec", "resume", "abc"]
    assert 'default_permissions="review"' in inherited
    assert "--model" not in inherited
    assert not any(a.startswith("model_reasoning_effort") for a in inherited)

    explicit = cd.build_command(request(intent="resume", session_id="abc", write=True, model="gpt-6-astra", effort="xhigh"), OUT)
    assert 'default_permissions="development"' in explicit
    assert explicit[explicit.index("--model") + 1] == "gpt-6-astra"
    assert 'model_reasoning_effort="xhigh"' in explicit


@pytest.mark.parametrize(
    "overrides, message",
    [
        ({"intent": "consult", "model": ""}, "consult requires --model"),
        ({"intent": "resume"}, "session id"),
        ({"effort": "turbo"}, "effort must be one of"),
        ({"intent": "consult", "worktree": True}, "--worktree only applies"),
        ({"intent": "implement", "effort": None}, "needs a model and an effort"),
    ],
)
def test_invalid_requests_are_rejected(overrides, message):
    with pytest.raises(cd.DelegateError, match=message):
        cd.build_command(request(**overrides), OUT)


SANDBOX_CHANGING_FLAGS = {"--sandbox", "-s", "--add-dir", "--yolo", "--dangerously-bypass-approvals-and-sandbox",
                          "--approve-for-me", "--ignore-rules", "--ignore-user-config", "-p", "--profile"}


def test_only_pinned_config_overrides_are_emitted():
    """The only -c overrides are the profile and effort pins, and nothing touches the sandbox."""
    for intent, extra in (("review", {}), ("adversarial", {}), ("consult", {}), ("implement", {"worktree": True})):
        argv = cd.build_command(request(intent=intent, **extra), OUT, SCHEMA if intent == "adversarial" else None)
        overrides = [argv[i + 1] for i, arg in enumerate(argv) if arg == "-c"]
        assert all(o.startswith(("default_permissions=", "model_reasoning_effort=")) for o in overrides), argv
        assert not SANDBOX_CHANGING_FLAGS & set(argv), argv


# --- project configuration that could widen the sandbox ---


def git_repo(path):
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", "."], cwd=path, check=True)
    return path


def test_project_config_that_could_change_the_sandbox_is_refused(tmp_path):
    repo = git_repo(tmp_path / "repo")
    assert cd.project_config_problems(repo) == []

    codex_dir = repo / ".codex"
    codex_dir.mkdir()
    (codex_dir / "config.toml").write_text('model = "gpt-6-luna"\n')
    assert cd.project_config_problems(repo) == [], "harmless project keys are fine"

    (codex_dir / "config.toml").write_text('sandbox_mode = "danger-full-access"\n[permissions.review]\nextends = ":workspace"\n')
    problems = cd.project_config_problems(repo)
    assert len(problems) == 1 and "sandbox_mode, permissions" in problems[0]

    (codex_dir / "config.toml").write_text('model = "gpt-6-luna"\n')
    (codex_dir / "rules").mkdir()
    (codex_dir / "rules" / "escape.rules").write_text('prefix_rule(pattern = ["curl"], decision = "allow")\n')
    assert any("allow rule" in p for p in cd.project_config_problems(repo))


def test_project_config_is_checked_at_the_git_root_too(tmp_path):
    repo = git_repo(tmp_path / "repo")
    (repo / ".codex").mkdir()
    (repo / ".codex" / "config.toml").write_text('default_permissions = ":danger-full-access"\n')
    nested = repo / "src" / "pkg"
    nested.mkdir(parents=True)
    assert any("default_permissions" in p for p in cd.project_config_problems(nested))


# --- session rollouts: what actually ran ---


def rollout_lines(model="gpt-6-sol", effort="high", profile="review", sandbox="read-only", last="done", turn_id="turn-1", cwd="/repo"):
    records = [
        {"type": "session_meta", "payload": {"id": "sess-1", "cli_version": "0.156.1", "cwd": cwd}},
        {
            "type": "turn_context",
            "payload": {
                "turn_id": turn_id,
                "model": model,
                "effort": effort,
                "cwd": cwd,
                "approval_policy": "on-request",
                "sandbox_policy": {"type": sandbox},
                "active_permission_profile": {"id": profile, "extends": ":read-only"},
            },
        },
        {"type": "event_msg", "payload": {"type": "task_complete", "last_agent_message": last}},
    ]
    return [json.dumps(r) for r in records]


def write_rollout(day, name, lines):
    day.mkdir(parents=True, exist_ok=True)
    (day / f"rollout-x-{name}.jsonl").write_text("\n".join(lines))


@pytest.fixture
def sessions(tmp_path, monkeypatch):
    """A throwaway CODEX_HOME; returns the day directory rollouts go in."""
    monkeypatch.setenv("CODEX_HOME", str(tmp_path))
    monkeypatch.setattr(cd, "ROLLOUT_FLUSH_WAIT_S", 0)
    return tmp_path / "sessions" / "2026" / "09" / "22"


def test_summary_reads_model_profile_and_message(sessions):
    write_rollout(sessions, "sess-1", rollout_lines())
    write_rollout(sessions, "sess-2", [])
    summary = cd.load_summary("sess-1")
    assert (summary.session_id, summary.cli_version, summary.turns) == ("sess-1", "0.156.1", 1)
    assert (summary.model, summary.effort, summary.profile, summary.sandbox) == ("gpt-6-sol", "high", "review", "read-only")
    assert summary.last_message == "done"
    assert cd.load_summary("missing") is None


def test_report_flags_mismatches_and_missing_rollout(sessions):
    write_rollout(sessions, "sess-1", rollout_lines(model="gpt-6-luna", profile="development"))
    run = cd.RunResult(exit_code=0, thread_id="sess-1", errors=[], agent_messages=[], duration_s=1.0)
    report = cd.build_report(request(), ["codex"], run, None)
    assert report["model_actual"] == "gpt-6-luna"
    assert any("model mismatch" in w for w in report["warnings"])
    assert any("profile mismatch" in w for w in report["warnings"])
    assert report["message"] == "done"

    lost = cd.RunResult(exit_code=1, thread_id="nope", errors=["boom"], agent_messages=["partial"], duration_s=1.0)
    report = cd.build_report(request(), ["codex"], lost, None)
    assert report["model_actual"] is None
    assert any("rollout not found" in w for w in report["warnings"])
    assert any("boom" in w for w in report["warnings"])
    assert report["message"] == "partial"


def test_inherited_resume_has_no_mismatch_warnings(sessions):
    write_rollout(sessions, "sess-1", rollout_lines(model="gpt-6-astra", effort="xhigh"))
    run = cd.RunResult(exit_code=0, thread_id="sess-1", errors=[], agent_messages=[], duration_s=1.0)
    report = cd.build_report(request(intent="resume", session_id="sess-1", model=None, effort=None), ["codex"], run, None)
    assert report["warnings"] == []
    assert report["model_actual"] == "gpt-6-astra"


def test_report_parses_adversarial_findings(sessions):
    findings = {"verdict": "ship", "summary": "fine", "findings": []}
    write_rollout(sessions, "sess-1", rollout_lines(last=json.dumps(findings)))
    run = cd.RunResult(exit_code=0, thread_id="sess-1", errors=[], agent_messages=[], duration_s=1.0)
    report = cd.build_report(request(intent="adversarial"), ["codex"], run, json.dumps(findings))
    assert report["findings"] == findings
    assert report["warnings"] == []


def test_turn_that_omits_a_field_does_not_inherit_the_previous_turn(sessions):
    lines = rollout_lines()
    lines.append(json.dumps({"type": "turn_context", "payload": {"turn_id": "turn-2", "model": "gpt-6-luna",
                                                                 "sandbox_policy": {"type": "danger-full-access"}}}))
    write_rollout(sessions, "sess-1", lines)
    summary = cd.load_summary("sess-1")
    assert (summary.model, summary.effort, summary.profile, summary.sandbox) == ("gpt-6-luna", None, None, "danger-full-access")


def test_resume_only_counts_a_turn_newer_than_the_ones_it_started_with(sessions):
    """A resumed session's file already has turns; reporting them would describe the previous run."""
    write_rollout(sessions, "sess-1", rollout_lines(model="gpt-6-astra", turn_id="turn-old"))
    prior = cd.load_summary("sess-1").turn_ids
    assert prior == {"turn-old"}

    stale = cd.load_summary("sess-1", wait_s=0, prior_turn_ids=prior)
    assert stale.model is None and stale.turns == 0, "no new turn yet: unverified, not the old values"

    lines = rollout_lines(model="gpt-6-astra", turn_id="turn-old")
    lines.append(json.dumps({"type": "turn_context", "payload": {"turn_id": "turn-new", "model": "gpt-6-sol", "effort": "high",
                                                                 "active_permission_profile": {"id": "development"},
                                                                 "sandbox_policy": {"type": "workspace-write"}}}))
    write_rollout(sessions, "sess-1", lines)
    fresh = cd.load_summary("sess-1", wait_s=0, prior_turn_ids=prior)
    assert (fresh.model, fresh.profile, fresh.turns) == ("gpt-6-sol", "development", 2)


def test_report_says_unverified_when_no_turn_matched(sessions):
    write_rollout(sessions, "sess-1", rollout_lines()[:1])
    run = cd.RunResult(exit_code=0, thread_id="sess-1", errors=[], agent_messages=[], duration_s=1.0)
    report = cd.build_report(request(), ["codex"], run, "text")
    assert report["model_actual"] is None and report["profile_actual"] is None
    assert report["warnings"] == ["no turn context recorded for this run; model, effort, and profile unverified"]


def test_load_summary_waits_for_codex_to_flush_turn_context(sessions):
    """Right after exit the rollout may hold only session_meta; the wait gives up cleanly on a deadline."""
    write_rollout(sessions, "sess-1", rollout_lines()[:1])
    assert cd.load_summary("sess-1", wait_s=0.6).turns == 0
    write_rollout(sessions, "sess-1", rollout_lines())
    assert cd.load_summary("sess-1", wait_s=5).turns == 1


def test_review_child_thread_is_matched_by_turn_id(sessions):
    """codex exec review records model and profile only in a child thread that names the parent."""
    write_rollout(sessions, "parent-1", [
        json.dumps({"type": "session_meta", "payload": {"id": "parent-1", "cli_version": "0.156.1", "cwd": "/repo"}}),
        json.dumps({"type": "event_msg", "payload": {"type": "task_started", "turn_id": "turn-B"}}),
        json.dumps({"type": "event_msg", "payload": {"type": "task_complete", "turn_id": "turn-B", "last_agent_message": "review text"}}),
    ])

    def child(name, **kw):
        lines = rollout_lines(**kw)
        lines[0] = json.dumps({"type": "session_meta", "payload": {"id": name, "parent_thread_id": "parent-1"}})
        write_rollout(sessions, name, lines)

    child("child-1", model="gpt-6-astra", profile="development", turn_id="turn-A")  # earlier run, different turn
    child("child-2", model="gpt-6-sol", profile="review", last="child text", turn_id="turn-B")
    write_rollout(sessions, "other", rollout_lines(model="gpt-6-luna", turn_id="turn-B"))  # not a child at all

    summary = cd.load_summary("parent-1")
    assert (summary.model, summary.profile, summary.sandbox, summary.turns) == ("gpt-6-sol", "review", "read-only", 1)
    assert summary.last_message == "review text"

    write_rollout(sessions, "child-2", [])  # with no child matching turn-B, nothing is attributed
    unmatched = cd.load_summary("parent-1")
    assert unmatched.model is None and unmatched.turns == 0

    child("child-2", model="gpt-6-sol", profile="review", turn_id="turn-B")
    resumed = cd.load_summary("parent-1", prior_turn_ids={"turn-B"})  # this run added nothing new
    assert resumed.model is None and resumed.turns == 0


def test_resume_runs_in_the_sessions_own_directory(sessions, tmp_path, monkeypatch):
    workspace = tmp_path / "worktree"
    workspace.mkdir()
    write_rollout(sessions, "sess-1", rollout_lines(cwd=str(workspace)))
    monkeypatch.setattr("sys.stdin", __import__("io").StringIO("continue"))
    args = cd.build_parser().parse_args(["resume", "sess-1", "--write"])
    req, stdin_text = cd.request_from_args(args)
    assert req.cwd == workspace.resolve()
    assert req.prior_turn_ids == {"turn-1"}
    assert req.profile == "development" and stdin_text == "continue"

    args = cd.build_parser().parse_args(["resume", "sess-1", "--cwd", str(tmp_path), "x"])
    req, _ = cd.request_from_args(args)
    assert req.cwd == tmp_path.resolve(), "an explicit --cwd still wins"
