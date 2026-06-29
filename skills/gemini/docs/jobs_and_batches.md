# Jobs And Batches

Gemini has official batch operations, and this CLI exposes those as named `batches` commands from the discovery docs:

- `gemini-api-tool batches list --name batches`
- `gemini-api-tool batches get --name batches/<id>`
- `gemini-api-tool batches cancel --name batches/<id>`
- `gemini-api-tool batches delete --name batches/<id>`
- `gemini-api-tool batches update-generate-content-batch --name batches/<id> --request-json request.json`
- `gemini-api-tool batches update-embed-content-batch --name batches/<id> --request-json request.json`

Batch updates, cancels, and deletes are state-changing operations. Run them as a plan first, review the target, then apply only with the required approvals.

The older `jobs run` command remains as a local safety sample for CSV-driven plan and receipt behavior. It is not the way to call Gemini batch APIs. Use the named `batches` commands for real Gemini batch work.
