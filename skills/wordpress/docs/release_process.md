# Release process

This page is for maintainers preparing a WordPress tool release. It is not needed for normal agent use.

Before a release, check the user-facing docs, run the tests, and make sure the version matches in both `src/wordpress_api_tool/__init__.py` and `pyproject.toml`.

Suggested process:

1. Update the version in `src/wordpress_api_tool/__init__.py`.
2. Update the version in `pyproject.toml`.
3. Run the unit tests and any relevant CLI smoke checks.
4. Review the public docs that changed.
5. Tag a release only after the release contents are clear.

Do not include secrets, local `.env` values, or private site content in release notes or examples.
