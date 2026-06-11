---
title: checkoutProfile - GraphQL Admin
description: >-
  Returns a
  [`CheckoutProfile`](https://shopify.dev/docs/api/admin-graphql/latest/objects/CheckoutProfile).
  Checkout profiles define the branding settings and UI extensions for a store's
  checkout experience. Stores can have one published profile that renders on
  their live checkout and multiple draft profiles for testing customizations in
  the checkout editor.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/checkoutProfile'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/checkoutProfile.md'
---

# checkout​Profile

query

Requires access to the checkout and accounts editor.

Returns a [`CheckoutProfile`](https://shopify.dev/docs/api/admin-graphql/latest/objects/CheckoutProfile). Checkout profiles define the branding settings and UI extensions for a store's checkout experience. Stores can have one published profile that renders on their live checkout and multiple draft profiles for testing customizations in the checkout editor.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the checkout profile.

***

## Possible returns

* Checkout​Profile

  [Checkout​Profile](https://shopify.dev/docs/api/admin-graphql/latest/objects/CheckoutProfile)

  A checkout profile defines the branding settings and the UI extensions for a store's checkout. A checkout profile could be published or draft. A store might have at most one published checkout profile, which is used to render their live checkout. The store could also have multiple draft profiles that were created, previewed, and published using the admin checkout editor.

  * created​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time when the checkout profile was created.

  * edited​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time when the checkout profile was last edited.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * is​Published

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the checkout profile is published or not.

  * name

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The profile name.

  * typ​Osp​Pages​Active

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the checkout profile Thank You Page and Order Status Page are actively using extensibility or not.

  * updated​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time when the checkout profile was last updated.

***

## Examples

* ### checkoutProfile reference
