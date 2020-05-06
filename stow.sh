#/bin/sh

DOTFILES_DIR=$(dirname "$0")

echo "$DOTFILES_DIR"

cd "$DOTFILES_DIR"

find . -maxdepth 1 -type d -not -name '.git' | sed -n 's/\.\/\(.*\)/\1/p' |  xargs -n 1 stow -R
