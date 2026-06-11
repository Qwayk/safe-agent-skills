---
title: appInstallations - GraphQL Admin
description: >-
  A paginated list of
  [`AppInstallation`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppInstallation)
  objects across multiple stores where your app is installed. Use this query to
  monitor installation status, track billing and subscriptions through
  [`AppSubscription`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppSubscription)
  objects, and review granted
  [`AccessScope`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AccessScope)
  objects.


  Filter by
  [`AppInstallationCategory`](https://shopify.dev/docs/api/admin-graphql/latest/enums/AppInstallationCategory)
  to find specific types of installations (such as POS or channel apps) and by
  [`AppInstallationPrivacy`](https://shopify.dev/docs/api/admin-graphql/latest/enums/AppInstallationPrivacy)
  to scope to public or private installations.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/appInstallations'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/appInstallations.md
---

# app​Installations

query

A paginated list of [`AppInstallation`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppInstallation) objects across multiple stores where your app is installed. Use this query to monitor installation status, track billing and subscriptions through [`AppSubscription`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppSubscription) objects, and review granted [`AccessScope`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AccessScope) objects.

Filter by [`AppInstallationCategory`](https://shopify.dev/docs/api/admin-graphql/latest/enums/AppInstallationCategory) to find specific types of installations (such as POS or channel apps) and by [`AppInstallationPrivacy`](https://shopify.dev/docs/api/admin-graphql/latest/enums/AppInstallationPrivacy) to scope to public or private installations.

## AppInstallationConnection arguments

[AppInstallationConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/AppInstallationConnection)

* after

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* before

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* category

  [App​Installation​Category](https://shopify.dev/docs/api/admin-graphql/latest/enums/AppInstallationCategory)

  The category of app installations to fetch.

* first

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* last

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* privacy

  [App​Installation​Privacy](https://shopify.dev/docs/api/admin-graphql/latest/enums/AppInstallationPrivacy)

  Default:PUBLIC

  The privacy level of app installations to fetch.

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

* sort​Key

  [App​Installation​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/AppInstallationSortKeys)

  Default:INSTALLED\_AT

  Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

***

## Possible returns

* edges

  [\[App​Installation​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppInstallationEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[App​Installation!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppInstallation)

  non-null

  A list of nodes that are contained in AppInstallationEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### appInstallations reference
