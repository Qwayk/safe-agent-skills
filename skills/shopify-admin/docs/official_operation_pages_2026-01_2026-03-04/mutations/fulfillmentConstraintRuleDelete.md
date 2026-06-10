---
title: fulfillmentConstraintRuleDelete - GraphQL Admin
description: Deletes a fulfillment constraint rule and its metafields.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/fulfillmentConstraintRuleDelete
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/fulfillmentConstraintRuleDelete.md
---

# fulfillment​Constraint​Rule​Delete

mutation

Requires `write_fulfillment_constraint_rules` access scope.

Deletes a fulfillment constraint rule and its metafields.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  A globally-unique identifier for the fulfillment constraint rule.

***

## Fulfillment​Constraint​Rule​Delete​Payload returns

* success

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Whether or not the fulfillment constraint rule was successfully deleted.

* user​Errors

  [\[Fulfillment​Constraint​Rule​Delete​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentConstraintRuleDeleteUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### fulfillmentConstraintRuleDelete reference
