# Diagnosis reference

`snapshot analyze diagnose` is the default offline optimization workflow:

- export `optimization_pack_v1`
- run `google-ads-api-tool snapshot analyze diagnose --pack-dir ./out/google-ads-pack`
- review the JSON findings
- use official Google Ads docs for the highest-importance categories before planning live changes

## Output contract

Top-level keys:
- `ok`
- `pack_dir`
- `summary`
- `data_quality`
- `tables_used`
- `tables_missing`
- `findings`
- `actions`
- `notes`

Each `finding` has stable keys:
- `id`
- `level`
- `category`
- `scope`
- `support_route`
- `entity_refs`
- `evidence`
- `explanation`
- `recommended_next_step`
- `recommended_doc_queries`
- `requires_human_review`

`actions` is grouped into:
- `read_only_next_steps`
- `plan_first_write_candidates`
- `human_review_required`

## Finding categories

- `budget_pressure`
- `rank_pressure`
- `mixed_pressure`
- `low_volume_or_targeting_limited`
- `quality_score_issue`
- `rsa_issue`
- `search_term_cleanup`
- `keyword_pause_candidate`
- `landing_page_review`
- `placement_review`
- `tracking_risk`
- `recommendation_review`

## Built-in thresholds

These are hard-coded in v1 so the workflow stays simple:

- minimum impressions for pressure diagnosis: `50`
- high lost impression share by budget or rank: `0.20`
- low search impression share: `0.20`
- low Quality Score: `5`
- minimum Quality Score signal impressions: `5`
- high-confidence Quality Score impressions: `10`
- high-confidence Quality Score clicks: `2`
- high-confidence Quality Score spend: `5,000,000` micros
- low optimization score: `0.80`
- tracking risk minimum clicks: `15`
- tracking risk minimum spend: `10,000,000` micros
- poor RSA strength: `POOR` or `AVERAGE`

## Interpretation notes

- `diagnose` is offline-only. It reads the exported pack and does not call Google Ads.
- Recommendation findings are review-only. They exist to frame a plan, not to auto-apply changes.
- If `tables_missing` is non-empty, some finding families were skipped because the pack lacked those tables.
- `analysis_pack_max_v1` can still be diagnosed, but the best results come from `optimization_pack_v1` because it includes campaign pressure, keyword quality, conversion-action, and recommendation tables directly.
- `quality_score_issue` now skips empty-signal rows and only marks `high` when the keyword has stronger evidence.
- expensive one-click QS rows now stay `medium` unless they also have stronger traffic signal.
- `rsa_issue` evidence now comes from aggregated `ad_daily_metrics`, not just ad metadata rows.
- `keyword_pause_candidate` uses `support_route = books_or_human`, so the final decision should not rely on Google Help alone.

## What the agent should do next

- For `budget_pressure` or `mixed_pressure`: build a no-apply budget review first.
- For `rank_pressure`, `quality_score_issue`, or `rsa_issue`: review search intent, ad relevance, and landing-page fit before planning live edits.
- For `tracking_risk`: check conversion actions and primary-goal setup before trusting zero-conversion reads.
- For `recommendation_review`: inspect recommendation types and auto-apply context, but keep the next step as review or plan-only.
- For `keyword_pause_candidate`: use books or human review for the final decision, because this is a judgment call rather than a Google Help mechanics question.
