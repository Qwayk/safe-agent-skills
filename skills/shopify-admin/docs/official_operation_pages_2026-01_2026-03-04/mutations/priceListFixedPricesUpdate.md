---
title: priceListFixedPricesUpdate - GraphQL Admin
description: >-
  Updates fixed prices on a
  [`PriceList`](https://shopify.dev/docs/api/admin-graphql/latest/objects/PriceList).
  This mutation lets you add new fixed prices for specific
  [`ProductVariant`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant)
  objects and remove existing prices in a single operation.


  Use this mutation to modify variant pricing on a price list by providing
  prices to add and variant IDs to delete.


  Learn more about [setting fixed prices for product
  variants](https://shopify.dev/docs/apps/build/markets/build-catalog#step-3-set-fixed-prices-for-specific-product-variants).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/priceListFixedPricesUpdate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/priceListFixedPricesUpdate.md
---

# price​List​Fixed​Prices​Update

mutation

Requires `write_products` access scope. Also: The user must have permission to create and edit catalogs.

Updates fixed prices on a [`PriceList`](https://shopify.dev/docs/api/admin-graphql/latest/objects/PriceList). This mutation lets you add new fixed prices for specific [`ProductVariant`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant) objects and remove existing prices in a single operation.

Use this mutation to modify variant pricing on a price list by providing prices to add and variant IDs to delete.

Learn more about [setting fixed prices for product variants](https://shopify.dev/docs/apps/build/markets/build-catalog#step-3-set-fixed-prices-for-specific-product-variants).

## Arguments

* price​List​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The price list that the prices will be updated against.

* prices​To​Add

  [\[Price​List​Price​Input!\]!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/PriceListPriceInput)

  required

  The fixed prices to add.

* variant​Ids​To​Delete

  [\[ID!\]!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  A list of product variant IDs to remove from the price list.

***

## Price​List​Fixed​Prices​Update​Payload returns

* deleted​Fixed​Price​Variant​Ids

  [\[ID!\]](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  A list of deleted variant IDs for prices.

* price​List

  [Price​List](https://shopify.dev/docs/api/admin-graphql/latest/objects/PriceList)

  The price list for which the fixed prices were modified.

* prices​Added

  [\[Price​List​Price!\]](https://shopify.dev/docs/api/admin-graphql/latest/objects/PriceListPrice)

  The prices that were added to the price list.

* user​Errors

  [\[Price​List​Price​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PriceListPriceUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### priceListFixedPricesUpdate reference
