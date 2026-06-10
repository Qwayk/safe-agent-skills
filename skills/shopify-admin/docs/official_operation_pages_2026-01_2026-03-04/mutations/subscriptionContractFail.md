---
title: subscriptionContractFail - GraphQL Admin
description: Fails a Subscription Contract.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/subscriptionContractFail
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/subscriptionContractFail.md
---

# subscription​Contract​Fail

mutation

Requires `write_own_subscription_contracts` access scope. Also: The user must have manage\_orders\_information permission.

Fails a Subscription Contract.

## Arguments

* subscription​Contract​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the Subscription Contract.

***

## Subscription​Contract​Fail​Payload returns

* contract

  [Subscription​Contract](https://shopify.dev/docs/api/admin-graphql/latest/objects/SubscriptionContract)

  The new Subscription Contract object.

* user​Errors

  [\[Subscription​Contract​Status​Update​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/SubscriptionContractStatusUpdateUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### subscriptionContractFail reference
