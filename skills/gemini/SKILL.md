---
name: gemini
description: Use Gemini API through safe named commands for models, generation, embeddings, token counting, files, cached content, batches, file search stores, corpora, tuned models, permissions, and operations.
---

# Gemini API

Use this skill when a user wants an agent to work with the official Gemini API from Google AI for Developers.

Start with reads unless the user clearly asks for a change:

```bash
gemini-api-tool --output json auth check
gemini-api-tool --output json models list
```

Use explicit commands only. Do not invent raw REST calls, use a generic HTTP bridge, or mix this with the Qwayk GCP tool. This skill is for `generativelanguage.googleapis.com`, not Google Cloud control-plane APIs.

Good tasks:

- list models and recommend one for a prompt, embedding, or document-review job
- count tokens before sending a long prompt
- generate content or embeddings from a reviewed request body
- list files, generated files, cached contents, file search stores, documents, corpora, batches, tuned models, and operations
- prepare a dry-run plan for uploads, deletes, cached content changes, file-search imports, permission changes, tuned model changes, batch updates, or cancellations

Safety rules:

- Never ask the user to paste `GEMINI_API_KEY` into chat.
- Reads and compute calls may run directly.
- State-changing commands must dry-run first and be applied only from a reviewed `--plan-in`.
- Live applies need `--apply --yes`.
- No-snapshot writes need `--ack-no-snapshot`.
- Destructive or irreversible applies need `--ack-irreversible`.
- Save or review receipts for live applies.

Useful first ask:

List available Gemini models and recommend one for long document review with structured JSON output.
