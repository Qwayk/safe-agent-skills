# References

The generated inventory is grounded in the pinned provider snapshot `openapi.json`.

- Official API reference: https://elevenlabs.io/docs/api-reference/introduction
- Official authentication: https://elevenlabs.io/docs/api-reference/authentication
- Official streaming guidance: https://elevenlabs.io/docs/api-reference/streaming
- Official speech-to-text realtime WebSocket: https://elevenlabs.io/docs/api-reference/speech-to-text/v-1-speech-to-text-realtime
- Official ElevenAgents conversation WebSocket: https://elevenlabs.io/docs/eleven-agents/api-reference/eleven-agents/websocket
- Official text-to-speech WebSocket: https://elevenlabs.io/docs/api-reference/text-to-speech/v-1-text-to-speech-voice-id-stream-input
- Official text-to-speech multi-context WebSocket: https://elevenlabs.io/docs/api-reference/text-to-speech/v-1-text-to-speech-voice-id-multi-stream-input
- Official text-to-dialogue WebSocket: https://elevenlabs.io/docs/api-reference/text-to-dialogue/ttd-websocket
- Official text-to-dialogue multi-context WebSocket: https://elevenlabs.io/docs/api-reference/text-to-dialogue/ttd-multi-websocket
- Official speech-engine upstream WebSocket: https://elevenlabs.io/docs/api-reference/speech-engine/speech-engine-upstream
- Official native Twilio integration: https://elevenlabs.io/docs/eleven-agents/phone-numbers/twilio-integration/native-integration/
- Official Twilio register-call integration: https://elevenlabs.io/docs/eleven-agents/phone-numbers/twilio-integration/register-call
- Official Twilio conversation-initiation webhook: https://elevenlabs.io/docs/eleven-agents/phone-numbers/twilio-integration/customising-calls

Snapshot SHA-256: `a82cfab5db1adc845ac5890bf536552a2f2c75836bdebff8019a80c1bf647cd1`.

The snapshot yields 388 HTTP operations: 367 stable implemented and 21 deprecated. The manual ledger adds seven WebSocket surfaces (six plan-only commands and one callback-only reverse connection), one callback-only Twilio webhook, and one docs-only authentication row. These sources document interface shape; live provider behavior is unverified for the current account.
