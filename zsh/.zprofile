### ZSH Profile ###

# Homebrew Configuration

export HOMEBREW_PREFIX="/opt/homebrew";
export HOMEBREW_CELLAR="/opt/homebrew/Cellar";
export HOMEBREW_REPOSITORY="/opt/homebrew";
export PATH="/opt/homebrew/bin:/opt/homebrew/sbin${PATH+:$PATH}";
export MANPATH="/opt/homebrew/share/man${MANPATH+:$MANPATH}:";
export INFOPATH="/opt/homebrew/share/info:${INFOPATH:-}";

export HOMEBREW_NO_ENV_HINTS=1

# Keep old (pre-BUSL) versions of terraform for now
export HOMEBREW_NO_CLEANUP_FORMULAE=terraform
