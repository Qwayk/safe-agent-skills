# Authentication

Cloudinary authentication is meant to be local and checked before an agent works with assets, folders, backups, transformations, and media delivery settings. Keep credentials local, run the safe check first, and do not paste secrets into chat.

The goal is simple: prove the tool can reach the right account without exposing private values or making a live change.

A good first auth check is: "Check the Cloudinary credential setup, run the safe auth check, and stop before any account change."

## Product APIs

These areas use product environment credentials:
- `upload`
- `admin`
- `analyze`
- `live_streaming`
- `player_profiles`
- `video_config`

Set:
- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`

The tool sends HTTP Basic Auth for product-auth commands.

## Account APIs

These areas use account credentials:
- `provisioning`
- most `permissions` commands

Set:
- `CLOUDINARY_ACCOUNT_ID`
- `CLOUDINARY_ACCOUNT_API_KEY`
- `CLOUDINARY_ACCOUNT_API_SECRET`

The tool sends HTTP Basic Auth for account-auth commands.

## Public Permissions endpoints

Some permissions commands are public utilities and do not need credentials.
Example:

```bash
cloudinary-safe-agent-cli --output json operations permissions validatecedarpolicy \
  --body-json-file examples/validate-cedar-policy.sample.json
```

## Auth smoke test

```bash
cloudinary-safe-agent-cli --output json auth check
```

That command:
- calls product `GET /ping` when product credentials are present
- calls account provisioning `GET /sub_accounts` when account credentials are present
- reports missing values clearly when setup is incomplete

Secret values are redacted from errors and logs.
