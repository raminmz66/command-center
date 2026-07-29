# App icon — Launcher grid (option B)

**Date:** 2026-07-30  
**Phase:** 4 — Framework Release  
**Cycle:** App icon  
**Status:** Approved  
**Visual ref:** [docs/superpowers/visuals/2026-07-30-app-icon-options.html](../visuals/2026-07-30-app-icon-options.html) (choice **B**)

## Goal

Ship a proper Soft GNOME app icon (launcher-grid mark) so the desktop entry no longer uses generic `utilities-terminal`.

## Decisions

| Topic | Choice |
|-------|--------|
| Concept | **B — Launcher grid** (2×2 cards, one mustard highlight) |
| Desktop `Icon=` | `command-center` |
| Formats | Source SVG + hicolor PNGs `48`, `64`, `128`, `256` + `scalable` SVG |
| Symbolic | **Out of scope** this cycle |
| Install | `.deb` under `/usr/share/icons/hicolor/…`; `install.sh` under `~/.local/share/icons/hicolor/…` |

## Layout

```
icons/command-center.svg                 # source
icons/hicolor/scalable/apps/command-center.svg
icons/hicolor/48x48/apps/command-center.png
icons/hicolor/64x64/apps/command-center.png
icons/hicolor/128x128/apps/command-center.png
icons/hicolor/256x256/apps/command-center.png
```

Packaged to the same relative paths under `/usr/share/icons/` (`.deb`) or `~/.local/share/icons/` (`install.sh`).

## In scope

- Author SVG matching picker option B (mustard `#f6c32a`, Soft GNOME flat)
- Export PNGs for listed sizes
- `packaging/command-center.desktop` → `Icon=command-center`
- `build-deb.sh` + `install.sh` install icons; refresh icon cache when tools exist
- Short note in `packaging/README.md`
- Rebuild `.deb`

## Out of scope

- Symbolic / dark-variant icon
- In-window headerbar branding change
- Flatpak icon story

## Success

1. App menu / overview shows the grid icon after install + cache update  
2. `Icon=command-center` resolves from hicolor  
3. `utilities-terminal` no longer referenced  
