# Authentication

The Gemini API uses an API key in the `x-goog-api-key` header for normal REST calls.

Set the key locally:

```dotenv
GEMINI_API_KEY=replace-with-your-local-key
```

The tool reads `.env` by default. OS environment variables override `.env`.

Do not commit `.env`, paste the key into chat, or put it in examples. `auth check` only reports whether a key is present.
