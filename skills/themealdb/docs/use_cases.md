# What you can do with TheMealDB

TheMealDB work usually starts with a very human question: what can I cook with this ingredient, what kind of meal do I want, or can you open one recipe and show the ingredients clearly?
If you need setup first, start with [Start with the free public key](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

No account is needed for the default free public key. The useful limit is that free V1 can filter by one ingredient, one category, or one area at a time, so the agent should not promise multi-ingredient recipe matching.

## Good jobs to give the agent

### Meal ideas from ingredients

- "Find meals with chicken breast and show a few options."
- "Show seafood meals, then open one recipe that looks easy."
- "Find vegetarian-looking ideas from the available categories and ingredients."
- "Give me one random dinner idea and list the main ingredients."
- "Find a dessert recipe and show the instructions in a clean checklist."

### Browse by category, area, or ingredient

- "List the available meal categories so I can choose what kind of food I want."
- "Show meals from the Canadian area."
- "List available ingredients and help me pick the closest match for chicken breast."
- "Filter by pasta, seafood, dessert, or another category and show the meal IDs."
- "Search by first letter when I only remember the start of a recipe name."

### Recipe lookup and planning

- "Look up meal 52772 and show ingredients, measurements, and instructions."
- "Open this meal ID and turn the recipe into a simple shopping list."
- "Compare three meal results and tell me which one looks easiest for a weeknight dinner."
- "Find a recipe by name, then open the exact meal record before summarizing."
- "Build a small dinner shortlist, but tell me when TheMealDB does not have enough detail."

## What the agent should show you

- The category, area, ingredient, name, first letter, or meal ID it used.
- A short list of matching meals before opening a full recipe.
- Ingredients and measurements together, not separated in a way that is hard to cook from.
- A plain warning when a search returns no meals or when the recipe record is incomplete.
- A reminder that free V1 does not support true multi-ingredient filtering.

## Good first recipe path

Start with one ingredient or category, pick one promising meal ID, then ask the agent to open that recipe and turn the ingredients and steps into something easy to cook from.
