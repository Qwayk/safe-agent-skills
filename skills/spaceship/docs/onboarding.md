# Connect Spaceship without sharing secrets

You need a Spaceship API key and API secret. Create and manage those values in Spaceship's API Manager; this tool does not create, rotate, or delete credentials.

## Create the local file

From the tool folder:

```bash
cp .env.example .env
```

Open `.env` and fill these two values:

```text
SPACESHIP_API_KEY=<your key>
SPACESHIP_API_SECRET=<your secret>
```

Keep `.env` local and never paste either value into chat, a plan, a receipt, or a Git commit. The production host is fixed in code to `https://spaceship.dev/api`; there is no general base-URL setting.

You can also let the command create `.env` from the example:

```bash
qwayk-spaceship-safe-agent-cli --output json onboarding
```

## Check the local setup

```bash
qwayk-spaceship-safe-agent-cli --output json auth check
```

This checks that both values are present and reports the fixed host. It does not send a provider request or prove that the key has the required Spaceship scopes.

## Run the first real read

```bash
qwayk-spaceship-safe-agent-cli --output json domains list --take 10
```

If Spaceship rejects the request, check that the credentials are active and have the permissions required for that operation. The error output must never contain the key or secret.
