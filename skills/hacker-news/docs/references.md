# References

Last verified (UTC): 2026-05-21T00:00:00Z

Official sources used for this tool:

| Source | Purpose | Notes |
|---|---|---|
| `https://github.com/HackerNews/API` | Official Hacker News API documentation | Primary source for the documented v0 HTTP surface, field notes, and examples |
| `https://raw.githubusercontent.com/HackerNews/API/master/README.md` | Stable raw copy of the official README | Used to confirm exact endpoint paths and example payload shapes |
| `https://hacker-news.firebaseio.com/v0/maxitem.json` | Safe live read proof endpoint | Used during validation because it is public, read-only, and small |

Key implementation facts taken from the official docs:
- Base API root: `https://hacker-news.firebaseio.com/v0/`
- Auth: none
- Rate limits: the official README says there is currently no rate limit
- Official documented HTTP endpoints: item, user, topstories, newstories, beststories, askstories, showstories, jobstories, maxitem, updates

Non-goals:
- This tool does not try to wrap undocumented Firebase transport behavior.
- This tool does not scrape HTML pages from `news.ycombinator.com`.
