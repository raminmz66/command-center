# Step 20 — Soft GNOME CSS Redesign

**Date:** 2026-07-23  
**Phase:** 1 — UI Professionalization  
**Cycle:** Step 20 — Professional CSS redesign  
**Status:** Approved for planning

## Goal

Make Command Center look like a polished **Soft GNOME** utility: rounded command cards, light elevation, Adwaita-style blue hover outline, balanced icon + title + short description — while remaining **theme-aware** (light/dark follow the desktop).

## Decisions

| Topic | Choice |
|-------|--------|
| Visual identity | Soft custom skin (not pure stock, not strong brand) |
| Light/dark | Follow system theme |
| Scope of code changes | Broader UI pass: CSS + light Python hooks / layout tweaks |
| Card density | Balanced: icon + title + short description on card |
| Visual direction | **A — Soft GNOME** (from companion mockups) |
| Implementation approach | **CSS-first + light widget hooks** |

## In scope

- Soft GNOME visuals in `framework/style.css`
- HeaderBar polish (spacing, button feel)
- Light Python hooks in `widgets.py` / `menu.py`: style classes, description truncation, spacing/size tweaks as needed for CSS targeting
- Keep 3-column grid unless a small padding/size tweak is required for the look

## Out of scope

- Search, categories, favorites (Steps 21–23)
- Confirm dialogs, status command types, keyboard shortcuts
- Custom brand colors that ignore the system theme
- Full `CommandCard` rewrite
- Automated UI test suite

## Architecture

```
style.css  →  appearance (radius, elevation, hover, typography, spacing)
widgets.py →  structure + style classes (command-card, command-title, command-desc)
menu.py    →  optional window/grid style classes; minor layout spacing
metadata.py / launcher.py → unchanged
```

Appearance stays in CSS. Python does not hard-code colors for the Soft GNOME look except where GTK requires a style class hook.

## Components

### `style.css`

- Window / content padding consistent with Soft GNOME mockup
- HeaderBar action buttons: rounded, quiet default, clear hover
- `.command-card`: ~14px radius, light border/elevation, fixed-ish card size for balanced layout
- Hover: accent outline/border (Adwaita blue family, e.g. `#3584e4` or theme accent where available) + slight brightness — no heavy animation
- `.command-title` / `.command-desc`: hierarchy (title emphasized, description quieter, wrapped/centered)

Prefer theme-inherited colors; use accent mainly for hover focus treatment so light and dark both feel native.

### `widgets.py`

- Keep vertical layout: icon → title → description
- Add style classes: `command-title`, `command-desc` (and retain `command-card`)
- Truncate long descriptions to a short line count / character budget so cards stay balanced
- Icon fallback unchanged (`application-x-executable` when theme lacks the named icon)

### `menu.py`

- Optionally add a style class on the window or grid for CSS scoping
- Adjust border width / grid spacing only if needed for Soft GNOME spacing
- Behavior unchanged: load `.sh` scripts, refresh, open folder, run via launcher

## Data flow

Unchanged: script discovery → `read_metadata` → `CommandCard` → click → `run_command`.

## Error handling

- Missing CSS file: app still runs (existing `load_css` guard)
- Missing icons: existing fallback
- Empty descriptions: omit or show empty desc area without breaking layout
- Overlong descriptions: truncated in the widget layer

## Verification

Manual only for this cycle:

1. Run `framework/menu.py` under light and dark system themes
2. Confirm Soft GNOME: rounded cards, balanced content, blue-ish hover outline
3. Header folder / refresh still work; refresh reapplies styled cards
4. Terminal and non-terminal scripts still launch
5. Icon fallback still works

**Done when:** Soft GNOME look in both themes, CSS owns appearance, Python only has light hooks, no regressions in launch / refresh / open-folder / run.

## Risks

- GTK 3 CSS varies by theme; primary targets are Adwaita and Yaru. Small differences on other themes are acceptable.
- CSS transitions in GTK 3 are limited; hover is outline/brightness, not web-style motion.

## Companion reference

Mockup session chose **A — Soft GNOME** (elevated light cards, blue hover outline on middle card). Session artifacts under `.superpowers/brainstorm/` (local only; gitignored).
