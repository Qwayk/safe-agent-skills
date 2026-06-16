# Jobs and batches

Reddit jobs should stay explicit and reviewable. The shipped API coverage is based on named Reddit commands, not an open-ended batch system.

Some generic template helpers still exist in the repo copy. They are not part of Reddit API coverage and should not be presented as the normal way to work with Reddit.

Current helper commands:

- `qwayk-reddit-safe-agent-cli jobs run --file jobs.csv`
- `qwayk-reddit-safe-agent-cli demo read`
- `qwayk-reddit-safe-agent-cli demo write --selector demo-resource`

For real Reddit work, prefer the command reference and API coverage pages. Ask the agent to name the subreddit, account, endpoint, and planned action before any write-like operation.
