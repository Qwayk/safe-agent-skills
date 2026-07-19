# Xero skill wrapper

The tracked wrapper lives at `skills/xero/SKILL.md`. It tells an agent when to use this CLI and preserves the same auth, tenant, privacy, and write-review rules as the source tool.

The wrapper must:

- translate a normal Xero request into one or more fixed commands
- inspect `inventory show` when the exact input or access rule is unclear
- connect with minimum scopes and select the exact tenant before tenanted reads
- send full sensitive results to a protected local file
- create and explain a saved plan before every write
- ask for the separate approvals required by that plan
- apply only the exact saved plan and read the receipt honestly
- state when a family is regional, paid, partner-only, callback-only, superseded, or unavailable

The wrapper must never accept or reveal secrets, claim live behavior without evidence, use browser automation, add a raw request escape hatch, or treat an accepted Xero response as a stronger business outcome.
