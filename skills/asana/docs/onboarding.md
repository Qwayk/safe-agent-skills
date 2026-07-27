# Set up the Asana connection

The simplest setup uses an Asana personal access token. It gives the tool the same API access as the Asana user who created it, so use a user with only the access needed for the work.

## 1. Confirm the CLI runs

From the tool folder:

```bash
.venv/bin/asana-safe --version
```

For a fresh source checkout, create the environment first:

```bash
/path/to/python3.12 -m venv .venv
.venv/bin/python -m pip install -e .
```

## 2. Create the private settings file

Run:

```bash
.venv/bin/asana-safe --env-file .env onboarding
```

If `.env` does not exist, the command creates a placeholder file with owner-only permissions. It never creates or retrieves a token.

## 3. Add an issued bearer token

Create a personal access token from Asana's developer console, or obtain an approved OAuth access token or service-account token from the person who manages that integration. Put only the token value after `ASANA_ACCESS_TOKEN=` in `.env`:

```dotenv
ASANA_ACCESS_TOKEN=
ASANA_TIMEOUT_S=30
```

Do not paste the token into chat, commit `.env`, or put it in command arguments.

This tool accepts already-issued bearer tokens. It does not register an OAuth app, exchange an authorization code, refresh or revoke a token, create a service account, or provision SCIM.

## 4. Check the connection

```bash
.venv/bin/asana-safe --env-file .env auth check
```

Success returns the current user's GID, name, and resource type. It does not return the token or the user's email.

## 5. Get the first useful result

```bash
.venv/bin/asana-safe --env-file .env api get-workspaces
```

You now know which workspaces the token can see. Continue with the [Quickstart](quickstart.md) or ask your agent to review one of those workspaces without making changes.

## Access limits

Asana can still refuse a fixed command because of the user's workspace permissions, account plan, OAuth scopes, service-account status, or feature availability. Inspect an operation with `commands show` to see its official OAuth scope guidance, then change the account or token outside this tool if needed.
