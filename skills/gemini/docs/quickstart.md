# List models and count tokens

[Install and connect the CLI](onboarding.md). From the same folder, list the models your key can use:

```bash
.venv/bin/gemini-api-tool --output json models list
```

Choose a model from the list. Save your prompt in `request.json` in this form:

```json
{"contents":[{"parts":[{"text":"Give me a one-sentence summary of this request."}]}]}
```

Replace `models/MODEL_FROM_LIST` with the model’s name:

```bash
.venv/bin/gemini-api-tool --output json models count-tokens \
  --model models/MODEL_FROM_LIST --request-json request.json
```

If you want to generate an answer, check the model’s price and approve the request first:

```bash
.venv/bin/gemini-api-tool --output json models generate-content \
  --model models/MODEL_FROM_LIST --request-json request.json --ack-spend-money
```

Keep `request.json` private if it contains customer text or other sensitive information. See [examples for account changes](command_reference.md#review-and-send-a-change).
