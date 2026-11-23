# Cloudinary

Use Cloudinary to find the images and videos a site or campaign uses. Give your agent an asset ID, folder, or search term. It can check which file you mean, where it lives, and what tags or delivery settings it has.

For example, ask “Find this video and tell me its format and which folder it’s in.” The agent starts by reading the media library you chose. It can also look at upload presets, streaming profiles, or account settings if you give it access to those areas.

If you ask the agent to upload, replace, or delete something, it shows the exact change first and waits for you to approve it.

## Install

Ask your agent to install the `cloudinary` skill from `Qwayk/safe-agent-skills`, or run:

```bash
npx skills add Qwayk/safe-agent-skills@cloudinary -g -y
```

If you use the tool from a terminal, follow [Quickstart](docs/quickstart.md) to install it and read one asset.

## Guides

- [Quickstart](docs/quickstart.md) to look up an asset and preview an upload.
- [Connect Cloudinary](docs/onboarding.md) to pick the right settings and check access.
- [Approve and check changes](docs/safety_model.md) to review a plan and read its receipt.
- [All guides](docs/README.md) for commands, coverage, and test results.
