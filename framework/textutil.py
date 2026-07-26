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


PREFERRED_CATEGORIES = (
    "Desktop",
    "System",
    "Network",
    "Maintenance",
    "Security",
    "General",
)

_PREFERRED_BY_CASEFOLD = {
    name.casefold(): name for name in PREFERRED_CATEGORIES
}


def normalize_category(value):
    if value is None:
        return "General"
    text = str(value).strip()
    if not text:
        return "General"
    return _PREFERRED_BY_CASEFOLD.get(text.casefold(), text)


def ordered_categories(categories):
    seen = set()
    unique = []
    for raw in categories or []:
        if raw is None:
            continue
        text = str(raw).strip()
        if not text:
            continue
        canonical = normalize_category(text)
        key = canonical.casefold()
        if key in seen:
            continue
        seen.add(key)
        unique.append(canonical)

    preferred = [name for name in PREFERRED_CATEGORIES if name.casefold() in seen]
    extras = sorted(
        [name for name in unique if name.casefold() not in _PREFERRED_BY_CASEFOLD],
        key=lambda n: n.casefold(),
    )
    return preferred + extras


def matches_filters(meta, query, category):
    if not matches_query(meta, query):
        return False
    if category is None or not str(category).strip():
        return True
    if str(category).strip().casefold() == "all":
        return True
    meta_cat = normalize_category(meta.get("category") if meta else None)
    want = normalize_category(category)
    return meta_cat.casefold() == want.casefold()
