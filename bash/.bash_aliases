### Bash Aliases ###


# Common Aliases

[ -f ~/.common_aliases.sh ] && . ~/.common_aliases.sh


# Bash Configuration

HISTSIZE=20000
HISTFILESIZE=20000


# Google Cloud CLI Homebrew Autocomplete

if command -v brew >/dev/null 2>&1
then
    GCLOUD_PATH="$(brew --prefix)/share/google-cloud-sdk/path.bash.inc"
    GCLOUD_COMPLETION="$(brew --prefix)/share/google-cloud-sdk/completion.bash.inc"

    [ -f "$GCLOUD_PATH" ] && source "$GCLOUD_PATH"
    [ -f "$GCLOUD_COMPLETION" ] && source "$GCLOUD_COMPLETION"
fi
