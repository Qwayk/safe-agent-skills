# Architecture

## Main runtime modules

- `src/giantpanda_api_tool/cli.py`
  - parses commands and arguments,
  - validates input shapes,
  - dispatches command handlers.
- `src/giantpanda_api_tool/commands/onboarding.py`
  - creates `.env` when missing,
  - reports missing fields.
- `src/giantpanda_api_tool/commands/auth.py`
  - local token readiness check.
- `src/giantpanda_api_tool/commands/domains.py`
  - stats and add endpoints,
  - domain validation,
  - plan generation and apply binding.
- `src/giantpanda_api_tool/config.py`
  - fixed host,
  - env loading,
  - timeout and env-var precedence.
- `src/giantpanda_api_tool/http.py`
  - request client with redaction in verbose output.
- `src/giantpanda_api_tool/safety_state.py`
  - plan id generation,
  - private 0600 plan/receipt writes,
  - safe JSON read/write helpers.
- `src/giantpanda_api_tool/output.py`
  - JSON/text output formatting.
- `src/giantpanda_api_tool/errors.py`
  - shared controlled error types.
