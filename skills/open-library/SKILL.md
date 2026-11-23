---
name: open-library
description: Find books, authors, editions and ISBNs in the public Open Library catalog.
---

Use `qwayk-open-library-safe-agent-cli --output json` for public catalog reads. If the command is missing, follow the [quickstart](docs/quickstart.md).

Start with the user's book, author or ISBN. For a title search, run `qwayk-open-library-safe-agent-cli --output json search books --q "dune" --limit 3` with the title the user asked for. Use a matching work or edition ID to check details before reporting them. [See all nine commands](docs/command_reference.md).

Keep searches small and follow [Open Library's usage guidelines](https://openlibrary.org/developers/api#usage-guidelines). For requests to edit records or use an account, explain that the tool reads public data.
