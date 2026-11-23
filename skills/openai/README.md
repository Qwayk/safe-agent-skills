# OpenAI Platform

Use this tool to see which models and files your OpenAI API key can access, or to check projects and usage when the key allows it. It can also prepare a file upload, response, batch, or other change for your approval.

## Get started

Install the skill for your agent.

```bash
npx skills add Qwayk/safe-agent-skills@openai -g -y
```

The command-line tool needs Python 3.12 or newer. From the downloaded tool folder, run `python -m pip install .` in your Python environment. Then set up your key in a [private settings file](docs/onboarding.md).

```bash
openai-api-tool onboarding
openai-api-tool auth check
openai-api-tool api ops list
openai-api-tool --live api listModels
```

The first three commands stay on your machine. Use the last command when you want to see which models are available to your key. Try asking “Check which OpenAI models this project can use.”

## Review a change

Ask the agent to save a plan before it uploads data, starts a batch, deletes a file, or makes a request that can cost money. Review the project, exact request, and any cost or recovery limits. Then follow the [approval steps](docs/safety_model.md).

The command list comes from a dated [OpenAI API inventory](docs/api_coverage.md). The old Assistants API commands stop locally and point to Responses and Conversations. See [all guides](docs/README.md) or [what we tested](docs/proof.md).
