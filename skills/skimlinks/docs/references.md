# References

Last verified: **2026-06-08**

Official Skimlinks sources used for this build:

- `https://developers.skimlinks.com/`
- `https://developers.skimlinks.com/merchant.html`
- `https://skimlinksmerchantapi.docs.apiary.io/api-description-document`
- `https://developers.skimlinks.com/reporting.html`
- `https://skimlinksreporting.docs.apiary.io/api-description-document`
- `https://developers.skimlinks.com/product-key.html`
- `https://skimlinksproducts.docs.apiary.io/api-description-document`
- `https://developers.skimlinks.com/link.html`
- `https://jsapi.apiary.io/apis/skimlinkslinkapi`
- `https://developers.skimlinks.com/data-pipe.html`
- `https://datapipe1.docs.apiary.io/api-description-document`
- `https://developers.skimlinks.com/skimlinks-script.html`
- `https://jsapi.apiary.io/apis/skimjs`

Important source decisions:
- Merchant v4 is the shipped Merchant API surface.
- Merchant v3 is documented as an old duplicate group and is accounted for but not shipped.
- Reporting helper endpoints for link/page dimensions and metrics are included because the official report docs name them directly.
- Product Key uses separate optional credentials because the official Product Key docs say usual credentials may not work. Product Key also requires `publisher_domain_id` and uses `sort_desc` as `asc` or `desc`.
- Link Wrapper is covered from the official Apiary JSON because the developer page embeds `skimlinkslinkapi`.
- Data Pipe is treated as managed export guidance, not an HTTP API.
- Skimlinks JavaScript is treated as browser-side implementation guidance, not an HTTP API.
