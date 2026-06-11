---
title: cartTransformDelete - GraphQL Admin
description: >-
  Removes an existing cart transform function from the merchant's store,
  disabling any customized bundle or cart modification logic it provided. This
  mutation persistently deletes the transform configuration and stops all
  associated cart processing.


  For example, when discontinuing a bundle app or removing specific
  merchandising features, you would delete the corresponding cart transform to
  ensure customers no longer see the bundled products or modified cart behavior.


  Use `CartTransformDelete` to:

  - Deactivate customized bundle logic when removing app features

  - Clean up unused transform functions

  - Disable cart modifications during app uninstallation

  - Remove outdated merchandising strategies

  - Restore default cart behavior for merchants


  The deletion processes immediately and returns the ID of the removed cart
  transform for confirmation. Once deleted, the transform function stops
  processing new cart operations, though existing cart sessions may retain their
  current state until refresh. This ensures a clean transition without
  disrupting active customer sessions.


  Consider the timing of deletions carefully, as removing transforms during peak
  shopping periods could affect customer experience if they have active carts
  with transformed items.


  Learn more about [managing cart
  transforms](https://shopify.dev/docs/apps/selling-strategies/bundles).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/cartTransformDelete
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/cartTransformDelete.md
---

# cart​Transform​Delete

mutation

Requires `write_cart_transforms` access scope. Also: The user must have products and preferences permission to delete a cart transform function.

Removes an existing cart transform function from the merchant's store, disabling any customized bundle or cart modification logic it provided. This mutation persistently deletes the transform configuration and stops all associated cart processing.

For example, when discontinuing a bundle app or removing specific merchandising features, you would delete the corresponding cart transform to ensure customers no longer see the bundled products or modified cart behavior.

Use `CartTransformDelete` to:

* Deactivate customized bundle logic when removing app features
* Clean up unused transform functions
* Disable cart modifications during app uninstallation
* Remove outdated merchandising strategies
* Restore default cart behavior for merchants

The deletion processes immediately and returns the ID of the removed cart transform for confirmation. Once deleted, the transform function stops processing new cart operations, though existing cart sessions may retain their current state until refresh. This ensures a clean transition without disrupting active customer sessions.

Consider the timing of deletions carefully, as removing transforms during peak shopping periods could affect customer experience if they have active carts with transformed items.

Learn more about [managing cart transforms](https://shopify.dev/docs/apps/selling-strategies/bundles).

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  A globally-unique identifier for the cart transform.

***

## Cart​Transform​Delete​Payload returns

* deleted​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The globally-unique ID for the deleted cart transform.

* user​Errors

  [\[Cart​Transform​Delete​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CartTransformDeleteUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### cartTransformDelete reference
