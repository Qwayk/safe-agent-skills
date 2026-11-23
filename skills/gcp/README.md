# Google Cloud

Check what’s running in a Google Cloud project, who can access it, and what may be adding to your bill. Start with a project you recognize and one small read. The agent tells you which account it used, what it found, and what’s worth checking next.

> Check which Google Cloud account and project you’re using. List the Compute Engine instances in one zone I recognize. Tell me what’s running and wait before changing anything.

## What you can ask for

- List running servers and external IPs. Point out anything we may be paying for without using.
- Check who can access a project, or whether a storage bucket is public.
- List Cloud Run and Cloud SQL resources. Check which APIs are enabled.
- Read recent logs for a service and summarize the errors.
- Plan a change to a server, network or billing account and wait for approval.

[More examples](docs/use_cases.md) · [Commands and input files](docs/command_reference.md)

## Before changing anything

A write starts with a preview. Use `--bind-adc` to prepare a plan for approval with the actual Google identity, quota project and endpoint. When you apply the plan, the tool checks that the approved request still matches. Some actions, such as starting a VM or linking billing, also need explicit permission to spend money. The receipt says what Google reported and whether you still need to check the result. [Review and approval rules](docs/safety_model.md)

## Install

Ask your agent to install `gcp` from `Qwayk/safe-agent-skills`, or run:

```bash
npx skills add Qwayk/safe-agent-skills@gcp -g -y
```

If you have the CLI source, install it from that folder with Python 3.12 or later:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

Use [the setup guide](docs/onboarding.md) to connect Google Application Default Credentials and check access. Then [run your first read](docs/quickstart.md). Keep credential files, tokens, keys and private settings out of chat.

## Coverage and checks

The inventory includes 175 services and 9,781 operations from Google Discovery and selected official fallback sources on June 25, 2026. It includes 4,614 reads, 902 writes, 2,969 higher-risk operations without a guaranteed snapshot, and 1,296 irreversible operations. The inventory recorded zero unclassified writes and zero unresolved gaps in the selected sources. Google IAM controls what your account can do. The CLI only offers operations listed in the inventory. [API coverage](docs/api_coverage.md)

The install and approval checks have been tested locally. Live use with a Google Cloud account still needs a separate check. [Test results](docs/proof.md) · [All guides](docs/README.md)
