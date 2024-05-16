### Common Shell Aliases ###
#
#
# Common aliases across shells (bash, zsh, etc.)
#


## PATH Variable ##

# /usr/local/go/bin
if [ -d "/usr/local/go/bin" ]
then
    export PATH="$PATH:/usr/local/go/bin"
fi


## Aliases ##

# Ansible Configure playbook shortcuts
ANSIBLE_REPO_URL="https://github.com/jacobfgrant/ansible-configure.git"

alias ansible-configure="sudo ansible-pull --url $ANSIBLE_REPO_URL -i $(uname -n), main.yml"
alias ansible-configure-base="sudo ansible-pull --url $ANSIBLE_REPO_URL -i $(uname -n), main.yml --skip-tags installs"
alias ansible-configure-server="sudo ansible-pull --url $ANSIBLE_REPO_URL -i $(uname -n), main.yml --skip-tags gui"



# General Aliases

alias celar="clear"

if command -v xdg-open >/dev/null 2>&1
then
    alias open='xdg-open'
fi



# Git shortcuts
alias gogit="cd $HOME/Documents/Git/ && ls"
alias gpo="git push origin"
alias gum="git checkout master && git pull upstream master"



# Python aliases/functions

if ! command -v python &> /dev/null
then
    alias python="python3"
fi


venv() {
    local python_interpreter=python3
    local env_name
    local verbose=0

    while [[ "$1" ]]
    do
        case "$1" in
            -p)
                python_interpreter="$2"
                shift 2
                ;;
            -v)
                verbose=1
                shift
                ;;
            *)
                env_name="$1"
                shift
                ;;
        esac
    done

    if [ -z "$env_name" ]
    then
        echo "Usage: venv <env_name> [-p python_interpreter] [-v]"
        return 1
    fi

    local activate_script="$env_name/bin/activate"

    if [ -d "$env_name" ]
    then
        if [ -f "$activate_script" ]
        then
            [ $verbose -eq 1 ] && echo "Activating existing Python virtual environment in '$env_name'"
            source "$activate_script"
        else
            echo "Directory '$env_name' exists but does not appear to be a Python virtual environment."
            return 1
        fi
    else
        [ $verbose -eq 1 ] && echo "Creating new Python virtual environment in '$env_name' with interpreter $python_interpreter"
        $python_interpreter -m venv "$env_name"
        if [ -f "$activate_script" ]
        then
            [ $verbose -eq 1 ] && echo "Activating the new Python virtual environment"
            source "$activate_script"
        else
            echo "Failed to find the activate script. Virtual environment may not have been created correctly."
            return 1
        fi
    fi
}


# Terraform Aliases

alias tf="terraform"
alias tfi="terraform init"
alias tfv="terraform validate"
alias tfp="terraform plan"
alias tfa="terraform apply"
alias tfd="terraform destroy"
alias tff="terraform fmt"
alias tfs="terraform state"
alias tfw="terraform workspace"


# Terragrunt Aliases

alias tg="terragrunt"
