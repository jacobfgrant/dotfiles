# dotfiles

*nix configuration files


### ansible/

- `.ansible.cfg` – Ansible configuration file


### aws/

- `.aws/config` – AWS CLI profiles (IAM Identity Center; no credentials)
- `.aws/agent-config` – Read-only profiles used by agents via `AWS_CONFIG_FILE`


### bash/

- `.bash_aliases` – Bash-specific configuration and completion
  - Sources `.common_aliases.sh`
  - Sets Bash history length
  - AWS CLI and Google Cloud CLI completion


### claude/

- `.claude/CLAUDE.md` – Claude Code global conventions and preferences
- `.claude/settings.json` – Permission rules, model, and environment (pins AWS to the read-only profiles)
- `.claude/rules/python.md` – Python conventions, loaded for Python files
- `.claude/skills/codex-delegate/` – Contract for reviews, consults, and delegated work via `codex-delegate`
- `.claude/skills/codex-audit/` – Checks `codex-delegate` against the installed Codex CLI after an update


### codex/

- `.codex/AGENTS.md` – Codex global conventions and preferences
- `.codex/config.toml` – Model, approvals, and permission profiles (`development`, `review`)
- `.codex/rules/safety.rules` – Command permission rules (copied, not linked; see `stow.sh`)
- `.local/bin/codex-delegate` – Runs Codex non-interactively for Claude Code with pinned permissions
- `.stow-local-ignore` – Keeps `rules/`, `tests/`, and the README out of `$HOME`
- `tests/` – Unit tests for `codex-delegate`
- [Setup and configuration](codex/README.md)


### common/

- `.common_aliases.sh` – Common shell aliases used by bash, zsh, etc.
  - Environment setup (PATH, Go configuration)
  - Tool aliases (Ansible, package managers)
  - Core system aliases (ls, grep, navigation)
  - Development tools (Docker, Python, Terraform ecosystem)
  - Utility functions (AWS, SSH keys, archives, LaTeX)


### ghostty/

- `.config/ghostty/config.ghostty` – Configuration for the Ghostty terminal


### git/

- `.gitconfig` – Global configuration for `git`
  - Comprehensive alias collection
  - Custom log formatting
  - Sensible defaults

- `.gitignore_global` – Global `.gitignore` for files/directories that should always be ignored by `git`
  - Multi-language and platform coverage
  - IDE and editor patterns
  - Security-focused exclusions


### ssh/

- `.ssh/config` – Default SSH client settings (no hosts or keys)


### vim/

- `.vimrc` – Vim editor configuration
  - Syntax highlighting and line numbers
  - Smart indentation and search
  - Status line and spellcheck for prose filetypes
  - Vi improvements and key mappings


### zsh/

- `.zprofile` – Configures Homebrew variables/PATH

- `.zshrc` – ZSH configuration and prompt setup
  - Sources `.common_aliases.sh`
  - Tool completion (AWS CLI, Google Cloud CLI, Docker, Terragrunt)
  - History settings matching bash
  - Custom prompt with git integration


### stow.sh

The `stow.sh` script can be used to quickly and easily symlink the dotfiles in this repository into a users home directory. Using GNU Stow with `--no-folding`, it links individual files into the user's home directory while keeping destination directories real.

Codex ignores symlinked rules files, so the script copies `codex/.codex/rules/*.rules` into `~/.codex/rules/` instead. Edits there take effect only after re-running `stow.sh`.
