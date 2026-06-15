# Authentication

Open Library authentication is meant to be local and boring: put the required key or token in your `.env` file, keep it out of chat, and run the safe check before asking an agent for real account data.

That matters because public books, authors, editions, subjects, and ISBN data can contain account or business data. The auth check should prove the credential works without printing the secret value.

A good first auth check is: "Confirm the required Open Library environment values are present, run the safe auth check, and tell me whether the credential works without showing the secret."

## Authentication notes

No authentication is required.
Open Library endpoints used by this tool are public read-only endpoints.

Do not add or pass API keys.

If your environment blocks requests, use these public-friendly settings:

## Setup details

- Keep query volume small.
- Keep timeouts low when needed (`OPEN_LIBRARY_TIMEOUT_S`).
- Set `OPEN_LIBRARY_USER_AGENT_APP` and `OPEN_LIBRARY_CONTACT` so your requests are identifiable.
