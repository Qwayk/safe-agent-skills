# Quickstart

Find the Cloudflare zone for your website and see where its DNS records point. If you’re working with an agent, ask it to find your zone and show the records for your website.

## Install the CLI

Use Python 3.11 or later and run these commands in the Cloudflare tool folder. If `cloudflare-api-tool --version` already works, go straight to setup.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install .
cloudflare-api-tool --version
```

## Check setup

Follow the [setup guide](onboarding.md) to create a token that can read your account, zone, and DNS records. Run `cloudflare-api-tool --env-file .env onboarding` to create a private settings file, then fill in `CLOUDFLARE_API_TOKEN`. The same command works after installing outside the checkout. Keep the token, settings file, and private results out of prompts and Git.

```bash
cloudflare-api-tool --env-file .env --output json config check
```

## Find your account and zone

Replace `example.com` with your website's domain. If your project uses a different settings file, pass its path on every command.

```bash
cloudflare-api-tool --env-file .env --output json auth check
cloudflare-api-tool --env-file .env --output json accounts list
cloudflare-api-tool --env-file .env --output json zones resolve --name example.com
```

Check the account name and `zone.name` in the replies. If more than one zone matches, run `zones resolve` again with `--account-id` set to the account you mean to use.

## See where the DNS records point

Copy the `zone.id` from the zone reply and replace `ZONE_ID` in this command.

```bash
cloudflare-api-tool --env-file .env --output json dns records list --zone-id ZONE_ID
```

Look at each record's name, type, and content to see where it points. To focus on one name, add `--name www.example.com`. If you want to change a record, review the exact change before approving it. [DNS commands](command_reference.md#dns-records--scans) · [Approvals](safety_model.md)
