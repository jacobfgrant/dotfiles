# Codex

Global configuration for the Codex CLI, stowed to `~/.codex`.


## Configuration

- `.codex/AGENTS.md`: working preferences and coding conventions, mirroring the global `CLAUDE.md`.
- `.codex/config.toml`: model, approval policy, permission profile, and project trust.
- `.codex/rules/safety.rules`: command rules that forbid destructive operations and prompt for the rest.

Codex writes to `config.toml` through its symlink: switching models in a session and trusting a new project both land in the tracked file. Review the diff before committing and drop anything machine-specific.


## Deployment

`stow.sh` uses `--no-folding` for every package. `~/.codex` stays a real directory holding Codex's runtime data, and the three managed files are symlinks into this repository. Edits take effect immediately.

Codex silently ignores symlinked `.rules` files ([openai/codex#32658](https://github.com/openai/codex/issues/32658)), so `safety.rules` is deployed but not loaded. Until that is fixed, the restrictions in `AGENTS.md` are the only guard. Verify the rules themselves with:

```sh
codex execpolicy check --pretty --rules ~/.dotfiles/codex/.codex/rules/safety.rules -- git clean -n
```


## Permissions

The development profile allows workspace edits, denies credential directories and secret file globs, and requires approval for network access. Authenticated tools may need approval to reach their credential stores. Do not set legacy `sandbox_mode` or `sandbox_workspace_write` alongside permission profiles; they override them.

Command rules match argument prefixes, not every equivalent script or argument order. The strictest matching decision wins. An `allow` decision also runs the command outside the sandbox, so the rules file has none.

References: [profiles](https://learn.chatgpt.com/docs/config-file/config-advanced), [permissions](https://learn.chatgpt.com/docs/permissions), [command rules](https://learn.chatgpt.com/docs/agent-configuration/rules).
