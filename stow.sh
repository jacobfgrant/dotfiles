#/bin/sh
#
# Script to use GNU stow to symlink dotifles.
#
# Run this script to symlink the contents of the directories in the same directory as this
# script to the user's home directory. 
#
#
# Author:  Jacob F. Grant
# Created: 05/05/2020
#


DOTFILES_DIR=$(dirname "$0")
STOW=$(which stow)

# Check that stow is installed
if [ -z "$STOW" ]
then
    echo "'stow' is not installed"
    exit 1
else
    # Stow dotfiles
    cd "$DOTFILES_DIR"
    find . -mindepth 1 -maxdepth 1 -type d -not -name '.git' | xargs -n 1 basename | xargs -n 1 `which stow` -t "$HOME" -R
fi
