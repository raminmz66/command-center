# Terminal hold — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** After every `TERMINAL=true` script exits, keep gnome-terminal open until the user presses Enter.

**Architecture:** Pure `terminal_argv(path)` builds the gnome-terminal command with a `bash -c` wrapper that runs the quoted script then `read -r -p 'Press Enter to close…'`. `run_command` uses it when `terminal=True`.

**Tech Stack:** Python 3, `subprocess`, `shlex`, unittest

**Spec:** [docs/superpowers/specs/2026-08-08-terminal-hold-design.md](../specs/2026-08-08-terminal-hold-design.md)

## Global Constraints

- Always hold for terminal launches; simple Enter prompt only
- Do not modify user script files
- Quote paths with `shlex.quote`
- Keep hard-coded `gnome-terminal`
- Commit after each task

## File map

| File | Role |
|------|------|
| `framework/launcher.py` | `terminal_argv`, `run_command` |
| `framework/test_launcher.py` | Unit tests |
| `STATUS.md` | Cycle gate |

---

### Task 1: `terminal_argv` + tests + wire `run_command`

**Files:**
- Modify: `framework/launcher.py`
- Create: `framework/test_launcher.py`

**Interfaces:**
- Produces: `terminal_argv(path: str) -> list[str]`
- Produces: `run_command(widget, path, terminal=False)` uses `terminal_argv` when `terminal` is true

- [x] **Step 1: Write failing tests**

```python
# framework/test_launcher.py
import unittest
from unittest import mock

import launcher


class LauncherTests(unittest.TestCase):
    def test_terminal_argv_shape(self):
        argv = launcher.terminal_argv("/tmp/hello.sh")
        self.assertEqual(argv[:3], ["gnome-terminal", "--", "bash"])
        self.assertEqual(argv[3], "-c")
        self.assertIn("/tmp/hello.sh", argv[4])
        self.assertIn("Press Enter to close", argv[4])

    def test_terminal_argv_quotes_spaces(self):
        argv = launcher.terminal_argv("/tmp/my script.sh")
        self.assertIn("'/tmp/my script.sh'", argv[4])

    def test_run_command_terminal_uses_argv(self):
        with mock.patch("launcher.subprocess.Popen") as popen:
            launcher.run_command(None, "/tmp/x.sh", terminal=True)
            popen.assert_called_once()
            self.assertEqual(
                popen.call_args[0][0],
                launcher.terminal_argv("/tmp/x.sh"),
            )

    def test_run_command_non_terminal(self):
        with mock.patch("launcher.subprocess.Popen") as popen:
            launcher.run_command(None, "/tmp/x.sh", terminal=False)
            popen.assert_called_once_with(["/tmp/x.sh"])
```

- [x] **Step 2:** `cd framework && python3 -m unittest test_launcher -v` — FAIL

- [x] **Step 3: Implement**

```python
# framework/launcher.py
#!/usr/bin/env python3

import shlex
import subprocess

HOLD_PROMPT = "Press Enter to close…"


def terminal_argv(path):
    quoted = shlex.quote(path)
    # Run script, then prompt. Preserve script exit for the shell but still hold.
    shell = (
        f"bash {quoted}; "
        f"printf '\\n'; "
        f"read -r -p {shlex.quote(HOLD_PROMPT)} _"
    )
    return ["gnome-terminal", "--", "bash", "-c", shell]


def run_command(widget, path, terminal=False):
    if terminal:
        subprocess.Popen(terminal_argv(path))
    else:
        subprocess.Popen([path])
```

- [x] **Step 4:** Tests PASS; `python3 -m unittest discover` PASS

- [x] **Step 5: Commit** `feat: hold terminal open until Enter after script exit.`

---

### Task 2: STATUS + mark plan done

**Files:**
- Modify: `STATUS.md`
- Modify: this plan checkboxes

- [x] **Step 1:** Set cycle Terminal hold → `done`; next action = Reorder favorites (or continue).

- [x] **Step 2:** Optional smoke: launch a `TERMINAL=true` sample and confirm prompt (manual; no screenshot required).

- [x] **Step 3: Commit** `docs: mark terminal-hold cycle done.`

---

## Plan self-review

- Spec success criteria covered by Task 1 tests + behavior  
- No HOLD metadata / exit banner creep  
- Commit per task
