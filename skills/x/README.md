# X

Use this tool to find posts and mentions, check an X account, and prepare changes such as a post, reply or direct message. You can check which account is connected before approving a change.

## Install

Ask your agent to install the X skill from Qwayk, or run:

~~~bash
npx skills add Qwayk/safe-agent-skills@x -g -y
~~~

Follow [Quickstart](docs/quickstart.md) to install the command and run the first checks. Follow [Connect your X account](docs/onboarding.md) when you are ready to use your account.

## What you can ask

- Show my connected account and the five most recent mentions.
- Draft a reply and show me the exact post and account before publishing.
- Check whether this person can receive a direct message from my account. Show me the message and why we have permission before sending.

X may charge for live reads and writes, including the account and recipient checks used to prepare a plan. Review the cost and exact action before approving live work. [X API pricing](https://docs.x.com/x-api/getting-started/pricing)

See [Commands](docs/command_reference.md), [How approvals work](docs/safety_model.md), and [What we tested](docs/proof.md).
