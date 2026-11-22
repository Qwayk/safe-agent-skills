# Meta Ads report presets

List the presets or inspect one before exporting:

```bash
meta-ads-api-tool --output json presets list
meta-ads-api-tool --output json presets show --preset ecom_core
```

| Preset | Use it for |
| --- | --- |
| `ecom_core` | Ecommerce results and a small set of account and creative fields. |
| `leadgen_core` | Lead results with spend and cost per action. |
| `creative_fatigue_daily` | Daily ad results and ranking fields for reviewing creative performance. |
| `maximal_firehose` | A wider export of fields. Check the manifest for fields your account cannot read. |

These commands read the packaged preset list without calling Meta. A preset gives [snapshot export](snapshot_export.md) its starting fields and settings. You can still choose the period, splits, and fields for the report you need.
