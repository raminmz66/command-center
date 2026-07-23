#!/usr/bin/env python3


def truncate_description(text, max_len=48):
    if not text:
        return ""

    if len(text) <= max_len:
        return text

    if max_len <= 1:
        return "…"[:max_len]

    return text[: max_len - 1].rstrip() + "…"
