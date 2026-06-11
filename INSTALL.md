# Install

Qwayk skills are made for people who already use an AI agent that supports installed skills, like Codex, Claude Code, OpenCode, Cursor, GitHub Copilot, or Windsurf. If you already know which skill you want, the fastest path is to ask your agent to install it from `Qwayk/safe-agent-skills`. If you still need to choose a skill first, open the full [skill catalog](skills/README.md).

## Ask your agent to install it

Ask your agent to install the skill you want from this repo:

```text
Install the <skill-name> skill from Qwayk/safe-agent-skills for me.
```

Replace `<skill-name>` with any skill name from the full [skill catalog](skills/README.md).

If the skill needs account access after install, ask your agent to run `onboarding`.

That flow can guide API key setup or another supported sign-in method and tell you where to put it locally.

## Install it yourself

If your host does not let the agent handle the install directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@<skill-name> -g -y
```

Then close and reopen the app if new skills do not appear automatically. If your host asks you to attach, enable, or activate the skill in the current chat or workspace, do that too.

If the skill needs account access after install, ask your agent to run `onboarding`.

After that, ask for the job you want done. Each skill page has example requests and deeper setup notes when you need them.
