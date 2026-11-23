#!/bin/sh
#
# Claude Code status line: model · directory · context tokens [· cache]
#

jq -r --arg home "$HOME" '
  def thousands: "\(. / 1000 | round)k";

  def directory:
    .workspace.current_dir
    | if . == $home or startswith($home + "/") then "~" + .[($home | length):] else . end
    | split("/") | .[-2:] | join("/");

  def tokens:
    .context_window
    | (.total_input_tokens // 0 | thousands) as $used
    | if .context_window_size == 1000000 then $used
      else "\($used) / \(.context_window_size | thousands)"
      end;

  def color($code): "\u001b[\($code)m\(.)\u001b[0m";

  # Silent until the prompt cache has 30 minutes or less to live, and while
  # the context is empty (right after /compact), when there is nothing to lose.
  def cache:
    (.context_window.total_input_tokens // 0) as $used
    | (.prompt_cache // {})
    | (((.expires_at // 0) - now) / 60 | ceil) as $minutes
    | if .caching_observed != true or $used == 0 then empty
      elif $minutes <= 0 then "cache cold" | color(34)
      elif $minutes <= 10 then "cache \($minutes)m" | color(33)
      elif $minutes <= 30 then "cache \($minutes)m"
      else empty
      end;

  [.model.display_name, directory, tokens, cache] | join(" · ")
'
