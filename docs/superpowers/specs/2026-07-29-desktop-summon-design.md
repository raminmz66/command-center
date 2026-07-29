# Desktop summon (global shortcut)

**Date:** 2026-07-29  
**Phase:** 3 — Desktop Integration (pulled forward)  
**Cycle:** Desktop summon (global shortcut)  
**Status:** Approved for planning  
**Parent:** PROJECT_ROADMAP Step 27 (lite)

## Goal

Make Command Center one keystroke away: a GNOME Custom Shortcut launches or focuses the app and puts the cursor in search. No in-app global key grab.

## Decisions

| Topic | Choice |
|-------|--------|
| Shortcut behavior | **Always show/focus** — never hide via the shortcut |
| On appear | **Focus search** |
| Process model | **Cold start OK** — closing the window quits; next shortcut launches again |
| Who binds keys | **GNOME Custom Shortcuts** (not in-app grab) |
| Default recommendation | **`Ctrl+Space`** (user changes it in GNOME Settings) |
| In-app settings | **Guidance popover** + Open Keyboard Settings + copyable Exec command |
| Single-instance | **`Gtk.Application`** with stable application id |
| Escape (main grid) | **Launcher-style** — clear search if non-empty; if empty, close/quit |
| Escape (authoring / confirm) | Unchanged existing behavior |

## In scope

- Migrate startup from bare `Gtk.Window` + `Gtk.main()` to `Gtk.Application`
- Single-instance: second launch activates existing window (`present` + focus search when main view is visible)
- `present_and_focus_search()` shared helper
- `.desktop` file + small install helper for `~/.local/share/applications/`
- Header gear/Shortcut control → Soft GNOME popover with setup copy, Copy command, Open Keyboard Settings
- Main-grid Escape: clear then close
- Soft GNOME styling for the new header button / popover

## Out of scope

- In-app global hotkey grab / key recorder writing gsettings
- Detecting whether the user already bound the shortcut
- System tray, autostart daemon, notifications
- Per-command shortcuts
- Packaging (.deb / Flatpak / AppImage)
- Changing authoring Esc rules

## Architecture

```
GNOME Custom Shortcut (Ctrl+Space by default, user-owned)
        │
        ▼
Exec from command-center.desktop
        │
        ▼
Gtk.Application (org.commandcenter.App)
   ├─ first launch → create CommandCenter window → show → focus search
   └─ later activate → present window → focus search (if main view)
```

### Components

| Unit | Responsibility |
|------|----------------|
| `CommandCenterApp` (`Gtk.Application`) | Lifecycle, single-instance activate |
| `CommandCenter` (window) | Existing UI; expose `present_and_focus_search()` |
| `command-center.desktop` | Name, Exec, Icon, StartupWMClass |
| `install-desktop-entry.sh` | Install/symlink desktop file for the user |
| Shortcut popover | Setup guidance UI only |

### Activate / focus rules

1. Always `present()` the primary window.
2. Focus search **only** when the visible stack child is the main launcher (not authoring).
3. Do not discard an in-progress authoring form on activate.

### Escape (main launcher)

Handled for the main view (including when search is focused):

1. If a confirm popover is open → dismiss confirm (existing).
2. Else if search text non-empty → clear search.
3. Else → close window (quit application).

Authoring: unchanged (popover dismiss / cancel).

### Setup popover content

- Title: “Desktop shortcut”
- Body: recommend `Ctrl+Space`; steps to add a Custom Shortcut in GNOME
- Read-only / selectable launch command (same as desktop `Exec`)
- **Copy command** button
- **Open Keyboard Settings** — best-effort launch of GNOME keyboard settings; on failure show manual path text

## Success criteria

- Two launches → one window; second focuses and (on main view) focuses search
- Custom Shortcut using desktop Exec summons correctly when cold or warm
- Esc clears then quits on main grid as specified
- User can discover how to bind/change the shortcut without leaving docs-only README
- Soft GNOME look preserved; no tray/daemon

## Risks

- Wayland focus stealing: `present()` may need `Gtk.Window.present()` + urgency hint; accept best-effort
- Opening exact GNOME “Custom Shortcuts” panel varies by GNOME version — fallback instructions required
- Hardcoded `~/CommandCenter` paths in Exec must match this repo layout until packaging
