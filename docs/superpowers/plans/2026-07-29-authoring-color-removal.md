# Authoring Color Removal Implementation Plan

**Goal:** Remove color selection and color-tint behavior from authoring and cards, while preserving backward compatibility for existing script metadata.

## Constraints

- Spec: `docs/superpowers/specs/2026-07-29-authoring-color-removal-design.md`
- Keep old `# COLOR=` lines readable
- Do not break create/edit/save flows

## Tasks

### Task 1: Remove color feature from UI and rendering

- [x] Remove color controls from `framework/authoring.py`
- [x] Remove icon tint usage from `framework/widgets.py`
- [x] Remove now-unused color CSS from `framework/style.css`

### Task 2: Remove color persistence from new saves

- [x] Stop defaulting / returning `color` in authoring data
- [x] Stop writing `# COLOR=` in `framework/scriptio.py`
- [x] Leave `framework/metadata.py` tolerant of old color metadata

### Task 3: Verify with tests

- [x] Update focused tests to reflect color removal
- [x] Run targeted test suite for changed modules
- [x] Update `STATUS.md` to `done`
