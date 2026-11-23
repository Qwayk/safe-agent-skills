# Find and open your first recipe

Open a terminal in the skill folder that contains `pyproject.toml`. Use Python 3.12 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
qwayk-themealdb-safe-agent-cli --output json search name --name "Arrabiata"
```

For development or education, the tool uses TheMealDB's built-in test key. The search works without a settings file. Look for `"ok": true` and read the `meals` list. Use the result's `idMeal` to open the full recipe.

```bash
qwayk-themealdb-safe-agent-cli --output json lookup id --meal-id 52771
```

This ID opens Spicy Arrabiata Penne. [See the commands and optional settings](command_reference.md).
