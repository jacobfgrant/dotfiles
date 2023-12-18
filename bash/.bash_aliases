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


# Google Cloud CLI Homebrew Autocomplete

if command -v brew >/dev/null 2>&1
then
    GCLOUD_PATH="$(brew --prefix)/share/google-cloud-sdk/path.bash.inc"
    GCLOUD_COMPLETION="$(brew --prefix)/share/google-cloud-sdk/completion.bash.inc"

    [ -f "$GCLOUD_PATH" ] && source "$GCLOUD_PATH"
    [ -f "$GCLOUD_COMPLETION" ] && source "$GCLOUD_COMPLETION"
fi
