#!/usr/bin/env python3
"""XDG / install-aware paths for Command Center."""

import os


APP_ID = "command-center"


def _xdg_data_home():
    return os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")


def data_dir():
    """User data root: ~/.local/share/command-center"""
    return os.path.join(_xdg_data_home(), APP_ID)


def scripts_dir():
    """User command scripts (always under XDG data)."""
    return os.path.join(data_dir(), "scripts")


def framework_dir():
    """Directory containing this package (git checkout or installed tree)."""
    return os.path.dirname(os.path.abspath(__file__))


def css_path():
    return os.path.join(framework_dir(), "style.css")


def ensure_scripts_dir():
    path = scripts_dir()
    os.makedirs(path, mode=0o755, exist_ok=True)
    return path
