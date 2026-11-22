# Contentsquare

Use Contentsquare to see how visitors use your site, download data for your own reports, and check where pages load slowly.

A good first ask:

> Check my Contentsquare connection and list up to five export jobs from the project I choose.

The agent checks the connection, reads from the project you chose, and explains what came back. If you want to create an export job, send an enrichment batch, or change a Speed Analysis event, it shows you the exact request and waits for approval.

You’ll need a Contentsquare account with server-to-server OAuth credentials for the API you want to use. Keep the client secret on your machine.

## Install

Install name: `contentsquare`

```bash
npx skills add Qwayk/safe-agent-skills@contentsquare -g -y
```

For a local copy of the source, use Python 3.12 or newer and run these commands from the Contentsquare folder:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
```

Then follow the [quickstart](docs/quickstart.md) for the first read or [setup guide](docs/onboarding.md) for the account settings.

## Guides

- [Commands and examples](docs/command_reference.md)
- [Approvals and receipts](docs/safety_model.md)
- [API coverage and limits](docs/api_coverage.md)
- [What we've checked](docs/proof.md)

For Data Connect, Web Tag, WebView or mobile SDK setup, use the [Contentsquare guides](docs/references.md). This CLI handles server-side API requests.
