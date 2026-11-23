# Run an OpenAI batch

A live batch sends a file of API requests to OpenAI for later processing. Prepare the file in the format OpenAI expects. Review the file and requested models before uploading it, then review the cost and the batch plan before starting the batch. [OpenAI Batch guide](https://developers.openai.com/api/docs/guides/batch)

Use `api createFile` with a multipart file and the purpose `batch` for the upload. Use the returned file ID in the request for `api createBatch`. Both actions use the normal [plan and approval commands](command_reference.md#review-and-send-a-request).

After the batch starts, check its status.

```bash
openai-api-tool --live api retrieveBatch --path batch_id=your_batch_id
```

Use the output file ID to find the results once the batch finishes. A reply that gives a batch ID confirms the request was received. The later status tells you whether the work finished.

For a local practice run, `openai-api-tool jobs run --file examples/jobs.csv` uses sample CSV actions. The CSV needs an `action` column with `read.ping` or `write.ping`. The demo actions stay on your machine.
