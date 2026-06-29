# API coverage

## Source of truth

- Source: `docs/official_inventory.json` (mirrored from `src/make_com_safe_agent_cli/data/official_inventory.json`).
- Boundary: official Make Developer Hub API reference pages with embedded OpenAPI blocks.
- Total operations: `376`
- Total family pages: `59`
- Base URL family: `/api/v2`

## Command coverage shape

Every documented operation maps to an explicit command path under:

```bash
make-com-safe api <family> <operation>
```

`api list` enumerates all families and operation names at runtime.

## Coverage by family

| Family | Operations |
|---|---:|
| affiliate | 5 |
| on-prem-agents | 5 |
| ai-agents | 7 |
| ai-agents-context | 3 |
| ai-agents-llm-providers | 3 |
| analytics | 1 |
| audit-logs | 5 |
| cashier | 3 |
| connections | 9 |
| credential-requests | 11 |
| custom-properties | 2 |
| custom-properties-structure-items | 4 |
| data-stores | 5 |
| data-stores-data | 5 |
| data-structures | 6 |
| devices | 5 |
| devices-incomings | 4 |
| devices-outgoings | 3 |
| incomplete-executions | 11 |
| enums | 16 |
| custom-functions | 7 |
| general | 1 |
| hooks | 11 |
| hooks-incomings | 4 |
| hooks-logs | 2 |
| keys | 6 |
| notifications | 4 |
| organizations | 36 |
| organizations-user-organization-roles | 3 |
| mms | 4 |
| remote-procedures | 1 |
| scenarios | 22 |
| scenarios-logs | 5 |
| scenarios-blueprints | 2 |
| scenarios-consumptions | 1 |
| scenarios-tools | 1 |
| scenarios-custom-properties-data | 5 |
| scenarios-folders | 5 |
| sdk-apps | 28 |
| sdk-apps-invites | 2 |
| sdk-apps-modules | 16 |
| sdk-apps-rpcs | 8 |
| sdk-apps-functions | 8 |
| sdk-apps-connections | 10 |
| sdk-apps-webhooks | 7 |
| sso-certificates | 1 |
| teams | 14 |
| teams-user-team-roles | 2 |
| templates | 8 |
| templates-public | 3 |
| users | 9 |
| users-me | 5 |
| users-api-tokens | 3 |
| users-user-team-roles | 3 |
| users-user-team-notifications | 3 |
| users-user-organization-roles | 4 |
| users-roles | 3 |
| users-unread-notifications | 1 |
| users-user-email-preferences-mailhub | 5 |

## Write safety breakdown

- Write-capable operations: `196`
- No-snapshot operations: `196`
- Destructive operations: `40`

These values come from the pinned operation metadata. For no-snapshot and destructive writes, extra acknowledgements are enforced.
