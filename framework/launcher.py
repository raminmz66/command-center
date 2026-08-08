#!/usr/bin/env python3

import shlex
import subprocess


HOLD_PROMPT = "Press Enter to close…"


def terminal_argv(path):
    quoted = shlex.quote(path)
    shell = (
        f"bash {quoted}; "
        f"printf '\\n'; "
        f"read -r -p {shlex.quote(HOLD_PROMPT)} _"
    )
    return ["gnome-terminal", "--", "bash", "-c", shell]


def run_command(widget, path, terminal=False):
    if terminal:
        subprocess.Popen(terminal_argv(path))
    else:
        subprocess.Popen([path])
