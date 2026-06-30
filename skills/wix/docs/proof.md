# Proof and verification

This page records what was checked before the Wix skill was published.

Most users do not need to run these commands. They are here so an agent, reviewer, or maintainer can see the coverage boundary, the safety proof, and the limits without reading the build chat.

## Last verified

- Date (UTC): `2026-06-30`
- Verified by: `Codex governor source-readiness and public-publish review`
- Tool version: `0.1.0`
- Provider boundary: official Wix API reference current from the 2026-06-29 inventory pass plus the 2026-06-30 final family checks
- Environment: local unit tests with mocked Wix responses; no live Wix account changes were made

## Final validation

- Focused source docs/wrapper/inventory/formatting suite: 236 tests, 0 failures.
- Full source Wix suite: 1809 tests, 0 failures.
- Focused public-copy docs/wrapper/inventory/formatting suite: 236 tests, 0 failures.
- Full public-copy Wix suite: 1809 tests, 0 failures.
- Wix-scoped whitespace check: clean.
- Public-copy hygiene check: no virtualenv, cache folders, local run state, private instruction files, or real secrets are part of the published skill.

## Coverage proof

- `docs/api_coverage.md` has 283 total coverage rows.
- 250 rows are real callable Wix command rows.
- 250 real callable rows are implemented with explicit named commands.
- 0 real callable rows remain `not-yet-implemented`.
- Limited rows are accounted honestly: 6 gated, 11 callback-only, 2 deprecated, 3 developer-preview, 9 docs-only, 1 site-defined, and 1 disabled.
- `docs/official_inventory.json` is marked `complete` for this boundary.
- The official inventory tracks 226 families and 1793 operations.

## Evidence anchors

- `2026-06-24-marketing-email-setup-contract-run`: early marketing email setup proof run kept as a named regression anchor.
- Final inventory cleanup: `docs/official_inventory.json` moved from partial to complete after the callable ledger reached zero open rows.
- Final source validation: 1809 local source tests passed after the public install slug was finalized as `wix`.
- Final public-copy validation: 1809 local public-copy tests passed from the mirrored `skills/wix` folder.
- Public slug check: README, catalog row, and `SKILL.md` all use install slug `wix`.

## Shipped family proof map

The public skill ships explicit command families for the official callable Wix boundary, including:

- App Management, app instance, app installation, app permissions, embedded scripts, site plugins, BI event, and market listing.
- Sites, site actions, site folders, domains, DNS, connected domains, account-level reads, contributors, AI Credits, and partner/reseller boundaries.
- CRM contacts, tasks, pipelines, cards, labels, fields, notes, attachments, members, badges, privacy, authentication, reports, followers, and related member surfaces.
- CMS data collections, data items, folders, indexes, permissions, sharing, extension schemas, functions, and site-defined HTTP Functions classification.
- Wix Stores Catalog V3, products, categories, variants, brands, ribbons, info sections, customizations, inventory, locations, orders, order billing, payments, coupons, gift cards, pricing plans, and related commerce helpers.
- Wix Bookings, services, writer/reader, attendance, waitlist, policies, policy snapshots, external calendars, resource/resource-type/staff surfaces, time slots, and course-flow coverage.
- Wix Events, tickets, RSVPs, reservations, guests, orders, registration forms, schedules, policies, categories, staff, and settings.
- Wix Restaurants menus, sections, items, labels, variants, modifiers, online-order settings, fulfillment, service fees, notifications, reservations, locations, time slots, and experiences.
- Marketing, email campaigns, email subscriptions, sender setup, marketing consent, referral program, rewards, tracker, referred/referring customer records, loyalty, donations, receipts, payment links, and multilingual.
- Media files, media folders, rich content, portfolio, Pro Gallery, analytics, semantic models, async jobs, branches, site search, viewer cache, SEO tags, headless auth/OAuth/recovery/redirect/sitemap/verification, and online programs.
- Non-command surfaces such as GraphQL, callbacks, service plugins, generic async runner, Captcha, Forum, and selected docs-only recipes are accounted without adding generic bridges.

## Safety proof

- Reads can run directly.
- Writes are plan-first and require reviewed plans before live apply.
- Live apply uses `--plan-in`, `--apply`, and `--yes`.
- Destructive, irreversible, permission, spend, send, bulk, production-risk, and no-snapshot actions require stronger approval such as `--ack-irreversible` where the command family needs it.
- Plans and receipts redact secrets and avoid storing token values.
- Verification rereads provider state when Wix exposes a useful read-after-write path.
- The skill does not expose raw REST, raw GraphQL, SDK pass-through, generic async job runner, or call-anything commands.

## Live-unverified by design

The suite proves parser behavior, request shaping, safety gates, docs alignment, inventory alignment, redaction, and mocked provider responses. It does not prove that every Wix endpoint succeeds against a real Wix account.

That is intentional. Many Wix surfaces require installed apps, site-specific scopes, account-level API keys, selected beta access, signed contracts, strategic-partner access, a visitor/member identity, or a specific business app state. Those areas stay marked gated, developer-preview, callback-only, disabled, docs-only, site-defined, or live-unverified where appropriate.

## How to rerun the local checks

From the skill folder, run:

```bash
python -m unittest -q
```

For the focused docs and inventory contract:

```bash
python -m unittest -q tests.test_official_inventory tests.test_docs_and_skill_wrapper tests.test_docs_formatting
```
