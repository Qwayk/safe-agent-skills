# Engineering notes

This page keeps the short history of real problems we hit and how we solved them.

It is here to reduce repeated debugging, not to tell the whole build story.

Guidelines:
- Keep entries short and factual.
- Link to the provider doc and the PR or issue when that helps.
- Never include secrets.

## 2026-06-29 - Inventory-backed command surface

- Symptom: Make does not publish one single OpenAPI file at a guessed URL.
- Root cause: the official GitBook reference pages publish one embedded OpenAPI 3.0 JSON block per operation.
- Fix: `scripts/refresh_official_inventory.py` reads `llms.txt`, fetches the API Reference Markdown pages, extracts the OpenAPI blocks, and pins 376 operations from 59 endpoint pages.
- Validation: `.venv/bin/python scripts/refresh_official_inventory.py` and `.venv/bin/python -m unittest -q`.
