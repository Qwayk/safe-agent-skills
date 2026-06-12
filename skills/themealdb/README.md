# TheMealDB

**Capability:** Read-only

TheMealDB is useful when you want quick recipe ideas from a structured public recipe database instead of asking an agent to guess from memory. It works well for meal inspiration, ingredient-based ideas, category browsing, and simple recipe lookups.

This skill lets an agent search meals by name, browse categories, list areas and ingredients, look up one meal by ID, filter by one category, area, or ingredient, and fetch one random meal idea.

No account is needed for the default setup. The tool uses TheMealDB's public V1 development key unless you choose to add your own key.

A good first ask is: "Find meal ideas with chicken breast, show a few options, and open one recipe with ingredients and instructions."

## Start here first

- Want ideas for real recipe work? [What you can do with TheMealDB](docs/use_cases.md)
- Need setup? [Start with the free public key](docs/onboarding.md)
- Want the safety story first? [How this skill stays read-only](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Browse meal categories, areas, and ingredients.
- Search meals by name or first letter.
- Find meals that match one ingredient, category, or area.
- Look up a full recipe by meal ID.
- Ask for one random meal idea when you need inspiration.

## What access this skill needs

- No account for the default free V1 public API.
- No secret for the default public development key `1`.
- Optional custom TheMealDB API key if you have one and want to use it locally.

## Install and first run

Install slug: `themealdb`

Ask your agent to install the `themealdb` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@themealdb -g -y
```

Then try a safe first ask like:

```text
Find meal ideas with chicken breast, show a few options, and open one recipe with ingredients and instructions.
```

## How this skill stays safe

- It is read-only by design.
- It uses TheMealDB free V1 public endpoints.
- It has named commands only, not a raw request bridge.
- It does not upload, edit, or delete anything.
- Custom API keys are redacted from errors and verbose HTTP logs.

## What it covers today

This skill covers:

- meal search by name or first letter
- meal lookup by ID
- one random meal
- category, area, and ingredient lists
- filtering by one ingredient, one category, or one area

## What happens before live changes

There are no live changes in this skill. It reads public recipe data and returns structured output.

## What proof it leaves behind

- Normal reads return machine-readable JSON you can review or save.
- The proof pack shows smoke commands and example outputs.
- The API coverage page lists the free V1 endpoints the tool supports.
- Tests check command behavior, output shape, and redaction.

## Limits

- Free V1 only.
- Premium V2 endpoints are not included.
- Multi-ingredient filtering is not available in the free V1 API.
- Recipe data comes from TheMealDB and can vary in completeness.

## Helpful docs

- [Browse all TheMealDB docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)
