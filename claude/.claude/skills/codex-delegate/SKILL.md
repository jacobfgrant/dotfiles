---
name: codex-delegate
description: Contract for getting reviews and second opinions from OpenAI models (GPT-6 Sol by default, GPT-6 Astra by exception) and for delegating bounded implementation work, by running the local codex-delegate wrapper directly. Load proactively once a substantive change is ready for review, especially one touching concurrency, persistence, security, networking, retries, failure handling, or rollback; when stuck or when two explanations compete; whenever asked for a second opinion, an independent or adversarial review, or a Codex, GPT, Sol, or Astra run; and when deciding whether to hand work to another model.
user-invocable: false
---

# Delegating to Codex

`codex-delegate` (in `~/.local/bin`, source in `~/.dotfiles/codex/.local/bin/`) runs `codex exec` with the permission profile, model, effort, and flags pinned per intent, then reports what actually ran by reading the Codex session file. It never passes `--sandbox` or any bypass flag, so the profile in `~/.codex/config.toml` always governs access.

## Intents

| Subcommand | Profile | Access | Default |
|---|---|---|---|
| `review [--base REF \| --uncommitted]` | review | read-only, no network, secrets denied | gpt-6-sol / high |
| `adversarial [--base REF \| --uncommitted] [FOCUS... \| -]` | review | same | gpt-6-sol / high |
| `consult --model M [PROMPT \| -]` | review | same | model required, high |
| `implement [--worktree] [PROMPT \| -]` | development | workspace writes, no network, secrets denied | gpt-6-sol / high, in place |
| `resume SESSION_ID [--write] [PROMPT \| -]` | review, or development with `--write` | as above | inherits model, effort, and directory |
| `show SESSION_ID` | none | reads the session file | |
| `doctor [--skip-canary]` | none | no model calls | |

Common flags: `--model`, `--effort {low,medium,high,xhigh,max,ultra}`, `--cwd DIR`, `--json`, `--dry-run`, `--verbose`. There is no pass-through to `codex`.

Before running, the wrapper refuses any project whose own `.codex/config.toml` sets sandbox, permission, approval, or provider keys, or whose `.codex/rules` contain an `allow` rule, because Codex would load them and they could replace the pinned profile. It also refuses a `--base` ref that does not exist. Report a refusal; do not alter the project's files to get past it.

Prompts go on stdin (`-` or omitted) via a quoted heredoc (`<<'EOF'`, so `$` and backticks stay literal). Never build a long prompt as an argv element. Adversarial focus text is the same: a short phrase can be an argument, but anything longer goes on stdin with `-`; omitted focus never reads stdin.

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

A `session started: <id>` line on stderr comes first, as soon as Codex starts, so an interrupted run still leaves an id for `codex-delegate show`. `requested -> actual` comes from the session file, not from the output. Any `WARNING:` line or `unverified` value means the run could not be verified or did not run as pinned; treat that as a failed delegation and report it first. `--json` gives the same fields plus `findings`, `message`, `warnings`, `command`.

## Running it

Run the wrapper yourself with one Bash call using `run_in_background: true`; a run takes minutes and can outlast the Bash timeout. The harness notifies you with the output when it finishes, so keep working or end your turn in the meantime. Do not poll, sleep, background with `&`, or redirect the output to a file.

- **Review a change.** Use proactively for substantive changes, especially concurrency, persistence, security, networking, retries, failure handling, rollback. `review` hunts defects and takes scope only; `adversarial` challenges the design and assumptions and takes focus text. Pass `--base <ref>` for a branch review; without it the uncommitted working tree is reviewed. For a multi-reviewer pass, start the Codex run in the same message as the Claude reviewer Agent calls so they run in parallel.
- **Consult.** Use when stuck, when explanations compete, or for a deliberate outside opinion. Give the concrete symptoms, what has been tried, and what a useful answer looks like.
- **Implement.** Use for an alternative implementation, a mechanical refactor, or a bounded fix. State the acceptance criteria, what to leave alone, and which checks to run; do not prescribe the implementation unless the user did. The `development` profile has no network, so a task that needs an install reports the blocked operation instead.

```bash
codex-delegate adversarial --base master - <<'EOF'
Retries, idempotency, and rollback in the new upload path.
Deliberate, not findings: uploads are best effort; there is no resume.
EOF

codex-delegate consult --model gpt-6-sol - <<'EOF'
<the question and the facts>
EOF

codex-delegate implement - <<'EOF'
<the task, acceptance criteria, what to leave alone, checks to run>
EOF
```

Add `--cwd <path>` for a repository other than the current directory. Codex reads the checkout live: hold edits to the files under review until a review returns, and leave the checkout alone entirely while an in-place `implement` runs. If you or the user need to keep editing, pass `--worktree` to `implement`; Codex then works in a managed git worktree on its own branch, and the header shows its path as `workspace:`.

When a run returns, read the header before anything else. Verify each review finding before acting on it, and tell the user which model produced it. For an implementation, read the diff (in the worktree, if one was used), run the checks yourself, and surface anything Codex reported as blocked or incomplete; nothing is committed or merged for you. Continue a thread with `codex-delegate resume <id>`, adding `--write` to continue an implementation in the same directory or worktree. If a run fails or is interrupted, report that with any partial output; do not rerun it with different flags.

## Policy

- GPT-6 Sol at high is the default for everything. Escalate to `gpt-6-astra` only for genuinely hard or ambiguous problems, or when Claude and Sol disagree. Astra shares the usage pool and consumes it roughly twice as fast. Do not use `max` or `ultra` unless asked.
- Being right matters more than being cheap, so reviews and opinions never drop below Sol. `gpt-6-luna` is for cheap, checkable work, mostly testing: smoke-testing a prompt, a classification run, a quick factual check. Pass `--model gpt-6-luna` explicitly, usually with `--effort low`.
- Give Codex scope and concerns, not conclusions. Anchoring the reviewer on Claude's framing defeats the purpose. Decisions already made are different: a deliberate product or design choice the user has settled is a fact, and stating it as focus text ("deliberate, not findings: ...") cuts noise without anchoring the review. Name the choice, not its consequences: "the palette hues are deliberate" leaves contrast and accessibility in scope, where "the colour values are deliberate" reads as exempting them too.
- Treat findings as peer-review input. Verify each one before acting on it, and say which model produced it.
- Never widen permissions to make a run succeed. If Codex reports a blocked read, write, or network call, surface it and let the user decide.
- Do not edit a checkout while Codex is writing to it. If work must continue in parallel, run `implement` with `--worktree`.
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
