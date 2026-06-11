# Release process

This repo uses editable installs during development.

When releasing:
1) Update `ghost_api_tool/__init__.py` version.
2) Update `pyproject.toml` version.
3) Re-run unit tests.

Do not publish secrets in docs or examples.
