# 🚨 Illacme-Plenipes — Copilot Boot Sequence & Engineering Standards

## MANDATORY FIRST ACTION

When starting work on this project, you **MUST** read these files before processing any request:

1. **`.plenipes/rules.md`** — 10 chapters of binding governance standards
2. **`.plenipes/evolution_records.md`** — Documented pitfalls with Guard bindings to automated checks

Do NOT rely on memory or assumptions. These files contain project-specific rules that override general coding practices.

## Pre-commit Governance Gate

This project has **28 automated governance checks** that run on every `git commit` via a pre-commit hook. Commits that fail any check are physically blocked. Key requirements:

- **Three-Phase Archiving**: Run `python3 scripts/harvest.py "Task Title"` before committing to generate required `plan.md`, `task.md`, `walkthrough.md` in `.plenipes/history/`
- **Code Traceability**: Any commit modifying `core/` Python files must include an `[AEL-Iter-ID]` tag
- **Architecture Protection**: 7 sacred class signatures (Pipeline, ConfigManager, EgressDispatcher, etc.) must never be deleted
- **Defensive Coding**: Use `dict.get()` instead of bare `dict[key]` in `core/` files
- **No Mass Deletion**: Removing 30+ lines from a single `core/` file triggers a warning
- **Comment Preservation**: Deleting 10+ comment lines from `core/` triggers a warning

## Engineering Standards

- **Zero Truncation**: Never use `// ... existing code ...` or placeholder comments in edits
- **Chinese Documentation**: All docstrings and comments must follow the established Chinese industrial-grade style
- **Simulation-First**: Changes to egress pipeline must pass `tests/autonomous_simulation.py` before commit

## Post-Session

Append new lessons to `.plenipes/evolution_records.md` with a `Guard:` tag binding to the governance check function that prevents recurrence.
