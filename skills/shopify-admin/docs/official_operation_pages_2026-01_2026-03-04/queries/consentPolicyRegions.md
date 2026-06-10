---
title: consentPolicyRegions - GraphQL Admin
description: >-
  List of countries and regions for which consent policies can be created or
  updated.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/consentPolicyRegions
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/consentPolicyRegions.md
---

# consent​Policy​Regions

query

List of countries and regions for which consent policies can be created or updated.

## Possible returns

* Consent​Policy​Region

  [\[Consent​Policy​Region!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ConsentPolicyRegion)

  A country or region code.

  * country​Code

    [Privacy​Country​Code](https://shopify.dev/docs/api/admin-graphql/latest/enums/PrivacyCountryCode)

    The `ISO 3166` country code for which the policy applies.

  * region​Code

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The `ISO 3166` region code for which the policy applies.

***

## Examples

* ### consentPolicyRegions reference
