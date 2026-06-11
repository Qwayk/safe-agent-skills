---
title: shopifyPaymentsPayoutAlternateCurrencyCreate - GraphQL Admin
description: Creates an alternate currency payout for a Shopify Payments account.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/shopifyPaymentsPayoutAlternateCurrencyCreate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/shopifyPaymentsPayoutAlternateCurrencyCreate.md
---

# shopify​Payments​Payout​Alternate​Currency​Create

mutation

Requires `write_shopify_payments_tooling` access scope.

Creates an alternate currency payout for a Shopify Payments account.

## Arguments

* account​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of the Shopify Payments account on which the mutation is being performed.

* currency

  [Currency​Code!](https://shopify.dev/docs/api/admin-graphql/latest/enums/CurrencyCode)

  required

  The currency of the balance to payout.

***

## Shopify​Payments​Payout​Alternate​Currency​Create​Payload returns

* payout

  [Shopify​Payments​Tooling​Provider​Payout](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopifyPaymentsToolingProviderPayout)

  The resulting alternate currency payout created.

* success

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Whether the alternate currency payout was created successfully.

* user​Errors

  [\[Shopify​Payments​Payout​Alternate​Currency​Create​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopifyPaymentsPayoutAlternateCurrencyCreateUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### shopifyPaymentsPayoutAlternateCurrencyCreate reference
