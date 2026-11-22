# Preview a Reddit request offline

Run these commands from the Reddit tool folder with Python 3.12 or newer and the project’s `requests` package available. The command list comes from the files in this checkout.

```bash
PYTHONPATH=src python3 -m qwayk_reddit_safe_agent_cli --version
PYTHONPATH=src python3 -m qwayk_reddit_safe_agent_cli api ops list --section account
PYTHONPATH=src python3 -m qwayk_reddit_safe_agent_cli --no-artifacts api get-new --path subreddit=python --query limit=5
```

The last command previews the request for five recent posts.

To see what a post would send, use a sample title and text:

```bash
PYTHONPATH=src python3 -m qwayk_reddit_safe_agent_cli --no-artifacts api post-api-submit \
  --body sr=example --body kind=self --body 'title=Example title' \
  --body 'text=Example text' --body api_type=json
```

Look for `dry_run: true` in the output. The preview shows the action, the subreddit, and the text. These examples use no Reddit credentials and send no requests. See the [command reference](command_reference.md) for more options and the [test results](proof.md) for what the audit found.
