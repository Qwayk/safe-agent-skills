# Changelog

This tool uses Semantic Versioning. Before version 1.0, a minor release can change how commands work.

## Unreleased

- Included the command list in the Python package so the installed tool can start.
- Onboarding creates an empty settings file if needed and prints a command that works with spaces in its path. An older sample address no longer overrides your company name.
- Reads use the next page Pipedrive returns, show empty results correctly, and report errors as errors.
- Help shows options for the route the command uses. Tokens stay with the configured host during redirects. File checks close the reply after reading headers.
- Merged setup guides and removed examples for features this tool never shipped.

## 0.1.0, May 21, 2026

- Added the read-only CLI, onboarding, and a connection check. The tool uses a local route list and prefers version 2 where both versions are available.
- Added file header checks, support for company names, and cursor paging.
- Kept JSON results and argument errors to one object. Later checks added JSON defaults, a local audit log, stack traces, and examples that show the actual method used for file checks.
