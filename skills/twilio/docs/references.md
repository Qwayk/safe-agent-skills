# Official sources

Checked on **2026-07-19**. The pinned OpenAPI commit supplies the raw operation inventory. Current Twilio docs and Twilio-owned product schemas supply supporting request detail where that pinned inventory is incomplete. They can narrow an existing operation to a fixed contract; they do not add routes outside the pinned boundary.

## Boundary

- [Twilio OpenAPI repository](https://github.com/twilio/twilio-oai)
- [Pinned OpenAPI commit `1a9189c79a73781ddf45afcd0afd1f210742d68c`](https://github.com/twilio/twilio-oai/commit/1a9189c79a73781ddf45afcd0afd1f210742d68c)
- [Twilio Node repository](https://github.com/twilio/twilio-node)
- [Supporting Twilio-owned Node schema commit `e9e546985dcc293e4f71888160725739e7b28c37`](https://github.com/twilio/twilio-node/commit/e9e546985dcc293e4f71888160725739e7b28c37)
- [Twilio API overview](https://www.twilio.com/docs/usage/api)

## Audited write contracts

- [Verify Verification resource](https://www.twilio.com/docs/verify/api/verification)
- [Studio Flow resource](https://www.twilio.com/docs/studio/rest-api/v2/flow), [Execution resource](https://www.twilio.com/docs/studio/rest-api/v2/execution), and [Flow JSON schemas](https://www.twilio.com/docs/studio/rest-api/v2/schemas)
- [Video Rooms](https://www.twilio.com/docs/video/api/rooms-resource), [Recording Rules](https://www.twilio.com/docs/video/api/recording-rules), and [Transcriptions](https://www.twilio.com/docs/video/api/transcriptions)
- [Sync Documents](https://www.twilio.com/docs/sync/api/document-resource), [List Items](https://www.twilio.com/docs/sync/api/listitem-resource), [Map Items](https://www.twilio.com/docs/sync/api/map-item-resource), and [Stream Messages](https://www.twilio.com/docs/sync/api/stream-message-resource)
- [Proxy Sessions](https://www.twilio.com/docs/proxy/api/session)
- [Event Streams Sinks](https://www.twilio.com/docs/events/event-streams/sink-resource) and [Subscriptions](https://www.twilio.com/docs/events/event-streams/subscription)
- [Numbers End Users](https://www.twilio.com/docs/phone-numbers/regulatory/api/end-users), [End User Types](https://www.twilio.com/docs/phone-numbers/regulatory/api/end-user-types), [Supporting Documents](https://www.twilio.com/docs/phone-numbers/regulatory/api/supporting-documents), and [Supporting Document Types](https://www.twilio.com/docs/phone-numbers/regulatory/api/supporting-document-types)
- [TrustHub End Users](https://www.twilio.com/docs/trust-hub/trusthub-rest-api/enduser-resource), [End User Types](https://www.twilio.com/docs/trust-hub/trusthub-rest-api/endusertype-resource), and [Supporting Documents](https://www.twilio.com/docs/trust-hub/trusthub-rest-api/supportingdocument-resource)
- [IAM SCIM API reference](https://www.twilio.com/docs/iam/scim/api-reference)
- [Porting Webhooks Public Beta](https://www.twilio.com/docs/phone-numbers/port-in/porting-webhooks)

The generated [coverage ledger](api_coverage.md) links the exact official evidence used for every audited row, including the rows that remain non-callable.

## Authentication and routing

- [Twilio API requests and authentication](https://www.twilio.com/docs/usage/requests-to-twilio)
- [API keys overview](https://www.twilio.com/docs/iam/api-keys)
- [Restricted API keys](https://www.twilio.com/docs/iam/api-keys/restricted-api-keys)
- [Understanding Edge Locations](https://www.twilio.com/docs/global-infrastructure/understanding-edge-locations)

## Status, security, and testing

- [Outbound message status meanings](https://www.twilio.com/docs/messaging/guides/outbound-message-status-in-status-callbacks)
- [Twilio test credentials](https://www.twilio.com/docs/iam/test-credentials)
- [Lookup magic numbers](https://www.twilio.com/docs/lookup/magic-numbers-for-lookup)
- [SIM-swap test magic numbers](https://www.twilio.com/docs/lookup/magic-numbers-for-lookup/testing-sim-swap-with-magic-numbers)
- [Twilio security guidance](https://www.twilio.com/docs/usage/security)
- [Validate Twilio webhook signatures](https://www.twilio.com/docs/usage/security#validating-requests)
- [Twilio Messaging Policy](https://www.twilio.com/en-us/legal/messaging-policy)
- [Voice dialing geographic permissions](https://www.twilio.com/docs/sip-trunking/voice-dialing-geographic-permissions)
- [Voice Recording settings and encryption](https://www.twilio.com/docs/voice/recording-settings)
- [Recording media authentication](https://www.twilio.com/docs/voice/api/recording#authentication-required)

## End-of-life decisions

- [Programmable Chat End of Life Notice](https://www.twilio.com/en-us/changelog/programmable-chat-end-of-life-notice)
- [Programmable Chat in Flex end of life on June 1, 2026](https://www.twilio.com/en-us/changelog/programmable-chat-in-flex-reaching-end-of-life-on-june-1--2026)
- [Notify EOL extension to December 31, 2025](https://www.twilio.com/en-us/changelog/notify-api-end-of-life-further-extension-notice)
- [Frontline end-of-sale and retirement on September 30, 2026](https://www.twilio.com/en-us/changelog/frontline-is-entering-eol--here-s-what-that-means-for-customers)

The generated coverage ledger records the source file and disposition for every raw operation. If Twilio changes a product status or official specification, update the pinned boundary, recheck the manual contracts, and regenerate the catalog before changing public coverage claims.
