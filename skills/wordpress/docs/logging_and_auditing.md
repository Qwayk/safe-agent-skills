# Logging and auditing

WordPress work can touch real posts, media, captions, categories, and publishing state. Use audit logs when you need a record of what the command planned, applied, and verified.

Add `--log-file audit.jsonl` to write JSONL audit events. JSONL means one JSON object per line, which makes the log easy to inspect or process later.

Secrets are redacted.

Keep audit logs local unless you have reviewed them. They may include post titles, media URLs, IDs, and other site details.

## Example

Each line is a JSON object:

```json
{"ts": 1730000000.0, "event": "media.set", "payload": {"target": {"media_id": 123}, "apply": true, "changed": true, "verified": true}}
```

Tip: don’t commit audit logs to git; they often contain URLs and content details.
