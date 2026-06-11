---
title: inventoryShipment - GraphQL Admin
description: >-
  Retrieves an
  [`InventoryShipment`](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryShipment)
  by ID. Returns tracking details,
  [`InventoryShipmentLineItem`](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryShipmentLineItem)
  objects with quantities, and the shipment's current
  [`InventoryShipmentStatus`](https://shopify.dev/docs/api/admin-graphql/latest/enums/InventoryShipmentStatus).
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/inventoryShipment'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/inventoryShipment.md
---

# inventory​Shipment

query

Requires `read_inventory_shipments` access scope. Also: The user must have permission to view products.

Retrieves an [`InventoryShipment`](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryShipment) by ID. Returns tracking details, [`InventoryShipmentLineItem`](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryShipmentLineItem) objects with quantities, and the shipment's current [`InventoryShipmentStatus`](https://shopify.dev/docs/api/admin-graphql/latest/enums/InventoryShipmentStatus).

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the inventory shipment.

***

## Possible returns

* Inventory​Shipment

  [Inventory​Shipment](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryShipment)

  Represents an inventory shipment.

  * date​Created

    [Date​Time](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    The date the shipment was created in UTC.

  * date​Received

    [Date​Time](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    The date the shipment was initially received in UTC.

  * date​Shipped

    [Date​Time](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    The date the shipment was shipped in UTC.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * line​Items

    [Inventory​Shipment​Line​Item​Connection](https://shopify.dev/docs/api/admin-graphql/latest/connections/InventoryShipmentLineItemConnection)

    The line items included in this shipment.

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      ### Arguments

      The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * after

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * last

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * before

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * reverse

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Default:false

      Reverse the order of the underlying list.

    * sort​Key

      [Shipment​Line​Item​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/ShipmentLineItemSortKeys)

      Default:ID

      Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

    * query

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      A filter made up of terms, connectives, modifiers, and comparators. You can apply one or more filters to a query. Learn more about [Shopify API search syntax](https://shopify.dev/api/usage/search-syntax).

      * * default

          string

        * id

          id

        - Filter by a case-insensitive search of multiple fields in a document.

        - Example:

          * `query=Bob Norman`
          * `query=title:green hoodie`

          Filter by `id` range.

          Example:

          * `id:1234`
          * `id:>=1234`
          * `id:<=1234`

    ***

  * line​Items​Count

    [Count](https://shopify.dev/docs/api/admin-graphql/latest/objects/Count)

    The number of line items associated with the inventory shipment. Limited to a maximum of 10000 by default.

    * query

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      ### Arguments

      A filter made up of terms, connectives, modifiers, and comparators. You can apply one or more filters to a query. Learn more about [Shopify API search syntax](https://shopify.dev/api/usage/search-syntax).

      * * default

          string

        * id

          id

        - Filter by a case-insensitive search of multiple fields in a document.

        - Example:

          * `query=Bob Norman`
          * `query=title:green hoodie`

          Filter by `id` range.

          Example:

          * `id:1234`
          * `id:>=1234`
          * `id:<=1234`

    * limit

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      Default:10000

      The upper bound on count value before returning a result. Use `null` to have no limit.

    ***

  * line​Item​Total​Quantity

    [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    non-null

    The total quantity of all items in the shipment.

  * name

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The name of the inventory shipment.

  * status

    [Inventory​Shipment​Status!](https://shopify.dev/docs/api/admin-graphql/latest/enums/InventoryShipmentStatus)

    non-null

    The current status of the shipment.

  * total​Accepted​Quantity

    [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    non-null

    The total quantity of items accepted across all line items in this shipment.

  * total​Received​Quantity

    [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    non-null

    The total quantity of items received (both accepted and rejected) across all line items in this shipment.

  * total​Rejected​Quantity

    [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    non-null

    The total quantity of items rejected across all line items in this shipment.

  * tracking

    [Inventory​Shipment​Tracking](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryShipmentTracking)

    The tracking information for the shipment.

***

## Examples

* ### inventoryShipment reference
