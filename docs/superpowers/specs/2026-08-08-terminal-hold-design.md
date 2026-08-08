# Terminal hold after script exit

**Date:** 2026-08-08  
**Phase:** Polish backlog  
**Cycle:** Terminal hold / press a key  
**Status:** Approved  
**Parent:** User request — keep terminal output readable for `TERMINAL=true` scripts

## Goal

When a terminal command finishes, keep the gnome-terminal window open until the user presses Enter, so short scripts (status, echo, one-shots) remain readable.

## Decisions

| Topic | Choice |
|-------|--------|
| Scope | **Always** for `TERMINAL=true` |
| Mechanism | **Launcher wrapper** (`bash -c`) — do not edit user scripts |
| Prompt | **Simple:** `Press Enter to close…` |
| Approach | **A** — inline argv builder in `launcher.py` |
| Non-terminal | Unchanged |
| Exit code in prompt | Out of scope |
| Other terminals | Stay on `gnome-terminal` (existing behavior) |

## Behavior

1. User launches a command with `TERMINAL=true`.
2. Command Center opens gnome-terminal and runs the user script.
3. After the script exits (any exit code), print a blank line and:
   `Press Enter to close…`
4. Enter closes the shell → terminal window closes.
5. Paths with spaces/special characters are safely quoted (`shlex.quote`).

## In scope

- `framework/launcher.py`: `terminal_argv(path)` + `run_command` uses it when `terminal=True`
- Unit tests for argv shape and quoting
- Update `STATUS.md` when done

## Out of scope

- Exit-status banner
- “Press any key”
- Per-command `HOLD=` metadata
- `xdg-terminal-exec` / multi-emulator support
- Injecting pause lines into script files
- Changing non-terminal launch

## Success

1. Short `TERMINAL=true` script shows output, then the Enter prompt.  
2. Enter closes the window.  
3. Script files on disk are unchanged.  
4. Non-terminal launch still `Popen([path])`.  
5. Unit tests cover argv construction and spaced paths.
