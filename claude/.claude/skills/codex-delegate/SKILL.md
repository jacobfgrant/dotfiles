---
name: codex-delegate
description: Contract for delegating to OpenAI models (GPT-6 Sol, GPT-6 Astra) through the local Codex CLI via the codex-delegate wrapper and the codex-reviewer, codex-consult, and codex-implementer agents. Load when asked for a second opinion, an independent or adversarial review, a Codex or GPT or Astra or Sol run, or when deciding whether to hand work to another model.
user-invocable: false
---

# Delegating to Codex

`codex-delegate` (in `~/.local/bin`, source in `~/.dotfiles/codex/.local/bin/`) runs `codex exec` with the permission profile, model, effort, and flags pinned per intent, then reports what actually ran by reading the Codex session file. It never passes `--sandbox` or any bypass flag, so the profile in `~/.codex/config.toml` always governs access.

## Intents

| Subcommand | Profile | Access | Default |
|---|---|---|---|
| `review [--base REF \| --uncommitted]` | review | read-only, no network, secrets denied | gpt-6-sol / high |
| `adversarial [--base REF \| --uncommitted] [FOCUS...]` | review | same | gpt-6-sol / high |
| `consult --model M [PROMPT \| -]` | review | same | model required, high |
| `implement [--worktree] [PROMPT \| -]` | development | workspace writes, no network, secrets denied | gpt-6-sol / high |
| `resume SESSION_ID [--write] [PROMPT \| -]` | review, or development with `--write` | as above | inherits |
| `show SESSION_ID` | none | reads the session file | |
| `doctor [--skip-canary]` | none | no model calls | |

Common flags: `--model`, `--effort {low,medium,high,xhigh,max,ultra}`, `--cwd DIR`, `--json`, `--dry-run`, `--verbose`, `--codex-arg=--flag` (pass-through; sandbox and bypass flags are refused).

Prompts go on stdin (`-` or omitted) via a heredoc. Never build a long prompt as an argv element.

## Report

Text mode prints a header, then Codex's final message (or the adversarial findings JSON):

```
intent:    adversarial
model:     gpt-6-sol -> gpt-6-sol
effort:    high -> high
profile:   review -> review (read-only)
session:   <id>
exit:      0  (312.4s)
```

`requested -> actual` comes from the session file, not from the output. A `WARNING:` line means a mismatch or an unverifiable run; treat that as a failed delegation. `--json` gives the same fields plus `findings`, `message`, `warnings`, `command`.

## Agents

- **codex-reviewer**: `review` or `adversarial`. Use for substantive changes, especially concurrency, persistence, security, networking, retries, failure handling, rollback. Launch it in the same Agent call as Claude reviewers when running a multi-reviewer pass.
- **codex-consult**: `consult`. Use when stuck, when explanations compete, or for a deliberate outside opinion.
- **codex-implementer**: `implement --worktree`. Use for an alternative implementation, a mechanical refactor, or a bounded fix. Inspect the worktree it reports before taking anything from it.

Each agent runs one command, returns the report verbatim, and adds a labeled synthesis. Reviews and consults are safe to run in parallel with Claude's own work; write-capable runs always get their own worktree.

## Policy

- GPT-6 Sol at high is the default for everything. Escalate to `gpt-6-astra` only for genuinely hard or ambiguous problems, or when Claude and Sol disagree. Astra shares the usage pool and consumes it roughly twice as fast. Do not use `max` or `ultra` unless asked.
- Give Codex scope and concerns, not conclusions. Anchoring the reviewer on Claude's framing defeats the purpose.
- Treat findings as peer-review input. Verify each one before acting on it, and say which model produced it.
- Never widen permissions to make a run succeed. If Codex reports a blocked read, write, or network call, surface it and let the user decide.
- Never edit the same checkout Codex is writing to. `implement` defaults to a worktree for this reason.

## Raw fallback

When the wrapper does not fit, `codex exec` directly is fine as long as the profile is selected explicitly and no sandbox or bypass flag is passed:

```bash
codex exec -c 'default_permissions="review"' -c 'model_reasoning_effort="high"' -m gpt-6-sol --json - <<'EOF'
...
EOF
```

Then `codex-delegate show <session id>` to confirm what ran.

## Keeping it current

`codex-delegate doctor` checks the Codex version against the validated one, the model catalog, the flags the wrapper uses, the profiles in config.toml, and runs sandbox canaries for both profiles. It makes no model calls. Run it after a Codex update; run `/codex-audit` when doctor warns or when a notable Codex release lands.
