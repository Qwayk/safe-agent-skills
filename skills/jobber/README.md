# Jobber

See which quotes need follow-up, check upcoming jobs and visits, and find invoices that are still unpaid. If you need to change a client or job, ask the agent to show you the exact change first.

> Check that this is the right Jobber account, then show me a few open jobs and unpaid invoices.

Start by checking the connection and confirming the account. Review the saved plan before approving any change. [Approvals and receipts](docs/safety_model.md)

## Install and connect

Install the `jobber` skill using:

```bash
npx skills add Qwayk/safe-agent-skills@jobber -g -y
```

To install the CLI from this folder, use Python 3.12 or later:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install .
```

Follow [Connect Jobber](docs/onboarding.md) to add a token from your own Jobber app. Then [check the connection and read one account](docs/quickstart.md).

## What you can do

Read clients and properties, requests, quotes, jobs, visits, invoices and payments. Use CSV jobs to preview several changes together. The tool also lists webhook topics and checks a webhook signature against the original message.

Jobber controls which records your app can access. The [command list](docs/api_coverage.md) shows what the tool includes, and the [test record](docs/proof.md) shows what has been checked with simulated replies.

[All Jobber guides](docs/README.md)
