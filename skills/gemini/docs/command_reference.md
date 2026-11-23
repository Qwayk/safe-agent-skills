# Gemini commands

See [first-time setup](onboarding.md) for installation, or [list models and count tokens](quickstart.md) for a first run.

## Setup and run history

- `gemini-api-tool --output json --version`
- `gemini-api-tool --output json auth check`
- `gemini-api-tool onboarding [--no-write-env]`
- `gemini-api-tool runs list [--limit 20]`
- `gemini-api-tool runs show --run-id <run-id>`

## Gemini Commands

Commands with a body take a JSON file or string after `--request-json`. Use `--query-json` for optional query parameters where listed. Run any command with `--help` to see which flags are required.

### `batches`

- `gemini-api-tool batches cancel --name` — `generativelanguage.batches.cancel`, versions `v1beta, v1`, review a plan first, `--ack-irreversible` on apply.
- `gemini-api-tool batches delete --name` — `generativelanguage.batches.delete`, versions `v1beta, v1`, review a plan first, `--ack-irreversible` on apply.
- `gemini-api-tool batches get --name` — `generativelanguage.batches.get`, versions `v1beta, v1`, runs directly.
- `gemini-api-tool batches list --name --query-json` — `generativelanguage.batches.list`, versions `v1beta, v1`, runs directly.
- `gemini-api-tool batches update-embed-content-batch --name --request-json --query-json` — `generativelanguage.batches.updateEmbedContentBatch`, versions `v1beta, v1`, review a plan first.
- `gemini-api-tool batches update-generate-content-batch --name --request-json --query-json` — `generativelanguage.batches.updateGenerateContentBatch`, versions `v1beta, v1`, review a plan first.

### `cached-contents`

- `gemini-api-tool cached-contents create --request-json` — `generativelanguage.cachedContents.create`, versions `v1beta`, review a plan first, `--ack-spend-money` on apply.
- `gemini-api-tool cached-contents delete --name` — `generativelanguage.cachedContents.delete`, versions `v1beta`, review a plan first, `--ack-irreversible` on apply.
- `gemini-api-tool cached-contents get --name` — `generativelanguage.cachedContents.get`, versions `v1beta`, runs directly.
- `gemini-api-tool cached-contents list --query-json` — `generativelanguage.cachedContents.list`, versions `v1beta`, runs directly.
- `gemini-api-tool cached-contents patch --name --request-json --query-json` — `generativelanguage.cachedContents.patch`, versions `v1beta`, review a plan first, `--ack-spend-money` on apply.

### `corpora`

- `gemini-api-tool corpora create --request-json` — `generativelanguage.corpora.create`, versions `v1beta`, review a plan first.
- `gemini-api-tool corpora delete --name --query-json` — `generativelanguage.corpora.delete`, versions `v1beta`, review a plan first, `--ack-irreversible` on apply.
- `gemini-api-tool corpora get --name` — `generativelanguage.corpora.get`, versions `v1beta`, runs directly.
- `gemini-api-tool corpora list --query-json` — `generativelanguage.corpora.list`, versions `v1beta`, runs directly.

### `corpora-operations`

- `gemini-api-tool corpora-operations get --name` — `generativelanguage.corpora.operations.get`, versions `v1beta, v1`, runs directly.

### `corpora-permissions`

- `gemini-api-tool corpora-permissions create --parent --request-json` — `generativelanguage.corpora.permissions.create`, versions `v1beta`, review a plan first.
- `gemini-api-tool corpora-permissions delete --name` — `generativelanguage.corpora.permissions.delete`, versions `v1beta`, review a plan first, `--ack-irreversible` on apply.
- `gemini-api-tool corpora-permissions get --name` — `generativelanguage.corpora.permissions.get`, versions `v1beta`, runs directly.
- `gemini-api-tool corpora-permissions list --parent --query-json` — `generativelanguage.corpora.permissions.list`, versions `v1beta`, runs directly.
- `gemini-api-tool corpora-permissions patch --name --request-json --query-json` — `generativelanguage.corpora.permissions.patch`, versions `v1beta`, review a plan first.

### `dynamic`

- `gemini-api-tool dynamic generate-content --model --request-json` — `generativelanguage.dynamic.generateContent`, versions `v1beta, v1`, runs directly, `--ack-spend-money`.
- `gemini-api-tool dynamic stream-generate-content --model --request-json` — `generativelanguage.dynamic.streamGenerateContent`, versions `v1beta, v1`, runs directly, `--ack-spend-money`.

### `file-search-stores`

- `gemini-api-tool file-search-stores create --request-json` — `generativelanguage.fileSearchStores.create`, versions `v1beta`, review a plan first.
- `gemini-api-tool file-search-stores delete --name --query-json` — `generativelanguage.fileSearchStores.delete`, versions `v1beta`, review a plan first, `--ack-irreversible` on apply.
- `gemini-api-tool file-search-stores get --name` — `generativelanguage.fileSearchStores.get`, versions `v1beta`, runs directly.
- `gemini-api-tool file-search-stores import-file --file-search-store-name --request-json` — `generativelanguage.fileSearchStores.importFile`, versions `v1beta`, review a plan first, `--ack-spend-money` on apply.
- `gemini-api-tool file-search-stores list --query-json` — `generativelanguage.fileSearchStores.list`, versions `v1beta`, runs directly.

### `file-search-stores-documents`

- `gemini-api-tool file-search-stores-documents delete --name --query-json` — `generativelanguage.fileSearchStores.documents.delete`, versions `v1beta`, review a plan first, `--ack-irreversible` on apply.
- `gemini-api-tool file-search-stores-documents get --name` — `generativelanguage.fileSearchStores.documents.get`, versions `v1beta`, runs directly.
- `gemini-api-tool file-search-stores-documents list --parent --query-json` — `generativelanguage.fileSearchStores.documents.list`, versions `v1beta`, runs directly.

### `file-search-stores-operations`

- `gemini-api-tool file-search-stores-operations get --name` — `generativelanguage.fileSearchStores.operations.get`, versions `v1beta, v1`, runs directly.

### `file-search-stores-upload-operations`

- `gemini-api-tool file-search-stores-upload-operations get --name` — `generativelanguage.fileSearchStores.upload.operations.get`, versions `v1beta, v1`, runs directly.

### `files`

- `gemini-api-tool files delete --name` — `generativelanguage.files.delete`, versions `v1beta`, review a plan first, `--ack-irreversible` on apply.
- `gemini-api-tool files get --name` — `generativelanguage.files.get`, versions `v1beta`, runs directly.
- `gemini-api-tool files list --query-json` — `generativelanguage.files.list`, versions `v1beta`, runs directly.
- `gemini-api-tool files register --request-json` — `generativelanguage.files.register`, versions `v1beta`, review a plan first.

### `generated-files`

- `gemini-api-tool generated-files list --query-json` — `generativelanguage.generatedFiles.list`, versions `v1beta`, runs directly.

### `generated-files-operations`

- `gemini-api-tool generated-files-operations get --name` — `generativelanguage.generatedFiles.operations.get`, versions `v1beta, v1`, runs directly.

### `media`

- `gemini-api-tool media upload --request-json --media-file` — `generativelanguage.media.upload`, versions `v1beta`, review a plan first.
- `gemini-api-tool media upload-to-file-search-store --file-search-store-name --request-json --media-file` — `generativelanguage.media.uploadToFileSearchStore`, versions `v1beta`, review a plan first, `--ack-spend-money` on apply.

### `models`

- `gemini-api-tool models async-batch-embed-content --model --request-json` — `generativelanguage.models.asyncBatchEmbedContent`, versions `v1beta, v1`, review a plan first, `--ack-spend-money` on apply.
- `gemini-api-tool models batch-embed-contents --model --request-json` — `generativelanguage.models.batchEmbedContents`, versions `v1beta, v1`, runs directly, `--ack-spend-money`.
- `gemini-api-tool models batch-embed-text --model --request-json` — `generativelanguage.models.batchEmbedText`, versions `v1beta`, runs directly, `--ack-spend-money`.
- `gemini-api-tool models batch-generate-content --model --request-json` — `generativelanguage.models.batchGenerateContent`, versions `v1beta, v1`, review a plan first, `--ack-spend-money` on apply.
- `gemini-api-tool models count-message-tokens --model --request-json` — `generativelanguage.models.countMessageTokens`, versions `v1beta`, runs directly.
- `gemini-api-tool models count-text-tokens --model --request-json` — `generativelanguage.models.countTextTokens`, versions `v1beta`, runs directly.
- `gemini-api-tool models count-tokens --model --request-json` — `generativelanguage.models.countTokens`, versions `v1beta, v1`, runs directly.
- `gemini-api-tool models embed-content --model --request-json` — `generativelanguage.models.embedContent`, versions `v1beta, v1`, runs directly, `--ack-spend-money`.
- `gemini-api-tool models embed-text --model --request-json` — `generativelanguage.models.embedText`, versions `v1beta`, runs directly, `--ack-spend-money`.
- `gemini-api-tool models generate-answer --model --request-json` — `generativelanguage.models.generateAnswer`, versions `v1beta`, runs directly, `--ack-spend-money`.
- `gemini-api-tool models generate-content --model --request-json` — `generativelanguage.models.generateContent`, versions `v1beta, v1`, runs directly, `--ack-spend-money`.
- `gemini-api-tool models generate-message --model --request-json` — `generativelanguage.models.generateMessage`, versions `v1beta`, runs directly, `--ack-spend-money`.
- `gemini-api-tool models generate-text --model --request-json` — `generativelanguage.models.generateText`, versions `v1beta`, runs directly, `--ack-spend-money`.
- `gemini-api-tool models get --name` — `generativelanguage.models.get`, versions `v1beta, v1`, runs directly.
- `gemini-api-tool models list --query-json` — `generativelanguage.models.list`, versions `v1beta, v1`, runs directly.
- `gemini-api-tool models predict --model --request-json` — `generativelanguage.models.predict`, versions `v1beta`, runs directly, `--ack-spend-money`.
- `gemini-api-tool models predict-long-running --model --request-json` — `generativelanguage.models.predictLongRunning`, versions `v1beta`, runs directly, `--ack-spend-money`.
- `gemini-api-tool models stream-generate-content --model --request-json` — `generativelanguage.models.streamGenerateContent`, versions `v1beta, v1`, runs directly, `--ack-spend-money`.

### `models-operations`

- `gemini-api-tool models-operations get --name` — `generativelanguage.models.operations.get`, versions `v1beta, v1`, runs directly.
- `gemini-api-tool models-operations list --name --query-json` — `generativelanguage.models.operations.list`, versions `v1beta, v1`, runs directly.

### `operations`

- `gemini-api-tool operations delete --name` — `generativelanguage.operations.delete`, versions `v1`, review a plan first, `--ack-irreversible` on apply.
- `gemini-api-tool operations list --name --query-json` — `generativelanguage.operations.list`, versions `v1`, runs directly.

### `tuned-models`

- `gemini-api-tool tuned-models async-batch-embed-content --model --request-json` — `generativelanguage.tunedModels.asyncBatchEmbedContent`, versions `v1beta, v1`, review a plan first, `--ack-spend-money` on apply.
- `gemini-api-tool tuned-models batch-generate-content --model --request-json` — `generativelanguage.tunedModels.batchGenerateContent`, versions `v1beta, v1`, review a plan first, `--ack-spend-money` on apply.
- `gemini-api-tool tuned-models create --request-json --query-json` — `generativelanguage.tunedModels.create`, versions `v1beta`, review a plan first, `--ack-spend-money` on apply.
- `gemini-api-tool tuned-models delete --name` — `generativelanguage.tunedModels.delete`, versions `v1beta`, review a plan first, `--ack-irreversible` on apply.
- `gemini-api-tool tuned-models generate-content --model --request-json` — `generativelanguage.tunedModels.generateContent`, versions `v1beta, v1`, runs directly, `--ack-spend-money`.
- `gemini-api-tool tuned-models generate-text --model --request-json` — `generativelanguage.tunedModels.generateText`, versions `v1beta`, runs directly, `--ack-spend-money`.
- `gemini-api-tool tuned-models get --name` — `generativelanguage.tunedModels.get`, versions `v1beta`, runs directly.
- `gemini-api-tool tuned-models list --query-json` — `generativelanguage.tunedModels.list`, versions `v1beta`, runs directly.
- `gemini-api-tool tuned-models patch --name --request-json --query-json` — `generativelanguage.tunedModels.patch`, versions `v1beta`, review a plan first.
- `gemini-api-tool tuned-models stream-generate-content --model --request-json` — `generativelanguage.tunedModels.streamGenerateContent`, versions `v1beta, v1`, runs directly, `--ack-spend-money`.
- `gemini-api-tool tuned-models transfer-ownership --name --request-json` — `generativelanguage.tunedModels.transferOwnership`, versions `v1beta`, review a plan first, `--ack-irreversible` on apply.

### `tuned-models-operations`

- `gemini-api-tool tuned-models-operations cancel --name --request-json` — `generativelanguage.tunedModels.operations.cancel`, versions `v1`, review a plan first, `--ack-irreversible` on apply.
- `gemini-api-tool tuned-models-operations get --name` — `generativelanguage.tunedModels.operations.get`, versions `v1beta, v1`, runs directly.
- `gemini-api-tool tuned-models-operations list --name --query-json` — `generativelanguage.tunedModels.operations.list`, versions `v1beta, v1`, runs directly.

### `tuned-models-permissions`

- `gemini-api-tool tuned-models-permissions create --parent --request-json` — `generativelanguage.tunedModels.permissions.create`, versions `v1beta`, review a plan first.
- `gemini-api-tool tuned-models-permissions delete --name` — `generativelanguage.tunedModels.permissions.delete`, versions `v1beta`, review a plan first, `--ack-irreversible` on apply.
- `gemini-api-tool tuned-models-permissions get --name` — `generativelanguage.tunedModels.permissions.get`, versions `v1beta`, runs directly.
- `gemini-api-tool tuned-models-permissions list --parent --query-json` — `generativelanguage.tunedModels.permissions.list`, versions `v1beta`, runs directly.
- `gemini-api-tool tuned-models-permissions patch --name --request-json --query-json` — `generativelanguage.tunedModels.permissions.patch`, versions `v1beta`, review a plan first.

## Review and send a change

This example uses a sample cache name. A dry run saves the plan. After approval, use the same target and API key:

```bash
gemini-api-tool --plan-out plan.json cached-contents delete --name cachedContents/example
gemini-api-tool --apply --yes --plan-in plan.json --receipt-out receipt.json cached-contents delete --name cachedContents/example --ack-no-snapshot --ack-irreversible
```

See [approvals and receipts](safety_model.md) for the flags to use, what to review and how to check the result.

## Work with Gemini batches

Use `models batch-generate-content` or `models async-batch-embed-content` to plan a new job. The corresponding `tuned-models` commands use the same approval steps. After sending an approved plan, check the batch with `batches list --name batches` or `batches get --name batches/<id>`. Cancel, delete and update commands need a plan. `jobs run` is a local CSV example for trying out plans and receipts.
