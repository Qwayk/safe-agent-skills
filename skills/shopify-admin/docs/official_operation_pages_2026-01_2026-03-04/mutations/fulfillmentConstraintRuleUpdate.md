---
title: fulfillmentConstraintRuleUpdate - GraphQL Admin
description: Update a fulfillment constraint rule.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/fulfillmentConstraintRuleUpdate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/fulfillmentConstraintRuleUpdate.md
---

# fulfillment​Constraint​Rule​Update

mutation

Requires `write_fulfillment_constraint_rules` access scope.

Update a fulfillment constraint rule.

## Arguments

* delivery​Method​Types

  [\[Delivery​Method​Type!\]!](https://shopify.dev/docs/api/admin-graphql/latest/enums/DeliveryMethodType)

  required

  Specifies the delivery method types to be updated. If not provided or providing an empty list will associate the function with all delivery methods.

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  A globally-unique identifier for the fulfillment constraint rule.

***

## Fulfillment​Constraint​Rule​Update​Payload returns

* fulfillment​Constraint​Rule

  [Fulfillment​Constraint​Rule](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentConstraintRule)

  The updated fulfillment constraint rule.

* user​Errors

  [\[Fulfillment​Constraint​Rule​Update​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentConstraintRuleUpdateUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### fulfillmentConstraintRuleUpdate reference
