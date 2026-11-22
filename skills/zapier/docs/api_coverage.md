# API coverage

## Commands in the saved Zapier API files

- Partner API 2024.11.0 (OpenAPI 3.1.0) lists 21 commands.
- Trigger Inbox lists 13 commands.
- Promotions lists 3 commands.
- Zapier’s retired AI Actions API lists 25 commands.
- Total explicit commands: 62

Of these, 35 can send requests. Access depends on the operation and your Zapier integration. The other 27 give a local explanation. See the [connection guide](onboarding.md) for access.

| API | Endpoint | Capability | CLI command | Approval | Status |
|---|---|---|---|---|---|
| ai-actions | GET /api/v2/ai-actions/ | List AI Actions | `ai-actions ai-actions-list-ai-actions` | Stops locally | [Retired by Zapier](https://nla.shared.zapier.com/updates) |
| ai-actions | POST /api/v2/ai-actions/ | Create AI Action | `ai-actions ai-actions-create-ai-action` | Stops locally | [Retired by Zapier](https://nla.shared.zapier.com/updates) |
| ai-actions | DELETE /api/v2/ai-actions/{ai_action_id}/ | Delete AI Action | `ai-actions ai-actions-delete-ai-action` | Stops locally | [Retired by Zapier](https://nla.shared.zapier.com/updates) |
| ai-actions | GET /api/v2/ai-actions/{ai_action_id}/ | Get AI Action | `ai-actions ai-actions-get-ai-action` | Stops locally | [Retired by Zapier](https://nla.shared.zapier.com/updates) |
| ai-actions | PUT /api/v2/ai-actions/{ai_action_id}/ | Update AI Action | `ai-actions ai-actions-update-ai-action` | Stops locally | [Retired by Zapier](https://nla.shared.zapier.com/updates) |
| ai-actions | POST /api/v2/ai-actions/{ai_action_id}/execute/ | Execute Stored AI Action | `ai-actions ai-actions-execute-ai-action` | Stops locally | [Retired by Zapier](https://nla.shared.zapier.com/updates) |
| ai-actions | POST /api/v2/ai-actions/{ai_action_id}/preview/ | Preview Stored AI Action | `ai-actions ai-actions-preview-ai-action` | Stops locally | [Retired by Zapier](https://nla.shared.zapier.com/updates) |
| ai-actions | GET /api/v2/apps/search/ | Search Apps | `ai-actions search-search-apps` | Stops locally | [Retired by Zapier](https://nla.shared.zapier.com/updates) |
| ai-actions | GET /api/v2/apps/{app}/ | Get App Details | `ai-actions actions-get-app-details` | Stops locally | [Retired by Zapier](https://nla.shared.zapier.com/updates) |
| ai-actions | GET /api/v2/apps/{app}/actions/ | Search Actions | `ai-actions search-search-actions` | Stops locally | [Retired by Zapier](https://nla.shared.zapier.com/updates) |
| ai-actions | POST /api/v2/apps/{app}/actions/{action}/ | Get Action Details | `ai-actions actions-get-action-details` | Stops locally | [Retired by Zapier](https://nla.shared.zapier.com/updates) |
| ai-actions | GET /api/v2/apps/{app}/auths/ | List Authentications For App | `ai-actions actions-list-authentications-for-app` | Stops locally | [Retired by Zapier](https://nla.shared.zapier.com/updates) |
| ai-actions | POST /api/v2/apps/{app}/choices/{prefill}/ | Get Prefill Choices | `ai-actions actions-get-prefill-choices` | Stops locally | [Retired by Zapier](https://nla.shared.zapier.com/updates) |
| ai-actions | GET /api/v2/auth/accounts/ | Get Account List | `ai-actions meta-get-account-list` | Stops locally | [Retired by Zapier](https://nla.shared.zapier.com/updates) |
| ai-actions | GET /api/v2/auth/check/ | Check User Auth | `ai-actions meta-check-user-auth` | Stops locally | [Retired by Zapier](https://nla.shared.zapier.com/updates) |
| ai-actions | GET /api/v2/auth/login-link/ | Get User Login Link | `ai-actions meta-get-user-login-link` | Stops locally | [Retired by Zapier](https://nla.shared.zapier.com/updates) |
| ai-actions | GET /api/v2/auth/oauth-login-link/ | Get Oauth Login Link | `ai-actions meta-get-oauth-login-link` | Stops locally | [Retired by Zapier](https://nla.shared.zapier.com/updates) |
| ai-actions | POST /api/v2/execute/ | Execute Stateless AI Action | `ai-actions execute-execute-stateless-action` | Stops locally | [Retired by Zapier](https://nla.shared.zapier.com/updates) |
| ai-actions | POST /api/v2/execute/log/{execution_log_id}/rate/ | Rate Execution Log | `ai-actions execution-log-rate-execution-log` | Stops locally | [Retired by Zapier](https://nla.shared.zapier.com/updates) |
| ai-actions | POST /api/v2/guess-actions/ | Guess Actions | `ai-actions guess-guess-actions` | Stops locally | [Retired by Zapier](https://nla.shared.zapier.com/updates) |
| ai-actions | GET /api/v2/health/ | App Health Check | `ai-actions meta-app-health-check` | Stops locally | [Retired by Zapier](https://nla.shared.zapier.com/updates) |
| ai-actions | POST /api/v2/shrink-result/ | Shrink Result | `ai-actions meta-shrink-result` | Stops locally | [Retired by Zapier](https://nla.shared.zapier.com/updates) |
| ai-actions | POST /api/v2/unfurl/ | Unfurl URLs into resources | `ai-actions unfurl-unfurl-url` | Stops locally | [Retired by Zapier](https://nla.shared.zapier.com/updates) |
| ai-actions | GET /api/v2/unfurl/apps/ | List unfurl apps and their URL patterns | `ai-actions unfurl-get-unfurl-apps` | Stops locally | [Retired by Zapier](https://nla.shared.zapier.com/updates) |
| ai-actions | GET /api/v2/unfurl/apps/{app}/auth/ | Checks if the app has any auths configured for the specific app | `ai-actions unfurl-check-user-auth-for-app` | Stops locally | [Retired by Zapier](https://nla.shared.zapier.com/updates) |
| partner | GET /v1/apps | Get Apps [v1] | `partner apps-list` | Read directly | Can send request |
| partner | GET /v1/categories | Get Categories | `partner categories-list` | Read directly | Can send request |
| partner | GET /v1/profiles/me | User Profile | `partner profiles-me-list` | Read directly | Can send request |
| partner | GET /v1/zap-templates | Get Zap Templates | `partner zap-templates-list` | Read directly | Can send request |
| partner | GET /v1/zaps | Get Zaps [v1] | `partner zaps-list` | Read directly | Can send request |
| partner | POST /v2/action-runs | Create an Action Run | `partner create-action-run` | Review a plan before applying | Can send request |
| partner | GET /v2/action-runs/{id} | Retrieve Action Run | `partner retrieve-action-run` | Read directly | Can send request |
| partner | GET /v2/actions | Get Actions | `partner get-actions` | Read directly | Can send request |
| partner | POST /v2/actions/{action_id}/inputs | Get Input Fields | `partner get-fields-inputs` | Review a plan before applying | Can send request |
| partner | POST /v2/actions/{action_id}/inputs/{input_id}/choices | Get Choices | `partner get-choices` | Review a plan before applying | Can send request |
| partner | POST /v2/actions/{action_id}/outputs | Get Output Fields | `partner get-fields-outputs` | Review a plan before applying | Can send request |
| partner | POST /v2/actions/{action_id}/test | Step Test | `partner test-action` | Review a plan before applying | Can send request |
| partner | GET /v2/apps | Get Apps [v2] | `partner get-v2-apps` | Read directly | Can send request |
| partner | GET /v2/authentications | Get Authentications | `partner get-authentications` | Read directly | Can send request |
| partner | POST /v2/authentications | Create Authentication | `partner create-authentication` | Review a plan before applying | Can send request |
| partner | GET /v2/authorize | Create Account | `partner authorize-list` | Stops locally | [Browser consent](https://docs.zapier.com/powered-by-zapier/zap-creation/quick-account-creation) |
| partner | POST /v2/guess | Guess a Zap [Beta] | `partner create-zap-guess` | Review a plan before applying | Can send request |
| partner | GET /v2/whitelabel/apps | Get Whitelabel Apps [v2] | `partner v2-whitelabel-apps-list` | Read directly | Can send request |
| partner | GET /v2/zap-runs | Get Zap Runs | `partner get-zap-runs` | Read directly | Can send request |
| partner | GET /v2/zaps | Get Zaps [v2] | `partner get-v2-zaps` | Read directly | Can send request |
| partner | POST /v2/zaps | Create a Zap | `partner post-zaps` | Review a plan before applying | Can send request |
| promotions | POST /v2/promotions | Create a promotion enrollment | `promotions create` | Review a plan before applying | Can send request |
| promotions | DELETE /v2/promotions/{enrollment_id} | Unenroll an account from a promotion. Endpoint available to Partners only. The request must be authenticated by an app access token the Part... | `promotions destroy` | Review a plan before applying | Can send request |
| promotions | GET /v2/promotions/{enrollment_id} | Retrieve promotion enrollment details by enrollment ID. Endpoint available to Partners only. The request must be authenticated by a user acc... | `promotions retrieve` | Read directly | Can send request |
| trigger-inbox | GET /trigger-inbox/v1/inboxes | List all inboxes. | `trigger-inbox listTriggerInboxes` | Read directly | Can send request |
| trigger-inbox | POST /trigger-inbox/v1/inboxes | Create an inbox. | `trigger-inbox createTriggerInbox` | Review a plan before applying | Can send request |
| trigger-inbox | PUT /trigger-inbox/v1/inboxes | Ensure a named inbox exists. | `trigger-inbox ensureTriggerInbox` | Review a plan before applying | Can send request |
| trigger-inbox | DELETE /trigger-inbox/v1/inboxes/{id} | Mark an inbox for deletion. | `trigger-inbox deleteTriggerInbox` | Review a plan before applying | Can send request |
| trigger-inbox | GET /trigger-inbox/v1/inboxes/{id} | Get inbox details. | `trigger-inbox getTriggerInbox` | Read directly | Can send request |
| trigger-inbox | PATCH /trigger-inbox/v1/inboxes/{id} | Update inbox settings. | `trigger-inbox patchTriggerInbox` | Review a plan before applying | Can send request |
| trigger-inbox | POST /trigger-inbox/v1/inboxes/{id}/pause | Pause an inbox. | `trigger-inbox pauseTriggerInbox` | Review a plan before applying | Can send request |
| trigger-inbox | POST /trigger-inbox/v1/inboxes/{id}/resume | Resume an inbox. | `trigger-inbox resumeTriggerInbox` | Review a plan before applying | Can send request |
| trigger-inbox | GET /trigger-inbox/v1/inboxes/{inbox_id}/events | Subscribe to inbox notifications over SSE. | `trigger-inbox getTriggerInboxEvents` | Stops locally | Use the inbox message list |
| trigger-inbox | GET /trigger-inbox/v1/inboxes/{inbox_id}/messages | List messages from an inbox. | `trigger-inbox listTriggerInboxMessages` | Read directly | Can send request |
| trigger-inbox | POST /trigger-inbox/v1/inboxes/{inbox_id}/messages/ack | Acknowledge messages from an inbox. | `trigger-inbox acknowledgeTriggerInboxMessages` | Review a plan before applying | Can send request |
| trigger-inbox | POST /trigger-inbox/v1/inboxes/{inbox_id}/messages/lease | Lease messages from an inbox. | `trigger-inbox leaseTriggerInboxMessages` | Review a plan before applying | Can send request |
| trigger-inbox | POST /trigger-inbox/v1/inboxes/{inbox_id}/messages/release | Release leased messages back to an inbox without acknowledging them. | `trigger-inbox releaseTriggerInboxMessages` | Review a plan before applying | Can send request |

For AI Actions, use [Zapier MCP](https://docs.zapier.com/mcp/quickstart). For building and publishing an integration, use the [Zapier developer platform](https://docs.zapier.com/platform/home).
