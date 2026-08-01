# What you can ask your agent

Start with a read. These asks help you understand the account before deciding whether anything should change.

- "List my domains and tell me which ones need attention."
- "Is this domain available, and what does Spaceship report about it?"
- "Show the current DNS records and nameservers for this domain."
- "Check the transfer status and lock before I move this domain."
- "Review my SellerHub listings and sold-domain report."
- "Show up to 100 sold domains between these two sale dates, then continue from the returned cursor."
- "Show the status of this Spaceship async operation."

When you want a change, ask for a plan first:

- "Prepare a one-year renewal plan for this domain and show me every cost field Spaceship exposes."
- "Prepare new DNS records, but do not apply them."
- "Plan a contact or privacy update and mask the private details in the output."
- "Prepare a SellerHub checkout link or SafePay transaction and show the domain, amount, currency, fee split, and parties before approval."

The agent should stop after the plan unless you explicitly approve that exact saved plan. DNS and nameserver changes need a DNS-risk acknowledgement; registrations and renewals need spend and ownership acknowledgements; checkout and SafePay work needs financial and ownership acknowledgements; private contact or transfer data needs a private-data acknowledgement.

Do not use this tool to create API keys, change payment methods, accept legal terms, automate the Spaceship website, or call an undocumented endpoint.
