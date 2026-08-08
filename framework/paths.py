#!/usr/bin/env python3
"""XDG / install-aware paths for Command Center."""

import json
import os
import shutil


APP_ID = "command-center"
_USR_SAMPLES = "/usr/share/command-center/samples"


def _xdg_data_home():
    return os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")


def _xdg_config_home():
    return os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")


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


def deleted_samples_path():
    """Basenames the user deleted; seed must not restore these."""
    return os.path.join(_xdg_config_home(), APP_ID, "deleted-samples.json")


def load_deleted_samples():
    path = deleted_samples_path()
    if not os.path.isfile(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError, json.JSONDecodeError):
        return []
    if not isinstance(data, list):
        return []
    out = []
    for item in data:
        if isinstance(item, str) and item.strip():
            out.append(item.strip())
    return out


def save_deleted_samples(names):
    path = deleted_samples_path()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(list(names), fh, indent=2)
            fh.write("\n")
    except OSError:
        return


def remember_deleted_sample(basename):
    """Tombstone a sample basename so seed will not restore it."""
    if not basename or not basename.endswith(".sh"):
        return
    src_root = samples_dir()
    if not os.path.isdir(src_root):
        return
    if not os.path.isfile(os.path.join(src_root, basename)):
        return
    names = load_deleted_samples()
    if basename in names:
        return
    names.append(basename)
    save_deleted_samples(names)


def seed_sample_scripts():
    """Copy missing sample *.sh into scripts_dir. Never overwrite.

    Skips basenames recorded in deleted-samples.json (user deleted them).
    Returns basenames that were newly copied.
    """
    ensure_scripts_dir()
    src_root = samples_dir()
    created = []
    if not os.path.isdir(src_root):
        return created
    deleted = set(load_deleted_samples())
    dest_root = scripts_dir()
    for name in sorted(os.listdir(src_root)):
        if not name.endswith(".sh"):
            continue
        if name in deleted:
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
