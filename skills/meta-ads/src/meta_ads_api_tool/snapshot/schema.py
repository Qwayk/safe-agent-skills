from __future__ import annotations

from dataclasses import dataclass


SCHEMA_VERSION = "1"


@dataclass(frozen=True)
class TableSpec:
    table_name: str
    join_keys: tuple[str, ...]


TABLE_SPECS: dict[str, TableSpec] = {
    "campaigns": TableSpec(table_name="campaigns", join_keys=("ad_account_id", "campaign_id")),
    "ad_sets": TableSpec(table_name="ad_sets", join_keys=("ad_account_id", "adset_id", "campaign_id")),
    "ads": TableSpec(table_name="ads", join_keys=("ad_account_id", "ad_id", "adset_id", "campaign_id", "creative_id")),
    "creatives": TableSpec(table_name="creatives", join_keys=("ad_account_id", "creative_id")),
    "creative_anatomy": TableSpec(table_name="creative_anatomy", join_keys=("ad_account_id", "creative_id")),
    "asset_urls": TableSpec(table_name="asset_urls", join_keys=("ad_account_id", "creative_id", "url_sha256")),
    "insights": TableSpec(table_name="insights", join_keys=("ad_account_id", "ad_id", "date_start", "date_stop")),
    "assets": TableSpec(table_name="assets", join_keys=("ad_account_id", "creative_id", "url_sha256")),
}


def join_keys_for_table(table_name: str) -> tuple[str, ...]:
    """
    Return join keys for a table name.

    Supports dynamic tables derived from base tables (example: insights_placement).
    """
    t = str(table_name or "").strip()
    if not t:
        return ()
    if t in TABLE_SPECS:
        return TABLE_SPECS[t].join_keys
    if t.startswith("insights_"):
        return TABLE_SPECS["insights"].join_keys
    return ()


def join_keys_by_table(tables: list[str] | None = None) -> dict[str, list[str]]:
    if tables is None:
        return {k: list(v.join_keys) for k, v in TABLE_SPECS.items()}
    out: dict[str, list[str]] = {}
    for t in tables:
        out[str(t)] = list(join_keys_for_table(t))
    return out
