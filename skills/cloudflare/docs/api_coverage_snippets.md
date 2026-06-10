# Snippets (WAF) endpoint coverage (detailed)
This file is generated from Cloudflare's OpenAPI snapshot extracts.
- Snapshot (sha256): 73b3b8e9c0bca1cf59f22dd6e212eeaa433ea6b33370e7320af10b435d991824
- Source CSV: docs/cloudflare-api-docs/extracts/endpoints_snippets.csv

Regenerate:
```bash
python3 scripts/generate_snippets_coverage.py
```

Legend:
- Implemented: runnable via explicit per-operation `cloudflare-api-tool operations <area> <op_key>` commands (safe-by-default).

| Status | Method | Path | OperationId | Summary | Tags | Permissions | CLI command(s) | Notes |
|---|---|---|---|---|---|---|---|---|
| Implemented | GET | `/zones/{zone_id}/snippets` | `listZoneSnippets` | List zone snippets | Zone Snippets |  | cloudflare-api-tool operations snippets listzonesnippets |  |
| Implemented | DELETE | `/zones/{zone_id}/snippets/snippet_rules` | `deleteZoneSnippetRules` | Delete zone snippet rules | Zone Snippets |  | cloudflare-api-tool operations snippets deletezonesnippetrules | Implemented via allowlisted operation runner (plan by default; apply requires --apply --yes; best-effort verify). |
| Implemented | GET | `/zones/{zone_id}/snippets/snippet_rules` | `listZoneSnippetRules` | List zone snippet rules | Zone Snippets |  | cloudflare-api-tool operations snippets listzonesnippetrules |  |
| Implemented | PUT | `/zones/{zone_id}/snippets/snippet_rules` | `updateZoneSnippetRules` | Update zone snippet rules | Zone Snippets |  | cloudflare-api-tool operations snippets updatezonesnippetrules | Implemented via allowlisted operation runner (plan by default; apply requires --apply --yes; best-effort verify). |
| Implemented | DELETE | `/zones/{zone_id}/snippets/{snippet_name}` | `deleteZoneSnippet` | Delete a zone snippet | Zone Snippets |  | cloudflare-api-tool operations snippets deletezonesnippet | Implemented via allowlisted operation runner (plan by default; apply requires --apply --yes; best-effort verify). |
| Implemented | GET | `/zones/{zone_id}/snippets/{snippet_name}` | `getZoneSnippet` | Get a zone snippet | Zone Snippets |  | cloudflare-api-tool operations snippets getzonesnippet |  |
| Implemented | PUT | `/zones/{zone_id}/snippets/{snippet_name}` | `updateZoneSnippet` | Update a zone snippet | Zone Snippets |  | cloudflare-api-tool operations snippets updatezonesnippet | Implemented via allowlisted operation runner (plan by default; apply requires --apply --yes; best-effort verify). |
| Implemented | GET | `/zones/{zone_id}/snippets/{snippet_name}/content` | `getZoneSnippetContent` | Get a zone snippet content | Zone Snippets |  | cloudflare-api-tool operations snippets getzonesnippetcontent | Sensitive read. Requires --apply and --out; file-only output (never printed). |
