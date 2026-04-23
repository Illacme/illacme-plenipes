# Implementation Plan - Callout Stack Refactor

## Goal
Refactor the callout conversion logic from regex to a stack-based line scanner to support deep nesting.

## Proposed Changes
1. Update `SSGAdapter` to support individual callout rendering.
2. Implement `_staticize_callouts` in `StaticizerStep`.
3. Update `steps.py` and `egress_dispatcher.py` to use the new centralized logic.

## Verification
- Run governance audit.
- Manual test with nested callouts.
