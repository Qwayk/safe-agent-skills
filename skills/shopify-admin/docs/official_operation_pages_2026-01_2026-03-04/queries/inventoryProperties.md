---
title: inventoryProperties - GraphQL Admin
description: >-
  Returns the shop's inventory configuration, including all inventory quantity
  names. Quantity names represent different [inventory
  states](https://shopify.dev/docs/apps/build/orders-fulfillment/inventory-management-apps#inventory-states)
  that merchants use to track inventory.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/inventoryProperties
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/inventoryProperties.md
---

# inventory​Properties

query

Requires `read_inventory` access scope.

Returns the shop's inventory configuration, including all inventory quantity names. Quantity names represent different [inventory states](https://shopify.dev/docs/apps/build/orders-fulfillment/inventory-management-apps#inventory-states) that merchants use to track inventory.

## Possible returns

* Inventory​Properties

  [Inventory​Properties!](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryProperties)

  General inventory properties for the shop.

  * quantity​Names

    [\[Inventory​Quantity​Name!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryQuantityName)

    non-null

    All the quantity names.

***

## Examples

* ### Get inventory properties for a shop

  #### Description

  Retrieve the details of inventoryProperties.

  #### Query

  ```graphql
  query inventoryProperties {
    inventoryProperties {
      quantityNames {
        belongsTo
        comprises
        displayName
        isInUse
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
  "query": "query inventoryProperties { inventoryProperties { quantityNames { belongsTo comprises displayName isInUse name } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query inventoryProperties {
      inventoryProperties {
        quantityNames {
          belongsTo
          comprises
          displayName
          isInUse
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
    query inventoryProperties {
      inventoryProperties {
        quantityNames {
          belongsTo
          comprises
          displayName
          isInUse
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
    data: `query inventoryProperties {
      inventoryProperties {
        quantityNames {
          belongsTo
          comprises
          displayName
          isInUse
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
  'query inventoryProperties {
    inventoryProperties {
      quantityNames {
        belongsTo
        comprises
        displayName
        isInUse
        name
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "inventoryProperties": {
      "quantityNames": [
        {
          "belongsTo": [
            "on_hand"
          ],
          "comprises": [],
          "displayName": "Available",
          "isInUse": true,
          "name": "available"
        },
        {
          "belongsTo": [
            "on_hand"
          ],
          "comprises": [],
          "displayName": "Committed",
          "isInUse": true,
          "name": "committed"
        },
        {
          "belongsTo": [
            "on_hand"
          ],
          "comprises": [],
          "displayName": "Damaged",
          "isInUse": false,
          "name": "damaged"
        },
        {
          "belongsTo": [],
          "comprises": [],
          "displayName": "Incoming",
          "isInUse": true,
          "name": "incoming"
        },
        {
          "belongsTo": [],
          "comprises": [
            "available",
            "committed",
            "damaged",
            "quality_control",
            "reserved",
            "safety_stock"
          ],
          "displayName": "On hand",
          "isInUse": true,
          "name": "on_hand"
        },
        {
          "belongsTo": [
            "on_hand"
          ],
          "comprises": [],
          "displayName": "Quality control",
          "isInUse": false,
          "name": "quality_control"
        },
        {
          "belongsTo": [
            "on_hand"
          ],
          "comprises": [],
          "displayName": "Reserved",
          "isInUse": true,
          "name": "reserved"
        },
        {
          "belongsTo": [
            "on_hand"
          ],
          "comprises": [],
          "displayName": "Safety stock",
          "isInUse": false,
          "name": "safety_stock"
        }
      ]
    }
  }
  ```

* ### Get inventory quantity names to be used with inventory queries and mutations

  #### Description

  Retrieve the details of inventoryProperties.

  #### Query

  ```graphql
  query inventoryProperties {
    inventoryProperties {
      quantityNames {
        name
        isInUse
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
  "query": "query inventoryProperties { inventoryProperties { quantityNames { name isInUse } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query inventoryProperties {
      inventoryProperties {
        quantityNames {
          name
          isInUse
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
    query inventoryProperties {
      inventoryProperties {
        quantityNames {
          name
          isInUse
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
    data: `query inventoryProperties {
      inventoryProperties {
        quantityNames {
          name
          isInUse
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query inventoryProperties {
    inventoryProperties {
      quantityNames {
        name
        isInUse
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "inventoryProperties": {
      "quantityNames": [
        {
          "name": "available",
          "isInUse": true
        },
        {
          "name": "committed",
          "isInUse": true
        },
        {
          "name": "damaged",
          "isInUse": false
        },
        {
          "name": "incoming",
          "isInUse": true
        },
        {
          "name": "on_hand",
          "isInUse": true
        },
        {
          "name": "quality_control",
          "isInUse": false
        },
        {
          "name": "reserved",
          "isInUse": true
        },
        {
          "name": "safety_stock",
          "isInUse": false
        }
      ]
    }
  }
  ```
