# Start using Threads

Use Python 3.12 or later. Install from the Threads tool folder, then [connect your account](onboarding.md).

```bash
python -m pip install .
threads-api-tool --output json --version
```

## Read your latest posts

```bash
threads-api-tool auth check
threads-api-tool posts list-owned --limit 5 --fields id,text,permalink
```

The account check returns your ID and username. The post command uses the signed-in account unless you pass an ID or set a default account in the settings. Posts are under `result.data`. If there is a `result.paging.cursors.after` value, pass it with `--after` to see the next page.

Other useful requests include reading replies on a post, looking up a public profile, and reading post insights if your app has access. See the [command reference](command_reference.md) for those commands.

## Review and publish a post

Use the ID from `auth check` as `USER_ID`. Save a plan with the exact text you want to post.

```bash
threads-api-tool --plan-out draft-plan.json posts create-text --threads-user-id USER_ID --text 'Example post'
```

After reviewing and approving the plan, use it to create the draft. The approval flag allows the change without a saved copy of the previous state.

```bash
threads-api-tool --apply --ack-no-snapshot --plan-in draft-plan.json posts create-text --threads-user-id USER_ID --text 'Example post'
```

Use the ID under `receipt.result.id` as `DRAFT_ID`. Check that Threads has finished processing the draft, then save the publishing plan.

```bash
threads-api-tool posts status --threads-container-id DRAFT_ID
threads-api-tool --plan-out publish-plan.json posts publish --threads-user-id USER_ID --threads-container-id DRAFT_ID
```

After approval, publish with that plan and check the receipt. The tool reads the new post using the ID Threads returns. If it cannot confirm the post, check the draft status or read the post by ID before retrying.

```bash
threads-api-tool --apply --ack-no-snapshot --plan-in publish-plan.json posts publish --threads-user-id USER_ID --threads-container-id DRAFT_ID
```

See [what the receipt means](safety_model.md) and [what to do if publishing stalls](troubleshooting.md).
