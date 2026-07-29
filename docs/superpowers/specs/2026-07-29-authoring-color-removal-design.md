# Authoring color removal

**Date:** 2026-07-29  
**Phase:** 4 — Framework Release (reordered)  
**Cycle:** Authoring color removal  
**Status:** Approved for planning  
**Parent:** [2026-07-29-authoring-form-redesign-design.md](2026-07-29-authoring-form-redesign-design.md)

## Goal

Remove color selection from command authoring now that emoji icons carry the visual identity on their own.

## Decision

- Remove the color picker from the authoring form
- Stop tinting emoji icons on cards
- Stop writing new `# COLOR=` metadata
- Keep reading old `# COLOR=` metadata so existing scripts remain compatible

## In scope

- Remove color UI from `framework/authoring.py`
- Remove color swatch / icon tint CSS from `framework/style.css`
- Remove card tint application from `framework/widgets.py`
- Stop emitting color metadata in `framework/scriptio.py`
- Update tests

## Out of scope

- Rewriting old scripts to delete existing `# COLOR=` lines
- Changing emoji catalog contents

## Success criteria

- New and edited commands no longer expose color controls
- Newly saved scripts do not contain `# COLOR=`
- Existing scripts with `# COLOR=` still load and run
- Cards render consistently without color tint logic
