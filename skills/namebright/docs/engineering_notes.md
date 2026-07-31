# Engineering notes

## 2026-07-31

- Date (UTC): 2026-07-31
- Symptom: docs and sample artifacts still used template language and unsupported command flags.
- Root cause: command and wrapper docs were copied from scaffold and drifted from live flags.
- Fix: aligned docs/examples/tests to exact command schema (`--domain-name`, exact ack flags, `/auth/token`) and removed unsupported placeholders.
- Validation: updated `tests/test_docs_formatting.py` to assert example JSON parse, example schema, and wrapper endpoint path.
- References: `README.md`, `docs/command_reference.md`, `docs/skills_wrappers.md`, `tests/test_docs_formatting.py`.
