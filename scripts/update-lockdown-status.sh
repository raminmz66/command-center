#!/bin/bash
# NAME=Lockdown Status
# ICON=system-lock-screen-symbolic
# DESC=Show automatic update lockdown status
# COLOR=r
# TERMINAL=true
# CATEGORY=Security

sudo update-lockdown --status

echo
read -p "Press Enter to close..."
