# Presets reference

Presets are **built-in, packaged configurations** that define a starting point for common reporting/export workflows.

- They are **data-driven** (loaded from a packaged JSON file), so the tool can evolve the preset catalog without changing command code.
- Presets are **read-only metadata** in this phase: `presets list/show` do not call the Meta Graph API.
- Presets are meant to be used by future higher-level commands (example: `snapshot export`) to decide which surfaces to fetch and which default fields/params to use.

## Commands

- List all presets:
  - `meta-ads-api-tool presets list`
- Show a preset (full surfaces config):
  - `meta-ads-api-tool presets show --preset <id>`

## Included presets (built-in)

The exact catalog may change over time; use `presets list` for the current list.

- `ecom_core`
  - Ecommerce-focused ad-level performance metrics + minimal inventory context.
- `leadgen_core`
  - Lead-gen-focused ad-level performance metrics + minimal inventory context.
- `maximal_firehose`
  - A maximal preset intended for analysis/snapshot exports. May require additional permissions.
- `creative_fatigue_daily`
  - Daily ad-level performance + rankings for fatigue/diagnostic analysis.

## Preset schema (v1)

Top-level payload:

- `schema_version` (string; currently `"1"`)
- `presets` (array of preset objects)

Each preset object:

- `id` (string; stable identifier)
- `label` (string; human-friendly name)
- `description` (string; what it’s for)
- `use_case_tags` (string[])
- `surfaces` (object)
  - The `surfaces` object is a map of surface name → surface config.
  - Surface config values are intentionally flexible in v1 (they are treated as data).

## Notes

- Preset defaults are **starting points**, not guarantees. Some fields may be unavailable depending on:
  - token permissions/scopes
  - account type / feature availability
  - API version behavior
- Many `snapshot export` flags are designed to **override preset defaults** (time range, breakdowns, fields), so an agent can generate consistent packs without editing the preset catalog.
- This tool remains **GET-only**. Presets must not introduce any write flows.
