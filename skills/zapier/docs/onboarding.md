# Onboarding

Create `.env` once, then verify that the tool can connect.

## 1) Copy env

```bash
cp .env.example .env
```

## 2) Fill secrets

Set at least `ZAPIER_ACCESS_TOKEN`. Leave `ZAPIER_BASE_URL` on the default unless Zapier documents a different host for your access program.

Optional:

- `ZAPIER_CLIENT_ID`
- `ZAPIER_CLIENT_SECRET`
- `ZAPIER_JWT`
- `ZAPIER_AI_ACTIONS_BASE_URL`
- `ZAPIER_TRIGGER_INBOX_BASE_URL`

## 3) Verify connection

```bash
qwayk-zapier-safe-agent-cli --output json auth check
```

If credentials are missing, the command returns a structured error without printing secret values.

## 4) First safe run

```bash
qwayk-zapier-safe-agent-cli --output json partner apps-list
```
