#!/usr/bin/env bash
#
# Desktop notification hook: alerts when Claude Code needs input.
# Wired to the Notification event in ~/.claude/settings.json.
#
# Uses OSC 9 so the terminal itself fires the notification — clicking
# it focuses the exact window/tab that sent it. No external deps.
# Works in Ghostty, iTerm2, WezTerm, Kitty. Silently no-ops elsewhere.
#

set -u

input=$(cat)

message=$(printf '%s' "$input" | jq -r '.message // empty' 2>/dev/null)
[ -z "$message" ] && message="Claude needs your input"

{ printf '\033]9;%s\a' "$message" > /dev/tty; } 2>/dev/null

exit 0
