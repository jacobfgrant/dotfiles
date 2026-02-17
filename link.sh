#!/usr/bin/env sh
#
# Symlink dotfiles into the home directory.
#
# For each top-level directory (package), mirrors the directory structure
# under $HOME and creates symlinks to individual files. Pure POSIX shell,
# no external dependencies beyond ln and mkdir.
#
# Existing symlinks are updated. Existing regular files are never clobbered.
# Stale symlinks (pointing into the dotfiles tree at targets that no longer
# exist) are removed automatically.
#
#
# Author:  Jacob F. Grant
# Created: 05/05/2020
#

DOTFILES_DIR=$(cd "$(dirname "$0")" && pwd)

# Remove stale symlinks pointing into the dotfiles directory
find "$HOME" \( -path "$HOME/Library" -o -path "$DOTFILES_DIR" \) -prune \
    -o -type l -print | while IFS= read -r link; do
    # Skip symlinks whose targets still exist
    [ -e "$link" ] && continue

    # Resolve the symlink target to an absolute path
    raw=$(readlink "$link")
    case "$raw" in
        /*) target="$raw" ;;
        *)  target="$(cd "$(dirname "$link")" 2>/dev/null \
                && cd "$(dirname "$raw")" 2>/dev/null \
                && printf '%s/%s' "$(pwd)" "$(basename "$raw")")" || continue ;;
    esac

    # Remove if it pointed into our dotfiles directory
    case "$target" in
        "$DOTFILES_DIR"/*) echo "REMOVE: stale link $link" >&2; rm "$link" ;;
    esac
done

# Create symlinks for each package
for dir in "$DOTFILES_DIR"/*/; do
    # Skip empty directories
    [ -z "$(ls -A "$dir")" ] && continue

    find "$dir" -type f | while IFS= read -r file; do
        rel="${file#"$dir"}"
        target="$HOME/$rel"

        mkdir -p "$(dirname "$target")"

        if [ -L "$target" ]; then
            rm "$target"
        elif [ -e "$target" ]; then
            echo "SKIP: $target already exists" >&2
            continue
        fi

        ln -s "$file" "$target"
    done
done
