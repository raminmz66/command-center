#!/usr/bin/env bash
# NAME=Confirm Demo
# ICON=✓
# DESC=Safe example that asks before run
# CATEGORY=General
# TERMINAL=false
# CONFIRM=true

if command -v notify-send >/dev/null 2>&1; then
  notify-send "Command Center" "Confirm Demo ran successfully."
else
  echo "Confirm Demo ran successfully."
fi
