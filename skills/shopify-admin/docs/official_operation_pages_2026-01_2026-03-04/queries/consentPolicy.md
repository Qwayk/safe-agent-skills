---
title: consentPolicy - GraphQL Admin
description: Returns the customer privacy consent policies of a shop.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/consentPolicy'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/consentPolicy.md'
---

# consent​Policy

query

Returns the customer privacy consent policies of a shop.

## Arguments

* consent​Required

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Return policies where consent is required or not.

* country​Code

  [Privacy​Country​Code](https://shopify.dev/docs/api/admin-graphql/latest/enums/PrivacyCountryCode)

  Return policies with the provided country code.

* data​Sale​Opt​Out​Required

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Return policies where data sale opt out is required or not.

* id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  Return the policy with the provided ID.

* region​Code

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  Return policies with the provided region code.

***

## Possible returns

* Consent​Policy

  [\[Consent​Policy!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ConsentPolicy)

  A consent policy describes the level of consent that the merchant requires from the user before actually collecting and processing the data.

  * consent​Required

    [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    Whether consent is required for the region.

  * country​Code

    [Privacy​Country​Code](https://shopify.dev/docs/api/admin-graphql/latest/enums/PrivacyCountryCode)

    The `ISO 3166` country code for which the policy applies.

  * data​Sale​Opt​Out​Required

    [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    Whether data sale opt-out is required for the region.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    The global ID of the consent policy. IDs prefixed with `SD-` are system default policies.

  * region​Code

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The `ISO 3166` region code for which the policy applies.

  * shop​Id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    The global ID of the shop that owns the policy.

***

## Examples

* ### consentPolicy reference
