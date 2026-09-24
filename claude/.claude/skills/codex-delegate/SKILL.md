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
| `implement [--worktree] [PROMPT \| -]` | development | workspace writes, no network, secrets denied | gpt-6-sol / high, in place |
| `resume SESSION_ID [--write] [PROMPT \| -]` | review, or development with `--write` | as above | inherits model, effort, and directory |
| `show SESSION_ID` | none | reads the session file | |
| `doctor [--skip-canary]` | none | no model calls | |

Common flags: `--model`, `--effort {low,medium,high,xhigh,max,ultra}`, `--cwd DIR`, `--json`, `--dry-run`, `--verbose`. There is no pass-through to `codex`.

Before running, the wrapper refuses any project whose own `.codex/config.toml` sets sandbox, permission, approval, or provider keys, or whose `.codex/rules` contain an `allow` rule, because Codex would load them and they could replace the pinned profile. It also refuses a `--base` ref that does not exist. Report a refusal; do not alter the project's files to get past it.

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
workspace: <path>          (only when it differs from the requested directory, e.g. a worktree)
WARNING:   <text>          (zero or more)
---
```

`requested -> actual` comes from the session file, not from the output. Any `WARNING:` line or `unverified` value means the run could not be verified or did not run as pinned; treat that as a failed delegation and report it first. `--json` gives the same fields plus `findings`, `message`, `warnings`, `command`.

## Agents

- **codex-reviewer**: `review` or `adversarial`. Use for substantive changes, especially concurrency, persistence, security, networking, retries, failure handling, rollback. Always give it the base ref for a branch review. For a multi-reviewer pass, launch it in the same message as the Claude reviewers, as parallel Agent calls.
- **codex-consult**: `consult`. Use when stuck, when explanations compete, or for a deliberate outside opinion.
- **codex-implementer**: `implement`. Use for an alternative implementation, a mechanical refactor, or a bounded fix. It works in place unless something else is editing the same checkout, in which case it adds `--worktree`; tell it when that is the case.

Each agent runs one command, returns the report verbatim, and adds a short evidence check that is clearly its own. Verification of findings is the caller's job.

## Policy

- GPT-6 Sol at high is the default for everything. Escalate to `gpt-6-astra` only for genuinely hard or ambiguous problems, or when Claude and Sol disagree. Astra shares the usage pool and consumes it roughly twice as fast. Do not use `max` or `ultra` unless asked.
- Give Codex scope and concerns, not conclusions. Anchoring the reviewer on Claude's framing defeats the purpose. Decisions already made are different: a deliberate product or design choice the user has settled is a fact, and stating it as focus text ("deliberate, not findings: ...") cuts noise without anchoring the review.
- Treat findings as peer-review input. Verify each one before acting on it, and say which model produced it.
- Never widen permissions to make a run succeed. If Codex reports a blocked read, write, or network call, surface it and let the user decide.
- Do not edit a checkout while Codex is writing to it. If work must continue in parallel, ask the implementer for `--worktree`.
- Codex appends a `[projects]` trust entry to `~/.codex/config.toml` (a symlink into this repo) for every directory it runs in. Never stage those hunks alongside other work; drop entries for throwaway paths.

## Raw fallback

Only when the user asks for something the wrapper cannot express, and never as a retry after a wrapper refusal or failure, `codex exec` may be run directly with the profile selected explicitly and no sandbox or bypass flag:

```bash
codex exec -c 'default_permissions="review"' -c 'model_reasoning_effort="high"' -m gpt-6-sol --json - <<'EOF'
...
EOF
```

Then `codex-delegate show <session id>` to confirm what ran.

## Keeping it current

`codex-delegate doctor` checks the Codex install, the model catalog, the flags the wrapper uses, the profiles in config.toml, and runs sandbox canaries for both profiles. It makes no model calls and takes seconds. Run it after a Codex update; run `/codex-audit` when doctor fails or when a notable Codex release lands.
