---
title: inventoryTransfers - GraphQL Admin
description: >-
  Returns a paginated list of
  [`InventoryTransfer`](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryTransfer)
  objects between locations. Transfers track the movement of
  [`InventoryItem`](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryItem)
  objects between
  [`Location`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Location)
  objects.


  Supports filtering transfers using query parameters and sorting by various
  criteria. Use the connection's edges to access transfer details including
  [`InventoryTransferLineItem`](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryTransferLineItem)
  objects, quantities, and shipment status.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/inventoryTransfers'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/inventoryTransfers.md
---

# inventory​Transfers

query

Requires `read_inventory_transfers` access scope. Also: The user must have permission to view products.

Returns a paginated list of [`InventoryTransfer`](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryTransfer) objects between locations. Transfers track the movement of [`InventoryItem`](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryItem) objects between [`Location`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Location) objects.

Supports filtering transfers using query parameters and sorting by various criteria. Use the connection's edges to access transfer details including [`InventoryTransferLineItem`](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryTransferLineItem) objects, quantities, and shipment status.

## InventoryTransferConnection arguments

[InventoryTransferConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/InventoryTransferConnection)

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

  * * default

      string

    * created\_at

      time

    - Filter by a case-insensitive search of multiple fields in a document.

    - Example:
      * `query=Bob Norman`
      * `query=title:green hoodie`

  * destination\_id

    id

  * * id

      id

    * origin\_id

      id

    - Filter by `id` range.

    - Example:
      * `id:1234`
      * `id:>=1234`
      * `id:<=1234`

  * product\_id

    id

  * product\_variant\_id

    id

  * source\_id

    id

  * status

    string

  * * tag

      string

    * tag\_not

      string

    - Filter objects by the `tag` field.

    - Example:

      * `tag:my_tag`

      Filter by objects that don’t have the specified tag.

      Example:

      * `tag_not:my_tag`

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

* saved​Search​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of a [saved search](https://shopify.dev/api/admin-graphql/latest/objects/savedsearch#field-id). The search’s query string is used as the query argument.

* sort​Key

  [Transfer​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/TransferSortKeys)

  Default:ID

  Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

***

## Possible returns

* edges

  [\[Inventory​Transfer​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryTransferEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Inventory​Transfer!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryTransfer)

  non-null

  A list of nodes that are contained in InventoryTransferEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### inventoryTransfers reference
