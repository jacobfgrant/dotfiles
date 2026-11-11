# Codex

Global configuration for the Codex CLI, stowed to `~/.codex`.

- `.codex/AGENTS.md`: working preferences, mirroring the global `CLAUDE.md`.
- `.codex/config.toml`: model, approval policy, permission profiles, trusted projects.
- `.codex/rules/safety.rules`: command rules that forbid destructive operations and prompt for the rest.
- `.local/bin/codex-delegate`: runs Codex non-interactively for Claude Code.
- `tests/`: unit tests for `codex-delegate`; excluded from Stow.

Codex writes to `config.toml` through its symlink (model switches, project trust). Review the diff before committing and drop anything machine-specific.


## Deployment

`stow.sh` uses `--no-folding`, so `~/.codex` stays a real directory and `AGENTS.md` and `config.toml` are symlinks whose edits take effect immediately. `.codex/rules/` is the exception: Codex ignores symlinked `.rules` files ([openai/codex#32658](https://github.com/openai/codex/issues/32658)), so `stow.sh` copies them and edits need a re-run. Check a rule with:

```sh
codex execpolicy check --pretty --rules ~/.dotfiles/codex/.codex/rules/safety.rules -- git clean -n
```


## Permissions

Two named profiles, both without network and both denying credential stores, secret file globs, Codex's own auth and transcripts, and `~/Library` except `~/Library/Caches`:

- `development` (interactive default): extends `:workspace`, so the workspace is writable.
- `review` (what `codex-delegate` uses for read-only intents): extends `:read-only`, plus one writable directory, `~/.cache/codex-delegate/scratch`, where the wrapper sends each run's temp files.

Reads are "home minus credential stores" rather than workspace-only because a blanket `"~" = "deny"` also blocks the `~/.gitconfig` symlink and git stops working inside the sandbox. Never set `sandbox_mode` or pass `--sandbox` alongside profiles: an explicit sandbox mode makes Codex discard the profile ([openai/codex#46252](https://github.com/openai/codex/issues/46252)). An `allow` command rule runs outside the sandbox, so the rules file has none.


## codex-delegate

Each subcommand pins an intent to a permission profile, a model, an effort, and a fixed set of `codex exec` flags, then reads the Codex session file to report what actually ran. Nothing can pass `--sandbox` or a bypass flag through it. Codex loads a project's own `.codex/` only when its git root is trusted in `[projects]`; in a trusted project the wrapper refuses config that could change the sandbox (sandbox, permission, approval, or hook keys, `hooks.json`, `allow` rules) unless `--allow-project-config` is passed. Untrusted projects run without any check.

Read-only runs can run tests. Each gets a fresh directory under `~/.cache/codex-delegate/scratch`, and `TMPDIR`, `TMPPREFIX`, and pytest's `cache_dir` point there, so heredocs, `mktemp`, and pytest's `tmp_path` work while the repository stays read-only. The directory is removed when the run ends; anything left in the parent, by a killed run or by a model writing there directly, is removed by the next run once it is a day old. Codex labels any profile with a writable path `workspace-write`, so the report names the writable paths from Codex's resolved filesystem policy instead and warns if a review run could write anywhere beyond the scratch directory.

| Subcommand | Profile | Default |
|---|---|---|
| `review [--base REF \| --uncommitted]` | `review` | gpt-6.1-sol / high |
| `adversarial [--base REF \| --uncommitted] [FOCUS... \| -]` | `review` | gpt-6.1-sol / high |
| `consult --model M [PROMPT \| -]` | `review` | model required / high |
| `implement [--worktree] [PROMPT \| -]` | `development` | gpt-6.1-sol / high |
| `resume SESSION_ID [--write] [PROMPT \| -]` | `review`, or `development` with `--write` | inherits |
| `show SESSION_ID` | none | |
| `doctor [--skip-canary]` | none | |

`doctor` checks the install, Codex's own doctor report, the model catalog, the flags the wrapper relies on, the profiles in `config.toml`, and runs sandbox canaries for both profiles. No model calls. Run it after a Codex update; run `/codex-audit` in Claude Code when it fails or a notable release lands. Unit tests:

```sh
uvx pytest codex/tests
```

The Claude side is the `codex-delegate` skill, which holds the contract and the delegation policy. The official `codex-plugin-cc` was rejected because it starts every thread with an explicit sandbox value, which discards the permission profile.
