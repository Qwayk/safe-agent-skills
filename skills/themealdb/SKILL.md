---
name: themealdb-safe-reader
description: Find meals, filter by one ingredient, category or cuisine, and open full recipes from TheMealDB.
---

Use `qwayk-themealdb-safe-agent-cli --output json` for the documented V1 reads. If the command is missing, follow the [quickstart](docs/quickstart.md).

Search for the meal the user asked for, or filter by one ingredient, category or area. Open a matching `idMeal` with `lookup id --meal-id` before presenting the recipe. Keep its ingredients, measures and directions together and credit TheMealDB. Link to `https://www.themealdb.com/meal/{idMeal}`. If a search is empty, tell the user or try a different term.

The built-in key is for development and education. Use a user's own key through local settings when their use requires it. Keep keys out of chat and logs. For uploads, multiple-ingredient filters or other supporter features, explain that the tool covers the [11 named reads](docs/command_reference.md). [TheMealDB terms](https://www.themealdb.com/terms_of_use.php)
