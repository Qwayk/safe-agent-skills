# LocalServicesLeadService (Google Ads API v25)

Command shape:
- `google-ads-api-tool local-services-lead-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects matching the selected RPC request message. Unknown fields are rejected.
- Write methods are plan-first. Live apply requires the allowlist and applicable risk approvals; unsupported snapshot shapes remain blocked unless explicitly supported.

## Methods
- `append-lead-conversation` — `LocalServicesLeadService.AppendLeadConversation` (write; plan-first; unary_unary) — request: `AppendLeadConversationRequest` → response: `AppendLeadConversationResponse`
- `provide-lead-feedback` — `LocalServicesLeadService.ProvideLeadFeedback` (write; plan-first; unary_unary) — request: `ProvideLeadFeedbackRequest` → response: `ProvideLeadFeedbackResponse`
