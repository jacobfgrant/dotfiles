---
name: codex-audit
description: Audit the codex-delegate wrapper against the installed Codex CLI. Runs doctor, reads Codex release notes since the validated version, checks the flags, config keys, model catalog, and effort names the wrapper assumes, and proposes edits. Run after a Codex update or when doctor warns about the version.
disable-model-invocation: true
allowed-tools: Bash(codex-delegate *) Bash(codex --version) Bash(codex debug models) Bash(codex exec --help) Bash(codex exec review --help) Bash(gh api repos/openai/codex/*) Read Grep WebFetch
---

# Audit codex-delegate against the installed Codex

Source of truth for the wrapper: `~/.dotfiles/codex/.local/bin/codex-delegate`. Its `VALIDATED_CODEX_VERSION` constant records the last Codex release it was checked against.

## Steps

1. Run `codex-delegate doctor`. Note every WARN and FAIL. A FAIL is a bug to fix now; a version WARN is what the rest of this audit resolves.
2. Read the wrapper's constants: `VALIDATED_CODEX_VERSION`, `DEFAULT_MODEL`, `ESCALATION_MODEL`, `EFFORTS`, `FORBIDDEN_FLAGS`, `REQUIRED_EXEC_FLAGS`, `REQUIRED_REVIEW_FLAGS`, `PROFILE_FOR_INTENT`, and the `summarize_rollout` field names (`turn_context.model`, `effort`, `active_permission_profile.id`, `sandbox_policy.type`, `session_meta.cli_version`, `task_complete.last_agent_message`).
3. List Codex releases from the validated version to the installed one:

   ```bash
   gh api repos/openai/codex/releases --paginate --jq '.[] | select(.tag_name | test("alpha") | not) | "\(.tag_name) \(.published_at)\n\(.body)\n"'
   ```

   Stop at the validated tag. Skim for: renamed or removed `codex exec` flags, changes to permission profiles or `default_permissions`, sandbox behaviour, session rollout format, model retirements, effort levels, and anything about `--sandbox` precedence.
4. Compare `codex exec --help` and `codex exec review --help` against `REQUIRED_EXEC_FLAGS` and `REQUIRED_REVIEW_FLAGS`, and confirm nothing in `FORBIDDEN_FLAGS` has been renamed into something the wrapper no longer catches.
5. Compare `codex debug models` against `DEFAULT_MODEL`, `ESCALATION_MODEL`, and `EFFORTS`. Flag retirements (`upgrade.retirement_at`) and new flagship models.
6. Compare the newest session file under `~/.codex/sessions/` against the field names in step 2. Use `codex-delegate show <id>` on it; every header line should be populated.
7. Re-read the permissions docs (https://learn.chatgpt.com/docs/permissions) for new profile capabilities that would let the `review` profile be tighter, such as a working way to deny all of `~` while keeping the workspace and gitconfig readable.

## Report

Summarize as: what changed in Codex, what in the wrapper or `config.toml` needs to change, and what can stay. Propose concrete edits but do not apply them unless asked. When the user approves and the edits are in, bump `VALIDATED_CODEX_VERSION` to the installed version, run the unit tests (`.venv/bin/pytest codex/tests` from the dotfiles root) and `codex-delegate doctor`, and commit.

Never install, update, or reconfigure Codex as part of the audit.
