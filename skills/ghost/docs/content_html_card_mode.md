# Content HTML card mode

Why this exists:
- Ghost stores post bodies as Lexical by default.
- Full Lexical editing is powerful but more complex and easier to get wrong.

For migration tasks that require reliable text/HTML transforms (captions, inserting figures), this tool supports a safe mode:

## HTML card mode

The post HTML must contain a single HTML card:

```html
<!--kg-card-begin: html-->
<p>...</p>
<!--kg-card-end: html-->
```

In this mode, `ghost-api-tool post body ...` commands can:
- list images by `src`
- set/update `<figcaption>` for matching `<img src="...">`

If the post is not in HTML card mode, the tool refuses (safe default).

If you need to edit normal Ghost posts (Lexical), see `content_lexical_mode.md` and the `post bodylex ...` commands.
