# Cloudinary

Install slug: `cloudinary`

Use this skill when you want your AI agent to review assets, folders, uploads, delivery settings, and other Cloudinary API work with preview before live changes.

This tool ships 175 explicit Cloudinary REST operations across Upload, Admin, Provisioning, Permissions, Analyze, Live Streaming, Player Profiles, and Video Config. The non-REST Transformation URL API is intentionally out of scope.

## For non-technical users: start here

- [What you can do](docs/use_cases.md)
- [Connect your Cloudinary account](docs/onboarding.md)
- [How live changes stay safer](docs/safety_model.md)

## For technical users: start here

- [Quickstart](docs/quickstart.md)
- [Command reference](docs/command_reference.md)
- [API coverage](docs/api_coverage.md)
- [Proof pack](docs/proof.md)
- [Docs index](docs/README.md)

## What live work looks like

- Reads can run directly.
- Writes stay dry-run first.
- Approved write applies need `--apply --yes`, and when no saved before-state exists they also need explicit no-snapshot approval before Cloudinary HTTP.
- Delete-like actions and access-key actions also need `--ack-irreversible`.
- Sensitive or binary results go to `--out` under `--project-dir`.

## Example requests

- "Show me the details for this Cloudinary asset."
- "Preview deleting this folder, but do not run it yet."
- "Check which Cloudinary operations this tool already ships."
