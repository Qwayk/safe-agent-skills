# TheMealDB docs

TheMealDB is quickest to understand if you start with what the public data can answer, then check the first safe read. These docs explain how to look up public meals, recipes, ingredients, categories, and areas, what empty or missing results mean, and how to verify behavior without setting up a private account.

No private account is needed for the default path, so setup is mostly about defaults, timeouts, and knowing what a missing public result means.

## Start with the work
- [What you can do with TheMealDB](use_cases.md) - real jobs to hand to an agent for TheMealDB
- [Quickstart](quickstart.md) - the shortest path to one useful first result
- [Use TheMealDB with no account](onboarding.md) - what to know before the first public read
- [How this stays read-only](safety_model.md) - why the tool cannot change anything and what limits still matter

## Commands, setup, and fixes
- [Command reference](command_reference.md) - the exact commands and options
- [Authentication details](authentication.md) - why the default path does not need credentials
- [Configuration](configuration.md) - local settings, environment values, and precedence rules
- [Troubleshooting](troubleshooting.md) - what to check when a command fails or refuses to run

## Proof and details
- [Proof and verification](proof.md) - what has been checked and what still needs live verification
- [API coverage](api_coverage.md) - the API surfaces this skill actually covers
- [Source references](references.md) - source notes behind the implementation and docs
- [Technical architecture](architecture.md) - how the command, config, client, and output layers fit together
- [Examples](examples/) - sample inputs or outputs when the tool ships them
