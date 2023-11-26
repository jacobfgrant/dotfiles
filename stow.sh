#!/usr/bin/env sh
#
# Script to use GNU stow to symlink dotfiles.
#
# This script creates symlinks in the user's home directory for the contents of each directory 
# located in the same directory as this script. It utilizes GNU Stow for symlink management.
#
#
# Author:  Jacob F. Grant
# Created: 05/05/2020
#

DOTFILES_DIR=$(dirname "$0")

# Try to locate stow, check /opt/homebrew/bin/stow if not found
STOW=$(which stow 2>/dev/null)
if [ -z "$STOW" ]
then
    if [ -x "/opt/homebrew/bin/stow" ]
    then
        STOW="/opt/homebrew/bin/stow"
    else
        echo "'stow' is not installed"
        exit 1
    fi
fi

# Stow dotfiles
cd "$DOTFILES_DIR" || exit
for dir in */
do
    if [ "$dir" != ".git/" ] && [ "$(ls -A "$dir")" ]
    then
        $STOW -t "$HOME" -R "${dir%/}"
    fi
done
