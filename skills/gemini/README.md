# Gemini API

Ask your agent to find a Gemini model for a job, count the tokens in a long prompt, or run a request you’ve approved. It can also check files, cached content, and batch jobs in your Gemini account.

Start with “List the Gemini models I can use and suggest one for reviewing a long document.” The agent checks your local setup and asks Google which models your key can use.

When a request can cost money, the agent gets your approval before sending it. For changes such as uploading a file, starting a batch, or deleting a cache, it shows you a plan first.

## Get started

Install the `gemini` skill from Qwayk’s public catalog:

```bash
npx skills add Qwayk/safe-agent-skills@gemini -g -y
```

Then [set up the CLI and list models](docs/onboarding.md). You’ll need Python 3.12 or later, a Gemini API key from Google AI Studio, and the tool’s source folder. Keep your key in your local settings or shell.

## What you can ask for

- “Count the tokens in this prompt before I send it.”
- “Check whether our batch finished and show me its result.”
- “Show me which files are already in this file search store.”
- “Prepare a plan to upload this file. Show me the target and the file before you send it.”

See [more examples](docs/use_cases.md) or look up [the exact commands](docs/command_reference.md).

## Before you approve a change

Check the target, request and file with your agent. The tool uses the same API key and checks that the inputs still match the saved plan before it sends anything. After Gemini replies, check the receipt and confirm the result in Gemini where you can. If Gemini doesn’t reply, check whether the change happened before trying again. [How approvals and receipts work](docs/safety_model.md)

## What it covers

The tool ships 82 named commands from Google’s June 26, 2026 discovery files for `v1beta` and `v1`. It uses the Gemini Developer API at `generativelanguage.googleapis.com`. Vertex AI and Google Cloud administration use separate tools.

See [API coverage](docs/api_coverage.md) for the operation list and [test results](docs/proof.md) for what was checked with simulated Gemini replies.
