#!/usr/bin/env python3
import os
import re

from metadata import read_metadata

_META_KEYS = {
    "NAME",
    "ICON",
    "DESC",
    "CATEGORY",
    "TERMINAL",
    "CONFIRM",
    "COLOR",
}


def slug_filename(name):
    raw = (name or "").strip().lower()
    raw = re.sub(r"[^a-z0-9]+", "-", raw).strip("-")
    if not raw:
        raw = "command"
    return raw + ".sh"


def unique_path(directory, filename):
    base, ext = os.path.splitext(filename)
    if not ext:
        ext = ".sh"
    candidate = os.path.join(directory, base + ext)
    n = 2
    while os.path.exists(candidate):
        candidate = os.path.join(directory, f"{base}-{n}{ext}")
        n += 1
    return candidate


def read_script(path):
    meta = read_metadata(path)
    body_lines = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            stripped = line.strip()
            if stripped.startswith("#!"):
                continue
            if stripped.startswith("#"):
                payload = stripped.lstrip("#").strip()
                if "=" in payload:
                    key = payload.split("=", 1)[0].strip().upper()
                    if key in _META_KEYS:
                        continue
            body_lines.append(line)
    body = "".join(body_lines).lstrip("\n")
    return {"meta": meta, "body": body}


def write_script(path, meta, body):
    lines = ["#!/bin/bash\n"]

    def add(key, value):
        if value is None or value == "":
            return
        lines.append(f"# {key}={value}\n")

    add("NAME", meta.get("name"))
    add("ICON", meta.get("icon"))
    add("DESC", meta.get("desc"))
    if meta.get("color"):
        add("COLOR", meta.get("color"))
    add("TERMINAL", "true" if meta.get("terminal") else "false")
    add("CONFIRM", "true" if meta.get("confirm") else "false")
    add("CATEGORY", meta.get("category") or "General")
    lines.append("\n")
    body_text = body or ""
    if body_text and not body_text.endswith("\n"):
        body_text += "\n"
    lines.append(body_text)
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.writelines(lines)
    os.chmod(path, 0o755)


def delete_script(path):
    os.remove(path)
