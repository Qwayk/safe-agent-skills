# threads-api-tool

Safe CLI for the official Threads Graph API.

This tool ships an explicit command surface for Threads auth, profiles, posts, replies, mentions, insights, keyword search, locations, and oEmbed. It stays inside the documented Threads product line. Write-capable commands currently create dry-run plans and require explicit no-snapshot approval when no saved snapshot is available.

Start here:
- Non-technical setup: `docs/onboarding.md`
- Technical setup: `docs/quickstart.md`
- Full command list: `docs/command_reference.md`
- Endpoint coverage: `docs/api_coverage.md`
- Proof and verification status: `docs/proof.md`

Quick examples:

```bash
threads-api-tool --output json --version
threads-api-tool --output json auth check
threads-api-tool --output json profiles me
threads-api-tool --output json posts list-owned --threads-user-id <id>
threads-api-tool --output json posts list-public --username <handle>
threads-api-tool --output json replies list --threads-media-id <id>
threads-api-tool --output json search keyword --q <term>
threads-api-tool --output json locations search-query --q <query>
threads-api-tool --output json oembed get --url <threads_url>
```

Write planning flow:

```bash
threads-api-tool --output json --plan-out /tmp/create-text.plan.json posts create-text --threads-user-id <id> --text "Draft"
threads-api-tool --output json --apply posts create-text --threads-user-id <id> --text "Draft"
```

When required approval is missing, the tool stops safely before provider writes or receipt output. Approved supported writes proceed and emit receipts that record the no-snapshot limit.
