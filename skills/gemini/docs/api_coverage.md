# API coverage

This ledger is ordered `v1beta` first, then `v1`.
All command names below are implemented explicit wrapper commands, not a raw HTTP bridge.

## Summary

- Provider: Gemini API
- API base URL: `https://generativelanguage.googleapis.com/`
- Auth method: API key
- Last audited (UTC): 2026-06-28
- Discovery counts: `v1beta` = 79 operations; `v1` = 32 operations

## Version notes

- `v1beta` is the broader surface. It includes cached content, files, media upload, file search stores, corpora, permissions, and legacy model methods like `generateText`, `generateMessage`, `generateAnswer`, `predict`, and `countMessageTokens`.
- `v1` keeps the smaller compatibility surface. It keeps core generation, embedding, batch jobs, operation polling, and the Interactions-style `dynamic` methods, but drops the legacy text/message/admin methods.

## `v1beta` coverage

### batches
- Operation ids: `generativelanguage.batches.cancel`, `generativelanguage.batches.delete`, `generativelanguage.batches.get`, `generativelanguage.batches.list`, `generativelanguage.batches.updateEmbedContentBatch`, `generativelanguage.batches.updateGenerateContentBatch`
- Implemented commands: `gemini-api-tool batches cancel`, `gemini-api-tool batches delete`, `gemini-api-tool batches get`, `gemini-api-tool batches list`, `gemini-api-tool batches update-embed-content-batch`, `gemini-api-tool batches update-generate-content-batch`
- Note: shared with `v1`.

### cached-contents
- Operation ids: `generativelanguage.cachedContents.create`, `generativelanguage.cachedContents.delete`, `generativelanguage.cachedContents.get`, `generativelanguage.cachedContents.list`, `generativelanguage.cachedContents.patch`
- Implemented commands: `gemini-api-tool cached-contents create`, `gemini-api-tool cached-contents delete`, `gemini-api-tool cached-contents get`, `gemini-api-tool cached-contents list`, `gemini-api-tool cached-contents patch`
- Note: `v1beta` only.

### corpora
- Operation ids: `generativelanguage.corpora.create`, `generativelanguage.corpora.delete`, `generativelanguage.corpora.get`, `generativelanguage.corpora.list`
- Implemented commands: `gemini-api-tool corpora create`, `gemini-api-tool corpora delete`, `gemini-api-tool corpora get`, `gemini-api-tool corpora list`
- Note: `v1beta` only.

### corpora-operations
- Operation ids: `generativelanguage.corpora.operations.get`
- Implemented commands: `gemini-api-tool corpora-operations get`
- Note: shared with `v1`.

### corpora-permissions
- Operation ids: `generativelanguage.corpora.permissions.create`, `generativelanguage.corpora.permissions.delete`, `generativelanguage.corpora.permissions.get`, `generativelanguage.corpora.permissions.list`, `generativelanguage.corpora.permissions.patch`
- Implemented commands: `gemini-api-tool corpora-permissions create`, `gemini-api-tool corpora-permissions delete`, `gemini-api-tool corpora-permissions get`, `gemini-api-tool corpora-permissions list`, `gemini-api-tool corpora-permissions patch`
- Note: `v1beta` only.

### dynamic
- Operation ids: `generativelanguage.dynamic.generateContent`, `generativelanguage.dynamic.streamGenerateContent`
- Implemented commands: `gemini-api-tool dynamic generate-content`, `gemini-api-tool dynamic stream-generate-content`
- Note: shared with `v1`.

### file-search-stores
- Operation ids: `generativelanguage.fileSearchStores.create`, `generativelanguage.fileSearchStores.delete`, `generativelanguage.fileSearchStores.get`, `generativelanguage.fileSearchStores.importFile`, `generativelanguage.fileSearchStores.list`
- Implemented commands: `gemini-api-tool file-search-stores create`, `gemini-api-tool file-search-stores delete`, `gemini-api-tool file-search-stores get`, `gemini-api-tool file-search-stores import-file`, `gemini-api-tool file-search-stores list`
- Note: `v1beta` only.

### file-search-stores-documents
- Operation ids: `generativelanguage.fileSearchStores.documents.delete`, `generativelanguage.fileSearchStores.documents.get`, `generativelanguage.fileSearchStores.documents.list`
- Implemented commands: `gemini-api-tool file-search-stores-documents delete`, `gemini-api-tool file-search-stores-documents get`, `gemini-api-tool file-search-stores-documents list`
- Note: `v1beta` only.

### file-search-stores-operations
- Operation ids: `generativelanguage.fileSearchStores.operations.get`
- Implemented commands: `gemini-api-tool file-search-stores-operations get`
- Note: shared with `v1`.

### file-search-stores-upload-operations
- Operation ids: `generativelanguage.fileSearchStores.upload.operations.get`
- Implemented commands: `gemini-api-tool file-search-stores-upload-operations get`
- Note: shared with `v1`.

### files
- Operation ids: `generativelanguage.files.delete`, `generativelanguage.files.get`, `generativelanguage.files.list`, `generativelanguage.files.register`
- Implemented commands: `gemini-api-tool files delete`, `gemini-api-tool files get`, `gemini-api-tool files list`, `gemini-api-tool files register`
- Note: `v1beta` only.

### generated-files
- Operation ids: `generativelanguage.generatedFiles.list`
- Implemented commands: `gemini-api-tool generated-files list`
- Note: `v1beta` only.

### generated-files-operations
- Operation ids: `generativelanguage.generatedFiles.operations.get`
- Implemented commands: `gemini-api-tool generated-files-operations get`
- Note: shared with `v1`.

### media
- Operation ids: `generativelanguage.media.upload`, `generativelanguage.media.uploadToFileSearchStore`
- Implemented commands: `gemini-api-tool media upload`, `gemini-api-tool media upload-to-file-search-store`
- Note: `v1beta` only.

### models
- Operation ids: `generativelanguage.models.asyncBatchEmbedContent`, `generativelanguage.models.batchEmbedContents`, `generativelanguage.models.batchEmbedText`, `generativelanguage.models.batchGenerateContent`, `generativelanguage.models.countMessageTokens`, `generativelanguage.models.countTextTokens`, `generativelanguage.models.countTokens`, `generativelanguage.models.embedContent`, `generativelanguage.models.embedText`, `generativelanguage.models.generateAnswer`, `generativelanguage.models.generateContent`, `generativelanguage.models.generateMessage`, `generativelanguage.models.generateText`, `generativelanguage.models.get`, `generativelanguage.models.list`, `generativelanguage.models.predict`, `generativelanguage.models.predictLongRunning`, `generativelanguage.models.streamGenerateContent`
- Implemented commands: `gemini-api-tool models async-batch-embed-content`, `gemini-api-tool models batch-embed-contents`, `gemini-api-tool models batch-embed-text`, `gemini-api-tool models batch-generate-content`, `gemini-api-tool models count-message-tokens`, `gemini-api-tool models count-text-tokens`, `gemini-api-tool models count-tokens`, `gemini-api-tool models embed-content`, `gemini-api-tool models embed-text`, `gemini-api-tool models generate-answer`, `gemini-api-tool models generate-content`, `gemini-api-tool models generate-message`, `gemini-api-tool models generate-text`, `gemini-api-tool models get`, `gemini-api-tool models list`, `gemini-api-tool models predict`, `gemini-api-tool models predict-long-running`, `gemini-api-tool models stream-generate-content`
- Note: shared with `v1`, but `v1` is smaller and drops the legacy text/message/predict methods.

### models-operations
- Operation ids: `generativelanguage.models.operations.get`, `generativelanguage.models.operations.list`
- Implemented commands: `gemini-api-tool models-operations get`, `gemini-api-tool models-operations list`
- Note: shared with `v1`.

### tuned-models
- Operation ids: `generativelanguage.tunedModels.asyncBatchEmbedContent`, `generativelanguage.tunedModels.batchGenerateContent`, `generativelanguage.tunedModels.create`, `generativelanguage.tunedModels.delete`, `generativelanguage.tunedModels.generateContent`, `generativelanguage.tunedModels.generateText`, `generativelanguage.tunedModels.get`, `generativelanguage.tunedModels.list`, `generativelanguage.tunedModels.patch`, `generativelanguage.tunedModels.streamGenerateContent`, `generativelanguage.tunedModels.transferOwnership`
- Implemented commands: `gemini-api-tool tuned-models async-batch-embed-content`, `gemini-api-tool tuned-models batch-generate-content`, `gemini-api-tool tuned-models create`, `gemini-api-tool tuned-models delete`, `gemini-api-tool tuned-models generate-content`, `gemini-api-tool tuned-models generate-text`, `gemini-api-tool tuned-models get`, `gemini-api-tool tuned-models list`, `gemini-api-tool tuned-models patch`, `gemini-api-tool tuned-models stream-generate-content`, `gemini-api-tool tuned-models transfer-ownership`
- Note: shared with `v1`, but `v1` is smaller and keeps only the content-generation subset.

### tuned-models-operations
- Operation ids: `generativelanguage.tunedModels.operations.get`, `generativelanguage.tunedModels.operations.list`
- Implemented commands: `gemini-api-tool tuned-models-operations get`, `gemini-api-tool tuned-models-operations list`
- Note: shared with `v1`; `v1` adds `cancel`.

### tuned-models-permissions
- Operation ids: `generativelanguage.tunedModels.permissions.create`, `generativelanguage.tunedModels.permissions.delete`, `generativelanguage.tunedModels.permissions.get`, `generativelanguage.tunedModels.permissions.list`, `generativelanguage.tunedModels.permissions.patch`
- Implemented commands: `gemini-api-tool tuned-models-permissions create`, `gemini-api-tool tuned-models-permissions delete`, `gemini-api-tool tuned-models-permissions get`, `gemini-api-tool tuned-models-permissions list`, `gemini-api-tool tuned-models-permissions patch`
- Note: `v1beta` only.

Total: 79 operations across 19 command families.

## `v1` coverage

### batches
- Operation ids: `generativelanguage.batches.cancel`, `generativelanguage.batches.delete`, `generativelanguage.batches.get`, `generativelanguage.batches.list`, `generativelanguage.batches.updateEmbedContentBatch`, `generativelanguage.batches.updateGenerateContentBatch`
- Implemented commands: `gemini-api-tool batches cancel`, `gemini-api-tool batches delete`, `gemini-api-tool batches get`, `gemini-api-tool batches list`, `gemini-api-tool batches update-embed-content-batch`, `gemini-api-tool batches update-generate-content-batch`
- Note: shared with `v1beta`.

### corpora-operations
- Operation ids: `generativelanguage.corpora.operations.get`
- Implemented commands: `gemini-api-tool corpora-operations get`
- Note: shared with `v1beta`.

### dynamic
- Operation ids: `generativelanguage.dynamic.generateContent`, `generativelanguage.dynamic.streamGenerateContent`
- Implemented commands: `gemini-api-tool dynamic generate-content`, `gemini-api-tool dynamic stream-generate-content`
- Note: shared with `v1beta`.

### file-search-stores-operations
- Operation ids: `generativelanguage.fileSearchStores.operations.get`
- Implemented commands: `gemini-api-tool file-search-stores-operations get`
- Note: shared with `v1beta`.

### file-search-stores-upload-operations
- Operation ids: `generativelanguage.fileSearchStores.upload.operations.get`
- Implemented commands: `gemini-api-tool file-search-stores-upload-operations get`
- Note: shared with `v1beta`.

### generated-files-operations
- Operation ids: `generativelanguage.generatedFiles.operations.get`
- Implemented commands: `gemini-api-tool generated-files-operations get`
- Note: shared with `v1beta`.

### models
- Operation ids: `generativelanguage.models.asyncBatchEmbedContent`, `generativelanguage.models.batchEmbedContents`, `generativelanguage.models.batchGenerateContent`, `generativelanguage.models.countTokens`, `generativelanguage.models.embedContent`, `generativelanguage.models.generateContent`, `generativelanguage.models.get`, `generativelanguage.models.list`, `generativelanguage.models.streamGenerateContent`
- Implemented commands: `gemini-api-tool models async-batch-embed-content`, `gemini-api-tool models batch-embed-contents`, `gemini-api-tool models batch-generate-content`, `gemini-api-tool models count-tokens`, `gemini-api-tool models embed-content`, `gemini-api-tool models generate-content`, `gemini-api-tool models get`, `gemini-api-tool models list`, `gemini-api-tool models stream-generate-content`
- Note: shared with `v1beta`, but smaller here and limited to the current compatibility set.

### models-operations
- Operation ids: `generativelanguage.models.operations.get`, `generativelanguage.models.operations.list`
- Implemented commands: `gemini-api-tool models-operations get`, `gemini-api-tool models-operations list`
- Note: shared with `v1beta`.

### operations
- Operation ids: `generativelanguage.operations.delete`, `generativelanguage.operations.list`
- Implemented commands: `gemini-api-tool operations delete`, `gemini-api-tool operations list`
- Note: `v1` only.

### tuned-models
- Operation ids: `generativelanguage.tunedModels.asyncBatchEmbedContent`, `generativelanguage.tunedModels.batchGenerateContent`, `generativelanguage.tunedModels.generateContent`, `generativelanguage.tunedModels.streamGenerateContent`
- Implemented commands: `gemini-api-tool tuned-models async-batch-embed-content`, `gemini-api-tool tuned-models batch-generate-content`, `gemini-api-tool tuned-models generate-content`, `gemini-api-tool tuned-models stream-generate-content`
- Note: shared with `v1beta`, but smaller here and limited to the content-generation subset.

### tuned-models-operations
- Operation ids: `generativelanguage.tunedModels.operations.cancel`, `generativelanguage.tunedModels.operations.get`, `generativelanguage.tunedModels.operations.list`
- Implemented commands: `gemini-api-tool tuned-models-operations cancel`, `gemini-api-tool tuned-models-operations get`, `gemini-api-tool tuned-models-operations list`
- Note: shared with `v1beta`; `v1` adds `cancel`.

Total: 32 operations across 11 command families.
