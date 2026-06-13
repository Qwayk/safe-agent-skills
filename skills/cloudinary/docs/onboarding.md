# Connect your Cloudinary account

Cloudinary needs local cloud credentials before an agent can inspect assets, folders, tags, transformations, or media account data.

Keep the setup files private. Do not paste `.env` values, API keys, client secrets, OAuth files, or saved token files into chat.

After setup, start with an account check or small asset search before asking for uploads, deletes, or file writes.

## Step 1: Create or check `.env`

Run:

```bash
cloudinary-safe-agent-cli onboarding
```

The onboarding command will:

- if `.env` does not exist, it copies `.env.example` to `.env`
- checks which required Cloudinary values are still missing
- prints the next command to run: `cloudinary-safe-agent-cli --output json auth check`

Use `--no-write-env` if you only want the checklist:

```bash
cloudinary-safe-agent-cli onboarding --no-write-env
```

Fill these product values for Upload, Admin, Analyze, Video Live Streaming, Player Profiles, and Video Config:
- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`

Fill these account values for Provisioning and most Permissions commands:
- `CLOUDINARY_ACCOUNT_ID`
- `CLOUDINARY_ACCOUNT_API_KEY`
- `CLOUDINARY_ACCOUNT_API_SECRET`

Change the hosts only if Cloudinary gave you a different regional host:
- `CLOUDINARY_PRODUCT_API_HOST`
- `CLOUDINARY_ACCOUNT_API_HOST`

Then run:

```bash
cloudinary-safe-agent-cli --output json auth check
```

## First useful check

After the connection works, ask the agent to run a small account check or asset search. Confirm it is looking at the right cloud before asking for uploads, deletes, or downloads.
