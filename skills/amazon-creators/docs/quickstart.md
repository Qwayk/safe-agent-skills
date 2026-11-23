# Run your first Amazon Creators search

From the installed skill folder, use Python 3.12 or newer:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/amazon-creators-api-tool --version
source .venv/bin/activate
```

Follow [the account setup](onboarding.md) to create a private settings file and get a token. Add `--env-file /path/to/account.env` to each command below if you picked a separate account file.

Preview a small search and review the marketplace, tracking tag, and query:

```bash
.venv/bin/amazon-creators-api-tool search --keywords "office headphones" --item-count 2 --plan-out search-preview.json
```

After approval, send the same request:

```bash
.venv/bin/amazon-creators-api-tool search --keywords "office headphones" --item-count 2 --plan-in search-preview.json --apply
```

The reply includes the products Amazon returned, any product links, and the total match count when Amazon supplies it. A partial reply lists the products it found and the errors it received. The total is the number Amazon says matched the search. The rows are the page you asked for.

See [the command guide](command_reference.md) for item details, variations, and product categories.
