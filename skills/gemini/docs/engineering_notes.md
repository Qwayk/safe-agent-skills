# Engineering Notes

- Date (UTC): 2026-06-28
- Boundary: official Gemini Generative Language REST discovery documents for `v1beta` and `v1`.
- Build strategy: generated-inventory possible.
- Pinned revisions: `v1beta` revision `20260626`; `v1` revision `20260626`.
- Runtime shape: generated registry with explicit `<family> <method>` commands, no raw request bridge.
- Safety shape: reads and compute-style calls run directly; state changes dry-run first and require reviewed plan apply.
- Validation: `python3 -m unittest -q` passed with 23 tests.
