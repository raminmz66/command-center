# Command Center

Dynamic GTK command launcher.

## Where we are

See **[STATUS.md](STATUS.md)** for the current phase, cycle stage, and next action.

Long-term vision: [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md) · Version sketch: [ROADMAP.md](ROADMAP.md)

## Workflow

Each unit of work: **brainstorm → design spec → implementation plan → execute**.

| Path | Purpose |
|------|---------|
| `docs/superpowers/specs/` | Approved design specs |
| `docs/superpowers/plans/` | Implementation plans |

## Structure

```
framework/
  menu.py       Main GTK application
  widgets.py    UI components
  metadata.py   Script metadata parser
  launcher.py   Command execution
  style.css     GTK styling

scripts/        User commands
icons/          Custom icons
```
