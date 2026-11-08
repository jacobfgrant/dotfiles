# Codex

Global configuration for the Codex CLI, stowed to `~/.codex`.

- `.codex/AGENTS.md`: working preferences, mirroring the global `CLAUDE.md`.
- `.codex/config.toml`: model, approval policy, permission profiles, trusted projects.
- `.codex/rules/safety.rules`: command rules that forbid destructive operations and prompt for the rest.

Codex writes to `config.toml` through its symlink (model switches, project trust). Review the diff before committing and drop anything machine-specific.


## Deployment

`stow.sh` uses `--no-folding`, so `~/.codex` stays a real directory and `AGENTS.md` and `config.toml` are symlinks whose edits take effect immediately. `.codex/rules/` is the exception: Codex ignores symlinked `.rules` files ([openai/codex#32658](https://github.com/openai/codex/issues/32658)), so `stow.sh` copies them and edits need a re-run. Check a rule with:

```sh
codex execpolicy check --pretty --rules ~/.dotfiles/codex/.codex/rules/safety.rules -- git clean -n
```


## Permissions

Two named profiles, both without network and both denying credential stores, secret file globs, Codex's own auth and transcripts, and `~/Library` except `~/Library/Caches`:

- `development` (interactive default): extends `:workspace`, so the workspace is writable.
- `review`: extends `:read-only`, plus one writable scratch directory, `~/.cache/codex-delegate/scratch`, for temp files.

Reads are "home minus credential stores" rather than workspace-only because a blanket `"~" = "deny"` also blocks the `~/.gitconfig` symlink and git stops working inside the sandbox. Never set `sandbox_mode` or pass `--sandbox` alongside profiles: an explicit sandbox mode makes Codex discard the profile ([openai/codex#46252](https://github.com/openai/codex/issues/46252)). An `allow` command rule runs outside the sandbox, so the rules file has none.
