---
title: inventoryLevel - GraphQL Admin
description: >-
  Returns an

  [InventoryLevel](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryLevel)

  object by ID.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/inventoryLevel'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/inventoryLevel.md'
---

# inventory​Level

query

Returns an [InventoryLevel](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryLevel) object by ID.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the `InventoryLevel` to return.

***

## Possible returns

* Inventory​Level

  [Inventory​Level](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryLevel)

  The quantities of an inventory item at a specific location. Each inventory level connects one [`InventoryItem`](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryItem) to one [`Location`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Location), tracking multiple quantity states like available, on-hand, incoming, and committed.

  The [`quantities`](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryLevel#field-InventoryLevel.fields.quantities) field provides access to different inventory states. Learn [more about inventory states and relationships](https://shopify.dev/docs/apps/build/orders-fulfillment/inventory-management-apps/manage-quantities-states#inventory-object-relationships).

  * can​Deactivate

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the inventory items associated with the inventory level can be deactivated.

  * created​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time when the inventory level was created.

  * deactivation​Alert

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    Describes either the impact of deactivating the inventory level, or why the inventory level can't be deactivated.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * item

    [Inventory​Item!](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryItem)

    non-null

    Inventory item associated with the inventory level.

  * location

    [Location!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Location)

    non-null

    The location associated with the inventory level.

  * quantities

    [\[Inventory​Quantity!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryQuantity)

    non-null

    The quantity of an inventory item at a specific location, for a quantity [name](https://shopify.dev/docs/apps/fulfillment/inventory-management-apps#inventory-states).

    * names

      [\[String!\]!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      required

      ### Arguments

      The [names](https://shopify.dev/docs/apps/fulfillment/inventory-management-apps#inventory-states) of the requested inventory quantities.

    ***

  * scheduled​Changes

    [Inventory​Scheduled​Change​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/InventoryScheduledChangeConnection)

    non-null

    Scheduled changes for the requested quantity names.

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

      [Scheduled​Change​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/ScheduledChangeSortKeys)

      Default:ID

      Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

    * query

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      A filter made up of terms, connectives, modifiers, and comparators. You can apply one or more filters to a query. Learn more about [Shopify API search syntax](https://shopify.dev/api/usage/search-syntax).

      * expected\_at

        time

      * * id

          id

        * quantity\_names

          string

        - Filter by `id` range.

        - Example:
          * `id:1234`
          * `id:>=1234`
          * `id:<=1234`

    ***

  * updated​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time when the inventory level was updated.

***

## Examples

* ### Get the location, inventory item, and quantities for an inventory level

  #### Query

  ```graphql
  query {
    inventoryLevel(id: "gid://shopify/InventoryLevel/523463154?inventory_item_id=30322695") {
      id
      quantities(names: ["available", "incoming", "committed", "damaged", "on_hand", "quality_control", "reserved", "safety_stock"]) {
        name
        quantity
      }
      item {
        id
        sku
      }
      location {
        id
        name
      }
    }
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query { inventoryLevel(id: \"gid://shopify/InventoryLevel/523463154?inventory_item_id=30322695\") { id quantities(names: [\"available\", \"incoming\", \"committed\", \"damaged\", \"on_hand\", \"quality_control\", \"reserved\", \"safety_stock\"]) { name quantity } item { id sku } location { id name } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query {
      inventoryLevel(id: "gid://shopify/InventoryLevel/523463154?inventory_item_id=30322695") {
        id
        quantities(names: ["available", "incoming", "committed", "damaged", "on_hand", "quality_control", "reserved", "safety_stock"]) {
          name
          quantity
        }
        item {
          id
          sku
        }
        location {
          id
          name
        }
      }
    }`,
    );
    const json = await response.json();
    return json.data;
  }
  ```

  #### Ruby

  ```ruby
  session = ShopifyAPI::Auth::Session.new(
    shop: "your-development-store.myshopify.com",
    access_token: access_token
  )
  client = ShopifyAPI::Clients::Graphql::Admin.new(
    session: session
  )

  query = <<~QUERY
    query {
      inventoryLevel(id: "gid://shopify/InventoryLevel/523463154?inventory_item_id=30322695") {
        id
        quantities(names: ["available", "incoming", "committed", "damaged", "on_hand", "quality_control", "reserved", "safety_stock"]) {
          name
          quantity
        }
        item {
          id
          sku
        }
        location {
          id
          name
        }
      }
    }
  QUERY

  response = client.query(query: query)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: `query {
      inventoryLevel(id: "gid://shopify/InventoryLevel/523463154?inventory_item_id=30322695") {
        id
        quantities(names: ["available", "incoming", "committed", "damaged", "on_hand", "quality_control", "reserved", "safety_stock"]) {
          name
          quantity
        }
        item {
          id
          sku
        }
        location {
          id
          name
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    inventoryLevel(id: "gid://shopify/InventoryLevel/523463154?inventory_item_id=30322695") {
      id
      quantities(names: ["available", "incoming", "committed", "damaged", "on_hand", "quality_control", "reserved", "safety_stock"]) {
        name
        quantity
      }
      item {
        id
        sku
      }
      location {
        id
        name
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "inventoryLevel": {
      "id": "gid://shopify/InventoryLevel/523463154?inventory_item_id=30322695",
      "quantities": [
        {
          "name": "available",
          "quantity": 2
        },
        {
          "name": "incoming",
          "quantity": 146
        },
        {
          "name": "committed",
          "quantity": 1
        },
        {
          "name": "damaged",
          "quantity": 0
        },
        {
          "name": "on_hand",
          "quantity": 33
        },
        {
          "name": "quality_control",
          "quantity": 0
        },
        {
          "name": "reserved",
          "quantity": 30
        },
        {
          "name": "safety_stock",
          "quantity": 0
        }
      ],
      "item": {
        "id": "gid://shopify/InventoryItem/30322695",
        "sku": "element-151"
      },
      "location": {
        "id": "gid://shopify/Location/346779380",
        "name": "Ottawa Store"
      }
    }
  }
  ```
