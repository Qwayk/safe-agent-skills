# Logging and auditing

Use `--log-file audit.jsonl` to write JSONL audit events.

Secrets are redacted.

## Example

Each line is a JSON object:

```json
{"ts": 1730000000.0, "event": "media.set", "payload": {"target": {"media_id": 123}, "apply": true, "changed": true, "verified": true}}
```

Tip: don’t commit audit logs to git; they often contain URLs and content details.
