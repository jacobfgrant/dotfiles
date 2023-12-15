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

if command -v xdg-open >/dev/null 2>&1
then
    alias open='xdg-open'
fi



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


# SSH Keys

update_authorized_keys() {
    default_url="https://gist.githubusercontent.com/jacobfgrant/40328a116c7fa215e01af4c4a63a5059/raw/authorized_keys"
    default_authorized_keys_file="$HOME/.ssh/authorized_keys"
    backup=false
    overwrite=false

    while getopts ":u:a:bO" opt
    do
        case $opt in
            u) url="$OPTARG"
               ;;
            a) authorized_keys_file="$OPTARG"
               ;;
            b) backup=true
               ;;
            O) overwrite=true
               ;;
            \?) echo "Invalid option -$OPTARG" >&2
                return 1
                ;;
        esac
    done

    # Validate URL format (basic validation)
    if ! [[ $url =~ ^http[s]?:// ]]
    then
        echo "Invalid URL format: $url"
        return 1
    fi

    # Create a backup if -b flag is set
    if [ "$backup" = true ]
    then
        if [ -f "$authorized_keys_file" ]
        then
            cp "$authorized_keys_file" "${authorized_keys_file}.$(date +%s).bak" || {
                echo "Failed to create backup of $authorized_keys_file"
                return 1
            }
        else
            echo "Warning: Authorized keys file does not exist; no backup created."
        fi
    fi

    # Download the keys and handle errors
    curl_output=$(curl -s "$url")
    if [ $? -ne 0 ]
    then
        echo "Error downloading keys from $url"
        return 1
    fi

    if [ "$overwrite" = true ]
    then
        echo "$curl_output" > "$authorized_keys_file" || {
            echo "Error writing to $authorized_keys_file"
            return 1
        }
    else
        # Ensure authorized_keys file exists and is writable
        if [ ! -f "$authorized_keys_file" ]
        then
            touch "$authorized_keys_file" || {
                echo "Cannot create $authorized_keys_file. Check permissions."
                return 1
            }
        elif [ ! -w "$authorized_keys_file" ]
        then
            echo "No write permission to $authorized_keys_file"
            return 1
        fi

        echo "$curl_output" | while read -r key
        do
            if ! grep -qF "$key" "$authorized_keys_file"
            then
                echo "$key" >> "$authorized_keys_file" || {
                    echo "Error writing to $authorized_keys_file"
                    return 1
                }
            fi
        done
    fi

    echo "Authorized keys updated successfully."
}



# Terraform Aliases

alias tf="terraform"
alias tfi="terraform init"
alias tfv="terraform validate"
alias tfp="terraform plan"
alias tfa="terraform apply"
alias tfd="terrform destroy"
alias tff="terraform fmt"
alias tfmt="terraform fmt"
