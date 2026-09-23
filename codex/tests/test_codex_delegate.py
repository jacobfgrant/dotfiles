"""Unit tests for codex-delegate. No Codex or model calls; the canary run is the integration test."""

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


def test_review_uses_native_reviewer_with_review_profile():
    argv = cd.build_command(request(intent="review", base="master"), OUT)
    assert argv[:5] == ["codex", "exec", "review", "--base", "master"]
    assert cd.config_override("default_permissions", "review") == argv[5:7]
    assert cd.config_override("model_reasoning_effort", "high") == argv[7:9]
    assert "--model" in argv and argv[argv.index("--model") + 1] == "gpt-6-sol"
    assert "--json" in argv and str(OUT) in argv
    assert argv[-1] != "-", "review takes no prompt"


def test_review_defaults_to_uncommitted():
    argv = cd.build_command(request(intent="review"), OUT)
    assert "--uncommitted" in argv and "--base" not in argv


def test_adversarial_reads_prompt_from_stdin_and_uses_schema():
    argv = cd.build_command(request(intent="adversarial", base="main"), OUT, SCHEMA)
    assert argv[:2] == ["codex", "exec"] and "review" not in argv
    assert argv[argv.index("--output-schema") + 1] == str(SCHEMA)
    assert argv[-1] == "-"
    assert '-c' in argv and 'default_permissions="review"' in argv


def test_consult_requires_model():
    with pytest.raises(cd.DelegateError, match="consult requires --model"):
        cd.build_command(request(intent="consult", model=""), OUT)


def test_implement_uses_development_profile_and_worktree():
    argv = cd.build_command(request(intent="implement", worktree=True), OUT)
    assert 'default_permissions="development"' in argv
    assert "--worktree" in argv


def test_worktree_rejected_outside_implement():
    with pytest.raises(cd.DelegateError, match="--worktree only applies"):
        cd.build_command(request(intent="consult", worktree=True), OUT)


def test_resume_profile_follows_write_flag():
    read_only = cd.build_command(request(intent="resume", session_id="abc"), OUT)
    writable = cd.build_command(request(intent="resume", session_id="abc", write=True), OUT)
    assert read_only[1:4] == ["exec", "resume", "abc"]
    assert 'default_permissions="review"' in read_only
    assert 'default_permissions="development"' in writable


def test_resume_requires_session_id():
    with pytest.raises(cd.DelegateError, match="session id"):
        cd.build_command(request(intent="resume"), OUT)


def test_bad_effort_rejected():
    with pytest.raises(cd.DelegateError, match="effort must be one of"):
        cd.build_command(request(effort="turbo"), OUT)


@pytest.mark.parametrize("flag", ["--sandbox", "-s", "--dangerously-bypass-approvals-and-sandbox", "--ignore-rules", "--ephemeral"])
def test_forbidden_pass_through_flags_refused(flag):
    with pytest.raises(cd.DelegateError, match="not allowed"):
        cd.build_command(request(extra_args=[flag, "x"]), OUT)


def test_forbidden_flag_with_equals_refused():
    with pytest.raises(cd.DelegateError):
        cd.build_command(request(extra_args=["--sandbox=read-only"]), OUT)


def test_allowed_pass_through_flag_forwarded():
    argv = cd.build_command(request(extra_args=["--search"]), OUT)
    assert "--search" in argv


def test_no_forbidden_flag_ever_emitted():
    for intent, extra in (("review", {}), ("adversarial", {}), ("consult", {}), ("implement", {"worktree": True})):
        argv = cd.build_command(request(intent=intent, **extra), OUT, SCHEMA if intent == "adversarial" else None)
        assert not any(arg in cd.FORBIDDEN_FLAGS for arg in argv), argv


# --- event parsing ---


def test_parse_event_ignores_noise():
    assert cd.parse_event("not json") is None
    assert cd.parse_event('{"type": "thread.started", "thread_id": "t1"}')["thread_id"] == "t1"


# --- rollout summaries ---


def rollout_lines(model="gpt-6-sol", effort="high", profile="review", sandbox="read-only", last="done"):
    records = [
        {"type": "session_meta", "payload": {"id": "sess-1", "cli_version": "0.156.1", "cwd": "/repo"}},
        {
            "type": "turn_context",
            "payload": {
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


def test_summarize_rollout_reads_model_profile_and_message():
    summary = cd.summarize_rollout(rollout_lines())
    assert summary.session_id == "sess-1"
    assert summary.cli_version == "0.156.1"
    assert (summary.model, summary.effort, summary.profile, summary.sandbox) == ("gpt-6-sol", "high", "review", "read-only")
    assert summary.approval_policy == "on-request"
    assert summary.last_message == "done"
    assert summary.turns == 1


def test_find_rollout_by_session_id(tmp_path):
    day = tmp_path / "sessions" / "2026" / "09" / "22"
    day.mkdir(parents=True)
    target = day / "rollout-2026-09-22T10-00-00-sess-1.jsonl"
    target.write_text("\n".join(rollout_lines()))
    (day / "rollout-2026-09-22T11-00-00-sess-2.jsonl").write_text("")
    assert cd.find_rollout("sess-1", tmp_path) == target
    assert cd.find_rollout("missing", tmp_path) is None


def test_report_flags_model_and_profile_mismatch(tmp_path, monkeypatch):
    day = tmp_path / "sessions" / "2026" / "09" / "22"
    day.mkdir(parents=True)
    (day / "rollout-x-sess-1.jsonl").write_text("\n".join(rollout_lines(model="gpt-6-luna", profile="development")))
    monkeypatch.setenv("CODEX_HOME", str(tmp_path))
    run = cd.RunResult(exit_code=0, thread_id="sess-1", errors=[], agent_messages=[], duration_s=1.0)
    report = cd.build_report(request(intent="consult"), ["codex"], run, None)
    assert report["model_actual"] == "gpt-6-luna"
    assert any("model mismatch" in w for w in report["warnings"])
    assert any("profile mismatch" in w for w in report["warnings"])
    assert report["message"] == "done"


def test_report_parses_adversarial_findings(tmp_path, monkeypatch):
    findings = {"verdict": "ship", "summary": "fine", "findings": []}
    day = tmp_path / "sessions" / "2026" / "09" / "22"
    day.mkdir(parents=True)
    (day / "rollout-x-sess-1.jsonl").write_text("\n".join(rollout_lines(last=json.dumps(findings))))
    monkeypatch.setenv("CODEX_HOME", str(tmp_path))
    run = cd.RunResult(exit_code=0, thread_id="sess-1", errors=[], agent_messages=[], duration_s=1.0)
    report = cd.build_report(request(intent="adversarial"), ["codex"], run, json.dumps(findings))
    assert report["findings"] == findings
    assert report["warnings"] == []


def test_report_warns_when_rollout_missing(tmp_path, monkeypatch):
    monkeypatch.setenv("CODEX_HOME", str(tmp_path))
    run = cd.RunResult(exit_code=1, thread_id="nope", errors=["boom"], agent_messages=["partial"], duration_s=1.0)
    report = cd.build_report(request(), ["codex"], run, None)
    assert report["model_actual"] is None
    assert any("rollout not found" in w for w in report["warnings"])
    assert any("boom" in w for w in report["warnings"])
    assert report["message"] == "partial"


# --- doctor checks ---


def test_check_flags_reports_missing():
    assert cd.check_flags("x", "--json --model", ("--json", "--model")).ok
    check = cd.check_flags("x", "--json", ("--json", "--model"))
    assert not check.ok and "--model" in check.detail


def test_check_models_requires_default_and_escalation_with_high_effort():
    high = [{"effort": "high"}]
    ok = json.dumps({"models": [
        {"slug": "gpt-6-sol", "visibility": "list", "supported_reasoning_levels": high},
        {"slug": "gpt-6-astra", "visibility": "list", "supported_reasoning_levels": high},
    ]})
    assert cd.check_models(ok).ok
    missing = json.dumps({"models": [{"slug": "gpt-6-sol", "supported_reasoning_levels": high}]})
    assert not cd.check_models(missing).ok
    no_high = json.dumps({"models": [
        {"slug": "gpt-6-sol", "supported_reasoning_levels": [{"effort": "low"}]},
        {"slug": "gpt-6-astra", "supported_reasoning_levels": high},
    ]})
    assert not cd.check_models(no_high).ok
    assert not cd.check_models("garbage").ok


def test_check_config_file_detects_legacy_and_missing_profiles():
    good = 'default_permissions = "development"\n[permissions.review]\nextends = ":read-only"\n[permissions.development]\nextends = ":workspace"\n'
    assert cd.check_config_file(good).ok
    legacy = 'sandbox_mode = "read-only"\n' + good
    assert "sandbox_mode" in cd.check_config_file(legacy).detail
    assert "[permissions.review]" in cd.check_config_file('default_permissions = "x"\n[permissions.development]\n').detail
    assert not cd.check_config_file("not = [toml").ok


def test_check_codex_doctor_reads_config_and_auth_status():
    ok = json.dumps({"checks": {"config.load": {"status": "ok"}, "auth.credentials": {"status": "ok"}}})
    assert cd.check_codex_doctor(ok).ok
    bad = json.dumps({"checks": {"config.load": {"status": "fail"}, "auth.credentials": {"status": "ok"}}})
    assert "config.load: fail" in cd.check_codex_doctor(bad).detail
    assert not cd.check_codex_doctor("nope").ok
