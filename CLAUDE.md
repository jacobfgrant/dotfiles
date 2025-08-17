# Claude Context for Dotfiles Repository

## Project Overview
Cross-platform dotfiles for macOS and Linux using GNU Stow for symlink management. Emphasizes portability, maintainability, and avoiding non-standard tool dependencies.

## Repository Structure
- `ansible/`: Ansible configuration
- `bash/`: Bash-specific aliases and completion  
- `common/`: Shared shell configuration across bash/zsh
- `git/`: Git configuration and comprehensive global gitignore
- `vim/`: Vim editor configuration
- `zsh/`: ZSH-specific configuration, completion, and prompts
- `stow.sh`: GNU Stow deployment script

## Key Configuration Files
- `common/.common_aliases.sh`: Core shared aliases organized in sections:
  - ENVIRONMENT (PATH, Go config)
  - TOOLS & SERVICES (Ansible)
  - CORE ALIASES (system navigation, git)
  - PACKAGE MANAGERS (Homebrew, APT)
  - DEVELOPMENT TOOLS (Python, Terraform ecosystem, systemctl)
  - UTILITIES (Archives, SSH, LaTeX)

## Alias Conventions
- Package managers: `brew*` (Homebrew), `apt*` (APT-GET preferred over apt)
- Terraform tools: `tf*`, `tg*` (terragrunt), `tfl*` (tflint), etc.
- Systemctl: `s*` prefix (sstatus, sstart, sstop, srestart, etc.)
- Archives: `mktar`, `mkgz`, `untar`, `ungz`
- APT naming: `aptui` (uninstall), `aptuia` (uninstall all/purge), `aptrm` (autoremove)

## Shell Completion Setup
- AWS CLI completion for both bash and zsh
- Google Cloud CLI completion via Homebrew
- Terragrunt completion (zsh only)

## Cross-Platform Considerations
- Detect and adapt to macOS vs Linux environments
- Use standard tools over modern alternatives (ls vs exa, etc.)
- Test command availability before creating aliases
- Handle path differences ($HOME/Developer vs $HOME/Documents)

## Git Configuration
- Extensive alias collection in .gitconfig
- Avoid git shortcuts in shell aliases (prefer .gitconfig aliases)
- Comprehensive .gitignore_global with multi-language support

## Style Guidelines
- Headers: `## MAJOR SECTION ##` and `# Subsection #`
- Include table of contents in file headers
- Consistent spacing and formatting across files
- Descriptive comments for complex functions
- Group related functionality, separate aliases from functions

## Removed/Avoided Components
- tmux configuration deliberately removed (user learning tmux first)
- Modern tool replacements (bat, exa, htop) avoided for portability
- Aggressive git aliases removed in favor of .gitconfig usage
