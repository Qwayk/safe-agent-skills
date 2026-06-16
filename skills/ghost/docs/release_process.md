# Release process

This page is for maintainers preparing a Ghost tool release. Normal users should start with the README, quickstart, or use cases instead.

The repo uses editable installs during development.

When releasing:

1. Update the version in `ghost_api_tool/__init__.py`.
2. Update the version in `pyproject.toml`.
3. Re-run unit tests.
4. Check any docs that changed.
5. Confirm examples do not include private publication data.

Do not publish secrets in docs or examples.
