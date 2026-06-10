---
title: fulfillmentConstraintRuleCreate - GraphQL Admin
description: Creates a fulfillment constraint rule and its metafield.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/fulfillmentConstraintRuleCreate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/fulfillmentConstraintRuleCreate.md
---

# fulfillment​Constraint​Rule​Create

mutation

Requires `write_fulfillment_constraint_rules` access scope.

Creates a fulfillment constraint rule and its metafield.

## Arguments

* delivery​Method​Types

  [\[Delivery​Method​Type!\]!](https://shopify.dev/docs/api/admin-graphql/latest/enums/DeliveryMethodType)

  required

  Associate the function with one or multiple delivery method types.

* function​Handle

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The handle of the function providing the constraint rule.

* metafields

  [\[Metafield​Input!\]](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/MetafieldInput)

  Default:\[]

  Metafields to associate to the fulfillment constraint rule.

* function​Id

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  Deprecated

***

## Fulfillment​Constraint​Rule​Create​Payload returns

* fulfillment​Constraint​Rule

  [Fulfillment​Constraint​Rule](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentConstraintRule)

  The newly created fulfillment constraint rule.

* user​Errors

  [\[Fulfillment​Constraint​Rule​Create​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentConstraintRuleCreateUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### fulfillmentConstraintRuleCreate reference
