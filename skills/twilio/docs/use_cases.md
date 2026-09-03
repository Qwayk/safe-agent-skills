# What to ask your Twilio agent

The tool is most useful when you describe the result you need and let the agent choose the fixed Twilio reads that support it.

For a credential-free integration check, ask for local ConversationRelay TwiML or WebSocket validation, a webhook signature check, or the Agent Connect metadata contract. These checks do not contact Twilio or host a service; see [local voice and webhook checks](local_contracts.md).

## Check what happened

- "Show me messages that failed today and group them by failure reason. Do not send anything."
- "Check this call SID and tell me whether Twilio still considers it in progress, completed, or failed."
- "Review this message SID. Keep queued, sent, and delivered separate."
- "Show this month's Twilio usage by category and point out anything unusual."

## Review account setup

- "List the phone numbers in this account and tell me which application or messaging service uses each one."
- "Check our messaging services for missing senders or status callbacks. Do not change them."
- "Review our Studio flows and Serverless services and flag production settings that deserve a closer look."
- "List Verify services and report their current configuration. Do not start a verification."

## Prepare a change

- "Prepare a new messaging service for this project, but stop after the plan."
- "Prepare an update to this phone number's voice routing and show the current and proposed settings."
- "Prepare this SMS to one approved test recipient. Do not apply it."
- "Prepare the release of this unused phone number and tell me exactly what cannot be undone."

Preparing is not applying. The agent writes a plan tied to the exact account and input, then tells you which approvals the live action would need.

## Work with audited write contracts

The current command surface includes fixed request contracts for areas that the pinned OpenAPI did not describe completely. Useful asks include:

- "Prepare a Verify SMS start for this approved test number, but do not send it."
- "Validate this Studio flow definition, then prepare the flow update without publishing or starting an execution."
- "Prepare a Studio execution for this approved contact and show me the exact `Parameters` data before anything runs."
- "Prepare a Video room with recording disabled. Do not add participants."
- "Prepare this Sync document update and show me the exact `Data` object that will be stored."
- "Prepare a webhook Event Streams sink and subscription for these event types. Stop after the plan."
- "Fetch the required End User Type, then prepare the matching Numbers regulatory end user."

These commands do not accept an arbitrary JSON body. Flexible data is allowed only in the field Twilio documents for that operation. Proxy session creation, for example, refuses an undocumented `Participants` array; participants must be added through the separate fixed participant command. Event Streams sinks accept only a documented Kinesis, Webhook, or Segment configuration. Numbers and TrustHub `Attributes` must follow the selected type, which the agent should fetch before planning.

## Paid reads and bulk work

A phone-number Lookup can create usage cost, so ask: "Prepare a Lookup for this number and show me the price-risk acknowledgement before it runs."

There is no generic jobs runner. Bulk work is available only through a fixed Twilio bulk operation in the pinned catalog. The plan must derive the exact target list and count from the request body. The agent must verify that list locally, show a private-data-safe preview and the same count from 1 to 25, and wait for bulk approval. A missing list, count mismatch, or larger batch is refused.

## When not to use this tool

Use another tool for SendGrid email, Segment, Twilio Console browser work, webhook hosting, or client-SDK setup. Do not use this tool to decide consent, recording, identity, or communications-law questions. Those decisions stay with the account owner and qualified advisers.
