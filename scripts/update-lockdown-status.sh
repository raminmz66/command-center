#!/bin/bash
# NAME=Lockdown Status
# ICON=🔒
# DESC=Show automatic update lockdown status
# COLOR=r
# TERMINAL=true
# CATEGORY=Security
# CONFIRM=true

sudo update-lockdown --status

echo
read -p "Press Enter to close..."
