### Bash Aliases ###

# PATH Variable

export PATH=$PATH:/usr/local/go/bin


# Bash Configuration

HISTSIZE=20000
HISTFILESIZE=20000


# General Aliases
alias celar="clear"
alias open="xdg-open"


# Git shortcuts
alias gogit="cd $HOME/Dropbox/Git/ && ls"
alias gpo="git push origin"
alias gum="git checkout master && git pull upstream master"


# Ansible Configure playbook shortcuts
alias ansible-configure="sudo ansible-pull --url https://github.com/jacobfgrant/ansible-configure.git -i $(uname -n), main.yml"
alias ansible-configure-base="sudo ansible-pull --url https://github.com/jacobfgrant/ansible-configure.git -i $(uname -n), main.yml --skip-tags installs"
alias ansible-configure-server="sudo ansible-pull --url https://github.com/jacobfgrant/ansible-configure.git -i $(uname -n), main.yml --skip-tags gui"


# Terraform shortcuts
alias tf="$(which terraform)"
alias tfmt="find . -maxdepth 1 -type f -name '*.tf' -o -type f -name '*.tfvars' | xargs -n 1 terraform fmt"
