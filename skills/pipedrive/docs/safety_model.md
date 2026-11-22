# How Pipedrive reads work

The tool reads records and account settings. Use the [coverage table](api_coverage.md) to see which requests it supports. Keep saved results and logs private when they include CRM data.

The token is sent to your configured Pipedrive host. If a request is redirected to another host, the token is removed. Confirm the account with a small read before using the results in a report.

`files download` returns file details such as type, size, or a link when the server supplies them. It checks the headers with `HEAD`. If the server declines that method, it opens a `GET` response and reads only its headers. File checks stop at redirects and never save the file body.
