# Maintaining the Spaceship command inventory

Change the tool only when official Spaceship documentation changes the chosen External API boundary.

Start with the pinned official source and update the operation registry, parser, coverage row, command reference, safety mapping, and behavior tests together. Every provider operation must remain a fixed named command; do not add any escape surface around the reviewed operation-specific safety rules.

For reads, prove the fixed host, encoded path, redaction, status handling, and one-object JSON output. For writes, prove planning without credentials, exact apply-from-plan comparison, required acknowledgements, available preflight checks, drift refusal, exactly one provider write, 202 or 204 handling, honest readback status, and redacted receipts.

Run the complete Python 3.12+ suite, Ruff, mypy, compileall, source build, archive inspection, and clean installed-wheel checks. Then read the human front-door docs and wrapper manually; tests do not prove that the writing is useful.
