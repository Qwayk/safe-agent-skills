# What the Hacker News tool can read

The tool uses named read commands for the public Hacker News API. Posting, voting, editing, moderation and account actions are outside this API. It has no full-text search. The jobs list shows public job posts.

Story lists contain item IDs. A story can also contain the IDs of its comments. Open the items you need before you summarize a list or discussion. Use the links returned with the items to see their sources.

In JSON mode, each read returns a result or an error. The optional `--log-file` saves command events locally. The optional `onboarding` command can create a local settings file. [See the commands and options](command_reference.md).
