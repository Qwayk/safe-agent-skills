# Quickstart

In the X tool folder, install the command in a Python virtual environment.

~~~bash
python3 -m venv .venv
.venv/bin/python -m pip install .
source .venv/bin/activate
x-api-tool --version
x-api-tool api ops list
~~~

These last two commands run without an X account or API calls. To check the settings and see whether a local account token exists, run:

~~~bash
x-api-tool --env-file .env auth check
~~~

After [connecting your X account](onboarding.md), approve the account check and sample read before running them. X may charge for either call. Use the ID returned by the first command in place of `ACCOUNT_ID`.

~~~bash
x-api-tool --live auth check
x-api-tool --live api getUsersPosts --auth user --path id=ACCOUNT_ID --query max_results=5
~~~

The account check shows the username and ID. If those belong to the account you meant to use, you can ask for its recent posts or use the same ID with `getUsersMentions`. If you need to post or message someone, use the steps in [Commands](command_reference.md).
