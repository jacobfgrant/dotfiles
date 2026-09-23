# Codex

Global configuration for the Codex CLI, stowed to `~/.codex`.


## Configuration

- `.codex/AGENTS.md`: working preferences and coding conventions, mirroring the global `CLAUDE.md`.
- `.codex/config.toml`: model, approval policy, permission profiles, and project trust.
- `.codex/rules/safety.rules`: command rules that forbid destructive operations and prompt for the rest.
- `.local/bin/codex-delegate`: runs Codex non-interactively on behalf of Claude Code (below).
- `tests/`: unit tests for `codex-delegate`; excluded from Stow.

Codex writes to `config.toml` through its symlink: switching models in a session and trusting a new project both land in the tracked file. Review the diff before committing and drop anything machine-specific.


## Deployment

`stow.sh` uses `--no-folding` for every package. `~/.codex` stays a real directory holding Codex's runtime data, and `AGENTS.md` and `config.toml` are symlinks into this repository. Edits to them take effect immediately.

The exception is `.codex/rules/`. Codex silently ignores symlinked `.rules` files ([openai/codex#32658](https://github.com/openai/codex/issues/32658)), so `.stow-local-ignore` excludes that directory from Stow and `stow.sh` copies its files into `~/.codex/rules` instead. Edits there take effect only after re-running `stow.sh`. Verify the rules themselves with:

```sh
codex execpolicy check --pretty --rules ~/.dotfiles/codex/.codex/rules/safety.rules -- git clean -n
```


## Permissions

Two named profiles:

- `development` (the interactive default): workspace edits, no network. Credential stores, secret file globs, Codex's own auth and transcripts, the Docker auth file, and `~/Library` are denied; `~/Library/Caches` stays readable for package caches.
- `review` (used by `codex-delegate` for read-only intents): extends `:read-only`, no network, credential stores and secret file globs denied. Reads are "home minus credential stores" rather than strictly workspace-only: a blanket `"~" = "deny"` also blocks the `~/.gitconfig` symlink, and a per-file read entry does not override a denied parent for a symlink, so git breaks inside the sandbox.

Authenticated tools may need approval to reach their credential stores. Do not set legacy `sandbox_mode` or `sandbox_workspace_write` alongside permission profiles, and never pass `--sandbox`: any explicit sandbox mode makes Codex discard the profile entirely ([openai/codex#46252](https://github.com/openai/codex/issues/46252)).

Command rules match argument prefixes, not every equivalent script or argument order. The strictest matching decision wins. An `allow` decision also runs the command outside the sandbox, so the rules file has none.

References: [profiles](https://learn.chatgpt.com/docs/config-file/config-advanced), [permissions](https://learn.chatgpt.com/docs/permissions), [command rules](https://learn.chatgpt.com/docs/agent-configuration/rules).


## codex-delegate

`codex-delegate` is how Claude Code hands work to OpenAI models. Each subcommand pins an intent to a permission profile, a default model and reasoning effort, and a fixed set of `codex exec` flags, then reads the Codex session file afterwards to report the model, effort, and profile that actually applied. It never passes `--sandbox` or any bypass flag.

| Subcommand | Profile | Default model / effort |
|---|---|---|
| `review [--base REF \| --uncommitted]` | `review` | gpt-6-sol / high |
| `adversarial [--base REF \| --uncommitted] [FOCUS...]` | `review` | gpt-6-sol / high |
| `consult --model M [PROMPT \| -]` | `review` | model required / high |
| `implement [--worktree] [PROMPT \| -]` | `development` | gpt-6-sol / high |
| `resume SESSION_ID [--write] [PROMPT \| -]` | `review`, or `development` with `--write` | inherits |
| `show SESSION_ID` | none | reads the session file only |
| `doctor [--skip-canary]` | none | no model calls |

`codex exec review` does its work in a child thread, so for `review` the model and profile are read from the child whose turn ids match the parent session; if no new turn matches, the report says unverified rather than describing an earlier run. Prompts are read from stdin so long prompts never hit argument-length limits. `--json` prints a machine-readable report; `--dry-run` prints the `codex` command without running it. There is deliberately no pass-through to `codex`: hidden aliases such as `--yolo` made a denylist unsafe, and nothing needed it.

Before running, the wrapper refuses a project whose own `.codex/config.toml` sets sandbox, permission, approval, or provider keys, or whose `.codex/rules` contain an `allow` rule. Codex trusts every directory `codex exec` runs in and loads that configuration, which could replace the pinned profile. Codex also appends a `[projects]` trust entry to `~/.codex/config.toml` for each such directory; since that file is a symlink into this repo, review those hunks before committing.

The Claude side is three subagents in `claude/.claude/agents/` (`codex-reviewer`, `codex-consult`, `codex-implementer`) and the `codex-delegate` skill, which holds the contract and the delegation policy: GPT-6 Sol at high by default, GPT-6 Astra only for genuinely hard problems or disagreement, findings treated as peer input.

### Keeping it current

```sh
codex-delegate doctor
```

Checks the installed Codex version against the one the wrapper was validated on, Codex's own doctor report, the model catalog, every `codex exec` flag the wrapper relies on, the profiles in `config.toml`, and then runs sandbox canaries for both profiles through `codex sandbox` (reads, writes, secret files, `~/.ssh`, network, git). It makes no model calls and takes a few seconds. Run it after a Codex update. When it warns about the version, run `/codex-audit` in Claude Code to review the release notes against the wrapper's assumptions.

Unit tests cover command construction, the project-config refusal, session summaries and resume verification, and the doctor's config check:

```sh
python3 -m pytest codex/tests
```

Any environment with pytest works; a throwaway `.venv` at the repo root is ignored by git.

### Why not the official plugin

OpenAI's `codex-plugin-cc` starts every App Server thread with an explicit sandbox value, which makes Codex discard the permission profile, so plugin reviews can read `~/.ssh` and workspace `.env` files despite the denies above. It also rejects `max` and `ultra` effort, keeps review threads ephemeral so the model cannot be audited, and adds hooks and a broker daemon to every Claude session. `codex exec` with an explicit profile gives the same capability with fewer moving parts.
