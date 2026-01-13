# dotfiles

*nix configuration files


### ansible/

- `.ansible.cfg` – Ansible configuration file


### claude/

- `.claude/CLAUDE.md` – Claude Code global conventions and preferences
- `.claude/settings.json` – Claude Code permission rules


### bash/

- `.bash_aliases` – Bash-specific configuration and completion
  - Sources `.common_aliases.sh`
  - Sets Bash history length
  - AWS CLI and Google Cloud CLI completion


### common/

- `.common_aliases.sh` – Common shell aliases used by bash, zsh, etc.
  - Environment setup (PATH, Go configuration)
  - Tool aliases (Ansible, package managers)
  - Core system aliases (ls, grep, navigation)
  - Development tools (Python, Terraform ecosystem)
  - Utility functions (SSH keys, archives, LaTeX)


### git/

- `.gitconfig` – Global configuration for `git`
  - Comprehensive alias collection
  - Custom log formatting
  - Sensible defaults

- `.gitignore_global` – Global `.gitignore` for files/directories that should always be ignored by `git`
  - Multi-language and platform coverage
  - IDE and editor patterns
  - Security-focused exclusions


### vim/

- `.vimrc` – Vim editor configuration
  - Syntax highlighting and line numbers
  - Smart indentation and search
  - Vi improvements and key mappings


### zsh/

- `.zprofile` – Configures Homebrew variables/PATH

- `.zshrc` – ZSH configuration and prompt setup
  - Sources `.common_aliases.sh`
  - Tool completion (AWS CLI, Google Cloud CLI, Terragrunt)
  - Custom prompt with git integration


### stow.sh

The `stow.sh` script can be used to quickly and easily symlink the dotfiles in this repository into a users home directory. Using GNU Stow, it creates symlinks in the user's home directory for the contents of each directory located in the same directory as the script.
