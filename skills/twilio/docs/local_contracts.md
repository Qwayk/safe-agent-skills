# Local voice and webhook checks

These commands validate integration inputs on your machine. They need no Twilio credentials and make no provider request. They do not host a WebSocket or webhook, run an LLM, place a call, or decide compliance.

## ConversationRelay TwiML

Generate the only supported shape: `Response` containing `Connect` and one `ConversationRelay`. The `url` must be an absolute `wss://` URL. `Connect` may include a bounded relative path or absolute HTTP(S) `action` (no whitespace, query-only, fragment-only, or scheme-relative references) and `method` set to `GET` or `POST`; arbitrary TwiML and undocumented attributes are refused.

```bash
.venv/bin/qwayk-twilio-safe-agent-cli twiml conversation-relay-generate \
  --input-json examples/inputs/conversation-relay-generate.json
.venv/bin/qwayk-twilio-safe-agent-cli twiml conversation-relay-validate \
  --input-json examples/inputs/conversation-relay-validate.json
```

The validator covers the current documented ConversationRelay attributes, up to five `Language` children (each requiring `code` and allowing only `ttsProvider`, `voice`, `transcriptionProvider`, and `speechModel`), and up to 20 `Parameter` children, with a 16 KiB XML limit. Children have no text or descendants.

## ConversationRelay WebSocket messages

Validate an explicitly inbound or outbound message envelope. Current documented types include inbound `setup`, `prompt`, `dtmf`, `interrupt`, and `error`; outbound `text`, `play`, `sendDigits`, `language`, and `end`.

```bash
.venv/bin/qwayk-twilio-safe-agent-cli websocket conversation-relay-message-validate \
  --input-json examples/inputs/conversation-relay-message.json
```

Unknown fields, wrong direction/type pairs, and invalid URL, DTMF, boolean, or duration values are refused. This checks the message shape; it does not open a socket.

## Twilio webhook signatures

For form requests, the validator signs the full URL plus parameter names sorted uniquely, followed by each parameter's unique stringified value sorted lexically. Each parameter accepts one scalar or a bounded non-empty array of scalar strings, integers, floats, or booleans (up to 50 names and 20 values per name). Nested, empty, or oversized values are refused. For JSON requests, pass the raw body string and its SHA-256 digest; the full URL must include the matching `bodySHA256` query value. The Auth Token is read only from the environment variable named by `auth_token_env`; it is never accepted inline in JSON.

```bash
export TWILIO_LOCAL_AUTH_TOKEN='set-this-only-in-your-shell'
.venv/bin/qwayk-twilio-safe-agent-cli webhook twilio-signature-validate \
  --input-json examples/inputs/twilio-signature-validate.json
```

The example uses a placeholder signature and is safe to inspect; replace it with a signature from the request you are validating. Keep the token out of files and chat.

## Agent Connect metadata

```bash
.venv/bin/qwayk-twilio-safe-agent-cli agent-connect contract
```

This reports the local SDK/middleware metadata contract (channels and route names). It is descriptive metadata, not an Agent Connect server or REST operation. The command takes no input.
