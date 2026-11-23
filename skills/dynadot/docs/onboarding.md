# Connect your Dynadot account

In Dynadot, open **Tools → API** and copy the key for the account you want to connect. If you have a stable IP address, use Dynadot's IP settings to limit where the key can be used. [Dynadot's setup guide](https://www.dynadot.com/help/question/find-API-settings)

Create a private settings file:

```bash
dynadot-api-tool --output json --env-file dynadot.env onboarding
```

Open `dynadot.env` and fill in `DYNADOT_API_KEY`. The starter file points to the production API at `https://api.dynadot.com/api3.json`. For a sandbox key, use `https://api-sandbox.dynadot.com/api3.json`. The default timeout is 30 seconds. Set `DYNADOT_TIMEOUT_S` if you need a different timeout.

```bash
dynadot-api-tool --output json --env-file dynadot.env auth check
dynadot-api-tool --output json --env-file dynadot.env domains list --page 1
```

Use the same `--env-file` path on later commands. The default is `.env`. Values set in your shell take priority over the main file. Keep your key out of chat, Git, and shell arguments. For a guided move, pass the sender's file with `--env-file`, the receiver's with `--receiver-env-file`, and use the receiver's exact [Push Username](https://www.dynadot.com/community/help/question/what-is-push-username). The receiver file is read on its own.

## If a command stops

- If Dynadot rejects the key, check which account and API address your file uses and whether your current IP has access.
- If an availability lookup fails, use `domains availability`. It retries unresolved names. Keep one domain per request on a Regular Account, with the default 1.05 seconds between request starts.
- If Dynadot doesn't list an external provider's nameservers in your account, check the nameservers with that provider. The Dynadot list gives a warning by default.
- If Dynadot says “Please use your account firstly,” check that the sender account is unlocked for the move. If Dynadot says a domain needs renewal, check its expiration before deciding how to proceed.
- If the receiver can't accept a `.us` domain, check the receiver's US application and nexus settings.
- After a write error, check the current domain, order, or transfer before repeating anything. See [how to read the result](safety_model.md).
