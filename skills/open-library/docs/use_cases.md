# What you can do with Open Library

Open Library work usually starts with a book question: which title is the right one, which editions exist, who wrote it, what ISBN record matches, or what books belong on a small reading list?
If you need setup first, start with [Use Open Library with no account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

No login or API key is needed. The useful limit is that Open Library records can be incomplete, so the agent should show the record it found instead of pretending the catalog is perfect.

## Good jobs to give the agent

### Find books and compare matches

- "Find five books about Dune and show which matches look most useful."
- "Search for books about product management and give me a short reading shortlist."
- "Find books with this title and tell me which one looks like the original work."
- "Search for Spanish-language books on this topic and show the best matches."
- "Find books by keyword, then open the strongest work record before summarizing."

### Work, edition, and ISBN lookup

- "Look up this ISBN and explain which edition it is."
- "Open this work ID and show the available editions."
- "Compare the editions for this work and tell me which ones look like paperback, ebook, or audiobook records."
- "Find the Open Library work behind this edition record."
- "Check whether this ISBN resolves cleanly before I use it in a book list."

### Author research

- "Find the author record for Ursula K. Le Guin and list the author's works."
- "Open this author ID and show the works that look most relevant."
- "Search for authors with this name and help me avoid choosing the wrong person."
- "Build a small author bibliography from the public records."

### Topic exploration

- "Try a small subject search for cybernetics and tell me whether the results look useful."
- "Find a few books under this subject, but keep it exploratory."
- "Check whether this subject has ebooks before I plan a reading list."

## What the agent should show you

- The exact search query, ISBN, author ID, work ID, edition ID, or subject it used.
- The most useful title, author, publication, language, edition, or subject fields.
- A short explanation of why one result looks more relevant than another.
- A warning when records are sparse, duplicated, or ambiguous.
- A reminder that subject lookup is experimental in this tool and should stay small.

## Good first research path

Start with a small book search, open the best work record, then check editions or ISBNs only after the first match looks right.
