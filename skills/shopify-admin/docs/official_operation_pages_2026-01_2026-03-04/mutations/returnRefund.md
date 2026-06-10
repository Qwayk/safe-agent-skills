---
title: returnRefund - GraphQL Admin
description: >-
  Creates a refund for items being returned when the return status is `OPEN` or
  `CLOSED`. This mutation processes the financial aspects of a return by
  refunding line items, shipping costs, and duties back to the customer.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/returnRefund'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/returnRefund.md'
---

# return​Refund

mutation

Requires `write_returns` access scope or `write_marketplace_returns` access scope. Also: The user must have `refund_orders` permission.

Deprecated. Use [returnProcess](https://shopify.dev/docs/api/admin-graphql/latest/mutations/returnProcess) instead.

Creates a refund for items being returned when the return status is `OPEN` or `CLOSED`. This mutation processes the financial aspects of a return by refunding line items, shipping costs, and duties back to the customer.

## Arguments

* return​Refund​Input

  [Return​Refund​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/ReturnRefundInput)

  required

  The input fields to refund a return.

***

## Return​Refund​Payload returns

* refund

  [Refund](https://shopify.dev/docs/api/admin-graphql/latest/objects/Refund)

  The created refund.

* user​Errors

  [\[Return​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ReturnUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### returnRefund reference
