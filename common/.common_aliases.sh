### Common Shell Aliases ###
#
# Common aliases across shells (bash, zsh, etc.)
#
# Table of Contents:
#   - ENVIRONMENT
#   - TOOLS & SERVICES  
#   - CORE ALIASES
#   - PACKAGE MANAGERS
#   - DEVELOPMENT TOOLS
#   - UTILITIES
#

## ENVIRONMENT ##

# PATH Extensions #

# /usr/local/go/bin
if [ -d "/usr/local/go/bin" ]
then
    export PATH="$PATH:/usr/local/go/bin"
fi


# Go Configuration #

if [ -d "$HOME/Developer" ]
then
    export GOPATH="$HOME/Developer/go"
else
    export GOPATH="$HOME/.go"
fi


## TOOLS & SERVICES ##

# Ansible #

ANSIBLE_REPO_URL="https://github.com/jacobfgrant/ansible-configure.git"

alias ansible-configure="sudo ansible-pull --url $ANSIBLE_REPO_URL -i $(uname -n), main.yml"
alias ansible-configure-base="sudo ansible-pull --url $ANSIBLE_REPO_URL -i $(uname -n), main.yml --skip-tags installs"
alias ansible-configure-server="sudo ansible-pull --url $ANSIBLE_REPO_URL -i $(uname -n), main.yml --skip-tags gui"


## CORE ALIASES ##

# System & Navigation #

alias celar="clear"
alias cls="clear && ls -CF"


alias h="history"
alias hg="history | grep"


# ls with color
if command -v ls >/dev/null 2>&1
then
    if ls --color=auto >/dev/null 2>&1
    then
        alias ls="ls --color=auto"
    fi
fi


# ls
alias l="ls -CF"
alias la="ls -aCF"
alias ll="ls -lhF"
alias lla="ls -lahF"


# Grep with color
alias grep="grep --color=auto"
alias fgrep="fgrep --color=auto"
alias egrep="egrep --color=auto"


# Make "open" portable
if command -v xdg-open >/dev/null 2>&1
then
    alias open='xdg-open'
fi


# Directory Navigation #

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


# Git #

alias gpo="git push origin"
alias gum="git checkout master && git pull upstream master"


## PACKAGE MANAGERS ##

# Homebrew #

if command -v brew >/dev/null 2>&1
then
    alias brewup="brew update && brew upgrade"
    alias brewc="brew cleanup"
fi


# APT #

if command -v apt-get >/dev/null 2>&1
then
    alias aptup="sudo apt-get update && sudo apt-get upgrade"
    alias aptupd="sudo apt-get update && sudo apt-get dist-upgrade"
    alias apti="sudo apt-get install"
    alias aptui="sudo apt-get remove"
    alias aptuia="sudo apt-get purge"
    alias aptrm="sudo apt-get autoremove"
    alias aptcl="sudo apt-get autoclean"
    alias apts="apt-cache search"
    alias aptsh="apt-cache show"
fi


## DEVELOPMENT TOOLS ##

# Python #

# python -> python3
if ! command -v python &> /dev/null
then
    alias python="python3"
fi


# pip -> pip3
if ! command -v pip &> /dev/null
then
    alias pip="pip3"
fi


# venv
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


# Terraform #

if command -v terraform &> /dev/null
then
    alias tf="terraform"
    alias tfi="terraform init"
    alias tfiu="terraform init -upgrade"
    alias tfv="terraform validate"
    alias tfp="terraform plan"
    alias tfa="terraform apply"
    alias tfd="terraform destroy"
    alias tfc="terraform console"
    alias tff="terraform fmt"
    alias tfg="terraform get"
    alias tfm="terraform modules"
    alias tfo="terraform output"
    alias tfs="terraform state"
    alias tfw="terraform workspace"
fi


# Terragrunt #

if command -v terragrunt &> /dev/null
then
    alias tg="terragrunt"
fi


# Terrascan #

if command -v terrascan &> /dev/null
then
    alias ts="terrascan"
    alias tss="terrascan scan -iac-type terraform"
fi


# Terraform Lint #

if command -v tflint &> /dev/null
then
    alias tfl="tflint"
    alias tfli="tflint -init"
fi


# Terraform Docs #

if command -v terraform-docs &> /dev/null
then
    alias tfdoc="terraform-docs"
    alias tfdoca="terraform-docs asciidoc"
    alias tfdocj="terraform-docs json"
    alias tfdocm="terraform-docs markdown"
    alias tfdocp="terraform-docs pretty"
    alias tfdoct="terraform-docs toml"
    alias tfdocv="terraform-docs tfvars"
    alias tfdocx="terraform-docs xml"
    alias tfdocy="terraform-docs yaml"
fi


# System Administration #

# Allows using sudo with other aliases
alias sudo='sudo '


# systemd (systemctl)
if command -v systemctl > /dev/null 2>&1
then
    alias sstatus="systemctl status"
    alias sstart="sudo systemctl start"
    alias sstop="sudo systemctl stop"
    alias srestart="sudo systemctl restart"
    alias sreload="sudo systemctl reload"
    alias senable="sudo systemctl enable"
    alias sdisable="sudo systemctl disable"
    alias smask="sudo systemctl mask"
    alias sunmask="sudo systemctl unmask"
fi


## UTILITIES ##

# Archives (tar) #

alias mktar="tar -cvf"
alias untar="tar -xvf"
alias mkgz="tar -czvf" 
alias ungz="tar -xzvf"


# SSH #

# Get SSH public key
pubkey() {
    local pubkeyfile="${1:-id_rsa.pub}"

    # Append .pub if not present
    case "$pubkeyfile" in
        *.pub) ;;
        *) pubkeyfile="$pubkeyfile.pub" ;;
    esac

    local fullpath="$HOME/.ssh/$pubkeyfile"

    if [ ! -f "$fullpath" ]
    then
        echo "Key not found: $fullpath" >&2
        return 1
    fi

    if command -v pbcopy >/dev/null 2>&1
    then
        tee >(pbcopy) < "$fullpath"
    else
        cat "$fullpath"
    fi
}


# LaTeX #

# Compile LaTeX with Docker
latex_compile() {
    local image="jacobfgrant/texlive"
    local tier="extra"
    local engine=(latexmk -pdf)
    local watch=false
    local clean=false
    local mode="run"
    local OPTIND opt

    # Check Docker is running
    if ! docker info &>/dev/null; then
        echo "Error: Docker is not running"
        return 1
    fi

    while getopts "pxlswct:" opt; do
        case $opt in
            p) engine=(pdflatex);;
            x) engine=(latexmk -xelatex);;
            l) engine=(latexmk -lualatex);;
            s) mode="shell";;
            w) watch=true;;
            c) clean=true;;
            t) tier="$OPTARG";;
            *) return 1;;
        esac
    done
    shift $((OPTIND-1))

    # Validate tier
    case $tier in
        base|recommended|extra|full) ;;
        *)
            echo "Invalid tier: $tier (must be base, recommended, extra, or full)"
            return 1
            ;;
    esac

    # Watch mode only works with latexmk
    if $watch && [[ "${engine[0]}" != "latexmk" ]]; then
        echo "Error: watch mode (-w) only works with latexmk engines"
        return 1
    fi

    # Show usage if no file provided (unless shell mode)
    if [[ $# -eq 0 && "$mode" != "shell" ]]; then
        echo "Usage: latex_compile [-p|-x|-l|-s|-w|-c] [-t tier] [file.tex]"
        echo ""
        echo "Engines:"
        echo "  (default)  latexmk -pdf"
        echo "  -p         pdflatex"
        echo "  -x         latexmk -xelatex"
        echo "  -l         latexmk -lualatex"
        echo ""
        echo "Options:"
        echo "  -s         open interactive shell"
        echo "  -w         watch mode (recompile on change, Ctrl+C to stop)"
        echo "  -c         clean auxiliary files after compile"
        echo "  -t TIER    image tier: base, recommended, extra (default), full"
        return 1
    fi

    # Add watch flag if requested
    if $watch; then
        engine+=(-pvc)
    fi

    if [[ "$mode" == "shell" ]]; then
        docker run --rm -it \
            -v "$(pwd):/workdir" \
            -w /workdir \
            "${image}:${tier}" \
            /bin/bash
    elif $watch; then
        # Watch mode needs interactive terminal for Ctrl+C
        docker run --rm -it \
            -v "$(pwd):/workdir" \
            -w /workdir \
            "${image}:${tier}" \
            "${engine[@]}" "$@"
    else
        docker run --rm \
            -v "$(pwd):/workdir" \
            -w /workdir \
            "${image}:${tier}" \
            "${engine[@]}" "$@"

        # Clean auxiliary files if requested
        if $clean; then
            docker run --rm \
                -v "$(pwd):/workdir" \
                -w /workdir \
                "${image}:${tier}" \
                latexmk -c "$@"
        fi
    fi
}


# Alias for easier access
alias ltx='latex_compile'
