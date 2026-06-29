# Command Reference

This is the technical command list for the Gemini API safe CLI. If you are choosing what to ask first, start with `docs/use_cases.md` or `docs/quickstart.md`.

## Setup And Proof

- `gemini-api-tool --output json --version`
- `gemini-api-tool --output json auth check`
- `gemini-api-tool onboarding [--no-write-env]`
- `gemini-api-tool runs list [--limit 20]`
- `gemini-api-tool runs show --run-id <run-id>`

## Gemini Commands

Each command below is generated from the pinned official discovery inventory. Commands that need a request body use `--request-json` with either a JSON string or a JSON file path. Commands with optional query parameters use `--query-json`.

### `batches`

- `gemini-api-tool batches cancel --name --ack-no-snapshot (apply only)` - `generativelanguage.batches.cancel`; versions `v1beta, v1`; plan-first write.
- `gemini-api-tool batches delete --name --ack-no-snapshot (apply only)` - `generativelanguage.batches.delete`; versions `v1beta, v1`; plan-first write.
- `gemini-api-tool batches get --name` - `generativelanguage.batches.get`; versions `v1beta, v1`; direct read/compute.
- `gemini-api-tool batches list --name --query-json` - `generativelanguage.batches.list`; versions `v1beta, v1`; direct read/compute.
- `gemini-api-tool batches update-embed-content-batch --name --request-json --query-json --ack-no-snapshot (apply only)` - `generativelanguage.batches.updateEmbedContentBatch`; versions `v1beta, v1`; plan-first write.
- `gemini-api-tool batches update-generate-content-batch --name --request-json --query-json --ack-no-snapshot (apply only)` - `generativelanguage.batches.updateGenerateContentBatch`; versions `v1beta, v1`; plan-first write.

### `cached-contents`

- `gemini-api-tool cached-contents create --request-json --ack-no-snapshot (apply only)` - `generativelanguage.cachedContents.create`; versions `v1beta`; plan-first write.
- `gemini-api-tool cached-contents delete --name --ack-no-snapshot (apply only)` - `generativelanguage.cachedContents.delete`; versions `v1beta`; plan-first write.
- `gemini-api-tool cached-contents get --name` - `generativelanguage.cachedContents.get`; versions `v1beta`; direct read/compute.
- `gemini-api-tool cached-contents list --query-json` - `generativelanguage.cachedContents.list`; versions `v1beta`; direct read/compute.
- `gemini-api-tool cached-contents patch --name --request-json --query-json --ack-no-snapshot (apply only)` - `generativelanguage.cachedContents.patch`; versions `v1beta`; plan-first write.

### `corpora`

- `gemini-api-tool corpora create --request-json --ack-no-snapshot (apply only)` - `generativelanguage.corpora.create`; versions `v1beta`; plan-first write.
- `gemini-api-tool corpora delete --name --query-json --ack-no-snapshot (apply only)` - `generativelanguage.corpora.delete`; versions `v1beta`; plan-first write.
- `gemini-api-tool corpora get --name` - `generativelanguage.corpora.get`; versions `v1beta`; direct read/compute.
- `gemini-api-tool corpora list --query-json` - `generativelanguage.corpora.list`; versions `v1beta`; direct read/compute.

### `corpora-operations`

- `gemini-api-tool corpora-operations get --name` - `generativelanguage.corpora.operations.get`; versions `v1beta, v1`; direct read/compute.

### `corpora-permissions`

- `gemini-api-tool corpora-permissions create --parent --request-json --ack-no-snapshot (apply only)` - `generativelanguage.corpora.permissions.create`; versions `v1beta`; plan-first write.
- `gemini-api-tool corpora-permissions delete --name --ack-no-snapshot (apply only)` - `generativelanguage.corpora.permissions.delete`; versions `v1beta`; plan-first write.
- `gemini-api-tool corpora-permissions get --name` - `generativelanguage.corpora.permissions.get`; versions `v1beta`; direct read/compute.
- `gemini-api-tool corpora-permissions list --parent --query-json` - `generativelanguage.corpora.permissions.list`; versions `v1beta`; direct read/compute.
- `gemini-api-tool corpora-permissions patch --name --request-json --query-json --ack-no-snapshot (apply only)` - `generativelanguage.corpora.permissions.patch`; versions `v1beta`; plan-first write.

### `dynamic`

- `gemini-api-tool dynamic generate-content --model --request-json` - `generativelanguage.dynamic.generateContent`; versions `v1beta, v1`; direct read/compute.
- `gemini-api-tool dynamic stream-generate-content --model --request-json` - `generativelanguage.dynamic.streamGenerateContent`; versions `v1beta, v1`; direct read/compute.

### `file-search-stores`

- `gemini-api-tool file-search-stores create --request-json --ack-no-snapshot (apply only)` - `generativelanguage.fileSearchStores.create`; versions `v1beta`; plan-first write.
- `gemini-api-tool file-search-stores delete --name --query-json --ack-no-snapshot (apply only)` - `generativelanguage.fileSearchStores.delete`; versions `v1beta`; plan-first write.
- `gemini-api-tool file-search-stores get --name` - `generativelanguage.fileSearchStores.get`; versions `v1beta`; direct read/compute.
- `gemini-api-tool file-search-stores import-file --file-search-store-name --request-json --ack-no-snapshot (apply only)` - `generativelanguage.fileSearchStores.importFile`; versions `v1beta`; plan-first write.
- `gemini-api-tool file-search-stores list --query-json` - `generativelanguage.fileSearchStores.list`; versions `v1beta`; direct read/compute.

### `file-search-stores-documents`

- `gemini-api-tool file-search-stores-documents delete --name --query-json --ack-no-snapshot (apply only)` - `generativelanguage.fileSearchStores.documents.delete`; versions `v1beta`; plan-first write.
- `gemini-api-tool file-search-stores-documents get --name` - `generativelanguage.fileSearchStores.documents.get`; versions `v1beta`; direct read/compute.
- `gemini-api-tool file-search-stores-documents list --parent --query-json` - `generativelanguage.fileSearchStores.documents.list`; versions `v1beta`; direct read/compute.

### `file-search-stores-operations`

- `gemini-api-tool file-search-stores-operations get --name` - `generativelanguage.fileSearchStores.operations.get`; versions `v1beta, v1`; direct read/compute.

### `file-search-stores-upload-operations`

- `gemini-api-tool file-search-stores-upload-operations get --name` - `generativelanguage.fileSearchStores.upload.operations.get`; versions `v1beta, v1`; direct read/compute.

### `files`

- `gemini-api-tool files delete --name --ack-no-snapshot (apply only)` - `generativelanguage.files.delete`; versions `v1beta`; plan-first write.
- `gemini-api-tool files get --name` - `generativelanguage.files.get`; versions `v1beta`; direct read/compute.
- `gemini-api-tool files list --query-json` - `generativelanguage.files.list`; versions `v1beta`; direct read/compute.
- `gemini-api-tool files register --request-json --ack-no-snapshot (apply only)` - `generativelanguage.files.register`; versions `v1beta`; plan-first write.

### `generated-files`

- `gemini-api-tool generated-files list --query-json` - `generativelanguage.generatedFiles.list`; versions `v1beta`; direct read/compute.

### `generated-files-operations`

- `gemini-api-tool generated-files-operations get --name` - `generativelanguage.generatedFiles.operations.get`; versions `v1beta, v1`; direct read/compute.

### `media`

- `gemini-api-tool media upload --request-json --media-file --ack-no-snapshot (apply only)` - `generativelanguage.media.upload`; versions `v1beta`; plan-first write.
- `gemini-api-tool media upload-to-file-search-store --file-search-store-name --request-json --media-file --ack-no-snapshot (apply only)` - `generativelanguage.media.uploadToFileSearchStore`; versions `v1beta`; plan-first write.

### `models`

- `gemini-api-tool models async-batch-embed-content --model --request-json` - `generativelanguage.models.asyncBatchEmbedContent`; versions `v1beta, v1`; direct read/compute.
- `gemini-api-tool models batch-embed-contents --model --request-json` - `generativelanguage.models.batchEmbedContents`; versions `v1beta, v1`; direct read/compute.
- `gemini-api-tool models batch-embed-text --model --request-json` - `generativelanguage.models.batchEmbedText`; versions `v1beta`; direct read/compute.
- `gemini-api-tool models batch-generate-content --model --request-json` - `generativelanguage.models.batchGenerateContent`; versions `v1beta, v1`; direct read/compute.
- `gemini-api-tool models count-message-tokens --model --request-json` - `generativelanguage.models.countMessageTokens`; versions `v1beta`; direct read/compute.
- `gemini-api-tool models count-text-tokens --model --request-json` - `generativelanguage.models.countTextTokens`; versions `v1beta`; direct read/compute.
- `gemini-api-tool models count-tokens --model --request-json` - `generativelanguage.models.countTokens`; versions `v1beta, v1`; direct read/compute.
- `gemini-api-tool models embed-content --model --request-json` - `generativelanguage.models.embedContent`; versions `v1beta, v1`; direct read/compute.
- `gemini-api-tool models embed-text --model --request-json` - `generativelanguage.models.embedText`; versions `v1beta`; direct read/compute.
- `gemini-api-tool models generate-answer --model --request-json` - `generativelanguage.models.generateAnswer`; versions `v1beta`; direct read/compute.
- `gemini-api-tool models generate-content --model --request-json` - `generativelanguage.models.generateContent`; versions `v1beta, v1`; direct read/compute.
- `gemini-api-tool models generate-message --model --request-json` - `generativelanguage.models.generateMessage`; versions `v1beta`; direct read/compute.
- `gemini-api-tool models generate-text --model --request-json` - `generativelanguage.models.generateText`; versions `v1beta`; direct read/compute.
- `gemini-api-tool models get --name` - `generativelanguage.models.get`; versions `v1beta, v1`; direct read/compute.
- `gemini-api-tool models list --query-json` - `generativelanguage.models.list`; versions `v1beta, v1`; direct read/compute.
- `gemini-api-tool models predict --model --request-json` - `generativelanguage.models.predict`; versions `v1beta`; direct read/compute.
- `gemini-api-tool models predict-long-running --model --request-json` - `generativelanguage.models.predictLongRunning`; versions `v1beta`; direct read/compute.
- `gemini-api-tool models stream-generate-content --model --request-json` - `generativelanguage.models.streamGenerateContent`; versions `v1beta, v1`; direct read/compute.

### `models-operations`

- `gemini-api-tool models-operations get --name` - `generativelanguage.models.operations.get`; versions `v1beta, v1`; direct read/compute.
- `gemini-api-tool models-operations list --name --query-json` - `generativelanguage.models.operations.list`; versions `v1beta, v1`; direct read/compute.

### `operations`

- `gemini-api-tool operations delete --name --ack-no-snapshot (apply only)` - `generativelanguage.operations.delete`; versions `v1`; plan-first write.
- `gemini-api-tool operations list --name --query-json` - `generativelanguage.operations.list`; versions `v1`; direct read/compute.

### `tuned-models`

- `gemini-api-tool tuned-models async-batch-embed-content --model --request-json` - `generativelanguage.tunedModels.asyncBatchEmbedContent`; versions `v1beta, v1`; direct read/compute.
- `gemini-api-tool tuned-models batch-generate-content --model --request-json` - `generativelanguage.tunedModels.batchGenerateContent`; versions `v1beta, v1`; direct read/compute.
- `gemini-api-tool tuned-models create --request-json --query-json --ack-no-snapshot (apply only)` - `generativelanguage.tunedModels.create`; versions `v1beta`; plan-first write.
- `gemini-api-tool tuned-models delete --name --ack-no-snapshot (apply only)` - `generativelanguage.tunedModels.delete`; versions `v1beta`; plan-first write.
- `gemini-api-tool tuned-models generate-content --model --request-json` - `generativelanguage.tunedModels.generateContent`; versions `v1beta, v1`; direct read/compute.
- `gemini-api-tool tuned-models generate-text --model --request-json` - `generativelanguage.tunedModels.generateText`; versions `v1beta`; direct read/compute.
- `gemini-api-tool tuned-models get --name` - `generativelanguage.tunedModels.get`; versions `v1beta`; direct read/compute.
- `gemini-api-tool tuned-models list --query-json` - `generativelanguage.tunedModels.list`; versions `v1beta`; direct read/compute.
- `gemini-api-tool tuned-models patch --name --request-json --query-json --ack-no-snapshot (apply only)` - `generativelanguage.tunedModels.patch`; versions `v1beta`; plan-first write.
- `gemini-api-tool tuned-models stream-generate-content --model --request-json` - `generativelanguage.tunedModels.streamGenerateContent`; versions `v1beta, v1`; direct read/compute.
- `gemini-api-tool tuned-models transfer-ownership --name --request-json --ack-no-snapshot (apply only)` - `generativelanguage.tunedModels.transferOwnership`; versions `v1beta`; plan-first write.

### `tuned-models-operations`

- `gemini-api-tool tuned-models-operations cancel --name --request-json --ack-no-snapshot (apply only)` - `generativelanguage.tunedModels.operations.cancel`; versions `v1`; plan-first write.
- `gemini-api-tool tuned-models-operations get --name` - `generativelanguage.tunedModels.operations.get`; versions `v1beta, v1`; direct read/compute.
- `gemini-api-tool tuned-models-operations list --name --query-json` - `generativelanguage.tunedModels.operations.list`; versions `v1beta, v1`; direct read/compute.

### `tuned-models-permissions`

- `gemini-api-tool tuned-models-permissions create --parent --request-json --ack-no-snapshot (apply only)` - `generativelanguage.tunedModels.permissions.create`; versions `v1beta`; plan-first write.
- `gemini-api-tool tuned-models-permissions delete --name --ack-no-snapshot (apply only)` - `generativelanguage.tunedModels.permissions.delete`; versions `v1beta`; plan-first write.
- `gemini-api-tool tuned-models-permissions get --name` - `generativelanguage.tunedModels.permissions.get`; versions `v1beta`; direct read/compute.
- `gemini-api-tool tuned-models-permissions list --parent --query-json` - `generativelanguage.tunedModels.permissions.list`; versions `v1beta`; direct read/compute.
- `gemini-api-tool tuned-models-permissions patch --name --request-json --query-json --ack-no-snapshot (apply only)` - `generativelanguage.tunedModels.permissions.patch`; versions `v1beta`; plan-first write.

## Applying State Changes

State-changing commands create a plan by default. A live apply needs `--apply --yes --plan-in <plan.json>` and any command-specific acknowledgement flags.

Example:

```bash
gemini-api-tool --plan-out plan.json cached-contents delete --name cachedContents/example --ack-no-snapshot
gemini-api-tool --apply --yes --plan-in plan.json --receipt-out receipt.json cached-contents delete --name cachedContents/example --ack-no-snapshot --ack-irreversible
```
