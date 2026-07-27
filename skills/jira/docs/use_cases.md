# What you can ask your agent to do in Jira

## Find work that needs attention

Ask: "Find open bugs in the PAY project that have no assignee, then group them by priority."

The agent can choose the fixed JQL search command, explain the query, run the read, and summarize the returned issues. Searches do not need write approval.

## Review a board, backlog, or sprint

Ask: "Show me the active sprint on this Scrum board and tell me which issues are still in progress."

The Jira Software commands can inspect boards, backlogs, epics, sprints, and estimates. Your Jira Software access and project permissions still control the result.

## Prepare a new issue

Ask: "Prepare a bug for the checkout failure, but do not create it yet."

The agent checks the project and create metadata first, prepares the Jira JSON body in a local file, and saves a create-issue plan. Creating an issue has no reliable generic before-state, so apply needs the no-snapshot acknowledgement after you review the plan.

## Update an existing issue

Ask: "Prepare an update that assigns PAY-123 to me and adds the customer impact to the description."

The edit command has a matching issue read. During apply, the tool tries to save the current issue before sending the update, then reads it again to verify that Jira still returns the target.

## Move sprint work

Ask: "Prepare moving these three issues into the next sprint."

Sprint moves and ranking changes are production-risk actions. They always start with a saved plan and require the stronger high-risk approval. When a reliable generic snapshot is unavailable, the no-snapshot approval is also required.

## Review or change Jira administration

Ask: "Show me the workflow, permission scheme, issue type scheme, and notification scheme used by this project."

Administration reads can run directly. Changes to projects, users, groups, permissions, workflows, schemes, webhooks, or notifications need a saved plan and stronger approval.

## Know when this is not the right tool

Use another product-specific tool for Jira Service Management, Assets, Operations, Confluence, or Atlassian organization administration. This tool also does not support Jira Data Center, Jira Server, undocumented endpoints, arbitrary URLs, or arbitrary HTTP methods.
