---
title: subscriptionDraftDiscountRemove - GraphQL Admin
description: Removes a subscription discount from a subscription draft.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/subscriptionDraftDiscountRemove
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/subscriptionDraftDiscountRemove.md
---

# subscription​Draft​Discount​Remove

mutation

Requires `write_own_subscription_contracts` access scope. Also: The user must have manage\_orders\_information permission.

Removes a subscription discount from a subscription draft.

## Arguments

* discount​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The gid of the subscription draft discount to remove.

* draft​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The gid of the subscription contract draft to remove a subscription discount from.

***

## Subscription​Draft​Discount​Remove​Payload returns

* discount​Removed

  [Subscription​Discount](https://shopify.dev/docs/api/admin-graphql/latest/unions/SubscriptionDiscount)

  The removed subscription draft discount.

* draft

  [Subscription​Draft](https://shopify.dev/docs/api/admin-graphql/latest/objects/SubscriptionDraft)

  The subscription contract draft object.

* user​Errors

  [\[Subscription​Draft​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/SubscriptionDraftUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### subscriptionDraftDiscountRemove reference
