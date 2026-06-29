# Skill Wrapper

Source wrapper:

- `skills/gemini/SKILL.md`

Use the wrapper when an agent needs the official Gemini API through safe named commands. The first move should usually be `auth check` or `models list`, then a specific read, generation, token count, or dry-run plan.

The wrapper must keep the agent away from raw HTTP guesses, direct secret handling, and unreviewed state changes. It should remind the agent that writes need a plan first and that no-snapshot or irreversible applies need explicit acknowledgements.
