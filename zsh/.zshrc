### ZSH Run Commands ###
#
# ZSH configuration, completion, and prompt setup
#
# Table of Contents:
#   - ENVIRONMENT
#   - COMMON ALIASES
#   - TOOL COMPLETION
#   - ZSH CONFIGURATION
#

## ENVIRONMENT ##

# Homebrew #

# Keep Homebrew ahead of system tools in every interactive shell. Only login
# shells read .zprofile; a shell launched from a GUI app (not a terminal) starts
# from the bare system PATH and would otherwise find Apple's tools first.
# Only prepend when Homebrew is absent, so a shell started inside an activated
# virtualenv keeps the virtualenv's interpreter ahead of Homebrew's.
typeset -U PATH path fpath
if [[ -d /opt/homebrew/bin && -z ${path[(r)/opt/homebrew/bin]} ]]
then
    path=(/opt/homebrew/bin /opt/homebrew/sbin $path)
fi

# Homebrew's zsh completions (brew, gh, doctl, uv, terraform, kubectl, ...)
if [[ -d /opt/homebrew/share/zsh/site-functions ]]
then
    fpath=(/opt/homebrew/share/zsh/site-functions $fpath)
fi


## COMMON ALIASES ##

[ -f ~/.common_aliases.sh ] && . ~/.common_aliases.sh


## TOOL COMPLETION ##

# Initialize the completion system once, before any tool hooks into it
autoload -Uz compinit bashcompinit
compinit
bashcompinit

zstyle ':completion:*' menu select


# AWS CLI #

# Homebrew's lazy _aws stub wastes the first Tab of every shell; register directly.
(( $+commands[aws_completer] )) && complete -C aws_completer aws


# Google Cloud CLI #

# Homebrew links this file without a #compdef tag, so compinit skips it.
if [[ -f /opt/homebrew/share/google-cloud-sdk/completion.zsh.inc ]]
then
    source /opt/homebrew/share/google-cloud-sdk/completion.zsh.inc
fi


# Docker #

# Docker Desktop installs no zsh completion; the CLI generates its own.
(( $+commands[docker] )) && source <(docker completion zsh)


# Terragrunt #

(( $+commands[terragrunt] )) && complete -o nospace -C "$commands[terragrunt]" terragrunt


## ZSH CONFIGURATION ##

# History #

# macOS's /etc/zshrc caps SAVEHIST at 1000; match bash's 20000
HISTFILE="$HOME/.zsh_history"
HISTSIZE=20000
SAVEHIST=20000

setopt EXTENDED_HISTORY         # record timestamp and duration per entry
setopt INC_APPEND_HISTORY       # write each command as it runs, not at exit
setopt HIST_IGNORE_ALL_DUPS     # drop the older copy of a repeated command
setopt HIST_IGNORE_SPACE        # a leading space keeps a command out of history
setopt HIST_REDUCE_BLANKS


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
