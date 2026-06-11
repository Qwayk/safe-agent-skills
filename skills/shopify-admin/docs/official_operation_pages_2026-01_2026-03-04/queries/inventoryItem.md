---
title: inventoryItem - GraphQL Admin
description: >-
  Returns an

  [InventoryItem](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryItem)

  object by ID.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/inventoryItem'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/inventoryItem.md'
---

# inventory​Item

query

Returns an [InventoryItem](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryItem) object by ID.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the `InventoryItem` to return.

***

## Possible returns

* Inventory​Item

  [Inventory​Item](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryItem)

  A [product variant's](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant) inventory information across all locations. The inventory item connects the product variant to its [inventory levels](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryLevel) at different locations, tracking stock keeping unit (SKU), whether quantities are tracked, shipping requirements, and customs information for the product.

  Learn more about [inventory object relationships](https://shopify.dev/docs/apps/build/orders-fulfillment/inventory-management-apps/manage-quantities-states#inventory-object-relationships).

  * country​Code​Of​Origin

    [Country​Code](https://shopify.dev/docs/api/admin-graphql/latest/enums/CountryCode)

    The ISO 3166-1 alpha-2 country code of where the item originated from.

  * country​Harmonized​System​Codes

    [Country​Harmonized​System​Code​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/CountryHarmonizedSystemCodeConnection)

    non-null

    A list of country specific harmonized system codes.

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

    ***

  * created​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time when the inventory item was created.

  * duplicate​Sku​Count

    [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    non-null

    The number of inventory items that share the same SKU with this item.

  * harmonized​System​Code

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The harmonized system code of the item. This must be a number between 6 and 13 digits.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * inventory​History​Url

    [URL](https://shopify.dev/docs/api/admin-graphql/latest/scalars/URL)

    The URL that points to the inventory history for the item.

  * inventory​Level

    [Inventory​Level](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryLevel)

    The inventory item's quantities at the specified location.

    * location​Id

      [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

      required

      ### Arguments

      ID of the location for which the inventory level is requested.

    ***

  * inventory​Levels

    [Inventory​Level​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/InventoryLevelConnection)

    non-null

    A list of the inventory item's quantities for each location that the inventory item can be stocked at.

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

    * query

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      A filter made up of terms, connectives, modifiers, and comparators. You can apply one or more filters to a query. Learn more about [Shopify API search syntax](https://shopify.dev/api/usage/search-syntax).

      * created\_at

        time

      * * id

          id

        * inventory\_group\_id

          id

        - Filter by `id` range.

        - Example:
          * `id:1234`
          * `id:>=1234`
          * `id:<=1234`

      * inventory\_item\_id

        id

      * updated\_at

        time

    ***

  * legacy​Resource​Id

    [Unsigned​Int64!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/UnsignedInt64)

    non-null

    The ID of the corresponding resource in the REST Admin API.

  * locations​Count

    [Count](https://shopify.dev/docs/api/admin-graphql/latest/objects/Count)

    The number of locations where this inventory item is stocked.

  * measurement

    [Inventory​Item​Measurement!](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryItemMeasurement)

    non-null

    The packaging dimensions of the inventory item.

  * province​Code​Of​Origin

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The ISO 3166-2 alpha-2 province code of where the item originated from.

  * requires​Shipping

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the inventory item requires shipping.

  * sku

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    Inventory item SKU. Case-sensitive string.

  * tracked

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether inventory levels are tracked for the item.

  * tracked​Editable

    [Editable​Property!](https://shopify.dev/docs/api/admin-graphql/latest/objects/EditableProperty)

    non-null

    Whether the value of the `tracked` field for the inventory item can be changed.

  * unit​Cost

    [Money​V2](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyV2)

    Unit cost associated with the inventory item. Note: the user must have "View product costs" permission granted in order to access this field once product granular permissions are enabled.

  * updated​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time when the inventory item was updated.

  * variants

    [Product​Variant​Connection](https://shopify.dev/docs/api/admin-graphql/latest/connections/ProductVariantConnection)

    A paginated list of the variants that reference this inventory item.

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

    ***

  * variant

    [Product​Variant!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant)

    non-nullDeprecated

***

## Examples

* ### Get details about a specified inventory item

  #### Query

  ```graphql
  query inventoryItem {
    inventoryItem(id: "gid://shopify/InventoryItem/30322695") {
      id
      tracked
      sku
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
  "query": "query inventoryItem { inventoryItem(id: \"gid://shopify/InventoryItem/30322695\") { id tracked sku } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query inventoryItem {
      inventoryItem(id: "gid://shopify/InventoryItem/30322695") {
        id
        tracked
        sku
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
    query inventoryItem {
      inventoryItem(id: "gid://shopify/InventoryItem/30322695") {
        id
        tracked
        sku
      }
    }
  QUERY

  response = client.query(query: query)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: `query inventoryItem {
      inventoryItem(id: "gid://shopify/InventoryItem/30322695") {
        id
        tracked
        sku
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query inventoryItem {
    inventoryItem(id: "gid://shopify/InventoryItem/30322695") {
      id
      tracked
      sku
    }
  }'
  ```

  #### Response

  ```json
  {
    "inventoryItem": {
      "id": "gid://shopify/InventoryItem/30322695",
      "tracked": true,
      "sku": "element-151"
    }
  }
  ```

* ### Get inventory item levels and product/variant information

  #### Query

  ```graphql
  query inventoryItemToProductVariant {
    inventoryItem(id: "gid://shopify/InventoryItem/30322695") {
      id
      inventoryLevels(first: 1) {
        edges {
          node {
            id
            location {
              id
              name
            }
            quantities(names: ["available", "committed", "incoming", "on_hand", "reserved"]) {
              name
              quantity
            }
          }
        }
      }
      variant {
        id
        title
        product {
          id
          title
        }
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
  "query": "query inventoryItemToProductVariant { inventoryItem(id: \"gid://shopify/InventoryItem/30322695\") { id inventoryLevels(first: 1) { edges { node { id location { id name } quantities(names: [\"available\", \"committed\", \"incoming\", \"on_hand\", \"reserved\"]) { name quantity } } } } variant { id title product { id title } } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query inventoryItemToProductVariant {
      inventoryItem(id: "gid://shopify/InventoryItem/30322695") {
        id
        inventoryLevels(first: 1) {
          edges {
            node {
              id
              location {
                id
                name
              }
              quantities(names: ["available", "committed", "incoming", "on_hand", "reserved"]) {
                name
                quantity
              }
            }
          }
        }
        variant {
          id
          title
          product {
            id
            title
          }
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
    query inventoryItemToProductVariant {
      inventoryItem(id: "gid://shopify/InventoryItem/30322695") {
        id
        inventoryLevels(first: 1) {
          edges {
            node {
              id
              location {
                id
                name
              }
              quantities(names: ["available", "committed", "incoming", "on_hand", "reserved"]) {
                name
                quantity
              }
            }
          }
        }
        variant {
          id
          title
          product {
            id
            title
          }
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
    data: `query inventoryItemToProductVariant {
      inventoryItem(id: "gid://shopify/InventoryItem/30322695") {
        id
        inventoryLevels(first: 1) {
          edges {
            node {
              id
              location {
                id
                name
              }
              quantities(names: ["available", "committed", "incoming", "on_hand", "reserved"]) {
                name
                quantity
              }
            }
          }
        }
        variant {
          id
          title
          product {
            id
            title
          }
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query inventoryItemToProductVariant {
    inventoryItem(id: "gid://shopify/InventoryItem/30322695") {
      id
      inventoryLevels(first: 1) {
        edges {
          node {
            id
            location {
              id
              name
            }
            quantities(names: ["available", "committed", "incoming", "on_hand", "reserved"]) {
              name
              quantity
            }
          }
        }
      }
      variant {
        id
        title
        product {
          id
          title
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "inventoryItem": {
      "id": "gid://shopify/InventoryItem/30322695",
      "inventoryLevels": {
        "edges": [
          {
            "node": {
              "id": "gid://shopify/InventoryLevel/523463154?inventory_item_id=30322695",
              "location": {
                "id": "gid://shopify/Location/346779380",
                "name": "Ottawa Store"
              },
              "quantities": [
                {
                  "name": "available",
                  "quantity": 2
                },
                {
                  "name": "committed",
                  "quantity": 1
                },
                {
                  "name": "incoming",
                  "quantity": 0
                },
                {
                  "name": "on_hand",
                  "quantity": 33
                },
                {
                  "name": "reserved",
                  "quantity": 30
                }
              ]
            }
          }
        ]
      },
      "variant": {
        "id": "gid://shopify/ProductVariant/30322695",
        "title": "151cm",
        "product": {
          "id": "gid://shopify/Product/20995642",
          "title": "Element"
        }
      }
    }
  }
  ```
