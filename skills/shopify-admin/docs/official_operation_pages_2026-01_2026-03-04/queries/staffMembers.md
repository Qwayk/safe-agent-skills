---
title: staffMembers - GraphQL Admin
description: >-
  Returns a paginated list of
  [`StaffMember`](https://shopify.dev/docs/api/admin-graphql/latest/objects/StaffMember)
  objects for the shop. Staff members are users who can access the Shopify admin
  to manage store operations.


  Supports filtering by account type, email, and name, with an option to sort
  results. The query returns a
  [`StaffMemberConnection`](https://shopify.dev/docs/api/admin-graphql/latest/connections/StaffMemberConnection)
  for [cursor-based
  pagination](https://shopify.dev/docs/api/usage/pagination-graphql).
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/staffMembers'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/staffMembers.md'
---

# staff​Members

query

Returns a paginated list of [`StaffMember`](https://shopify.dev/docs/api/admin-graphql/latest/objects/StaffMember) objects for the shop. Staff members are users who can access the Shopify admin to manage store operations.

Supports filtering by account type, email, and name, with an option to sort results. The query returns a [`StaffMemberConnection`](https://shopify.dev/docs/api/admin-graphql/latest/connections/StaffMemberConnection) for [cursor-based pagination](https://shopify.dev/docs/api/usage/pagination-graphql).

## StaffMemberConnection arguments

[StaffMemberConnection](https://shopify.dev/docs/api/admin-graphql/latest/connections/StaffMemberConnection)

* after

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* before

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* first

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* last

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* query

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  A filter made up of terms, connectives, modifiers, and comparators. You can apply one or more filters to a query. Learn more about [Shopify API search syntax](https://shopify.dev/api/usage/search-syntax).

  * * account\_type

      string

    * email

      string

    - Filter by account type.

    - Valid values:

      * `collaborator`
      * `collaborator_team_member`
      * `invited`
      * `regular`
      * `requested`
      * `restricted`
      * `saml`

      Filter by email.

  * first\_name

    string

    Filter by first name.

  * * id

      id

    * last\_name

      string

    - Filter by `id` range.

    - Example:

      * `id:1234`
      * `id:>=1234`
      * `id:<=1234`

      Filter by last name.

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

* sort​Key

  [Staff​Members​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/StaffMembersSortKeys)

  Default:ID

  Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

***

## Possible returns

* edges

  [\[Staff​Member​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/StaffMemberEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Staff​Member!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/StaffMember)

  non-null

  A list of nodes that are contained in StaffMemberEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### staffMembers reference
