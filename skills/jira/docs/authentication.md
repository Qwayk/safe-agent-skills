# Authentication behavior

Basic auth sends the configured Atlassian email and API token through the HTTP client's auth field. OAuth sends the bearer token in the `Authorization` header. Neither value appears in plans, receipts, audit rows, JSON output, verbose timing, or HTTP error messages.

The CLI validates the destination before it creates an HTTP client. Basic credentials can go only to one root `https://your-domain.atlassian.net` Jira Cloud site. OAuth bearer tokens can go only through `https://api.atlassian.com/ex/jira/<cloudId>`. Arbitrary HTTPS hosts, extra API paths in the base URL, and custom production ports are refused.

`jira-safe auth check` calls the official `GET /rest/api/3/myself` endpoint. It proves only that the current credential can make that read. Jira permissions, product plans, OAuth scopes, and special app requirements still decide access for each operation.

Eight pinned operations expose OAuth without Basic auth and fail closed unless `JIRA_OAUTH_ACCESS_TOKEN` is active. Connect-only and Forge-only operations fail before HTTP regardless of configured Basic or bearer credentials.
