# List your Klaviyo audiences

[Set up the tool](onboarding.md) and save a private key with `lists:read`. Then run the command onboarding prints.

```bash
klaviyo-safe-agent-cli --env-file 'my klaviyo.env' --output json --live api get_lists
```

The response shows the lists your key can see. Choose the list by name and ID before asking for its profiles. You can also review segments, look at recent profile events, check flow status, or inspect campaign and catalog details. Use the [command reference](command_reference.md) to find the right read for the job.

To prepare a write, make a [saved plan](safety_model.md) first. Keep the same settings file when you preview and apply the change.
