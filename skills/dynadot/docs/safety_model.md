# Review changes and keep transfer codes private

## Before a change

Review the saved plan with the user. Check the accounts, exact domains, changes, price, and what you can verify afterward. For a move between Dynadot accounts, check the receiving Push Username and use the same two API keys when you apply. Save a fresh plan if you changed keys, changed the plan, or saved it before the account check was added.

Use `--apply --yes --plan-in` after approval. Add `--ack-irreversible` for monetary or irreversible actions, and `--ack-no-snapshot` when the tool can't save the state before a change. The plan tells you which flags apply. Dynadot can confirm some changes with a follow-up read. The tool has no built-in restore for these changes.

## Before registration or renewal

Use an explicit currency and `--max-price` for the approved total. For a one-year registration, the tool uses Dynadot's domain search price. For a renewal, it asks Dynadot for a price using the exact renewal inputs. It checks the quote before applying and stops if the price can't be confirmed or is above the maximum. Review any quote that is above your maximum before saving a new plan.

Dynadot decides the final charge. API3 checks the price in a separate request. If you need a price guaranteed at checkout, or need the full price of a multi-year registration, review and complete the order in Dynadot. For bids, review the amount and currency in the plan.

## After a change

Check the receipt for the provider result and any follow-up checks. A follow-up read may show what Dynadot returned without confirming every requested field. For nameserver updates, check which domains show the requested nameservers. After a move, check what is pending and what is already in the receiver's account.

If a server or connection error leaves the result unclear, check Dynadot's domain, order, or transfer before running the write again. The tool can retry safe reads. Some bulk commands can continue from a previous receipt with `--resume-from-receipt`. Review the earlier results first to see which domains finished and which still need checking.

## Transfer codes

Use `transfers auth-code --domain example.com --out code.json` to save an existing transfer code. For the API3 command that can also create a new code or unlock a domain, keep the normal write approvals and use `--secret-out code.json` when applying. Choose a new file in an existing folder. The tool reserves it before the request and gives only your user access to it. Keep codes out of chat, plans, logs, and shared receipts.
