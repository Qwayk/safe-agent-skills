# API coverage

## Summary

- Provider: Zapier
- API base URL: https://api.zapier.com
- AI Actions API base URL: https://actions.zapier.com
- Auth method: OAuth2 bearer token; optional client credentials / JWT where required
- Partner API schema: 21 operations (OpenAPI 3.1.0, Partner API 2024.11.0)
- Trigger Inbox API operations: 13
- Promotions API operations: 3
- AI Actions API operations: 25
- Total explicit commands: 62

## Endpoint coverage

| Surface | Endpoint | Capability | CLI command | Safety gates | Status |
|---|---|---|---|---|---|
| ai-actions | GET /api/v2/ai-actions/ | List AI Actions | `ai-actions ai-actions-list-ai-actions` | read-only direct run | implemented |
| ai-actions | POST /api/v2/ai-actions/ | Create AI Action | `ai-actions ai-actions-create-ai-action` | dry-run plan; apply requires --plan-in plus --yes/--ack-* | implemented |
| ai-actions | DELETE /api/v2/ai-actions/{ai_action_id}/ | Delete AI Action | `ai-actions ai-actions-delete-ai-action` | dry-run plan; apply requires --plan-in plus --yes/--ack-* | implemented |
| ai-actions | GET /api/v2/ai-actions/{ai_action_id}/ | Get AI Action | `ai-actions ai-actions-get-ai-action` | read-only direct run | implemented |
| ai-actions | PUT /api/v2/ai-actions/{ai_action_id}/ | Update AI Action | `ai-actions ai-actions-update-ai-action` | dry-run plan; apply requires --plan-in plus --yes/--ack-* | implemented |
| ai-actions | POST /api/v2/ai-actions/{ai_action_id}/execute/ | Execute Stored AI Action | `ai-actions ai-actions-execute-ai-action` | dry-run plan; apply requires --plan-in plus --yes/--ack-* | implemented |
| ai-actions | POST /api/v2/ai-actions/{ai_action_id}/preview/ | Preview Stored AI Action | `ai-actions ai-actions-preview-ai-action` | dry-run plan; apply requires --plan-in plus --yes/--ack-* | implemented |
| ai-actions | GET /api/v2/apps/search/ | Search Apps | `ai-actions search-search-apps` | read-only direct run | implemented |
| ai-actions | GET /api/v2/apps/{app}/ | Get App Details | `ai-actions actions-get-app-details` | read-only direct run | implemented |
| ai-actions | GET /api/v2/apps/{app}/actions/ | Search Actions | `ai-actions search-search-actions` | read-only direct run | implemented |
| ai-actions | POST /api/v2/apps/{app}/actions/{action}/ | Get Action Details | `ai-actions actions-get-action-details` | dry-run plan; apply requires --plan-in plus --yes/--ack-* | implemented |
| ai-actions | GET /api/v2/apps/{app}/auths/ | List Authentications For App | `ai-actions actions-list-authentications-for-app` | read-only direct run | implemented |
| ai-actions | POST /api/v2/apps/{app}/choices/{prefill}/ | Get Prefill Choices | `ai-actions actions-get-prefill-choices` | dry-run plan; apply requires --plan-in plus --yes/--ack-* | implemented |
| ai-actions | GET /api/v2/auth/accounts/ | Get Account List | `ai-actions meta-get-account-list` | read-only direct run | implemented |
| ai-actions | GET /api/v2/auth/check/ | Check User Auth | `ai-actions meta-check-user-auth` | read-only direct run | implemented |
| ai-actions | GET /api/v2/auth/login-link/ | Get User Login Link | `ai-actions meta-get-user-login-link` | read-only direct run | implemented |
| ai-actions | GET /api/v2/auth/oauth-login-link/ | Get Oauth Login Link | `ai-actions meta-get-oauth-login-link` | read-only direct run | implemented |
| ai-actions | POST /api/v2/execute/ | Execute Stateless AI Action | `ai-actions execute-execute-stateless-action` | dry-run plan; apply requires --plan-in plus --yes/--ack-* | implemented |
| ai-actions | POST /api/v2/execute/log/{execution_log_id}/rate/ | Rate Execution Log | `ai-actions execution-log-rate-execution-log` | dry-run plan; apply requires --plan-in plus --yes/--ack-* | implemented |
| ai-actions | POST /api/v2/guess-actions/ | Guess Actions | `ai-actions guess-guess-actions` | dry-run plan; apply requires --plan-in plus --yes/--ack-* | implemented |
| ai-actions | GET /api/v2/health/ | App Health Check | `ai-actions meta-app-health-check` | read-only direct run | implemented |
| ai-actions | POST /api/v2/shrink-result/ | Shrink Result | `ai-actions meta-shrink-result` | dry-run plan; apply requires --plan-in plus --yes/--ack-* | implemented |
| ai-actions | POST /api/v2/unfurl/ | Unfurl URLs into resources | `ai-actions unfurl-unfurl-url` | dry-run plan; apply requires --plan-in plus --yes/--ack-* | implemented |
| ai-actions | GET /api/v2/unfurl/apps/ | List unfurl apps and their URL patterns | `ai-actions unfurl-get-unfurl-apps` | read-only direct run | implemented |
| ai-actions | GET /api/v2/unfurl/apps/{app}/auth/ | Checks if the app has any auths configured for the specific app | `ai-actions unfurl-check-user-auth-for-app` | read-only direct run | implemented |
| partner | GET /v1/apps | Get Apps [v1] | `partner apps-list` | read-only direct run | implemented |
| partner | GET /v1/categories | Get Categories | `partner categories-list` | read-only direct run | implemented |
| partner | GET /v1/profiles/me | User Profile | `partner profiles-me-list` | read-only direct run | implemented |
| partner | GET /v1/zap-templates | Get Zap Templates | `partner zap-templates-list` | read-only direct run | implemented |
| partner | GET /v1/zaps | Get Zaps [v1] | `partner zaps-list` | read-only direct run | implemented |
| partner | POST /v2/action-runs | Create an Action Run | `partner create-action-run` | dry-run plan; apply requires --plan-in plus --yes/--ack-* | implemented |
| partner | GET /v2/action-runs/{id} | Retrieve Action Run | `partner retrieve-action-run` | read-only direct run | implemented |
| partner | GET /v2/actions | Get Actions | `partner get-actions` | read-only direct run | implemented |
| partner | POST /v2/actions/{action_id}/inputs | Get Input Fields | `partner get-fields-inputs` | dry-run plan; apply requires --plan-in plus --yes/--ack-* | implemented |
| partner | POST /v2/actions/{action_id}/inputs/{input_id}/choices | Get Choices | `partner get-choices` | dry-run plan; apply requires --plan-in plus --yes/--ack-* | implemented |
| partner | POST /v2/actions/{action_id}/outputs | Get Output Fields | `partner get-fields-outputs` | dry-run plan; apply requires --plan-in plus --yes/--ack-* | implemented |
| partner | POST /v2/actions/{action_id}/test | Step Test | `partner test-action` | dry-run plan; apply requires --plan-in plus --yes/--ack-* | implemented |
| partner | GET /v2/apps | Get Apps [v2] | `partner get-v2-apps` | read-only direct run | implemented |
| partner | GET /v2/authentications | Get Authentications | `partner get-authentications` | read-only direct run | implemented |
| partner | POST /v2/authentications | Create Authentication | `partner create-authentication` | dry-run plan; apply requires --plan-in plus --yes/--ack-* | implemented |
| partner | GET /v2/authorize | Create Account | `partner authorize-list` | read-only direct run | implemented |
| partner | POST /v2/guess | Guess a Zap [Beta] | `partner create-zap-guess` | dry-run plan; apply requires --plan-in plus --yes/--ack-* | implemented |
| partner | GET /v2/whitelabel/apps | Get Whitelabel Apps [v2] | `partner v2-whitelabel-apps-list` | read-only direct run | implemented |
| partner | GET /v2/zap-runs | Get Zap Runs | `partner get-zap-runs` | read-only direct run | implemented |
| partner | GET /v2/zaps | Get Zaps [v2] | `partner get-v2-zaps` | read-only direct run | implemented |
| partner | POST /v2/zaps | Create a Zap | `partner post-zaps` | dry-run plan; apply requires --plan-in plus --yes/--ack-* | implemented |
| promotions | POST /v2/promotions | Create a promotion enrollment | `promotions create` | dry-run plan; apply requires --plan-in plus --yes/--ack-* | implemented |
| promotions | DELETE /v2/promotions/{enrollment_id} | Unenroll an account from a promotion. Endpoint available to Partners only. The request must be authenticated by an app access token the Part... | `promotions destroy` | dry-run plan; apply requires --plan-in plus --yes/--ack-* | implemented |
| promotions | GET /v2/promotions/{enrollment_id} | Retrieve promotion enrollment details by enrollment ID. Endpoint available to Partners only. The request must be authenticated by a user acc... | `promotions retrieve` | read-only direct run | implemented |
| trigger-inbox | GET /trigger-inbox/v1/inboxes | List all inboxes. | `trigger-inbox listTriggerInboxes` | read-only direct run | implemented |
| trigger-inbox | POST /trigger-inbox/v1/inboxes | Create an inbox. | `trigger-inbox createTriggerInbox` | dry-run plan; apply requires --plan-in plus --yes/--ack-* | implemented |
| trigger-inbox | PUT /trigger-inbox/v1/inboxes | Ensure a named inbox exists. | `trigger-inbox ensureTriggerInbox` | dry-run plan; apply requires --plan-in plus --yes/--ack-* | implemented |
| trigger-inbox | DELETE /trigger-inbox/v1/inboxes/{id} | Mark an inbox for deletion. | `trigger-inbox deleteTriggerInbox` | dry-run plan; apply requires --plan-in plus --yes/--ack-* | implemented |
| trigger-inbox | GET /trigger-inbox/v1/inboxes/{id} | Get inbox details. | `trigger-inbox getTriggerInbox` | read-only direct run | implemented |
| trigger-inbox | PATCH /trigger-inbox/v1/inboxes/{id} | Update inbox settings. | `trigger-inbox patchTriggerInbox` | dry-run plan; apply requires --plan-in plus --yes/--ack-* | implemented |
| trigger-inbox | POST /trigger-inbox/v1/inboxes/{id}/pause | Pause an inbox. | `trigger-inbox pauseTriggerInbox` | dry-run plan; apply requires --plan-in plus --yes/--ack-* | implemented |
| trigger-inbox | POST /trigger-inbox/v1/inboxes/{id}/resume | Resume an inbox. | `trigger-inbox resumeTriggerInbox` | dry-run plan; apply requires --plan-in plus --yes/--ack-* | implemented |
| trigger-inbox | GET /trigger-inbox/v1/inboxes/{inbox_id}/events | Subscribe to inbox notifications over SSE. | `trigger-inbox getTriggerInboxEvents` | read-only direct run | implemented |
| trigger-inbox | GET /trigger-inbox/v1/inboxes/{inbox_id}/messages | List messages from an inbox. | `trigger-inbox listTriggerInboxMessages` | read-only direct run | implemented |
| trigger-inbox | POST /trigger-inbox/v1/inboxes/{inbox_id}/messages/ack | Acknowledge messages from an inbox. | `trigger-inbox acknowledgeTriggerInboxMessages` | dry-run plan; apply requires --plan-in plus --yes/--ack-* | implemented |
| trigger-inbox | POST /trigger-inbox/v1/inboxes/{inbox_id}/messages/lease | Lease messages from an inbox. | `trigger-inbox leaseTriggerInboxMessages` | dry-run plan; apply requires --plan-in plus --yes/--ack-* | implemented |
| trigger-inbox | POST /trigger-inbox/v1/inboxes/{inbox_id}/messages/release | Release leased messages back to an inbox without acknowledging them. | `trigger-inbox releaseTriggerInboxMessages` | dry-run plan; apply requires --plan-in plus --yes/--ack-* | implemented |

## Official docs outside the command surface

- Zapier MCP setup docs are intentionally excluded. This source is an API CLI, not an MCP installer.
- Zapier Platform Integration Builder docs are intentionally excluded. They teach developers how to build Zapier integrations, not how this CLI manages Zapier API resources.
- White Label guide pages are accounted for through the Trigger Inbox, Partner/Workflow, and auth notes. Guide-only pages do not become raw commands.

## Known gaps

None in this shipped source surface. Live behavior remains unverified until real Zapier credentials and partner access are available.
