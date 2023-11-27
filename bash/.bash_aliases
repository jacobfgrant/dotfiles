### Bash Aliases ###


# Common Aliases

[ -f ~/.common_aliases.sh ] && . ~/.common_aliases.sh


# PATH Variable

export PATH=$PATH:/usr/local/go/bin


# Bash Configuration

HISTSIZE=20000
HISTFILESIZE=20000


# Git shortcuts
alias gogit="cd $HOME/Dropbox/Git/ && ls"
alias gpo="git push origin"
alias gum="git checkout master && git pull upstream master"


# Terraform shortcuts
alias tf="$(which terraform)"
alias tfmt="find . -maxdepth 1 -type f -name '*.tf' -o -type f -name '*.tfvars' | xargs -n 1 terraform fmt"
