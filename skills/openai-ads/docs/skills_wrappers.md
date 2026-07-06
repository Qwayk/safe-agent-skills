# Skill Wrapper Notes

The skill wrapper is the short instruction file an agent reads before it works with ChatGPT Ads.

It should point the agent to this tool when the user asks about OpenAI Ads campaigns, ad groups, ads, insights, targeting, product-feed setup, custom audiences, files, conversion settings, pixels, image tags, or server-side conversion events.

It should keep the agent out of the wrong place too. This is not the broad OpenAI Platform tool, not Ads Manager browser automation, and not the place to upload product catalogs over SFTP.

The safest first action is an account check or a small read, such as listing campaigns or checking targeting options. If the user asks for a live change, the agent should show the plan first and ask before continuing.

The public wrapper is published as `SKILL.md` in the `openai-ads` skill folder.
