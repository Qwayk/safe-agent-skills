# Engineering notes

## 2026-08-11

- Scope locked: official two-operation GiantPanda Parking API family.
- Docs were rewritten to match implemented command flags, fixed host, plan/apply gates, local auth check behavior, and 100-domain add cap.
- Wrapper file set added under `skills/giantpanda-safe-cli/`.
- No runtime logic changes were made in this docs-only pass.
- Final main-builder review added explicit redirect refusal so token-bearing requests are never followed to another URL.
