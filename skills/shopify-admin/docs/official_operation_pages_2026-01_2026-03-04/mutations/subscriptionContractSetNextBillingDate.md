---
title: subscriptionContractSetNextBillingDate - GraphQL Admin
description: >-
  Sets the next billing date of a Subscription Contract. This field is managed
  by the apps.
          Alternatively you can utilize our
          [Billing Cycles APIs](https://shopify.dev/docs/apps/selling-strategies/subscriptions/billing-cycles),
          which provide auto-computed billing dates and additional functionalities.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/subscriptionContractSetNextBillingDate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/subscriptionContractSetNextBillingDate.md
---

# subscription​Contract​Set​Next​Billing​Date

mutation

Requires `write_own_subscription_contracts` access scope. Also: The user must have manage\_orders\_information permission.

Sets the next billing date of a Subscription Contract. This field is managed by the apps. Alternatively you can utilize our [Billing Cycles APIs](https://shopify.dev/docs/apps/selling-strategies/subscriptions/billing-cycles), which provide auto-computed billing dates and additional functionalities.

## Arguments

* contract​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The gid of the Subscription Contract to set the next billing date for.

* date

  [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

  required

  The next billing date.

***

## Subscription​Contract​Set​Next​Billing​Date​Payload returns

* contract

  [Subscription​Contract](https://shopify.dev/docs/api/admin-graphql/latest/objects/SubscriptionContract)

  The updated Subscription Contract object.

* user​Errors

  [\[Subscription​Contract​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/SubscriptionContractUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### subscriptionContractSetNextBillingDate reference
