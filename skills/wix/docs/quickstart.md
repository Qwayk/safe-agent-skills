# Quickstart

From the Wix tool folder, install the command and create a private settings file.

~~~bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
wix-safe-agent-cli --version
wix-safe-agent-cli --env-file .env onboarding
~~~

Follow [Connect Wix](onboarding.md) to fill in the settings your task needs. Then check the connection.

~~~bash
wix-safe-agent-cli --env-file .env auth check
~~~

With an account key and account ID, the check lists up to five sites. Use the next command to list sites separately, including when you have both an account key and an app token.

~~~bash
wix-safe-agent-cli --env-file .env sites query --limit 5
~~~

For work on a single site, the app check shows its name and ID when Wix returns them. Use the same settings file to check which catalog that site uses.

~~~bash
wix-safe-agent-cli --env-file .env catalog-versioning get
~~~

If the site uses Catalog V3, run `stores-products-v3 query` with the same settings file to see products. For booking and contact examples, see [Commands](command_reference.md). If a change is needed, follow [Approvals and receipts](safety_model.md).
