# What you can do with Hacker News

Hacker News work usually starts with a quick question: what people in tech are talking about right now, what a specific thread actually contains, or what a public user has been submitting.

This skill lets an agent use the official public Hacker News API instead of scraping the website or guessing from story IDs. It is read-only and needs no account, so the useful part is speed and structure: fetch the real items, summarize what is there, and keep the limits clear.

If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## Good first asks

- "Show me the current top stories, fetch the first five items, and tell me the main topics people are discussing."
- "Check Ask HN and Show HN for anything related to developer tools."
- "Fetch this story ID and explain the title, URL, author, score, and comment count."
- "Look up this public user and summarize their account age, karma, and submitted item IDs."
- "Create a small snapshot of top, new, and job stories for a morning research note."

## Research jobs this helps with

Use Hacker News when the agent needs a fast public pulse:

- "What topics are getting attention today?"
- "Which Show HN posts look relevant to AI tools, APIs, developer infrastructure, or startup research?"
- "What jobs are showing up right now?"
- "What does this thread actually include before we quote or summarize it?"
- "Which story IDs changed recently, and which ones are worth fetching?"

The agent should fetch item details before making a summary. A list of IDs alone is not enough to understand the discussion.

## Startup, content, and product research

Good work often looks like this:

1. Pull the relevant story list, such as top, new, best, Ask HN, Show HN, or jobs.
2. Fetch the actual items behind the first set of IDs.
3. Group them by topic, company type, audience, or problem.
4. Point out which stories deserve a human click.
5. Say what the API cannot know, such as the full outside article content or the whole comment tree.

That gives you a quick research brief without pretending Hacker News is a complete market report.

## What good output looks like

A useful Hacker News answer should include:

- which list or item was fetched
- story IDs plus the actual item titles or fields
- a short summary of the main topics
- links or URLs when they exist
- a warning if the answer is based only on a small sample
- a clear note when the agent has not expanded comments or opened outside links

## Honest limits

This skill reads public Hacker News API data only. It cannot post, vote, comment, hide, delete, moderate, or change an account. It also does not search all historical Hacker News text or automatically expand every nested comment.
