# Use cases

AWS work is safest when the important question is not only "can AWS do it?" but "which account will this touch, what risk does it carry, and can I review it before anything changes?"

AWS work becomes easier to trust when the agent can name the account, region, service, and risk before it acts.

## Good first asks

- Check which AWS account, role, and region this workspace is using, then stop.
- Show me the safest AWS read to run before we change anything.
- List IAM users and tell me what you can inspect without making changes.
- Show EC2 instances in this region and flag anything that looks risky to stop.
- Review S3 bucket access settings before I ask for any policy change.
- Tell me whether this AWS request touches identity, secrets, spend, public access, or data movement.
- Prepare a dry-run plan for this write and stop before any live change.

## Safe review jobs

- Confirm the AWS identity with STS before touching another service.
- Check IAM, EC2, S3, CloudWatch, billing, or other service state with named AWS commands.
- Compare the requested change against account and region allowlists.
- Ask the agent to explain whether a command is read-only, a normal write, no-snapshot, or irreversible.

## Review-first change jobs

- Create or update an IAM, EC2, S3, messaging, or billing-related resource only after a saved plan is reviewed.
- Stop, delete, remove, terminate, publish, send, or expose something only after the tool names the extra risk.
- Keep a receipt that says what was checked, whether resource read-back ran, and when verification is limited.

## What you should get back

When the tool is working well, the agent should give you:

- a plain summary
- the account and region in use
- a preview before any live change
- a refusal when the target or risk is wrong
- a redacted receipt after apply

## When not to use it

- Do not use it as a shortcut around AWS permissions or change review.
- Do not use it for undocumented console traffic or private AWS endpoints.
- Do not treat a limited receipt as proof that AWS resource state was read back. It means the reviewed plan matched and the AWS SDK call returned a captured response.
