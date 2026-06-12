from __future__ import annotations

from ..schema_registry import load_schema_registry


def cmd_schema_summary(args, ctx) -> int:
    _ = args
    schema = load_schema_registry()
    out = {
        "ok": True,
        "command": "schema.summary",
        "api_version": schema.get("api_version_header") or None,
        "counts": {
            "queries": schema.get("query_count", 0),
            "mutations": schema.get("mutation_count", 0),
            "webhook_topics": schema.get("webhook_topic_count", 0),
        },
        "fetched_utc": schema.get("fetched_utc"),
    }
    ctx["audit"].write("schema.summary", out)
    ctx["out"].emit(out)
    return 0


def cmd_schema_queries(args, ctx) -> int:
    _ = args
    schema = load_schema_registry()
    out = {
        "ok": True,
        "command": "schema.queries",
        "count": schema.get("query_count", 0),
        "items": [{"name": op.name, "deprecated": False} for op in schema.get("query_fields", [])],
    }
    ctx["audit"].write("schema.queries", out)
    ctx["out"].emit(out)
    return 0


def cmd_schema_mutations(args, ctx) -> int:
    _ = args
    schema = load_schema_registry()
    out = {
        "ok": True,
        "command": "schema.mutations",
        "count": schema.get("mutation_count", 0),
        "items": [{"name": op.name, "deprecated": False} for op in schema.get("mutation_fields", [])],
    }
    ctx["audit"].write("schema.mutations", out)
    ctx["out"].emit(out)
    return 0


def cmd_schema_webhook_topics(args, ctx) -> int:
    _ = args
    schema = load_schema_registry()
    out = {
        "ok": True,
        "command": "schema.webhook_topics",
        "count": schema.get("webhook_topic_count", 0),
        "items": schema.get("webhook_topics", []),
    }
    ctx["audit"].write("schema.webhook_topics", out)
    ctx["out"].emit(out)
    return 0
