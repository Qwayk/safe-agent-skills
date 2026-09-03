# Engineering notes

These notes record repository-level implementation evidence. They are deliberately separate from live-provider claims.

## 2026-09-02 — Inventory boundary and verification

- The shipped `openapi.json` is the source snapshot for the generated inventory.
- Its SHA-256 is `a82cfab5db1adc845ac5890bf536552a2f2c75836bdebff8019a80c1bf647cd1`.
- The inventory contains 388 HTTP operations: 367 stable implemented and 21 deprecated.
- Seven manual WebSocket surfaces are tracked outside the HTTP count: six plan-only commands and one callback-only reverse connection. One Twilio webhook is callback-only, and one authentication row is docs-only.
- Local tests and deterministic plan examples do not establish current live-provider behavior. Live behavior remains unverified for the current account.
