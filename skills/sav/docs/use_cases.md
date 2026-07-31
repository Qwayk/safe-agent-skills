# What you can do with SAV Domain APIs

Start with account information that SAV exposes as a read:

- "List active domains now."
- "Show the most recent auction sales."
- "Show recent premium sales."
- "Show current domain pricing."

For a domain change, ask the agent to prepare a plan first:

- "Prepare a plan to turn auto-renewal on for example.com."
- "Show me the plan to change example.com's nameservers to ns1.example.net and ns2.example.net."
- "Prepare a sale-price update for example.com, but do not send it."
- "Prepare a redacted plan to update the registrant contact."
- "Prepare the transfer-code submission locally without showing the code in chat."
- "Prepare the transfer submission from a local mode-`0600` file, then apply from the reviewed plan without retyping the code."

The agent should explain the target, requested values, missing before-state snapshot, and lack of rollback before asking whether to apply. This tool does not cover domain registration, auction bidding, browser automation, or any SAV action outside the published 12-operation collection.
