# Troubleshooting

When TheMealDB does not return what you expected, start by checking the target, the API response, and the exact JSON error. For this public read tool, most fixes are about the request itself: a missing ID, an empty result, a changed public record, a timeout, or an API root override.

Do not guess from an empty list or a `null` result. Ask the agent to fetch the actual record, show the error type, and explain whether the data is missing or the request needs to change.

A good first troubleshooting ask is: "Read the TheMealDB error, explain what failed in plain English, and tell me the safest next check without inventing missing data."

## `auth check` fails

- Confirm you can reach `www.themealdb.com`
- If you set your own key, check that `THEMEALDB_API_KEY` is correct
- If you did not change anything, try again with the default public key `1`

## Search or filter returns zero results

- That is a normal API result, not always an error
- Check spelling, especially for category and ingredient names
- Try `list categories` or `list ingredients` first if you are unsure

## `list ingredients` is large

- That endpoint returns a long payload from the API
- Use `filter ingredient` if you only need meals for one ingredient

## I want to use a custom key

- Put it in `.env`
- Do not paste it into chat
- The tool will redact it in most error paths, but `.env` should still stay local
