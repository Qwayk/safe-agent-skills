# Review an Asana write plan

Use this prompt after the CLI has saved a plan and before approval. Keep the bearer token out of the prompt.

```text
Review this Asana plan against my request.

Check that the fixed command and exact GIDs target the right workspace, project, task, team, goal, portfolio, or setting. Compare the proposed data with the saved before-state. Explain every risk reason, whether a snapshot exists, what acknowledgement the plan requires, and what the readback can actually prove.

Reject the plan if it changes more than I asked, uses the wrong target, contains an unexpected attachment, fails local integrity, or depends on a rollback that the plan does not provide. Do not edit or repair a refused plan; create a new one.

If it is correct, summarize the planned change and ask me to approve the exact plan ID. Do not apply it yet.

User request:
<describe the intended Asana change>

Plan JSON:
<paste or load the saved plan without any token>
```
