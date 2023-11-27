### Common Shell Aliases ###
#
#
# Common aliases across shells (bash, zsh, etc.)
#


# Ansible Configure playbook shortcuts
ANSIBLE_REPO_URL="https://github.com/jacobfgrant/ansible-configure.git"

alias ansible-configure="sudo ansible-pull --url $ANSIBLE_REPO_URL -i $(uname -n), main.yml"
alias ansible-configure-base="sudo ansible-pull --url $ANSIBLE_REPO_URL -i $(uname -n), main.yml --skip-tags installs"
alias ansible-configure-server="sudo ansible-pull --url $ANSIBLE_REPO_URL -i $(uname -n), main.yml --skip-tags gui"



# General Aliases

alias celar="clear"

if command -v xdg-open >/dev/null 2>&1; then
    alias open='xdg-open'
fi
