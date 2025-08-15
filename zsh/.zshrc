### ZSH Run Commands ###
#
# ZSH configuration, completion, and prompt setup
#
# Table of Contents:
#   - COMMON ALIASES
#   - TOOL COMPLETION
#   - ZSH CONFIGURATION
#

## COMMON ALIASES ##

[ -f ~/.common_aliases.sh ] && . ~/.common_aliases.sh


## TOOL COMPLETION ##

# AWS CLI #

if (( $+commands[brew] && $+commands[aws] ))
then
    AWS_ZSH_COMPLETER="$(brew --prefix)/share/zsh/site-functions/aws_zsh_completer.sh"

    if [[ -f "$AWS_ZSH_COMPLETER" ]]
    then
        autoload -Uz compinit
        compinit
        source "$AWS_ZSH_COMPLETER"
    fi
fi


# Google Cloud CLI #

if command -v brew >/dev/null 2>&1 && command -v gcloud >/dev/null 2>&1
then
    GCLOUD_PATH="$(brew --prefix)/share/google-cloud-sdk/path.zsh.inc"
    GCLOUD_COMPLETION="$(brew --prefix)/share/google-cloud-sdk/completion.zsh.inc"

    [[ -f "$GCLOUD_PATH" ]] && source "$GCLOUD_PATH"
    [[ -f "$GCLOUD_COMPLETION" ]] && source "$GCLOUD_COMPLETION"
fi


# Terragrunt #

if command -v terragrunt >/dev/null 2>&1
then
    autoload -U +X bashcompinit && bashcompinit
    complete -C "$(command -v terragrunt)" terragrunt
fi


## ZSH CONFIGURATION ##

# ZSH Prompt #

PROMPT='%(?.%F{10}⏺.%F{9}⏺)%f %2~ $ '


# ZSH Right Prompt #

# Autoload zsh's `add-zsh-hook` and `vcs_info` functions.
# -U: autoload without substitution, -z: use zsh style.
autoload -Uz add-zsh-hook
autoload -Uz vcs_info

# Set prompt substitution to use the vcs_info_message variable.
setopt prompt_subst

# Run the `vcs_info` hook to grab git info before displaying the prompt.
add-zsh-hook precmd vcs_info

# Style the vcs_info message for better readability and clarity.

# Enable vcs_info for git.
zstyle ':vcs_info:*' enable git

# Format for the vcs_info message: branch name, unstaged and staged changes.
zstyle ':vcs_info:git*' formats '%b%u%c'

# Format when the repo is in an action state (merge, rebase, etc).
# %F{14}: Set foreground color; %*: current time; %f: reset color.
zstyle ':vcs_info:git*' actionformats '%F{14}⏱ %*%f'

# Strings to represent unstaged (*) and staged (+) changes.
zstyle ':vcs_info:git*' unstagedstr '*'
zstyle ':vcs_info:git*' stagedstr '+'

# Enable checking for unstaged and staged changes. Note: Can be slow on large repos.
zstyle ':vcs_info:*:*' check-for-changes true

# Set the right prompt to the vcs_info message.
RPROMPT='%F{8}⎇ $vcs_info_msg_0_%f'
