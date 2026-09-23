"""Unit tests for codex-delegate. No Codex or model calls; `codex-delegate doctor` is the integration test."""

import json
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


@pytest.mark.parametrize(
    "extra",
    [
        ["--sandbox", "read-only"],
        ["--sandbox=read-only"],
        ["-s", "read-only"],
        ["-c", 'default_permissions="development"'],
        ['-cdefault_permissions="development"'],
        ['--config=default_permissions="x"'],
        ["-p", "other"],
        ["--add-dir", "/"],
        ["--dangerously-bypass-approvals-and-sandbox"],
        ["--ignore-rules"],
    ],
)
def test_pass_through_cannot_weaken_the_sandbox(extra):
    """A profile override or bypass smuggled through --codex-arg must never reach codex, in any spelling."""
    with pytest.raises(cd.DelegateError, match="not allowed"):
        cd.build_command(request(extra_args=extra), OUT)


def test_only_pinned_config_overrides_are_emitted():
    """The wrapper's own -c overrides are the profile and effort pins; harmless pass-through is kept."""
    for intent, extra in (("review", {}), ("adversarial", {}), ("consult", {}), ("implement", {"worktree": True})):
        argv = cd.build_command(request(intent=intent, extra_args=["--search"], **extra), OUT, SCHEMA if intent == "adversarial" else None)
        overrides = [argv[i + 1] for i, arg in enumerate(argv) if arg == "-c"]
        assert all(o.startswith(("default_permissions=", "model_reasoning_effort=")) for o in overrides), argv
        assert not [arg for arg in argv if arg != "-c" and arg in cd.FORBIDDEN_FLAGS], argv
        assert "--search" in argv


# --- session rollouts: what actually ran ---


def rollout_lines(model="gpt-6-sol", effort="high", profile="review", sandbox="read-only", last="done", turn_id="turn-1"):
    records = [
        {"type": "session_meta", "payload": {"id": "sess-1", "cli_version": "0.156.1", "cwd": "/repo"}},
        {
            "type": "turn_context",
            "payload": {
                "turn_id": turn_id,
                "model": model,
                "effort": effort,
                "cwd": "/repo",
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
