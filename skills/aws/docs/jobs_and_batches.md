# Jobs and Batches

AWS batch work is where small mistakes get multiplied. If the agent is checking many users, buckets, instances, regions, queues, or policies, keep each target visible and stop on the first surprise.

This tool does not ship a separate background worker. Each command runs in one process.

## Good repeated jobs

- Review IAM users or access keys one account at a time.
- Check S3 buckets for public access or policy review.
- List EC2 instances by region and flag obvious spend risk.
- Review security groups, Route 53 records, CloudFront distributions, queues, or alarms in small groups.
- Prepare one dry-run plan per change target instead of one vague multi-resource instruction.

## Safer batch rules

- Check identity and region before the loop starts.
- Use account and region allowlists when the wrong target would be serious.
- Run reads before writes when possible.
- Keep the resource id visible in every plan or summary.
- Do not hide many destructive targets behind one vague instruction.
- Stop on the first unexpected refusal, access error, or `limited` verification result.
- For writes, create and review plans before apply.

The local proof for write-capable commands lives under `.state/runs/`.
