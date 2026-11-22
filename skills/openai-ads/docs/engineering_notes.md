# Engineering notes

The CLI creates its named Advertiser API commands from the [packaged inventory](../src/qwayk_openai_ads/data/official_inventory.json). The [saved API spec](specs/openai-ads-openapi.json) is the July 6 reference. [API coverage](api_coverage.md) explains the difference between that snapshot and the current command list.

- [`cli.py`](../src/qwayk_openai_ads/cli.py) reads flags and builds commands. [`config.py`](../src/qwayk_openai_ads/config.py) chooses settings.
- [`api.py`](../src/qwayk_openai_ads/commands/api.py) handles Advertiser API requests and approvals. [`measurement.py`](../src/qwayk_openai_ads/commands/measurement.py) handles conversion sends and local measurement guidance.
- [`http.py`](../src/qwayk_openai_ads/http.py) sends requests. [`runs.py`](../src/qwayk_openai_ads/runs.py) saves run history and receipts.
- [`sanitize.py`](../src/qwayk_openai_ads/sanitize.py) protects private values in output. Keep private data out of tests and examples.

Test changes with simulated responses. Check the account read, approval checks, one send after an approved plan, and a receipt when the outcome is unknown. Use the [test results](proof.md) to see what was verified from a fresh install.
