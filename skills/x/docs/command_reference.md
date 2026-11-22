# X commands

Start with [Quickstart](quickstart.md) to install and [Connect your X account](onboarding.md) to sign in. Put shared flags such as `--live` and `--env-file` before the command. Values like `POST_ID` are examples.

## Find a command or read data

~~~bash
x-api-tool api ops list [--tag TAG] [--security-scheme SCHEME]
x-api-tool api OPERATION_ID [--auth auto|app|user|none] [--path key=value] [--query key=value] [--body-json '{}']
x-api-tool --live users resolve --username USERNAME [--include-receives-your-dm]
x-api-tool --live dm can-send --to-username USERNAME
~~~

Run a GET or HEAD command without `--live` to preview it. `dm can-send` checks whether the recipient can receive a message from your account. Confirm permission to message them separately.

## Post or delete a post

Approve the live account check used to save the preview. Read the account username and ID and the full post before approving apply. A reply uses the same `createPosts` command with reply details in the body.

~~~bash
x-api-tool --live --plan-out post.json api createPosts --auth user --body-json '{"text":"Example post"}'
x-api-tool --apply --yes --ack-no-snapshot --plan-in post.json api createPosts
x-api-tool --live --plan-out delete.json api deletePosts --auth user --path id=POST_ID
x-api-tool --apply --yes --ack-no-snapshot --ack-irreversible --plan-in delete.json api deletePosts
~~~

For other write operations, preview the exact command, get approval, then add `--apply --yes --ack-no-snapshot` and `--ack-irreversible` for deletes. See [How approvals work](safety_model.md).

## Send a direct message

Use a real reason the person asked for or agreed to this message. The text below is an example. The tool adds the opt-out line to the message.

~~~bash
x-api-tool --live --plan-out dm.json dm send --to-user-id USER_ID --message 'Example reply' --intent-evidence 'They asked for this on X' --opt-out-line 'Reply STOP to opt out.'
x-api-tool --apply --yes --ack-no-snapshot --plan-in dm.json dm send --to-user-id USER_ID --message 'Example reply' --intent-evidence 'They asked for this on X' --opt-out-line 'Reply STOP to opt out.'
~~~

You can use `--to-username` in place of `--to-user-id`. To review several one-to-one messages, use `dm bulk-send --csv job.csv` with the columns `recipient,message,intent_evidence`. Use the same `--opt-out-line` and `--min-delay-s` in preview and apply. Keep the wording specific to each person. If a recipient opts out, record it with `dm opt-out add --recipient NAME_OR_ID`. Use `dm opt-out list` to check the list.

## Jobs and saved runs

- `x-api-tool jobs run --file jobs.csv [--limit N] [--plan-out plan.json]` runs a CSV with an `action` column. The runner stops on the first error. Use `--apply --yes --plan-in plan.json` with the same file to apply a reviewed run that has a supported write action.
- `x-api-tool demo read` and `x-api-tool demo write --selector demo-resource` are examples. Applying `demo write` or the sample `write.ping` job refuses because neither has an X write handler. See [sample jobs](../examples/jobs.csv) and [the sample with a write](../examples/jobs_with_write.csv).
- `x-api-tool runs list [--limit 20]` and `x-api-tool runs show --run-id RUN_ID` open local run records. Write-capable commands save records under `.state/runs/` next to your settings file. `--run-id` and `--artifacts-dir` change where a record is saved. `--no-artifacts` turns off the automatic run record.
- Use `--plan-out` to save a preview, `--plan-in` to use a reviewed plan and `--receipt-out` to choose where the apply receipt is saved.
