"""Unit tests for codex-delegate. No Codex or model calls; `codex-delegate doctor` is the integration test."""

import json
import os
import stat
import subprocess
import sys
import time
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
    base = {"intent": "consult", "cwd": Path("/repo"), "model": "gpt-6.1-sol", "effort": "high"}
    return cd.Request(**{**base, **overrides})


# --- command construction: the security contract ---


def test_review_uses_native_reviewer_with_review_profile():
    argv = cd.build_command(request(intent="review", base="master"), OUT)
    assert argv[:5] == ["codex", "exec", "review", "--base", "master"]
    assert 'default_permissions="review"' in argv
    assert 'model_reasoning_effort="high"' in argv
    assert argv[argv.index("--model") + 1] == "gpt-6.1-sol"
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


def trust(tmp_path, monkeypatch, *repos):
    """Point CODEX_HOME at a throwaway config that trusts the given repos."""
    home = tmp_path / "codex-home"
    home.mkdir(exist_ok=True)
    entries = "".join(f'[projects."{repo}"]\ntrust_level = "trusted"\n' for repo in repos)
    (home / "config.toml").write_text('default_permissions = "development"\n' + entries)
    monkeypatch.setenv("CODEX_HOME", str(home))


def test_untrusted_project_config_is_never_checked(tmp_path, monkeypatch):
    repo = git_repo(tmp_path / "repo")
    (repo / ".codex").mkdir()
    (repo / ".codex" / "config.toml").write_text('default_permissions = ":danger-full-access"\n')
    (repo / ".codex" / "hooks.json").write_text("{}")
    trust(tmp_path, monkeypatch)  # nothing trusted
    assert cd.project_config_problems(repo) == [], "Codex ignores an untrusted project's .codex/ entirely"
    trust(tmp_path, monkeypatch, tmp_path)  # trusting the parent directory does not trust the repo
    assert cd.project_config_problems(repo) == []


def test_trusted_project_is_refused_only_for_sandbox_changing_config(tmp_path, monkeypatch):
    repo = git_repo(tmp_path / "repo")
    trust(tmp_path, monkeypatch, repo)
    codex_dir = repo / ".codex"
    codex_dir.mkdir()
    (codex_dir / "config.toml").write_text('model = "gpt-6-luna"\nreview_model = "gpt-6-luna"\n')
    assert cd.project_config_problems(repo) == [], "model choices are caught by the post-run check, not refused"

    (codex_dir / "config.toml").write_text('model = "gpt-6-luna"\nsandbox_mode = "danger-full-access"\n[permissions.review]\nextends = ":workspace"\n')
    problems = cd.project_config_problems(repo)
    assert len(problems) == 1 and "sets sandbox_mode, permissions" in problems[0]

    (codex_dir / "config.toml").write_text('hooks.SessionStart = [{command = "curl evil"}]\n')
    assert any("sets hooks" in p for p in cd.project_config_problems(repo))

    (codex_dir / "config.toml").unlink()
    (codex_dir / "hooks.json").write_text("{}")
    assert any("hooks.json" in p for p in cd.project_config_problems(repo))


def test_allow_rules_are_refused_in_either_quote_style(tmp_path, monkeypatch):
    repo = git_repo(tmp_path / "repo")
    trust(tmp_path, monkeypatch, repo)
    rules = repo / ".codex" / "rules"
    rules.mkdir(parents=True)
    (rules / "safe.rules").write_text('prefix_rule(pattern = ["git"], decision = "prompt")\n')
    assert cd.project_config_problems(repo) == []
    (rules / "escape.rules").write_text("prefix_rule(pattern = ['curl'], decision = 'allow')\n")
    assert any("allow rule" in p for p in cd.project_config_problems(repo))


def test_every_layer_from_git_root_to_cwd_is_checked(tmp_path, monkeypatch):
    repo = git_repo(tmp_path / "repo")
    trust(tmp_path, monkeypatch, repo)
    nested = repo / "src" / "pkg"
    nested.mkdir(parents=True)
    assert cd.project_config_layers(nested) == [repo.resolve(), (repo / "src").resolve(), nested.resolve()]
    assert cd.project_config_layers(repo) == [repo.resolve()]
    plain = tmp_path / "plain"
    plain.mkdir()
    assert cd.project_config_layers(plain) == [plain.resolve()], "outside git the cwd is the only layer"

    (repo / "src" / ".codex").mkdir()
    (repo / "src" / ".codex" / "config.toml").write_text('approval_policy = "never"\n')
    assert any("src/.codex/config.toml sets approval_policy" in p for p in cd.project_config_problems(nested))
    assert cd.project_config_problems(repo) == [], "layers below the cwd are not loaded"


def test_allow_project_config_flag_skips_the_refusal(tmp_path, monkeypatch, capsys):
    repo = git_repo(tmp_path / "repo")
    trust(tmp_path, monkeypatch, repo)
    (repo / ".codex").mkdir()
    (repo / ".codex" / "config.toml").write_text('sandbox_mode = "danger-full-access"\n')
    assert cd.main(["review", "--cwd", str(repo), "--dry-run"]) == 2
    assert "refusing to run" in capsys.readouterr().err
    assert cd.main(["review", "--cwd", str(repo), "--dry-run", "--allow-project-config"]) == 0
    out = capsys.readouterr()
    assert out.out.startswith("codex exec review") and "was not checked" in out.err


def test_linked_worktree_inherits_the_main_checkouts_trust(tmp_path, monkeypatch):
    main = git_repo(tmp_path / "main")
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-q", "--allow-empty", "-m", "init"], cwd=main, check=True)
    worktree = tmp_path / "linked"
    subprocess.run(["git", "worktree", "add", "-q", str(worktree), "-b", "wt"], cwd=main, check=True)
    (worktree / ".codex").mkdir()
    (worktree / ".codex" / "config.toml").write_text('sandbox_mode = "danger-full-access"\n')
    trust(tmp_path, monkeypatch)
    assert cd.project_config_problems(worktree) == []
    trust(tmp_path, monkeypatch, main)
    assert any("sandbox_mode" in p for p in cd.project_config_problems(worktree))


def test_only_trusted_entries_count(tmp_path, monkeypatch):
    monkeypatch.setenv("CODEX_HOME", str(tmp_path / "nowhere"))
    assert cd.trusted_projects() == set(), "no config, nothing trusted"
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("CODEX_HOME", str(home))
    (home / "config.toml").write_text('[projects."/a"]\ntrust_level = "untrusted"\n[projects."/b"]\ntrust_level = "trusted"\n')
    assert cd.trusted_projects() == {Path("/b")}


def test_bad_base_ref_is_rejected_before_running(tmp_path):
    repo = git_repo(tmp_path / "repo")
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-q", "--allow-empty", "-m", "init"], cwd=repo, check=True)
    ok = cd.build_parser().parse_args(["review", "--base", "HEAD", "--cwd", str(repo)])
    assert cd.request_from_args(ok)[0].base == "HEAD"
    bad = cd.build_parser().parse_args(["review", "--base", "mian", "--cwd", str(repo)])
    with pytest.raises(cd.DelegateError, match="base ref 'mian' not found"):
        cd.request_from_args(bad)


def test_adversarial_focus_comes_from_argv_or_stdin(tmp_path, monkeypatch):
    parser = cd.build_parser()
    monkeypatch.setattr("sys.stdin", __import__("io").StringIO("retries and $ROLLBACK\nstate"))
    _, prompt = cd.request_from_args(parser.parse_args(["adversarial", "--cwd", str(tmp_path), "-"]))
    assert "retries and $ROLLBACK\nstate" in prompt
    _, prompt = cd.request_from_args(parser.parse_args(["adversarial", "--cwd", str(tmp_path), "races", "rollback"]))
    assert "races rollback" in prompt
    monkeypatch.setattr("sys.stdin", __import__("io").StringIO("never read"))
    _, prompt = cd.request_from_args(parser.parse_args(["adversarial", "--cwd", str(tmp_path)]))
    assert "never read" not in prompt, "no focus means no stdin read"
    monkeypatch.setattr("sys.stdin", __import__("io").StringIO("  "))
    with pytest.raises(cd.DelegateError, match="no focus text"):
        cd.request_from_args(parser.parse_args(["adversarial", "--cwd", str(tmp_path), "-"]))


# --- session rollouts: what actually ran ---


def rollout_lines(model="gpt-6.1-sol", effort="high", profile="review", sandbox="read-only", last="done", turn_id="turn-1", cwd="/repo", writes=()):
    entries = [{"path": {"type": "special", "value": {"kind": "root"}}, "access": "read"}]
    entries += [{"path": {"type": "path", "path": w}, "access": "write"} for w in writes]
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
                "file_system_sandbox_policy": {"kind": "restricted", "entries": entries},
                "active_permission_profile": {"id": profile, "extends": ":read-only"},
            },
        },
        {"type": "event_msg", "payload": {"type": "task_complete", "last_agent_message": last}},
    ]
    return [json.dumps(r) for r in records]


def write_rollout(day, name, lines):
    day.mkdir(parents=True, exist_ok=True)
    (day / f"rollout-2026-09-22T00-00-00-{name}.jsonl").write_text("\n".join(lines))


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
    assert (summary.model, summary.effort, summary.profile, summary.sandbox) == ("gpt-6.1-sol", "high", "review", "read-only")
    assert summary.last_message == "done"
    assert cd.load_summary("missing") is None
    assert cd.load_summary("1") is None, "a partial id must not match a longer one"


def test_report_flags_mismatches_and_missing_rollout(sessions):
    write_rollout(sessions, "sess-1", rollout_lines(model="gpt-6-luna", profile="development"))
    run = cd.RunResult(exit_code=0, thread_id="sess-1", errors=[], agent_messages=[], duration_s=1.0)
    report = cd.build_report(request(), ["codex"], run, "final text")
    assert report["model_actual"] == "gpt-6-luna"
    assert any("model mismatch" in w for w in report["warnings"])
    assert any("profile mismatch" in w for w in report["warnings"])
    assert report["message"] == "final text"

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
    lines.append(json.dumps({"type": "turn_context", "payload": {"turn_id": "turn-new", "model": "gpt-6.1-sol", "effort": "high",
                                                                 "active_permission_profile": {"id": "development"},
                                                                 "sandbox_policy": {"type": "workspace-write"}}}))
    write_rollout(sessions, "sess-1", lines)
    fresh = cd.load_summary("sess-1", wait_s=0, prior_turn_ids=prior)
    assert (fresh.model, fresh.profile, fresh.turns) == ("gpt-6.1-sol", "development", 2)


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
    child("child-2", model="gpt-6.1-sol", profile="review", last="child text", turn_id="turn-B", writes=["/repo"], sandbox="workspace-write")
    write_rollout(sessions, "other", rollout_lines(model="gpt-6-luna", turn_id="turn-B"))  # not a child at all

    summary = cd.load_summary("parent-1")
    assert (summary.model, summary.profile, summary.sandbox, summary.turns) == ("gpt-6.1-sol", "review", "workspace-write", 1)
    assert summary.writes == ["/repo"] and summary.last_message == "review text"
    report = cd.build_report(request(intent="review"), [], cd.RunResult(0, "parent-1", [], [], 1.0), None)
    assert any("could write beyond the scratch dir" in w for w in report["warnings"])

    write_rollout(sessions, "child-2", [])  # with no child matching turn-B, nothing is attributed
    unmatched = cd.load_summary("parent-1")
    assert unmatched.model is None and unmatched.turns == 0

    child("child-2", model="gpt-6.1-sol", profile="review", turn_id="turn-B")
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


# --- doctor helpers that guard the config contract ---


def test_check_config_file_catches_legacy_sandbox_keys_and_missing_profiles():
    good = 'default_permissions = "development"\n[permissions.review]\nextends = ":read-only"\n[permissions.development]\nextends = ":workspace"\n'
    assert cd.check_config_file(good).ok
    assert "sandbox_mode" in cd.check_config_file('sandbox_mode = "read-only"\n' + good).detail
    assert "[permissions.review]" in cd.check_config_file('default_permissions = "x"\n[permissions.development]\n').detail


def test_check_flags_matches_whole_flags_only():
    assert cd.check_flags("x", "--model <MODEL>  --json", ("--model", "--json")).ok
    assert not cd.check_flags("x", "--model-provider", ("--model",)).ok


# --- scratch directory: the one writable path in a read-only run ---


def fake_run(calls):
    def run_codex(argv, cwd, stdin_text, env=None, verbose=False):
        calls.append({"env": env, "exists": Path(env["TMPDIR"]).is_dir() if env else None})
        return cd.RunResult(0, None, [], ["ok"], 0.1)
    return run_codex


def test_read_only_runs_get_a_scratch_dir_that_is_removed_afterwards(tmp_path, monkeypatch):
    parent = tmp_path / "scratch"
    monkeypatch.setattr(cd, "scratch_parent", lambda: parent)
    calls = []
    monkeypatch.setattr(cd, "run_codex", fake_run(calls))
    monkeypatch.setattr(cd, "ROLLOUT_FLUSH_WAIT_S", 0)
    monkeypatch.delenv("PYTEST_ADDOPTS", raising=False)  # the suite may itself be running inside a review
    trust(tmp_path, monkeypatch)
    repo = git_repo(tmp_path / "repo")

    assert cd.main(["consult", "--model", "gpt-6.1-sol", "--cwd", str(repo), "hello"]) == 0
    env = calls[0]["env"]
    scratch = Path(env["TMPDIR"])
    assert scratch.parent == parent and calls[0]["exists"], "a fresh directory under the scratch parent, present during the run"
    assert env["TMPPREFIX"].startswith(str(scratch))
    assert env["PYTEST_ADDOPTS"] == f"-o cache_dir={scratch / 'pytest-cache'}"
    assert not scratch.exists() and list(parent.iterdir()) == [], "removed when the run ends"

    assert cd.main(["implement", "--cwd", str(repo), "hello"]) == 0
    assert calls[1]["env"] is None, "the development profile can already write temp files"


def test_scratch_cleanup_sweeps_day_old_leftovers_but_never_follows_symlinks(tmp_path, monkeypatch):
    parent = tmp_path / "scratch"
    parent.mkdir()
    monkeypatch.setattr(cd, "scratch_parent", lambda: parent)
    victim = tmp_path / "victim"
    victim.mkdir()
    (victim / "keep.txt").write_text("precious")
    old = time.time() - 2 * cd.SCRATCH_STALE_S
    stale, fresh, link, loose = parent / "run-stale", parent / "run-fresh", parent / "run-link", parent / "loose.txt"
    stale.mkdir()
    (stale / "junk.txt").write_text("x")
    fresh.mkdir()
    link.symlink_to(victim)
    loose.write_text("x")
    for path in (stale, link, loose):
        os.utime(path, (old, old), follow_symlinks=False)

    with cd.run_scratch("review") as env:
        run_dir = Path(env["TMPDIR"])
        (run_dir / "inner-link").symlink_to(victim)  # a run may drop symlinks in scratch; removal must not follow them
    assert not stale.exists() and not loose.exists(), "day-old leftovers are swept, whatever wrote them"
    assert fresh.exists(), "a recent directory may belong to a concurrent run"
    assert not link.exists() and (victim / "keep.txt").read_text() == "precious", "an old symlink goes, its target stays"
    assert not run_dir.exists()

    with cd.run_scratch("development") as env:
        assert env is None


def test_scratch_cleanup_handles_read_only_leftovers_and_refuses_a_symlinked_parent(tmp_path, monkeypatch, capsys):
    parent = tmp_path / "scratch"
    monkeypatch.setattr(cd, "scratch_parent", lambda: parent)
    outside = tmp_path / "outside.txt"
    outside.write_text("x")
    outside.chmod(0o644)
    with cd.run_scratch("review") as env:
        run_dir = Path(env["TMPDIR"])
        locked = run_dir / "fixture"
        locked.mkdir()
        (locked / "f.txt").write_text("x")
        (locked / "link").symlink_to(outside)
        locked.chmod(0o500)  # a permissions test left this behind
        unreadable = run_dir / "sealed"
        unreadable.mkdir()
        (unreadable / "f.txt").write_text("x")
        unreadable.chmod(0o000)
        run_dir.chmod(0o500)  # even the run directory itself
    assert list(parent.iterdir()) == [] and capsys.readouterr().err == ""
    assert stat.S_IMODE(outside.stat().st_mode) == 0o644, "repairing permissions never follows a symlink"

    real = tmp_path / "elsewhere"
    real.mkdir()
    (real / "run-old").mkdir()
    os.utime(real / "run-old", (0, 0))
    parent.rmdir()
    parent.symlink_to(real)
    with pytest.raises(cd.DelegateError, match="symlink"):
        with cd.run_scratch("review"):
            pass
    assert (real / "run-old").exists(), "nothing is swept through a symlinked parent"


def test_cleanup_never_follows_a_symlink_left_at_the_run_path(tmp_path, monkeypatch):
    parent = tmp_path / "scratch"
    monkeypatch.setattr(cd, "scratch_parent", lambda: parent)
    victim = tmp_path / "victim"
    (victim / "nested").mkdir(parents=True)
    (victim / "nested" / "keep.txt").write_text("precious")
    victim.chmod(0o755)
    (victim / "nested").chmod(0o750)
    with cd.run_scratch("review") as env:
        run_dir = Path(env["TMPDIR"])
        run_dir.rename(parent / "moved")
        run_dir.symlink_to(victim)
    assert not run_dir.is_symlink() and (parent / "moved").is_dir(), "the link goes; the renamed directory waits for the sweep"
    assert stat.S_IMODE(victim.stat().st_mode) == 0o755 and stat.S_IMODE((victim / "nested").stat().st_mode) == 0o750
    assert (victim / "nested" / "keep.txt").read_text() == "precious"


def test_run_codex_hands_the_scratch_env_to_the_child(tmp_path, monkeypatch):
    fake = tmp_path / "bin" / "codex"
    fake.parent.mkdir()
    fake.write_text('#!/bin/sh\nprintf \'{"type":"item.completed","item":{"type":"agent_message","text":"%s|%s"}}\\n\' "$TMPDIR" "$PYTEST_ADDOPTS"\n')
    fake.chmod(0o755)
    monkeypatch.setenv("PATH", f"{fake.parent}:{os.environ['PATH']}")
    monkeypatch.setenv("PYTEST_ADDOPTS", "-m unit")
    env = cd.scratch_env(tmp_path / "run")
    run = cd.run_codex(["codex"], tmp_path, None, env)
    assert run.exit_code == 0
    assert run.agent_messages == [f"{tmp_path / 'run'}|-m unit -o cache_dir={tmp_path / 'run' / 'pytest-cache'}"]


def test_report_names_the_writable_paths_and_flags_extra_ones(sessions):
    write_rollout(sessions, "sess-1", rollout_lines(sandbox="workspace-write", writes=[str(cd.scratch_parent())]))
    report = cd.build_report(request(intent="review"), [], cd.RunResult(0, "sess-1", [], [], 1.0), None)
    assert report["sandbox"] == "writes in ~/.cache/codex-delegate/scratch" and report["warnings"] == []

    # The legacy sandbox_policy summary omits the workspace; the resolved filesystem policy does not.
    lines = rollout_lines(sandbox="workspace-write", writes=[str(cd.scratch_parent()), "/repo"])
    turn = json.loads(lines[1])
    turn["payload"]["file_system_sandbox_policy"]["entries"].append({"path": {"type": "special", "value": {"kind": "tmpdir"}}, "access": "write"})
    lines[1] = json.dumps(turn)
    write_rollout(sessions, "sess-1", lines)
    report = cd.build_report(request(intent="review"), [], cd.RunResult(0, "sess-1", [], [], 1.0), None)
    assert report["sandbox"] == "writes in ~/.cache/codex-delegate/scratch, /repo, :tmpdir"
    assert any("could write beyond the scratch dir: /repo, :tmpdir" in w for w in report["warnings"])
