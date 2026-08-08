#!/usr/bin/env python3

import shlex
import subprocess


HOLD_PROMPT = "Press Enter to close…"


def terminal_argv(path):
    quoted = shlex.quote(path)
    # setsid: script (and daemons it starts, e.g. conky) leave the terminal
    # session so SIGHUP on "Press Enter to close…" does not kill them.
    # Output still goes to this terminal (FDs are inherited).
    shell = (
        f"setsid bash {quoted}; "
        f"printf '\\n'; "
        f"read -r -p {shlex.quote(HOLD_PROMPT)} _"
    )
    return ["gnome-terminal", "--", "bash", "-c", shell]


def run_command(widget, path, terminal=False):
    if terminal:
        subprocess.Popen(terminal_argv(path))
    else:
        subprocess.Popen([path])
