# What we tested

## November 23, 2026 local checks

Both local copies passed 48 tests from a fresh install with no X account. Each install loaded all 156 API commands. Simulated X replies checked the account shown during setup, refusal when the account or request changed, reading a new post back from X, and accepted, rejected or unconfirmed messages. The checks sent no live X requests and used no X credits.

## June 11, 2026 local checks

The earlier Codex check ran on tool version 0.1.0 with X API snapshot 2.159. It checked the version, local account setup, the command list, a post preview and a write refused without no-snapshot approval. Provider replies were simulated. The post and message examples below were saved before the new account and plan checks.

- [Version](examples/outputs/version.json), [account check](examples/outputs/auth_check.json) and [API command list](examples/outputs/api_ops_list.json)
- [API call preview](examples/outputs/api_call_plan.json) and [message preview](examples/outputs/dm_bulk_send_plan.json)
- [Example plan](examples/plan.example.json) and [example receipt](examples/receipt.example.json)

See [Commands](command_reference.md) for the current commands and [X references](references.md) for the API sources.
