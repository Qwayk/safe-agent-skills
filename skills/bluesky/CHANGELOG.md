# Changelog

## Unreleased

- Include the May 25, 2026 list of 304 Bluesky API commands in the installed package.
- Create a settings file with the two sign-in fields even when the example file is missing.
- Use `auth login` to create a session and `auth refresh` to renew it. Public feed reads and `auth check` leave sign-in to those commands.
- Require a saved, reviewed plan when a repository command creates or updates a Bluesky post. Check the account, server and request before sending it. The post guide shows how to read it back separately.
- Put setup, examples and the steps for reviewing changes in the guides linked from the README.

## 0.1.0

The first package included 304 explicit Bluesky API commands, public reads, local session commands, WebSocket frame capture and the agent skill. It also included local previews, redacted JSON output, the command list and example results. The `jobs` and `demo` starter commands were dropped before this release. Generic `--plan-in` was removed at that time.
