# Quickstart

Want the short non-technical path first? Start with [What you can do](use_cases.md), [Connect your Instagram access](onboarding.md), and [How this skill stays safe](safety_model.md).

This page is the CLI path when you already want exact commands.

## 1. Install

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

## 2. Configure

Copy `.env.example` to `.env` and fill your Instagram app values.

If you want the tool to create the starter file for you, run:

```bash
instagram-api-tool onboarding
```

## 3. Build the login URL

```bash
instagram-api-tool auth login-url --scope instagram_business_basic
```

Add more scopes later only when the job needs them.

## 4. Exchange the auth code

After you sign in through the login URL and copy the `code` value from the redirect URL:

```bash
instagram-api-tool auth code exchange --code YOUR_CODE
```

That first run can show the plan first.
If the tool cannot save useful old token state first, finish the reviewed exchange with:

```bash
instagram-api-tool --apply --ack-no-snapshot auth code exchange --code YOUR_CODE
```

## 5. Smoke test

```bash
instagram-api-tool auth check
instagram-api-tool users me --fields user_id,username,account_type
```

Version output still works without `.env`:

```bash
instagram-api-tool --output json --version
```

## 6. First safe reads

List recent media:

```bash
instagram-api-tool media list --ig-user-id 17841400000000000 --fields id,caption,media_type,permalink --limit 10
```

List comments on one media item:

```bash
instagram-api-tool comments list --media-id 17900000000000000 --fields id,text,username,timestamp
```

Check account insights:

```bash
instagram-api-tool insights account get --ig-user-id 17841400000000000 --metric impressions,reach
```

## 7. Plan a write-capable change

Write-capable actions start as dry-run plans by default:

```bash
instagram-api-tool media publish --ig-user-id 17841400000000000 --creation-id 17890000000000000
```

## 8. Request apply only after review

Higher-risk write actions can need `--yes`, and some also need `--ack-irreversible`.
When no saved before-state exists, live apply also needs `--ack-no-snapshot`.

## 9. Need the full command list?

Use:

- [Command reference](command_reference.md)
- [Browse all docs](README.md)
