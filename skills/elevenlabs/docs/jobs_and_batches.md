# Jobs and batches

There is no supported generic CSV or template job runner in the customer-facing ElevenLabs command surface. The files under `examples/` are configuration/request examples, not executable batch inputs.

For larger work, use an explicit provider command repeatedly and review each plan. If a future batch feature is added, it must be a named ElevenLabs operation with a documented request contract, safety gates, proof, and tests. Update the generated coverage and command reference in the same change.

Do not use template ping actions; they are not ElevenLabs commands.
