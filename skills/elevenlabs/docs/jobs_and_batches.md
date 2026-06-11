# Jobs and batches

`v0.1.0` does not expose a supported generic jobs runner.

Why this page still exists:
- the template included batch-job notes before the ElevenLabs-specific cleanup pass
- the real supported CLI surface is documented in `docs/command_reference.md`
- future ElevenLabs batch features should come back only as explicit named commands, not as a generic CSV bridge

If you need bulk work later, add it as a provider-specific command family and update:
- `docs/api_coverage.md`
- `docs/command_reference.md`
- the public skill prompt
- tests for the new command family
