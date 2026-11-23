# Azure

See what’s running in an Azure subscription, who can access it, and which resources may add to your bill. Start with one read in a subscription you recognize. The agent confirms the target and explains what it found before suggesting a change.

> Check which Azure tenant and subscription you’re using. List the resource groups in that subscription and tell me what is worth checking next. Wait before changing anything.

## What you can ask for

- List resource groups, virtual machines, storage accounts or networks.
- Review role assignments and flag broad access that deserves a closer look.
- Check storage or network settings that could expose data.
- Find resources that may be adding to your bill.
- Prepare a change plan and show what needs approval.

[More examples](docs/use_cases.md) · [Commands and input files](docs/command_reference.md)

## Before changing anything

A write starts with an offline preview. Use `--bind-azure` to save a plan tied to the current sign-in and target. If the identity, subscription, endpoint or request changes, make a new plan for approval. Covered changes such as starting a VM need permission to spend. The receipt says what Azure reported and what still needs checking. [Approval and receipt steps](docs/safety_model.md)

## Install

Ask your agent to install `azure` from `Qwayk/safe-agent-skills`, or run:

```bash
npx skills add Qwayk/safe-agent-skills@azure -g -y
```

If you have the CLI files, install from that folder with Python 3.12 or later:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
```

Use your local Azure CLI sign-in or a token kept on your machine. [Set up access](docs/onboarding.md) · [Run a first read](docs/quickstart.md)

## Coverage and checks

The package has 339 service commands and 26,337 operations selected from 214,231 official Azure REST specification entries. It covers Azure Resource Manager and Azure service APIs, including selected preview operations. Microsoft Graph, Microsoft 365, Azure DevOps and other separate products sit outside that inventory. Azure permissions and each service’s connection settings still apply. The install and approval steps were checked offline. A real account check is separate. [API coverage](docs/api_coverage.md) · [Test results](docs/proof.md) · [All guides](docs/README.md)
