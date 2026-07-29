#!/usr/bin/env python3
"""XDG / install-aware paths for Command Center."""

import os
import shutil


APP_ID = "command-center"
_USR_SAMPLES = "/usr/share/command-center/samples"


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


def samples_dir():
    """Demo script templates for first-launch seed."""
    repo_samples = os.path.join(
        os.path.dirname(framework_dir()), "packaging", "samples"
    )
    beside_framework = os.path.join(os.path.dirname(framework_dir()), "samples")
    for path in (_USR_SAMPLES, beside_framework, repo_samples):
        if os.path.isdir(path):
            return path
    return repo_samples


def seed_sample_scripts():
    """Copy missing sample *.sh into scripts_dir. Never overwrite.

    Returns basenames that were newly copied.
    """
    ensure_scripts_dir()
    src_root = samples_dir()
    created = []
    if not os.path.isdir(src_root):
        return created
    dest_root = scripts_dir()
    for name in sorted(os.listdir(src_root)):
        if not name.endswith(".sh"):
            continue
        src = os.path.join(src_root, name)
        if not os.path.isfile(src):
            continue
        dest = os.path.join(dest_root, name)
        if os.path.exists(dest):
            continue
        shutil.copy2(src, dest)
        os.chmod(dest, 0o755)
        created.append(name)
    return created
