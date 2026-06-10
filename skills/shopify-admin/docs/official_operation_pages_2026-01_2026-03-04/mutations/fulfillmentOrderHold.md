---
title: fulfillmentOrderHold - GraphQL Admin
description: >-
  Applies a fulfillment hold on a fulfillment order.


  As of the

  [2025-01 API
  version](https://shopify.dev/changelog/apply-multiple-holds-to-a-single-fulfillment-order),

  the mutation can be successfully executed on fulfillment orders that are
  already on hold.

  To place multiple holds on a fulfillment order, apps need to supply the

  [handle](https://shopify.dev/api/admin-graphql/latest/objects/FulfillmentHold#field-handle)

  field. Each app can place up to

  10 active holds

  per fulfillment order. If an app attempts to place more than this, the
  mutation will return

  [a user error indicating that the limit has been
  reached](https://shopify.dev/api/admin-graphql/latest/enums/FulfillmentOrderHoldUserErrorCode#value-fulfillmentorderholdlimitreached).

  The app would need to release one of its existing holds before being able to
  apply a new one.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/fulfillmentOrderHold
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/fulfillmentOrderHold.md
---

# fulfillment​Order​Hold

mutation

Requires `write_merchant_managed_fulfillment_orders` access scope or `write_third_party_fulfillment_orders` access scope. Also: The user must have fulfill\_and\_ship\_orders permission.

Applies a fulfillment hold on a fulfillment order.

As of the [2025-01 API version](https://shopify.dev/changelog/apply-multiple-holds-to-a-single-fulfillment-order), the mutation can be successfully executed on fulfillment orders that are already on hold. To place multiple holds on a fulfillment order, apps need to supply the [handle](https://shopify.dev/api/admin-graphql/latest/objects/FulfillmentHold#field-handle) field. Each app can place up to 10 active holds per fulfillment order. If an app attempts to place more than this, the mutation will return [a user error indicating that the limit has been reached](https://shopify.dev/api/admin-graphql/latest/enums/FulfillmentOrderHoldUserErrorCode#value-fulfillmentorderholdlimitreached). The app would need to release one of its existing holds before being able to apply a new one.

## Arguments

* fulfillment​Hold

  [Fulfillment​Order​Hold​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/FulfillmentOrderHoldInput)

  required

  The details of the fulfillment hold applied on the fulfillment order.

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the fulfillment order on which a fulfillment hold is applied.

***

## Fulfillment​Order​Hold​Payload returns

* fulfillment​Hold

  [Fulfillment​Hold](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentHold)

  The fulfillment hold created for the fulfillment order. Null if no hold was created.

* fulfillment​Order

  [Fulfillment​Order](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentOrder)

  The fulfillment order on which a fulfillment hold was applied.

* remaining​Fulfillment​Order

  [Fulfillment​Order](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentOrder)

  The remaining fulfillment order containing the line items to which the hold wasn't applied, if specific line items were specified to be placed on hold.

* user​Errors

  [\[Fulfillment​Order​Hold​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentOrderHoldUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Applies a fulfillment hold on an open fulfillment order

  #### Query

  ```graphql
  mutation FulfillmentOrderHold($fulfillmentHold: FulfillmentOrderHoldInput!, $id: ID!) {
    fulfillmentOrderHold(fulfillmentHold: $fulfillmentHold, id: $id) {
      fulfillmentOrder {
        id
      }
      remainingFulfillmentOrder {
        id
      }
      userErrors {
        field
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "fulfillmentHold": {
      "reason": "INVENTORY_OUT_OF_STOCK",
      "reasonNotes": "Waiting on new shipment"
    },
    "id": "gid://shopify/FulfillmentOrder/1046001479"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation FulfillmentOrderHold($fulfillmentHold: FulfillmentOrderHoldInput!, $id: ID!) { fulfillmentOrderHold(fulfillmentHold: $fulfillmentHold, id: $id) { fulfillmentOrder { id } remainingFulfillmentOrder { id } userErrors { field message } } }",
   "variables": {
      "fulfillmentHold": {
        "reason": "INVENTORY_OUT_OF_STOCK",
        "reasonNotes": "Waiting on new shipment"
      },
      "id": "gid://shopify/FulfillmentOrder/1046001479"
    }
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    mutation FulfillmentOrderHold($fulfillmentHold: FulfillmentOrderHoldInput!, $id: ID!) {
      fulfillmentOrderHold(fulfillmentHold: $fulfillmentHold, id: $id) {
        fulfillmentOrder {
          id
        }
        remainingFulfillmentOrder {
          id
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "fulfillmentHold": {
              "reason": "INVENTORY_OUT_OF_STOCK",
              "reasonNotes": "Waiting on new shipment"
          },
          "id": "gid://shopify/FulfillmentOrder/1046001479"
      },
    },
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
    mutation FulfillmentOrderHold($fulfillmentHold: FulfillmentOrderHoldInput!, $id: ID!) {
      fulfillmentOrderHold(fulfillmentHold: $fulfillmentHold, id: $id) {
        fulfillmentOrder {
          id
        }
        remainingFulfillmentOrder {
          id
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "fulfillmentHold": {
      "reason": "INVENTORY_OUT_OF_STOCK",
      "reasonNotes": "Waiting on new shipment"
    },
    "id": "gid://shopify/FulfillmentOrder/1046001479"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation FulfillmentOrderHold($fulfillmentHold: FulfillmentOrderHoldInput!, $id: ID!) {
        fulfillmentOrderHold(fulfillmentHold: $fulfillmentHold, id: $id) {
          fulfillmentOrder {
            id
          }
          remainingFulfillmentOrder {
            id
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "fulfillmentHold": {
              "reason": "INVENTORY_OUT_OF_STOCK",
              "reasonNotes": "Waiting on new shipment"
          },
          "id": "gid://shopify/FulfillmentOrder/1046001479"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation FulfillmentOrderHold($fulfillmentHold: FulfillmentOrderHoldInput!, $id: ID!) {
    fulfillmentOrderHold(fulfillmentHold: $fulfillmentHold, id: $id) {
      fulfillmentOrder {
        id
      }
      remainingFulfillmentOrder {
        id
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "fulfillmentHold": {
      "reason": "INVENTORY_OUT_OF_STOCK",
      "reasonNotes": "Waiting on new shipment"
    },
    "id": "gid://shopify/FulfillmentOrder/1046001479"
  }'
  ```

  #### Response

  ```json
  {
    "fulfillmentOrderHold": {
      "fulfillmentOrder": {
        "id": "gid://shopify/FulfillmentOrder/1046001479"
      },
      "remainingFulfillmentOrder": null,
      "userErrors": []
    }
  }
  ```

* ### Put a fulfillment order on hold

  #### Description

  A merchant or order management app puts a fulfillment order on hold because the items are out of stock.

  #### Query

  ```graphql
  mutation fulfillmentOrderHold($fulfillmentHold: FulfillmentOrderHoldInput!, $id: ID!) {
    fulfillmentOrderHold(fulfillmentHold: $fulfillmentHold, id: $id) {
      fulfillmentOrder {
        id
        status
        requestStatus
        fulfillmentHolds {
          reason
          reasonNotes
        }
      }
      userErrors {
        field
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "fulfillmentHold": {
      "notifyMerchant": true,
      "reason": "INVENTORY_OUT_OF_STOCK",
      "reasonNotes": "Waiting on new shipment"
    },
    "id": "gid://shopify/FulfillmentOrder/1046001480"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation fulfillmentOrderHold($fulfillmentHold: FulfillmentOrderHoldInput!, $id: ID!) { fulfillmentOrderHold(fulfillmentHold: $fulfillmentHold, id: $id) { fulfillmentOrder { id status requestStatus fulfillmentHolds { reason reasonNotes } } userErrors { field message } } }",
   "variables": {
      "fulfillmentHold": {
        "notifyMerchant": true,
        "reason": "INVENTORY_OUT_OF_STOCK",
        "reasonNotes": "Waiting on new shipment"
      },
      "id": "gid://shopify/FulfillmentOrder/1046001480"
    }
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    mutation fulfillmentOrderHold($fulfillmentHold: FulfillmentOrderHoldInput!, $id: ID!) {
      fulfillmentOrderHold(fulfillmentHold: $fulfillmentHold, id: $id) {
        fulfillmentOrder {
          id
          status
          requestStatus
          fulfillmentHolds {
            reason
            reasonNotes
          }
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "fulfillmentHold": {
              "notifyMerchant": true,
              "reason": "INVENTORY_OUT_OF_STOCK",
              "reasonNotes": "Waiting on new shipment"
          },
          "id": "gid://shopify/FulfillmentOrder/1046001480"
      },
    },
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
    mutation fulfillmentOrderHold($fulfillmentHold: FulfillmentOrderHoldInput!, $id: ID!) {
      fulfillmentOrderHold(fulfillmentHold: $fulfillmentHold, id: $id) {
        fulfillmentOrder {
          id
          status
          requestStatus
          fulfillmentHolds {
            reason
            reasonNotes
          }
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "fulfillmentHold": {
      "notifyMerchant": true,
      "reason": "INVENTORY_OUT_OF_STOCK",
      "reasonNotes": "Waiting on new shipment"
    },
    "id": "gid://shopify/FulfillmentOrder/1046001480"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation fulfillmentOrderHold($fulfillmentHold: FulfillmentOrderHoldInput!, $id: ID!) {
        fulfillmentOrderHold(fulfillmentHold: $fulfillmentHold, id: $id) {
          fulfillmentOrder {
            id
            status
            requestStatus
            fulfillmentHolds {
              reason
              reasonNotes
            }
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "fulfillmentHold": {
              "notifyMerchant": true,
              "reason": "INVENTORY_OUT_OF_STOCK",
              "reasonNotes": "Waiting on new shipment"
          },
          "id": "gid://shopify/FulfillmentOrder/1046001480"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation fulfillmentOrderHold($fulfillmentHold: FulfillmentOrderHoldInput!, $id: ID!) {
    fulfillmentOrderHold(fulfillmentHold: $fulfillmentHold, id: $id) {
      fulfillmentOrder {
        id
        status
        requestStatus
        fulfillmentHolds {
          reason
          reasonNotes
        }
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "fulfillmentHold": {
      "notifyMerchant": true,
      "reason": "INVENTORY_OUT_OF_STOCK",
      "reasonNotes": "Waiting on new shipment"
    },
    "id": "gid://shopify/FulfillmentOrder/1046001480"
  }'
  ```

  #### Response

  ```json
  {
    "fulfillmentOrderHold": {
      "fulfillmentOrder": {
        "id": "gid://shopify/FulfillmentOrder/1046001480",
        "status": "ON_HOLD",
        "requestStatus": "UNSUBMITTED",
        "fulfillmentHolds": [
          {
            "reason": "INVENTORY_OUT_OF_STOCK",
            "reasonNotes": "Waiting on new shipment"
          }
        ]
      },
      "userErrors": []
    }
  }
  ```

* ### fulfillmentOrderHold reference
