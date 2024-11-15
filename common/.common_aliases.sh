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



## GOPATH ##

if [ -d "$HOME/Developer" ]
then
    export GOPATH="$HOME/Developer/go"
else
    export GOPATH="$HOME/.go"
fi



## Aliases ##

# Ansible Configure playbook shortcuts
ANSIBLE_REPO_URL="https://github.com/jacobfgrant/ansible-configure.git"

alias ansible-configure="sudo ansible-pull --url $ANSIBLE_REPO_URL -i $(uname -n), main.yml"
alias ansible-configure-base="sudo ansible-pull --url $ANSIBLE_REPO_URL -i $(uname -n), main.yml --skip-tags installs"
alias ansible-configure-server="sudo ansible-pull --url $ANSIBLE_REPO_URL -i $(uname -n), main.yml --skip-tags gui"



# General Aliases

alias celar="clear"

alias h="history"

alias l="ls -CF"
alias la="ls -aCF"

if command -v xdg-open >/dev/null 2>&1
then
    alias open='xdg-open'
fi


# Navigation shortcuts

if [ -d "$HOME/Developer" ]
then
    alias gogit="cd $HOME/Developer/Git/ && ls"
    alias cdev="cd $HOME/Developer"
else
    alias gogit="cd $HOME/Documents/Git/ && ls"
fi

alias cdes="cd $HOME/Desktop"
alias cdoc="cd $HOME/Documents"
alias cdot="cd $HOME/.dotfiles"
alias cdow="cd $HOME/Downloads"


# Git shortcuts

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


# Docker alias

latex_compile() {
    local container_name="latexcompiler"
    local engine=(latexmk -pdf)  # Default to latexmk -pdf
    local mode="run"
    local OPTIND opt
    
    # Parse flags
    while getopts "pxls" opt
    do
        case $opt in
            p) engine=(pdflatex);;
            x) engine=(latexmk -xelatex);;
            l) engine=(latexmk -lualatex);;
            s) mode="shell";;
            *) return 1;;
        esac
    done
    shift $((OPTIND-1))
    
    # Must have a file to compile
    if [ $# -eq 0 ] && [ "$mode" != "shell" ]
    then
        echo "Usage: latex_compile [-p|-x|-l|-s] [file.tex]"
        echo "  (no flag): latexmk -pdf (default)"
        echo "  -p: pdflatex"
        echo "  -x: latexmk -xelatex"
        echo "  -l: latexmk -lualatex"
        echo "  -s: open interactive shell in container"
        return 1
    fi
    
    # Check if container exists
    if ! docker ps --all --format '{{.Names}}' | grep -q "^${container_name}$"
    then
        # Create (but don't run) a new container
        docker create \
            --name "${container_name}" \
            -v /workdir \
            texlive/texlive:latest \
            tail -f /dev/null
    fi

    # Decide between running a command or opening a shell
    if [ "$mode" = "shell" ]
    then
        # Interactive shell mode
        docker run \
            --rm -it \
            --volumes-from "${container_name}" \
            -v "$(pwd):/workdir" \
            -w "/workdir" \
            texlive/texlive:latest \
            /bin/bash
    else
        # Normal command execution
        docker run \
            --rm \
            --volumes-from "${container_name}" \
            -v "$(pwd):/workdir" \
            -w "/workdir" \
            texlive/texlive:latest \
            "${engine[@]}" "$@"
    fi
}

# Alias for easier access
alias ltx='latex_compile'


# Sudo Aliases

# Allows using sudo with other aliases
alias sudo='sudo '


# Systemd Aliases

if command -v systemctl > /dev/null 2>&1
then
    alias stats="systemctl status"
    alias starts="sudo systemctl start"
    alias stops="sudo systemctl stop"
    alias restarts="sudo systemctl restart"
    alias reloads="sudo systemctl reload"
    alias enables="sudo systemctl enable"
    alias disables="sudo systemctl disable"
    alias masks="sudo systemctl mask"
    alias unmasks="sudo systemctl unmask"
fi


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
