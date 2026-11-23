# Connect your SAV account

Get the API key for the account you want to use. SAV's API docs ask you to have SAV allow the IP address that will send requests. It lists `support@sav.com` for that setup. [SAV API documentation](https://documenter.getpostman.com/view/9688716/TzzANHFJ)

From the tool folder, make a private settings file. This command preserves an existing file:

```bash
(set -C; umask 077; cat .env.example > .env)
```

Open `.env` and fill in `SAV_API_KEY`. Keep the file out of Git and the key out of chat and command arguments. Use `chmod 600 .env` if the file is already there and needs private permissions.

```bash
sav --output json --env-file .env --version
sav --output json --env-file .env domains active
```

Use the same `--env-file` on later commands. Without it, the tool looks for `.env`. A `SAV_API_KEY` set in the shell takes priority over the file. If the first account read fails, check that you selected the intended file and key, and that SAV allows your current IP.

The default timeout is 30 seconds. Set `SAV_TIMEOUT_S` in the environment or file, or pass `--timeout-s` on a command. Use a finite positive number.

Plans, receipts, and the local signing key go into private folders under `.state/` beside the selected settings file. The tool uses `0700` for these folders and `0600` for the files. Custom paths for plans and receipts stay under the settings file's parent folder and use a private parent directory. See [Quickstart](quickstart.md) for the private transfer-code file.
