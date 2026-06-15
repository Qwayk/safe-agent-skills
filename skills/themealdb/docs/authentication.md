# Authentication

TheMealDB does not need a private account connection for the default public recipe lookups. The default key is public, and the useful first check is simply whether the API is reachable from your machine.

If you use your own TheMealDB key, keep it in `.env` and do not paste it into chat. The safe check should prove the key works without printing the value.

A good first auth check is: "Confirm whether TheMealDB is using the default public key or a custom key, run the safe check, and tell me whether recipe lookup is reachable."

## Authentication notes

The default setup does not need a secret.

## Default mode

- TheMealDB free V1 public key `1` is used by default
- That value lives in `.env.example`
- `onboarding` copies it into `.env` for you when needed

## Optional custom key

If you have your own TheMealDB key, set:

```text
THEMEALDB_API_KEY=your_key_here
```

Keep it in `.env`. Do not paste it into chat.

## Health check

Use this read-only command:

```bash
qwayk-themealdb-safe-agent-cli auth check
```

It uses `categories.php` as the probe endpoint.
