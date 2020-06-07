### Bash Aliases ###

# PATH Variable

export PATH=$PATH:/usr/local/go/bin

# General Aliases
alias celar="clear"
alias open="xdg-open"

# Git shortcuts
alias gogit="cd $HOME/Dropbox/Git/ && ls"
alias gpo="git push origin"
alias gum="git checkout master && git pull upstream master"


# Ansible shortcuts
alias ansible-configure="sudo ansible-pull --url https://github.com/jacobfgrant/ansible-configure.git -i $(uname -n), main.yml"
