# AWS docs

AWS is easiest to use when you start with the real job, then check identity, account, region, and safety before asking an agent to do more. These docs explain how to inspect AWS identity, services, resources, access, and spend, what setup is needed, and where the tool stops before risky changes.

If you are new, read the first few links before asking for AWS data or changes. They explain useful jobs, the setup path, and the safety limits.

## Start with the work
- [What you can do with AWS](use_cases.md) - real jobs to hand to an agent for AWS
- [Quickstart](quickstart.md) - the shortest path to one useful first result
- [Set up AWS access locally](onboarding.md) - what must be connected or confirmed before the first run
- [How this stays safe](safety_model.md) - what the tool can and cannot change, and where approval is needed

## Commands, setup, and fixes
- [Command reference](command_reference.md) - the exact commands and options
- [Authentication details](authentication.md) - credential rules and safe auth checks
- [Configuration](configuration.md) - local settings, environment values, and precedence rules
- [Troubleshooting](troubleshooting.md) - what to check when a command fails or refuses to run
- [Jobs and batch work](jobs_and_batches.md) - repeatable or larger jobs that need more care

## Proof and details
- [Proof and verification](proof.md) - what has been checked and what still needs live verification
- [API coverage](api_coverage.md) - the AWS surface this skill actually covers
- [Source references](references.md) - source notes behind the implementation and docs
- [Technical architecture](architecture.md) - how the command, config, AWS SDK, and output layers fit together
- [Examples](examples/) - safe sample plans, receipts, and command outputs
