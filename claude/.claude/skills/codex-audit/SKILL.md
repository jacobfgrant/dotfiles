---
name: codex-audit
description: Audit the codex-delegate wrapper against the installed Codex CLI. Runs doctor, reads Codex release notes since the validated version, checks the flags, config keys, model catalog, and effort names the wrapper assumes, and proposes edits. Run after a Codex update or when doctor warns about the version.
disable-model-invocation: true
allowed-tools: Bash(codex-delegate doctor*) Bash(codex-delegate show *) Bash(codex --version) Bash(codex debug models) Bash(codex exec --help) Bash(codex exec review --help) Bash(gh api repos/openai/codex/*) Read Grep Glob WebFetch
---

# Audit codex-delegate against the installed Codex

Source of truth for the wrapper: `~/.dotfiles/codex/.local/bin/codex-delegate`. Its `VALIDATED_CODEX_VERSION` constant records the last Codex release it was checked against.

## Scope

This is a compatibility check: did the installed Codex break an assumption the wrapper makes? It is not a security review or research project. Out of scope:

- model runs of any kind beyond doctor's own canaries, including "reply OK" probes
- raw `codex exec`
- trying out new attack surfaces or profile ideas
- web reading beyond the release notes and the one docs page in step 7

If something looks worth investigating, list it under follow-ups in the report and stop there. Scratch files go in the session scratchpad, never in a repository.

## Steps

1. Run `codex-delegate doctor`. Note every FAIL and skip. A FAIL is a bug to fix now; the version line shows how far the installed Codex is from the validated one, which the rest of this audit resolves.
2. Read the wrapper's constants: `VALIDATED_CODEX_VERSION`, `DEFAULT_MODEL`, `ESCALATION_MODEL`, `EFFORTS`, `PROJECT_CONFIG_FORBIDDEN_KEYS`, `REQUIRED_EXEC_FLAGS`, `REQUIRED_REVIEW_FLAGS`, `PROFILE_FOR_INTENT`, and the `summarize_rollout` field names (`turn_context.model`, `effort`, `active_permission_profile.id`, `sandbox_policy.type`, `session_meta.cli_version`, `task_complete.last_agent_message`).
3. List Codex releases from the validated version to the installed one:

   ```bash
   gh api 'repos/openai/codex/releases?per_page=30' --jq '.[] | select(.tag_name | test("alpha") | not) | "\(.tag_name) \(.published_at)\n\(.body)\n"'
   ```

   Stop at the validated tag; raise `per_page` only if it is not in the first page. Skim for: renamed or removed `codex exec` flags, changes to permission profiles or `default_permissions`, sandbox behaviour, session rollout format, model retirements, effort levels, and anything about `--sandbox` precedence.
4. Compare `codex exec --help` and `codex exec review --help` against `REQUIRED_EXEC_FLAGS` and `REQUIRED_REVIEW_FLAGS`. Check the config reference for new project-level keys that could affect the sandbox, approvals, or the model provider; any such key belongs in `PROJECT_CONFIG_FORBIDDEN_KEYS`.
5. Compare `codex debug models` against `DEFAULT_MODEL`, `ESCALATION_MODEL`, and `EFFORTS`. Flag retirements (`upgrade.retirement_at`) and new flagship models.
6. Find the newest session file under `~/.codex/sessions/` (Glob `**/rollout-*.jsonl`) and compare it against the field names in step 2. Use `codex-delegate show <id>` on it; every header line should be populated.
7. Only if the release notes from step 3 mention permissions, profiles, or the sandbox: read the permissions docs (https://learn.chatgpt.com/docs/permissions) for capabilities that would let the `review` profile be tighter, such as a working way to deny all of `~` while keeping the workspace and gitconfig readable. Report what is new; do not experiment with it. If the page does not load, say so and move on.

If doctor is green and steps 3 to 6 find nothing, skip to the report and keep it to a few lines.

## Report

Summarize as: what changed in Codex, what in the wrapper or `config.toml` needs to change, what can stay, and any follow-ups. Propose concrete edits but do not apply them unless asked.

`VALIDATED_CODEX_VERSION` records that an audit happened, not that something changed. Always propose bumping it to the installed version:

- with edits: once the user approves and they are in, bump it in the same commit, run the unit tests and `codex-delegate doctor`, and commit
- with nothing to change: propose the bump as its own one-line commit

Never install, update, or reconfigure Codex as part of the audit.
