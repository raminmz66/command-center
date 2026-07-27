#!/usr/bin/env python3
import json
import os


def favorites_path():
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    return os.path.join(base, "command-center", "favorites.json")


def load_favorites():
    path = favorites_path()
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


def save_favorites(names):
    path = favorites_path()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(list(names), fh, indent=2)
            fh.write("\n")
    except OSError:
        return


def is_favorite(basename):
    return basename in load_favorites()


def toggle_favorite(basename, known=None):
    names = load_favorites()
    if basename in names:
        names = [n for n in names if n != basename]
        now = False
    else:
        names = names + [basename]
        now = True
    if known is not None:
        known_set = set(known)
        names = [n for n in names if n in known_set]
    save_favorites(names)
    return now
