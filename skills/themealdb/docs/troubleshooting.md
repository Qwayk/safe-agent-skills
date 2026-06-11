# Troubleshooting

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
