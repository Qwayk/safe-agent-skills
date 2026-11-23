# Change the Gemini tool

Start with [the code map](engineering_notes.md) and the [coverage list](api_coverage.md). Each operation has a named command tied to Google’s discovery files.

When changing behavior, update the code and check the normal CLI path. Keep the API key and private request text out of run logs. Keep command names and approval instructions aligned with the code.

When updating discovery, review both pinned API files, `official_inventory.json`, the operation registry, coverage, proof and tests together. Use named commands so an agent can see which operation it is about to call.
