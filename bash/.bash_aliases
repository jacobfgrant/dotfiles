### Bash Aliases ###
#
# Bash-specific aliases and configuration
#
# Table of Contents:
#   - COMMON ALIASES
#   - BASH CONFIGURATION
#   - TOOL COMPLETION
#

## COMMON ALIASES ##

[ -f ~/.common_aliases.sh ] && . ~/.common_aliases.sh


## BASH CONFIGURATION ##

HISTSIZE=20000
HISTFILESIZE=20000


## TOOL COMPLETION ##

# AWS CLI #

if command -v aws >/dev/null 2>&1 && command -v aws_completer >/dev/null 2>&1
then
    complete -C "$(command -v aws_completer)" aws
fi


# Google Cloud CLI #

if command -v brew >/dev/null 2>&1 && command -v gcloud >/dev/null 2>&1 
then
    GCLOUD_PATH="$(brew --prefix)/share/google-cloud-sdk/path.bash.inc"
    GCLOUD_COMPLETION="$(brew --prefix)/share/google-cloud-sdk/completion.bash.inc"

    [ -f "$GCLOUD_PATH" ] && source "$GCLOUD_PATH"
    [ -f "$GCLOUD_COMPLETION" ] && source "$GCLOUD_COMPLETION"
fi
