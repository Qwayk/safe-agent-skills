# Twilio

The Twilio API tool for agents helps you understand and manage the communications work in your Twilio account.

You can ask your agent to check message and call activity, review phone numbers and usage, inspect delivery or verification status, find account problems, and prepare changes across Twilio's public communications APIs.

For example: "Show me messages that failed today," "Check this call's status," "List phone numbers that are not attached to an application," or "Prepare a new messaging service for this project."

The agent looks first and explains what it found. If you ask it to contact someone, spend money, release a number, change routing or permissions, or make another live change, it shows you the exact plan and waits for the required approval before anything runs.

## Start here first

Ask your agent:

```text
Connect to Twilio, confirm which account I gave you access to, and tell me what is worth checking first. Do not change anything.
```

That gives you a useful account check without sending a message, making a call, buying a number, or changing live routing.

- [Connect your Twilio account](docs/onboarding.md)
- [Get the first safe result](docs/quickstart.md)
- [See what you can ask](docs/use_cases.md)

## What your agent can do

- Review accounts, usage, messages, calls, recordings, phone numbers, verification services, Conversations, and other supported Twilio resources.
- Find failed, queued, incomplete, misconfigured, or unexpectedly expensive activity and explain what needs attention.
- Prepare messaging, voice, routing, identity, compliance, Serverless, Studio, TaskRouter, and account changes for review.
- Run an approved change through one fixed Twilio operation, then record what Twilio accepted and what could be checked afterward.

The tool does not expose a raw request escape hatch. Every command names a pinned Twilio operation and accepts only the path, query, header, and body fields declared for that operation.

## What happens before live changes

Ordinary reads can run immediately. Normal output hides message content, phone numbers, identities, recording URLs, credentials, and other fields marked private by the pinned Twilio specification. Use `--sensitive-out` when sensitive provider output or a command-required snapshot must be saved in a protected local file. Some commands deliberately save only the state needed for that snapshot.

A paid read, such as a Twilio Lookup, is treated like a live action even though it uses `GET`. It produces a plan first and waits for cost approval.

Every write also starts with a plan tied to the exact account, command, input, catalog, and tool version. The tool validates the fixed input contract before it will even show or save that dry-run plan. Apply requires the plan to be saved and supplied again, plus `--apply --yes`, a new protected receipt path, and every extra acknowledgement named in the plan. Writes are never retried automatically.

Before contacting Twilio, apply creates the receipt file and refuses if it cannot create it or the path already exists. After the one provider attempt, that receipt records `succeeded` for a Twilio 2xx response, `failed` for a provider non-2xx response, or `uncertain` when no provider response arrives. An uncertain attempt must be checked before anyone considers another request.

For a fixed bulk command, the plan must derive the exact target list and count from the validated request body. The tool refuses a missing target list, a count that does not match that list, or more than 25 targets.

Twilio accepting or queueing a request is not the same as delivery. The result keeps `accepted`, `queued`, `sent`, and `delivered` separate.

## What access this tool needs

Use your Account SID with a Twilio API key SID and secret. A Restricted API key is preferred when its permissions cover the work. The Account Auth Token is a warned fallback, and OAuth is used only for operations whose pinned specification requires it.

Region and edge routing must be configured together. Never paste API secrets, Auth Tokens, OAuth tokens, SIP credentials, or secret-bearing URLs into chat.

## Install and first run

Install slug: `twilio`

Ask your agent to install the `twilio` skill from `Qwayk/safe-agent-skills`. If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@twilio -g -y
```

The bundled CLI requires Python 3.12 or newer. From the installed skill folder, set it up and connect the account:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/qwayk-twilio-safe-agent-cli onboarding --write-env
.venv/bin/qwayk-twilio-safe-agent-cli auth check
```

Fill the new `.env` file before the auth check. The [onboarding guide](docs/onboarding.md) explains the required values and the first live read.

## What it covers today

The pinned official source contains 1,550 raw operations across 61 JSON specifications. The tool exposes 1,325 fixed commands. The remaining rows are 205 past-end-of-life operations, 9 exact older routes mapped to a current command, 5 developer-preview operations without a stable public contract, and 6 operations whose complete request contract is not publicly available. The equation is `1,325 + 205 + 9 + 5 + 6 = 1,550`.

An official-source review resolved the 81 write definitions that the pinned OpenAPI did not type completely. Sixty-seven now have operation-specific commands, including strict SCIM user PATCH and Public Beta Porting webhook configuration, Verify starts, Studio flows and executions, Video rooms, Sync writes, Proxy sessions, Event Streams, and regulatory writes. Two deprecated Preview Marketplace routes point to the stable Marketplace v1 commands. The other 12 stay non-callable: one removed Studio v1 operation, five developer-preview operations without a stable contract, and six operations whose complete current request shape is not public.

SCIM user PATCH accepts only eight path-specific scalar replacements, requires paired equal username and primary-email changes, and binds `If-Match` to the protected paired-GET snapshot version. Porting webhook configuration accepts only its documented HTTPS targets on valid public hosts and 12 POST-side notification values; its plan states that POST overwrites the existing configuration and requires a paired snapshot. Both snapshots record and enforce the paired read command, account fingerprint, and exact read target. Normal SCIM and Porting output and provider errors hide user data and webhook URLs.

Flexible JSON is accepted only in fields where Twilio documents it, such as Studio `Parameters` and Sync `Data`. The tool parses stringified form JSON, checks its shape and size, hides private values recursively, and rejects undocumented branches. Studio Flow definitions accept only widget types with a complete current published child schema, enforce each widget's named property fields, and include nested JSON in contact, spend, and bulk risk checks. Video rules reject missing filters, conflicting `all` filters, and duplicates; a composition must name video or audio input. These controls never turn a nested field into a general body or raw-request bridge.

Preview and entitlement-gated commands remain visible, but their live behavior is not claimed without the needed Twilio access. [See every operation and its disposition](docs/api_coverage.md).

The two Frontline commands remain available for existing Frontline customers for now. Frontline has been end-of-sale since February 9, 2023 and is scheduled to retire on September 30, 2026, so this access is gated and live-unverified. The pinned boundary must be regenerated and reviewed before that retirement date.

SendGrid, Segment, Twilio Console automation, webhook hosting, client-SDK-only helpers, and TwiML as a generic execution language are outside this tool.

## Limits

- No live Twilio account request, send, call, Verify attempt, Lookup, number purchase, or delivery callback has been used as proof.
- Twilio test credentials cover only SMS, calls, number purchases, and Lookup. The four included fixtures check those documented request shapes locally; none was sent to Twilio, and they do not prove delivery callbacks.
- The tool does not promise rollback, backup, restore, or undo where Twilio provides no such path.
- It does not decide whether a message, call, identity check, recording, or compliance workflow is legal for your use case.

## Helpful docs

- [Choose the right guide](docs/README.md)
- [Use the fixed command surface](docs/command_reference.md)
- [Understand approvals and receipts](docs/safety_model.md)
- [Review what was checked](docs/proof.md)
- [Check the official sources](docs/references.md)
