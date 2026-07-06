# Use Cases

Ask the agent practical Ads questions first, then let it prepare plans only when a live change is needed.

## Useful asks

- “List active and paused campaigns, then explain which ones can serve.”
- “Show yesterday’s account insights by campaign and product where available.”
- “Find ad groups using a product feed and show their product filters.”
- “Prepare a paused campaign for California and San Francisco DMA targeting, but do not activate it.”
- “Build a plan to create one product-ad template from this feed setup.”
- “List supported conversion events and tell me which one fits a quote-request form.”
- “Build an image tag for `order_created` with a redacted Pixel ID.”
- “Prepare a server-side conversion event send in validate-only mode.”

## Not a fit

- Browser automation inside Ads Manager.
- Creating the product feed connection or uploading the merchant catalog over SFTP.
- Generic OpenAI API work outside OpenAI Ads.
- Raw HTTP calls that bypass named commands and safety gates.
