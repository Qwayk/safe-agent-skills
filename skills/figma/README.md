# Figma

Use this tool to review a Figma design before a handoff. Give your agent a file link and ask it to check the latest version, read the comments, or find the components used in a screen. It can also get image links for the frames you want to share.

For example, ask “Read the comments in this file and tell me what still needs a decision.” The agent starts by checking that it can open the file with your Figma connection. It can also review a team library or check which webhooks are set up if your account has access.

If you ask the agent to post a comment or make another change, it shows you the exact change first and waits for your approval.

## Install

Ask your agent to install the `figma-safe-cli` skill from `Qwayk/safe-agent-skills`, or run:

```bash
npx skills add Qwayk/safe-agent-skills@figma-safe-cli -g -y
```

If the skill does not show up, reopen the app or attach it to your workspace. For the command-line tool, use the install steps in [Quickstart](docs/quickstart.md).

## Guides

- [Quickstart](docs/quickstart.md) shows how to read a file, get image links, and preview a comment.
- [Connect Figma](docs/onboarding.md) explains tokens, permissions, and setup problems.
- [Approve and check changes](docs/safety_model.md) explains what to check before and after a change.
- [All Figma guides](docs/README.md) links to the commands, API coverage, and test results.
