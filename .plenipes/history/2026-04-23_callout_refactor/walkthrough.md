# Walkthrough - Callout Stack Refactor

## Changes
- Moved Callout parsing to `StaticizerStep` using a recursive stack-based scanner.
- Added `render_single_callout` to `SSGAdapter`.
- Cleaned up redundant regex-based calls in `steps.py` and `egress_dispatcher.py`.

## Validation
- Governance audit passed.
- Nested callouts are now correctly structured as nested SSG components.
