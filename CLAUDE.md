# Dotfiles Repository

Cross-platform dotfiles for macOS and Linux using GNU Stow for symlink management.


## Structure

- `ansible/` - Ansible configuration
- `bash/` - Bash-specific aliases and completion
- `claude/` - Claude Code global configuration (stowed to ~/.claude)
- `common/` - Shared shell configuration (sourced by bash/zsh)
- `git/` - Git configuration and global gitignore
- `vim/` - Vim editor configuration
- `zsh/` - ZSH-specific configuration and prompts
- `stow.sh` - GNU Stow deployment script


## Key Principles

- **Portability first**: Prefer standard tools (ls, grep) as the default. Modern alternatives (eza, ripgrep) are fine if wrapped with availability checks and graceful fallback.
- **Cross-platform**: Detect and adapt to macOS vs Linux; test command availability before aliasing
- **Stow-based deployment**: Each top-level directory stows into $HOME


## Core Files
- `common/.common_aliases.sh` is the heart of the config—sourced by both bash and zsh
- Git shortcuts belong in `.gitconfig`, not shell aliases


## When Adding Aliases
- Follow existing naming conventions (tf* for terraform, s* for systemctl, etc.)
- Group with related functionality
- Add to `common/` unless truly shell-specific
- Use section headers: `## MAJOR SECTION ##` and `# Subsection #`
