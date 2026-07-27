# Step 23c — Favorites section separation

**Date:** 2026-07-27  
**Phase:** 1 — UI Professionalization (polish)  
**Cycle:** Step 23c — Favorites section separation  
**Status:** Approved for planning

## Goal

Make the Favorites strip visually distinct from category chips above and the main command grid below, using a stronger Soft GNOME tinted panel and a larger **Favorites** label — CSS only.

## Decisions

| Topic | Choice |
|-------|--------|
| Separation needed | **C** — clearer separation above and below Favorites |
| Visual treatment | **C** — soft tinted Favorites panel (approved preview v2 “stronger”) |
| Implementation | **1** — CSS-only on `.cc-favorites-section` / `.cc-favorites-label` |

## In scope

- Stronger panel: fill `alpha(@theme_fg_color, 0.09)`, border `1px solid alpha(@borders, 1.0)`, radius ~12px
- Padding ~14px; margin ~14px top / ~16px bottom
- Label: ~17px, font-weight 700, full opacity (no fade)
- Empty Favorites section remains hidden (existing `no_show_all` behavior)

## Out of scope

- `menu.py` structure changes
- Card / chip / search / Apply-favorites behavior changes
- Shadows or gold chrome on the panel

## Architecture

```
style.css
  .cc-favorites-section  — panel chrome + spacing
  .cc-favorites-label    — larger, clearer title
```

Existing `favorites_box` already wraps label + favorites grid.

## Verification

- GTK CSS loads without error
- With favorites: panel reads as a clear band between chips and main grid
- Without favorites: no Favorites label/panel
- Soft GNOME cards, chips, search, edit/Apply unchanged

## Risks

- Theme variance: use `@theme_fg_color` / `@borders` alphas, not hard gray hex only
- Too-strong tint on dark themes — prefer alpha of fg so it adapts
