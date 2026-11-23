# OpenAI Platform commands

Put shared options such as `--env-file`, `--live`, and `--plan-in` before `api`, `auth`, or another command. Put the operation’s inputs after its name.

## Check setup and find a command

```bash
openai-api-tool --version
openai-api-tool onboarding
openai-api-tool --live auth check
openai-api-tool api ops list --tag Models
openai-api-tool --live api listModels
```

`onboarding --no-write-env` prints the steps without creating a file. Use `--output text` for text or `--output json` for JSON. `--timeout-s` changes the wait for this call. `--verbose` shows the HTTP method and status. [Settings help](onboarding.md)

## Review and send a request

Save this example as `request.json` with a model available to your project.

```json
{"model":"your-model","input":"Say hello"}
```

```bash
openai-api-tool --plan-out plan.json api createResponse --body-json request.json
openai-api-tool --live --apply --plan-in plan.json --yes \
  --ack-spend-money --ack-no-snapshot api createResponse --body-json request.json
```

Use the second command after the plan is approved. Flags depend on the action. See [what each approval covers](safety_model.md).

For a named resource, use `--path key=value` or `--path-json <file>`. For filters or pagination, use `--query key=value` or `--query-json <file>`. Use `--file field=path` for a multipart upload. Path, query, and file flags can be repeated. The JSON options accept inline JSON or a file.

## Run history

```bash
openai-api-tool runs list --limit 20
openai-api-tool runs show --run-id <run-id>
```

Run files go under `.state/runs/` next to the settings file. Use `--run-id` or `--artifacts-dir` to select a run or folder. `--no-artifacts` skips optional run files. A live write still saves its approval receipt. `--receipt-out` lets you save an extra copy and `--log-file` selects an extra audit log.

`demo` and `jobs run` show the local workflow with sample actions. For an actual OpenAI batch, use the [Batch API commands](jobs_and_batches.md).
