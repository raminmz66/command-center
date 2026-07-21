#!/usr/bin/env python3

import subprocess


def run_command(widget, path, terminal=False):

    if terminal:

        subprocess.Popen(
            [
                "gnome-terminal",
                "--",
                "bash",
                path
            ]
        )

    else:

        subprocess.Popen(
            [
                path
            ]
        )