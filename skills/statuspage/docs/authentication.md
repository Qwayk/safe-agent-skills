# Authentication

Statuspage authentication is meant to be local and boring: put the required key or token in your `.env` file, keep it out of chat, and run the safe check before asking an agent for real account data.

That matters because public incidents, components, maintenances, subscribers, and status summaries can contain account or business data. The auth check should prove the credential works without printing the secret value.

A good first auth check is: "Confirm the required Statuspage environment values are present, run the safe auth check, and tell me whether the credential works without showing the secret."

## Authentication notes

This tool is read-only and uses public Status API endpoints; it does not require authentication.

Note: private/trial pages may require an API key in an `Authorization` header, but that is intentionally out of scope for this tool.
