---
title: shopPayPaymentRequestReceipt - GraphQL Admin
description: Returns a Shop Pay payment request receipt.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/shopPayPaymentRequestReceipt
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/shopPayPaymentRequestReceipt.md
---

# shop​Pay​Payment​Request​Receipt

query

Returns a Shop Pay payment request receipt.

## Arguments

* token

  [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  required

  Unique identifier of the payment request receipt.

***

## Possible returns

* Shop​Pay​Payment​Request​Receipt

  [Shop​Pay​Payment​Request​Receipt](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopPayPaymentRequestReceipt)

  The receipt of Shop Pay payment request session submission.

  * created​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time when the payment request receipt was created.

  * order

    [Order](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order)

    The order that's associated with the payment request receipt.

  * payment​Request

    [Shop​Pay​Payment​Request!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopPayPaymentRequest)

    non-null

    The shop pay payment request object.

  * processing​Status

    [Shop​Pay​Payment​Request​Receipt​Processing​Status!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopPayPaymentRequestReceiptProcessingStatus)

    non-null

    The status of the payment request session submission.

  * source​Identifier

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The source identifier provided in the `ShopPayPaymentRequestSessionCreate` mutation.

  * token

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The token of the receipt, initially returned by an `ShopPayPaymentRequestSessionSubmit` mutation.

***

## Examples

* ### shopPayPaymentRequestReceipt reference
