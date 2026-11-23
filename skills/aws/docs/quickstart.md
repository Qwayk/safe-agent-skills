# Run your first AWS read

Follow [the setup guide](onboarding.md) to connect AWS. Confirm the account, role, region and whether the tool allows that target before you run a service command.

```bash
qwayk-aws-safe-agent-cli --output json auth check
qwayk-aws-safe-agent-cli ec2 describe-instances
```

If the role can read another service instead, try `qwayk-aws-safe-agent-cli iam list-users` or `qwayk-aws-safe-agent-cli s3 list-buckets`. Say which account and region you checked, what came back, and what is worth looking at next. [Find more commands](command_reference.md)

## Check the install offline

```bash
qwayk-aws-safe-agent-cli --output json --version
qwayk-aws-safe-agent-cli inventory summary
```

These commands read the installed package without contacting AWS. Follow [the change approval steps](safety_model.md) when you need to write.
