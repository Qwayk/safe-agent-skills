# Authentication

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
