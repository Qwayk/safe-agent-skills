# Run your first Google Cloud read

Use [the setup guide](onboarding.md) to sign in and check your Google credentials. Then list Compute Engine instances in a project and zone you know. If that project uses another service, pick a small read from [the command guide](command_reference.md).

## List Compute Engine instances

Save this as `input.json` and replace the example project and zone:

```json
{
  "path": {
    "project": "my-gcp-project",
    "zone": "us-central1-a"
  },
  "query": {
    "maxResults": 10
  }
}
```

```bash
qwayk-gcp-safe-agent-cli compute instances-list --input-json input.json
```

Say which account, project and zone you checked, what came back, and what is worth looking at next. If the read fails, check the project, zone, enabled API, IAM permission, quota project and local limits. [Troubleshooting](onboarding.md#fix-a-connection-problem)

## Check the command list offline

```bash
qwayk-gcp-safe-agent-cli --output json inventory summary
```

This reads the inventory included with the CLI without contacting Google. For anything that changes Google Cloud, [prepare a plan and ask for approval](safety_model.md).
