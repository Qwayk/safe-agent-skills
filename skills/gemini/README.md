# Gemini API

**Capability:** Reads, generation calls, uploads, and careful changes

Gemini is where an agent can compare models, count tokens before a long prompt, generate or embed content, manage files and cached context, check batch jobs, and review file-search stores without guessing which Google AI endpoint to call.

This skill gives the agent a named Gemini command surface instead of a free-form HTTP shortcut. It uses Google's official Generative Language discovery documents for `v1beta` and `v1`, keeps `v1beta` as the broadest default surface, and exposes each documented operation as a real command.

That matters because generic agents can mix `v1` and `v1beta`, invent request fields, or send a delete/upload/change directly. This tool keeps the agent inside explicit commands, sends reads directly, makes state-changing work produce a reviewed plan first, requires stronger approval for risky applies, redacts API keys, and saves receipts for live changes.

A useful first ask is: List available Gemini models and recommend one for long document review with structured JSON output.

## Start here first

- Want ideas for real work? [What this skill can help you do](docs/use_cases.md)
- Need setup? [Set up Gemini access](docs/onboarding.md)
- Want the safety story first? [See how this skill keeps changes safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- List Gemini models and pick the right one for a prompt, embedding, or document-review job.
- Count tokens before sending long prompts.
- Generate content or embeddings from reviewed request JSON.
- Upload and review files, generated files, cached contents, file search stores, documents, corpora, batches, tuned models, and operations.
- Prepare dry-run plans for uploads, deletes, cached content changes, file-search imports, permission changes, tuned model changes, batch updates, or cancellations.
- Keep local plans, receipts, and run history so Gemini API work can be checked later.

## Why this skill is different

Many Gemini examples are direct SDK or REST calls. That is useful for developers, but it gives an agent too much room to improvise when the user wants controlled API work.

This safe skill keeps the agent inside named commands generated from the official Gemini API boundary. It starts with reads when possible, shows plans before state-changing actions, asks for stronger approval on risky actions, redacts secrets from normal output, and leaves receipts so you can check what happened later.

It is for `generativelanguage.googleapis.com`, not Vertex AI and not the Google Cloud control plane. The Qwayk GCP skill covers Google Cloud APIs.

## What access this skill needs

- A Gemini API key from Google AI Studio.
- The normal Gemini API endpoint, which defaults to `https://generativelanguage.googleapis.com`.
- Local request JSON files when you ask the agent to generate content, embed content, upload files, or prepare more complex changes.

Never paste your Gemini API key into chat.

## Install and first run

Install slug: `gemini`

Ask your agent to install the `gemini` skill from `Qwayk/safe-agent-skills`.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@gemini -g -y
```

Then try:

```text
Connect this skill to my Gemini API key and list the available models. Do not apply any change.
```

## How this skill stays safe

- Reads and compute calls can run without a live write approval.
- State-changing operations start as dry-run plans.
- Live changes need a reviewed plan and `--apply --yes`.
- No-snapshot state changes need `--ack-no-snapshot`.
- Destructive or irreversible applies need `--ack-irreversible`.
- API keys and local tokens are redacted from normal output, plans, and receipts.

## What it covers today

- `v1beta`: 79 official operations.
- `v1`: 32 official operations.
- Merged command registry: 82 unique explicit commands.
- Discovery source: official Gemini Generative Language REST discovery revision `20260626` for both `v1beta` and `v1`.

See [API coverage](docs/api_coverage.md) for the full operation ledger.

## What happens before live changes

The agent creates a plan first. You review the exact operation, target, request body, media file path when relevant, warnings, and required approvals. Only then can the agent apply the change, and live applies can write a receipt.

The tool does not promise rollback for Gemini resources when the API does not provide a safe before-state snapshot.

## Limits

- Live Gemini behavior is source-ready but live-unverified until you connect a real `GEMINI_API_KEY`.
- File contents, prompts, cached content, and generated output can contain private data. Keep request files local and review them before sending.
- Streaming endpoints are exposed as official commands, but terminal output depends on the HTTP behavior returned by Gemini.

## Helpful docs

- [Set up Gemini access](docs/onboarding.md)
- [Run the first model check](docs/quickstart.md)
- [Command reference](docs/command_reference.md)
- [Safety model](docs/safety_model.md)
- [Use cases](docs/use_cases.md)
- [Proof and verification](docs/proof.md)
- [Official references](docs/references.md)
