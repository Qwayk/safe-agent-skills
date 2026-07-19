---
name: twilio
description: Use when a user asks to inspect or change a Twilio account through Messaging, Voice, Conversations, Verify, Numbers, Studio, or another covered Twilio REST API family.
---

# Twilio

Use `qwayk-twilio-safe-agent-cli` for Twilio REST API work. Start with the narrowest useful read, explain the result in normal words, and stop before any live change the user has not reviewed.

Read `README.md`, `docs/safety_model.md`, and `docs/command_reference.md` when setup, risk, or input fields are unclear. Use only fixed commands listed in `docs/api_coverage.md`. Check `--help` instead of inventing a command, parameter, or body field.

Before building an input file for an unfamiliar command, inspect its exact declared fields:

```bash
qwayk-twilio-safe-agent-cli inventory show --command api-v2010.create-message
```

The fixed catalog currently exposes 1,325 commands from 1,550 pinned operations. Current commands include strict SCIM user PATCH, Public Beta Porting webhook configuration, Verify starts, Studio flows and executions, Video rooms, Sync data, Proxy sessions, Event Streams, and Numbers or TrustHub compliance resources. Inspect the exact command before using any of them; product names do not imply that every optional provider field is accepted.

## Safe workflow

1. Confirm the local tool and configuration:

   ```bash
   qwayk-twilio-safe-agent-cli --version
   qwayk-twilio-safe-agent-cli auth check
   ```

2. Run an ordinary read directly. For example:

   ```bash
   qwayk-twilio-safe-agent-cli api-v2010 fetch-account --input-json examples/inputs/fetch-account.json
   ```

   A paid GET, including Lookup, is an effectful operation. It produces a dry-run plan first and needs spend approval before the request runs.

3. Put command-specific inputs in a protected local JSON file. Do not ask the user to paste credentials, message bodies, phone numbers, recordings, transcripts, or `.env` contents into chat. Use `--sensitive-out` when sensitive provider output or a command-required snapshot must be saved; the normal result stays redacted. Some commands deliberately save only the state needed for the snapshot.

4. Preview every effectful operation and save its plan:

   ```bash
   qwayk-twilio-safe-agent-cli api-v2010 create-message \
     --input-json examples/inputs/create-message-plan.json \
     --plan-out message-plan.json
   ```

   Review the protected input file and the plan together. The plan redacts contact details, binds the exact input hash, names the account fingerprint and region/edge, explains the expected effect, and lists every required acknowledgement.

5. Apply only after the user approves that exact command, input, account, and effect. Reuse the same `--input-json`; changing it makes the plan fail closed. Keep the reviewed plan at mode 600 and always save the live receipt.

   ```bash
   qwayk-twilio-safe-agent-cli api-v2010 create-message \
     --input-json examples/inputs/create-message-plan.json \
     --plan-in message-plan.json \
     --apply --yes --ack-contact --ack-spend --ack-no-snapshot \
     --receipt-out message-receipt.json
   ```

   Add the acknowledgement flags named by the plan. A create, send, call, verification, purchase, delete, permission, compliance, deploy, or routing action can require more than one.

6. Read the receipt and report Twilio's exact status. `accepted` or `queued` is not `delivered`. Say delivery was confirmed only when Twilio reports a delivery state.

## Guardrails

- Flexible JSON is never a generic request bridge. It is accepted only in the exact documented field named by a fixed command. Form-encoded JSON must be a valid JSON string and is checked for documented shape and size. Unknown top-level fields and unproved optional branches are refused.
- Studio Flow definitions accept only widget types with a complete current published child schema and enforce their named property fields. Nested Definition JSON still escalates contact, spend, and bulk risk. Video rule arrays refuse missing filters, `all` combined with another filter, duplicates, and compositions without audio or video input.
- Respect restricted command subsets. Event Sink creation excludes the undocumented `email` configuration, Proxy Session creation excludes inline `Participants`, Flex Plugin configuration excludes `phase`, and current Knowledge commands exclude incomplete policy and embedding branches. Use the separately fixed resource command when the wrapper points to one.
- Keep `api-v2010 create-message` to one recipient. Use only a fixed Twilio bulk command when the catalog provides one; require `--ack-bulk`, an exact `--target-count`, and no more than 25 targets. Never split work to bypass the cap.
- For an update or delete with a paired read, save the command's current-state snapshot with `--sensitive-out`, protect it at mode 600, and bind it with `--snapshot-in`. SCIM user PATCH and Porting webhook configuration require that snapshot and do not accept `--ack-no-snapshot`; SCIM also requires `If-Match` to equal the saved `meta.version`.
- Do not retry a write, send, call, purchase, verification attempt, or other non-idempotent action after an uncertain response. Read the receipt or perform a narrow read instead.
- Preview and access-gated commands need their extra acknowledgement and may still fail for account access.
- Use Twilio test credentials only for the officially supported message, call, number-purchase, and Lookup fixtures. Do not run a real send, call, Verify attempt, or number purchase merely to prove the skill works.

Refuse when the target is unclear, the command is outside coverage, a required secret would enter chat, the reviewed input changed, an acknowledgement is missing, the request exceeds the target cap, or safe verification is unavailable and the user has not accepted that limit.
