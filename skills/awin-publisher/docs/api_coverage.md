# API coverage

This table maps the official publisher-side pages to the shipped command families and the current build status.

Last updated (UTC): 2026-06-09
Core API host: `https://api.awin.com`
Legacy feed host: `https://productdata.awin.com`

Status labels used here:

- `implemented (local-tested, live-unverified)`: code and unit coverage are in place, but no live Awin credential proof has been recorded yet.
- `support-only`: official context page, not its own API command family.
- `inbound callback`: official webhook or notification docs, not a pull command for this CLI.

| Official publisher page | Locked command family | Status | Command family state | Notes |
| --- | --- | --- | --- | --- |
| Get Accounts | `accounts list` | implemented (local-tested, live-unverified) | `accounts list` | `GET /accounts`; bearer + `accessToken`; tool filters to publisher accounts only |
| Get Program Information | `programs list` | implemented (local-tested, live-unverified) | `programs list` | `GET /publishers/{publisherId}/programmes`; valid relationship values: `joined`, `pending`, `suspended`, `rejected`, `notjoined`; `includeHidden` only when `relationship` is not sent |
| Get Program Details | `programs details` | implemented (local-tested, live-unverified) | `programs details` | `GET /publishers/{publisherId}/programmedetails`; `advertiserId` is a required query param; details also allows `relationship=any` |
| Retrieve Offers | `offers list` | implemented (local-tested, live-unverified) | `offers list` | `POST /publisher/{publisherId}/promotions`; filters and pagination go in the JSON body |
| Get List of Transactions | `transactions list` | implemented (local-tested, live-unverified) | `transactions list` | `GET /publishers/{publisherId}/transactions/`; trailing slash matters; max supported date range is 31 days |
| Get List of Transactions by id's | `transactions by-ids` | implemented (local-tested, live-unverified) | `transactions by-ids` | `GET /publishers/{publisherId}/transactions`; no trailing slash; requires `ids` query param |
| Get List of Transaction Queries | `transaction-queries list` | implemented (local-tested, live-unverified) | `transaction-queries list` | `GET /publisher/{publisherId}/transactionqueries`; singular `/publisher`; max supported date range is 31 days |
| Advertiser Performance | `reports advertiser` | implemented (local-tested, live-unverified) | `reports advertiser` | `GET /publishers/{publisherId}/reports/advertiser` |
| Campaign Performance | `reports campaign` | implemented (local-tested, live-unverified) | `reports campaign` | `GET /publishers/{publisherId}/reports/campaign`; supports optional advertiser ids, campaign prefix, interval, and no-campaign numbers |
| Creative Performance | `reports creative` | implemented (local-tested, live-unverified) | `reports creative` | `GET /publishers/{publisherId}/reports/creative` |
| Generate Tracking Link | `linkbuilder generate` | implemented (local-tested, live-unverified) | `linkbuilder generate` | `POST /publishers/{publisherId}/linkbuilder/generate`; supports optional click parameters and short links |
| Generate Tracking Links (batch) | `linkbuilder generate-batch` | implemented (local-tested, live-unverified) | `linkbuilder generate-batch` | `POST /publishers/{publisherId}/linkbuilder/generate-batch`; JSON file input; max 100 requests; no shorten support |
| Get Link Builder Quota | `linkbuilder quota` | implemented (local-tested, live-unverified) | `linkbuilder quota` | `GET /publishers/{publisherId}/linkbuilder/quota` |
| Get Enhanced Feed (Google Format) | `feeds enhanced-download` | implemented (local-tested, live-unverified) | `feeds enhanced-download` | `GET /publishers/{publisherId}/awinfeeds/download/{advertiserId}-retail-{locale}.jsonl`; bearer auth only; writes JSONL to a file |
| Proof of Purchase Publisher Transaction API | `proof-of-purchase orders create` | implemented (local-tested, live-unverified) | `proof-of-purchase orders create` | `POST /publishers/{publisherId}/advertiser/{advertiserId}/orders`; `x-api-key`; dry-run by default; live apply requires `--apply --yes --plan-in`; official page says both Awin-side publisher enablement and advertiser-side CLO enablement are required |
| Product Feed Publisher Guide Overview | support-only | support-only | support-only | Guide page only; used to explain legacy vs enhanced feed access |
| Product Feed List Download | `feeds legacy-list` | implemented (local-tested, live-unverified) | `feeds legacy-list` | `GET https://productdata.awin.com/datafeed/list/apikey/{apiKey}`; writes CSV list to a file |
| Downloading feeds using Create-a-Feed | `feeds legacy-download` | implemented (local-tested, live-unverified) | `feeds legacy-download` | Downloads a legacy feed either from `--feed-id` via the list endpoint or from an exact generated Awin download URL |
| Receive Transaction Notifications | inbound notifications | inbound callback | inbound callback | No pull command; official docs describe inbound notifications only |
| Transaction notifications | inbound notifications | inbound callback | inbound callback | No pull command; official docs describe inbound notifications only |

## Endpoint shape notes

- Mixed `/publisher/...` and `/publishers/...` paths exist in the official docs and are implemented as documented.
- The transactions list and transactions by-id pages differ by trailing slash.
- Offers retrieval is a `POST` read path in the official publisher docs.
- Enhanced feeds use bearer auth only, while legacy feeds use the legacy feed API key in the URL.
- Proof-of-purchase uses `x-api-key`, is the only remote write command family in this tool, and requires `--plan-in` together with `--apply --yes` for live apply.
- The official proof-of-purchase page says live use also depends on both Awin Partner Development enabling the publisher and the advertiser enabling CLO for that program.
