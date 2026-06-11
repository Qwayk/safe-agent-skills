---
title: menu - GraphQL Admin
description: Returns a `Menu` resource by ID.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/menu'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/menu.md'
---

# menu

query

Returns a `Menu` resource by ID.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the `Menu` to return.

***

## Possible returns

* Menu

  [Menu](https://shopify.dev/docs/api/admin-graphql/latest/objects/Menu)

  Navigation menus that organize links into logical structures to guide customers through a store. Menus serve as the backbone of store navigation, making it easy for customers to find products, pages, and other content through organized hierarchical links.

  For example, a merchant might create a main navigation menu with top-level categories like "Products," "About Us," and "Contact," where each category can contain nested menu items linking to specific collections, pages, or external resources.

  Use the `Menu` object to:

  * Build and customize store navigation structures
  * Organize hierarchical menu systems with nested items
  * Work with default menus that can't be deleted
  * Access menu items for building navigation

  Menus can be designated as default navigation elements (like main menu or footer), which can't be deleted and have restricted handle updates. The handle provides a unique identifier that themes can reference, while the items collection enables nested navigation structures.

  Each menu contains menu items that can link to various resource types. This flexibility lets merchants create navigation experiences that guide customers through their store.

  * handle

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The menu's handle.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * is​Default

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the menu is a default. The handle for default menus can't be updated and default menus can't be deleted.

  * items

    [\[Menu​Item!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MenuItem)

    non-null

    A list of items on the menu sorted by position.

    * limit

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      ### Arguments

      The number of menu items to be returned.

    ***

  * title

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The menu's title.

  * translations

    [\[Translation!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Translation)

    non-null

    The published translations associated with the resource.

    * locale

      [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      required

      ### Arguments

      Filters translations locale.

    * market​Id

      [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

      Filters translations by market ID. Use this argument to retrieve content specific to a market.

    ***

***

## Examples

* ### menu reference
