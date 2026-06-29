# Troubleshooting

## Missing base URL

Fill `N8N_BASE_URL` in `.env`. It must end with `/api/v1`.

## Missing API key

Fill `N8N_API_KEY` in `.env`. Do not paste the key into chat.

## 401 or 403

The key is missing, invalid, expired, from the wrong instance, or lacks the needed n8n scope.

## Live write refused

This is usually expected. Live writes require a reviewed dry-run plan:

```bash
--apply --yes --plan-in plan.json
```

No-snapshot and high-risk writes need the extra approvals named in the plan.
