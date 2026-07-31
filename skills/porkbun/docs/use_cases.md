# Use cases

Ask your agent for real domain-work:

- “Check my Porkbun domain list and tell me which names expire soon.”
- “What is my account balance and can you list any active webhook settings?”
- “Check DNS records for `example.com` and flag any likely stale entries.”
- “Show current `.com` registration and transfer pricing so we can estimate next quarter costs.”
- “Review marketplace options for short domains and summarize by length and price.”
- “Prepare a plan to update nameservers for a domain, but don't apply yet.”

When you want live action:

- “Create a DNS A record for `app.example.com` and show me the plan first.”
- “Send a webhook test and show the last delivery result.”
- “Delete this old forwarding rule and check that it is no longer returned.”
- “Rotate a webhook signing secret and save the updated value to a protected file.”

If you are checking before action, ask in this order:
1) connection check, 2) what changed since last check, 3) one safe plan, 4) approval.

## What a healthy first response should contain

- what was found
- what was left unchanged
- what needs approval
- what will be verified next
