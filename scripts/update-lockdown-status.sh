#!/bin/bash
# NAME=Lockdown Status
# ICON=🔍
# DESC=Show automatic update lockdown status
# TERMINAL=true

sudo update-lockdown --status

echo
read -p "Press Enter to close..."
