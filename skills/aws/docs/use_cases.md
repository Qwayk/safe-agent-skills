# Use Cases

AWS work usually starts with a practical worry: someone needs to know what is running, who has access, whether a bucket is exposed, why a bill changed, what happened in the logs, or whether a proposed change could break production.

This skill helps an agent inspect the AWS account first, explain what it found in normal words, and prepare a reviewed plan only when a change is really needed.

## Good first asks

- Check which AWS account, role, and region this workspace is using, then stop.
- Show the safest AWS reads we can run before changing anything in this account.
- List IAM users, roles, policies, MFA status, and access keys that are worth a human access review.
- Show EC2 instances in this region, including state and type, and point out anything that may create avoidable spend.
- Review S3 bucket public-access settings and bucket policies before I ask for a policy change.
- Check CloudTrail for recent activity by this user, role, instance, bucket, key, or security group.
- Check CloudWatch alarms or logs that may explain this incident.
- Show billing, budget, Cost Explorer, or service quota information that could explain a cost or capacity limit.
- Tell me whether this request touches identity, secrets, spend, public access, messaging, data movement, or a hard-to-undo action.

## Access and identity review

- "Who am I in AWS right now?"
- "Which IAM users have console access, access keys, or old-looking credentials?"
- "Which roles and policies look powerful enough that a person should review them?"
- "Can this role see the service I need, or is it missing permission?"
- "Would this requested change affect IAM, KMS, Secrets Manager, SSO, or another identity-sensitive area?"

## Infrastructure and production review

- "Which EC2 instances are running in this region, and which ones look idle or expensive?"
- "Which security groups have broad inbound rules?"
- "Which load balancers, target groups, or Route 53 records point to this app?"
- "Which Lambda functions, ECS services, EKS clusters, RDS databases, or queues are connected to this workflow?"
- "What changed recently in CloudTrail or Config before this issue appeared?"

## Storage, data, and public exposure

- "Which S3 buckets exist, and which ones may need a public-access review?"
- "Show bucket policies, public-access blocks, encryption, versioning, and replication settings where permissions allow."
- "Which services could move data out of this account, such as DataSync, Kinesis, exports, backups, or replication?"
- "Would this change expose a bucket, CDN, DNS record, firewall rule, API endpoint, or shared snapshot?"

## Spend and capacity review

- "Why did AWS spend change?"
- "Which budgets, quotas, Savings Plans, or capacity settings are relevant here?"
- "Could this EC2, RDS, EMR, EKS, Bedrock, Marketplace, or data-transfer action increase cost?"
- "Which service quota could block this launch?"

## Review-first change jobs

- Create or update an IAM user, role, policy, access key, or login profile only after the plan is reviewed.
- Stop, start, terminate, delete, publish, send, expose, or move data only after the plan names the target and the extra risk.
- Change S3, CloudFront, Route 53, security group, KMS, Secrets Manager, billing, quota, messaging, or data-transfer settings only with clear approval.
- Use account and region allowlists when a mistake could touch production or the wrong customer account.
- Keep the receipt and read the verification status after apply, especially when the result is `limited`.

## What the agent should show you

- The AWS account id, caller ARN, role/user, and region.
- The exact service and resource it checked.
- A short explanation of what matters before raw JSON.
- Any missing AWS permission, wrong account, wrong region, or allowlist refusal.
- A dry-run plan before any action that changes AWS.
- The approval flags needed for writes, no-snapshot changes, and hard-to-undo actions.
- The receipt path and whether verification was full, limited, or failed after apply.

## When not to use it

- Do not use it to work around AWS permissions or your normal change-review process.
- Do not use it for undocumented console traffic, private endpoints, or AWS behavior outside the pinned Botocore models.
- Do not treat a `limited` receipt as proof that AWS resource state was read back. It means the reviewed plan matched and the SDK response was captured.
- Do not let the agent choose a destructive AWS target from a vague request. Ask it to identify the target and plan first.
