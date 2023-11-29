# dotfiles

*nix configuration files


### ansible/

- `.ansible.cfg` – Ansible configuration file


### bash/

- `.bash_aliases`
  - Sources `.common_aliases.sh`
  - Adds `/usr/local/go/bin` to PATH
  - Sets Bash history length
  - Other aliases


### common/

- `.common_aliases.sh` – Common shell aliases used by bash, zsh, etc.
  - Aliases for [ansible-configure](https://github.com/jacobfgrant/ansible-configure)
  - General aliases
  - Python aliases/functions


### git/

- `.gitconfig` – Global configuration for `git`

- `.gitignore_global` – Global `.gitignore` for files/directories that should always be ignored by `git`


### zsh/

- `.zprofile` – 
  - Configures Homebrew variables/PATH

- `.zshrc` – 
  - Sources `.common_aliases.sh`
  - Sets zsh prompt
  - Sets zsh right prompt using git info


### stow.sh

The `stow.sh` script can be used to quickly and easily symlink the dotfiles in this repository into a users home directory. Using GNU Stow, it creates symlinks in the user's home directory for the contents of each directory located in the same directory as the script.
