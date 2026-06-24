# Use Cases

AWS is broad enough that the first hard question is often not "which command can do this?" It is "which account and region will this touch, and could this affect access, spend, public exposure, secrets, or data?"

This skill is strongest when you ask it to look first, explain the risk, and only then prepare a reviewed plan.

## Good first asks

- Check which AWS account, role, and region this workspace is using, then stop.
- Show me safe AWS reads we can run before changing anything.
- List IAM users, access keys, and roles that are worth a human access review.
- Show EC2 instances in this region and point out anything that could create avoidable spend.
- Review S3 bucket access settings before I ask for a bucket policy change.
- Check CloudTrail or CloudWatch for recent evidence related to this resource.
- Show billing, budget, or service quota information that could explain a cost limit.
- Tell me whether this request touches identity, secrets, spend, public access, messaging, data movement, or a hard-to-undo action.

## Safe review jobs

- Confirm the AWS caller with STS before touching IAM, EC2, S3, or any other service.
- Review IAM users, groups, roles, access keys, MFA devices, policies, and last-used signals when the caller has permission.
- Inspect compute and network resources, such as EC2 instances, security groups, load balancers, and VPC-related resources.
- Review storage and data movement settings, such as S3 buckets, replication, DataSync, Kinesis, or export-style operations.
- Check cost-related areas, such as billing, budgets, Cost Explorer, service quotas, Savings Plans, or marketplace-related services.
- Ask the agent to classify a command as a read, a normal write, a no-snapshot write, an unknown mutating action, or an irreversible action.

## Review-first change jobs

- Create or update an IAM user, role, policy, access key, or login profile only after the plan is reviewed.
- Stop, start, terminate, delete, publish, send, expose, or move data only after the plan names the extra risk.
- Change S3, CloudFront, Route 53, security group, KMS, Secrets Manager, billing, quota, messaging, or data-transfer settings only with clear approval.
- Use account and region allowlists when a mistake could touch production or the wrong customer account.
- Keep the receipt and read the verification status after apply, especially when the result is `limited`.

## What you should get back

For a safe read, the agent should tell you the AWS identity, region, command result, and the next safe review step.

For a planned change, the agent should show the service, operation, input, risk categories, required approval flags, and why the plan is or is not safe to apply.

For a live apply, the agent should show whether the tool changed anything, whether verification was full or limited, and where the redacted receipt was saved.

## When not to use it

- Do not use it to work around AWS permissions or your normal change-review process.
- Do not use it for undocumented console traffic, private endpoints, or AWS behavior outside the pinned Botocore models.
- Do not treat a `limited` receipt as proof that AWS resource state was read back. It means the reviewed plan matched and the SDK response was captured.
- Do not let the agent choose a destructive AWS target from a vague request. Ask it to identify the target and plan first.
