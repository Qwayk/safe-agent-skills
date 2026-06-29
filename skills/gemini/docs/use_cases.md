# Use Cases

## Choose A Model Before Sending Work

Ask the agent to list Gemini models, compare the options, and recommend one for a task such as long document review, structured JSON, embeddings, or low-cost classification.

## Check Prompt Size

Ask the agent to count tokens before sending a long prompt. This helps avoid failed runs and makes model choice easier.

## Prepare Generation Or Embedding Requests

Ask for a small `generate-content`, `embed-content`, or batch request using the documented Gemini request body. The tool sends the named Gemini command instead of letting the agent invent an endpoint.

## Review Files And File Search

Ask the agent to list files, generated files, file-search stores, documents, and import operations before deciding what to upload, import, or delete.

## Plan State Changes

Ask for a dry-run plan before creating cached content, deleting files, updating batches, changing permissions, or touching tuned models. The plan makes the target and risk visible before any live apply.

## Not The Right Fit

Do not use this as a generic Google Cloud CLI, Vertex AI admin tool, hidden account scraper, or OpenAI-compatible bridge. It is only for the official Gemini API surface at `generativelanguage.googleapis.com`.
