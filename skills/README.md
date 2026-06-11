# Skill catalog

Use this page to choose a Qwayk skill by product, job, access, and change level.

Each skill keeps the agent instructions, safe API tool code, docs, and tests together. Some skills are read-only by design. Others can change real settings or data, but they are built to show the plan first, ask before important changes, check the result, and leave a record of what happened. When possible, they should save the exact thing they are about to change. When the product has its own restore, backup, or version history, they should use that too.

If your agent supports installed skills, ask it to install the skill you want from `Qwayk/safe-agent-skills`. For manual setup, use the [install guide](../INSTALL.md). For the safety model, read [How Qwayk skills keep agents safer](../docs/how-qwayk-keeps-agents-safe.md).

The install slug appears under each product name so you can tell your agent exactly which skill to install.

## Start here

If you already know the product, click it below. If not, start with the section that matches the job you want done:

- [Measurement, search, and monitoring](#measurement-search-and-monitoring) for reporting, search visibility, tracking, incidents, or monitoring
- [Ads, acquisition, and local presence](#ads-acquisition-and-local-presence) for ad accounts or local business surfaces
- [CRM, outreach, support, and email](#crm-outreach-support-and-email) for leads, pipelines, support, or lifecycle messaging
- [Commerce, stores, and payments](#commerce-stores-and-payments) for stores, products, orders, merchant feeds, or payment systems
- [Affiliate, partnerships, and publisher revenue](#affiliate-partnerships-and-publisher-revenue) for affiliate product research or creator catalog work
- [Publishing and social channels](#publishing-and-social-channels) for websites, posts, or social accounts
- [Creative and media tools](#creative-and-media-tools) for assets, design files, voice tools, or media workflows
- [Cloud, domains, and AI platforms](#cloud-domains-and-ai-platforms) for infrastructure, domains, storage, or model-platform work
- [Public data and reference](#public-data-and-reference) for read-only public datasets

## Measurement, search, and monitoring

Start here if you want reporting, tracking, search visibility, incidents, or account monitoring.

| Product | What it helps with | What you connect | Mode |
| --- | --- | --- | --- |
| [**Google Analytics 4**](google-analytics/README.md)<br><sub>Install slug: <code>google-analytics</code></sub> | Review GA4 properties, reports, metadata, and admin surfaces | Google account | Reads + careful changes |
| [**Google Search Console**](google-search-console/README.md)<br><sub>Install slug: <code>google-search-console</code></sub> | Review Search Console sites, sitemaps, URL inspection, and search analytics | Google account | Reads + careful changes |
| [**Google Tag Manager**](google-tag-manager/README.md)<br><sub>Install slug: <code>google-tag-manager</code></sub> | Review GTM containers, workspaces, tags, triggers, variables, and versions | Google account | Reads + careful changes |
| [**Plausible Analytics**](plausible/README.md)<br><sub>Install slug: <code>plausible</code></sub> | Review Plausible traffic, goals, sites, and site settings | Plausible account | Reads + careful changes |
| [**CallRail**](callrail/README.md)<br><sub>Install slug: <code>callrail</code></sub> | Review CallRail accounts, calls, forms, companies, trackers, integrations, and webhooks | CallRail account | Reads + careful changes |
| [**Statuspage**](statuspage/README.md)<br><sub>Install slug: <code>statuspage</code></sub> | Check public status, incidents, maintenance, and components | Public status page URL | Read-only |

## Ads, acquisition, and local presence

Start here if you want campaign work, ad-account review, or local business surfaces.

| Product | What it helps with | What you connect | Mode |
| --- | --- | --- | --- |
| [**Google Ads**](google-ads/README.md)<br><sub>Install slug: <code>google-ads</code></sub> | Review Google Ads accounts and make careful campaign changes | Google Ads account | Reads + careful changes |
| [**Meta Ads**](meta-ads/README.md)<br><sub>Install slug: <code>meta-ads</code></sub> | Review Meta Ads accounts, campaigns, ads, creatives, and insights | Meta Ads account | Read-only |
| [**Microsoft Advertising**](microsoft-ads/README.md)<br><sub>Install slug: <code>microsoft-ads</code></sub> | Review and plan Microsoft Ads account work | Microsoft Advertising account | Reads + careful changes |
| [**LinkedIn Ads**](linkedin-ads/README.md)<br><sub>Install slug: <code>linkedin-ads</code></sub> | Review and plan LinkedIn Ads account work | LinkedIn Ads account | Reads + careful changes |
| [**TikTok Marketing API**](tiktok-marketing/README.md)<br><sub>Install slug: <code>tiktok-marketing</code></sub> | Review and plan TikTok Marketing API work | TikTok Ads account | Reads + careful changes |
| [**Google Business Profile**](google-business-profile/README.md)<br><sub>Install slug: <code>google-business-profile</code></sub> | Review and plan Google Business Profile location, review, media, and insight work | Google Business Profile account | Reads + careful changes |

## CRM, outreach, support, and email

Start here if you want lead, pipeline, support, outreach, or lifecycle work.

| Product | What it helps with | What you connect | Mode |
| --- | --- | --- | --- |
| [**HubSpot**](hubspot/README.md)<br><sub>Install slug: <code>hubspot</code></sub> | Review HubSpot CRM data and make careful CRM changes | HubSpot account | Reads + careful changes |
| [**Pipedrive**](pipedrive/README.md)<br><sub>Install slug: <code>pipedrive</code></sub> | Review Pipedrive CRM data and build sales reports | Pipedrive account | Read-only |
| [**Salesforce**](salesforce-platform/README.md)<br><sub>Install slug: <code>salesforce-platform</code></sub> | Review and plan Salesforce platform object, data, and metadata work | Salesforce account | Reads + careful changes |
| [**Instantly**](instantly/README.md)<br><sub>Install slug: <code>instantly</code></sub> | Review Instantly outreach, campaigns, leads, sending accounts, analytics, and webhooks | Instantly account | Reads + careful changes |
| [**Klaviyo**](klaviyo/README.md)<br><sub>Install slug: <code>klaviyo</code></sub> | Review Klaviyo accounts, profiles, lists, campaigns, flows, forms, events, catalogs, and tags | Klaviyo account | Reads + careful changes |
| [**Zendesk**](zendesk/README.md)<br><sub>Install slug: <code>zendesk</code></sub> | Review Zendesk support data and make careful ticketing changes | Zendesk account | Reads + careful changes |

## Commerce, stores, and payments

Start here if you want store, order, product, merchant-feed, or payment-system work.

| Product | What it helps with | What you connect | Mode |
| --- | --- | --- | --- |
| [**Shopify**](shopify-admin/README.md)<br><sub>Install slug: <code>shopify-admin</code></sub> | Review Shopify store data and plan Admin API changes | Shopify store | Reads + careful changes |
| [**WooCommerce**](woocommerce/README.md)<br><sub>Install slug: <code>woocommerce</code></sub> | Review and plan WooCommerce product, order, customer, coupon, and report work | WooCommerce store | Reads + careful changes |
| [**Google Merchant Center**](google-merchant-api/README.md)<br><sub>Install slug: <code>google-merchant-api</code></sub> | Review and plan Google Merchant product, account, report, and promotion work | Google Merchant Center account | Reads + careful changes |
| [**Stripe**](stripe/README.md)<br><sub>Install slug: <code>stripe</code></sub> | Review Stripe account data and make careful payment-system changes | Stripe account | Reads + careful changes |
| [**PayPal**](paypal/README.md)<br><sub>Install slug: <code>paypal</code></sub> | Review and plan PayPal order, payment, payout, and dispute work | PayPal business account | Reads + careful changes |
| [**Mercury**](mercury/README.md)<br><sub>Install slug: <code>mercury</code></sub> | Check Mercury accounts and download statements, invoices, exports, and attachments | Mercury account | Read-only |

## Affiliate, partnerships, and publisher revenue

Start here if you want affiliate product research, creator catalogs, or partner-driven publishing work.

| Product | What it helps with | What you connect | Mode |
| --- | --- | --- | --- |
| [**Amazon Product Advertising API**](amazon-paapi-v5/README.md)<br><sub>Install slug: <code>amazon-paapi-v5</code></sub> | Search Amazon product data, resolve products, and build affiliate-ready product research | Amazon Associates account | Read-only |
| [**Amazon Creators**](amazon-creators/README.md)<br><sub>Install slug: <code>amazon-creators</code></sub> | Review Amazon creator catalog data and affiliate-style media product details | Amazon Creators account | Reads + local changes only |
| [**Awin Publisher**](awin-publisher/README.md)<br><sub>Install slug: <code>awin-publisher</code></sub> | Review Awin publisher accounts, programs, offers, transactions, reports, feeds, linkbuilder work, and proof-of-purchase uploads | Awin publisher account | Reads + careful changes |
| [**Sovrn**](sovrn/README.md)<br><sub>Install slug: <code>sovrn</code></sub> | Review Sovrn Commerce data, affiliate link checks, product suggestions, and advertising reports | Sovrn account | Read-only |
| [**Awin Advertiser**](awin-advertiser/README.md)<br><sub>Install slug: <code>awin-advertiser</code></sub> | Review Awin advertiser performance and prepare careful validation, offer, feed, or conversion work | Awin advertiser account | Reads + careful changes |
| [**Skimlinks**](skimlinks/README.md)<br><sub>Install slug: <code>skimlinks</code></sub> | Inspect merchants, publisher reports, Product Key lookups, and Link Wrapper URLs | Skimlinks account | Read-only + local URL build |

## Publishing and social channels

Start here if you want website publishing, content updates, or social account work.

| Product | What it helps with | What you connect | Mode |
| --- | --- | --- | --- |
| [**WordPress**](wordpress/README.md)<br><sub>Install slug: <code>wordpress</code></sub> | Review WordPress content and make careful content changes | WordPress site | Reads + careful changes |
| [**Ghost**](ghost/README.md)<br><sub>Install slug: <code>ghost</code></sub> | Review Ghost content and make careful publishing changes | Ghost site | Reads + careful changes |
| [**Pinterest**](pinterest/README.md)<br><sub>Install slug: <code>pinterest</code></sub> | Review Pinterest boards, pins, catalogs, and ads surfaces | Pinterest account | Reads + careful changes |
| [**Reddit**](reddit/README.md)<br><sub>Install slug: <code>reddit</code></sub> | Review and plan Reddit account, post, subreddit, and API work | Reddit account | Reads + careful changes |
| [**Bluesky**](bluesky/README.md)<br><sub>Install slug: <code>bluesky</code></sub> | Review and plan Bluesky account, feed, post, and session work | Bluesky account | Reads + careful changes |
| [**Instagram**](instagram/README.md)<br><sub>Install slug: <code>instagram</code></sub> | Review and plan Instagram media, comment, mention, message, and insight work | Instagram account | Reads + careful changes |
| [**Threads**](threads/README.md)<br><sub>Install slug: <code>threads</code></sub> | Review and plan Threads posts, replies, moderation, and account work | Threads account | Reads + careful changes |
| [**X**](x/README.md)<br><sub>Install slug: <code>x</code></sub> | Review and plan X API, DM, auth, and posting workflows | X account | Reads + careful changes |
| [**YouTube**](youtube/README.md)<br><sub>Install slug: <code>youtube</code></sub> | Review and plan YouTube channel, video, upload, and data workflows | YouTube channel | Reads + careful changes |

## Creative and media tools

Start here if you want assets, folders, uploads, voice tools, or design-platform work.

| Product | What it helps with | What you connect | Mode |
| --- | --- | --- | --- |
| [**Figma**](figma/README.md)<br><sub>Install slug: <code>figma</code></sub> | Review and plan Figma files, comments, components, and team workflows | Figma account | Reads + careful changes |
| [**Cloudinary**](cloudinary/README.md)<br><sub>Install slug: <code>cloudinary</code></sub> | Review Cloudinary assets, folders, uploads, and delivery settings | Cloudinary account | Reads + careful changes |
| [**ElevenLabs**](elevenlabs/README.md)<br><sub>Install slug: <code>elevenlabs</code></sub> | Review and plan ElevenLabs voice, text-to-speech, history, and workspace work | ElevenLabs account | Reads + careful changes |
| [**Freepik**](freepik/README.md)<br><sub>Install slug: <code>freepik</code></sub> | Search, review, and download Freepik assets through a safer local workflow | Freepik account | Reads + local changes only |
| [**Unsplash**](unsplash/README.md)<br><sub>Install slug: <code>unsplash</code></sub> | Search, review, and download Unsplash assets through a safer local workflow | Unsplash account | Reads + local changes only |

## Cloud, domains, and AI platforms

Start here if you want infrastructure, domain, account, or AI-platform work.

| Product | What it helps with | What you connect | Mode |
| --- | --- | --- | --- |
| [**Cloudflare**](cloudflare/README.md)<br><sub>Install slug: <code>cloudflare</code></sub> | Review Cloudflare zones, DNS, Workers, Pages, security, storage, and account settings | Cloudflare account | Reads + careful changes |
| [**Dynadot**](dynadot/README.md)<br><sub>Install slug: <code>dynadot</code></sub> | Review and plan domain, DNS, auction, transfer, and account work | Dynadot account | Reads + careful changes |
| [**OpenAI Platform**](openai/README.md)<br><sub>Install slug: <code>openai</code></sub> | Review and plan OpenAI API operations through a safer local workflow | OpenAI account | Reads + careful changes |
| [**Qdrant Cloud**](qdrant-cloud/README.md)<br><sub>Install slug: <code>qdrant-cloud</code></sub> | Review Qdrant Cloud resources and use provider backup or restore workflows where supported | Qdrant Cloud account | Reads + careful changes |

## Public data and reference

Start here if you want read-only public datasets or reference lookups.

| Product | What it helps with | What you connect | Mode |
| --- | --- | --- | --- |
| [**Hacker News**](hacker-news/README.md)<br><sub>Install slug: <code>hacker-news</code></sub> | Read Hacker News stories, users, and public item data | No account | Read-only |
| [**Open Library**](open-library/README.md)<br><sub>Install slug: <code>open-library</code></sub> | Search Open Library books, authors, works, and public metadata | No account | Read-only |
| [**TheMealDB**](themealdb/README.md)<br><sub>Install slug: <code>themealdb</code></sub> | Search recipes, ingredients, categories, and public meal data | No account | Read-only |
