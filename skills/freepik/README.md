# Freepik

Find stock photos, review previews, and download the exact assets you approve. The tool keeps a CSV with the license link and a record of each file it saves. Freepik is now called Magnific. The skill still installs as `freepik-api-safe-cli`, and the command is still `freepik-api-tool`.

Ask your agent to install `freepik-api-safe-cli` from `Qwayk/safe-agent-skills`, or run the command below.

```bash
npx skills add Qwayk/safe-agent-skills@freepik-api-safe-cli -g -y
```

Then [connect your account](docs/onboarding.md) and try this request.

> Find 15 non-AI photos for mushroom pasta. Show me the best previews so I can choose what to download.

A licensed download can use credits and create a record in your account. Review a saved preview first. The tool checks that the account, assets and settings still match before sending the download request.

- [Get started](docs/quickstart.md)
- [See all commands](docs/command_reference.md)
- [See what happens before and after a download](docs/safety_model.md)
- [Browse all guides](docs/README.md)
