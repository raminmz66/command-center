#!/usr/bin/env python3


# Short keys used as CSS suffixes: command-icon-r, command-icon-g, …
_COLOR_ALIASES = {
    "r": "r",
    "red": "r",
    "g": "g",
    "green": "g",
    "b": "b",
    "blue": "b",
    "o": "o",
    "orange": "o",
    "p": "p",
    "purple": "p",
    "y": "y",
    "yellow": "y",
}


def normalize_icon_color(value):
    """Return a CSS color key (r/g/b/o/p/y) or None if unset/invalid."""
    if not value:
        return None
    return _COLOR_ALIASES.get(str(value).strip().lower())


def truncate_description(text, max_len=48):
    if not text:
        return ""

    if len(text) <= max_len:
        return text

    if max_len <= 1:
        return "…"[:max_len]

    return text[: max_len - 1].rstrip() + "…"


def matches_query(meta, query):
    if query is None or not str(query).strip():
        return True

    needle = str(query).casefold()
    name = str(meta.get("name") or "").casefold()
    desc = str(meta.get("desc") or "").casefold()
    return needle in name or needle in desc
