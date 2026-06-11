---
title: fulfillmentOrderReleaseHold - GraphQL Admin
description: Releases the fulfillment hold on a fulfillment order.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/fulfillmentOrderReleaseHold
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/fulfillmentOrderReleaseHold.md
---

# fulfillment​Order​Release​Hold

mutation

Requires `write_merchant_managed_fulfillment_orders` access scope, `write_third_party_fulfillment_orders` access scope or `write_marketplace_fulfillment_orders` access scope. Also: The user must have fulfill\_and\_ship\_orders permission.

Releases the fulfillment hold on a fulfillment order.

## Arguments

* external​Id

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  A configurable ID used to track the automation system releasing this hold.

* hold​Ids

  [\[ID!\]](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The IDs of the fulfillment holds to release.\
  \
  Holds will only be released if they belong to the fulfillment order specified by the `id` argument.\
  \
  **NOTE:** If not supplied, all holds for the fulfillment order will be released. It is highly recommended that apps supply the ids of the holds that they intend to release. Releasing all holds on a fulfillment order will result in the fulfillment order being released prematurely and items being incorrectly fulfilled.

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the fulfillment order for which to release the fulfillment hold.

***

## Fulfillment​Order​Release​Hold​Payload returns

* fulfillment​Order

  [Fulfillment​Order](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentOrder)

  The fulfillment order on which the hold was released.

* user​Errors

  [\[Fulfillment​Order​Release​Hold​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentOrderReleaseHoldUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Release all holds on a fulfillment order

  #### Description

  An app releases a fulfillment order.

  #### Query

  ```graphql
  mutation fulfillmentOrderReleaseHold($id: ID!) {
    fulfillmentOrderReleaseHold(id: $id) {
      fulfillmentOrder {
        id
        status
        requestStatus
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
    "id": "gid://shopify/FulfillmentOrder/564786110"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation fulfillmentOrderReleaseHold($id: ID!) { fulfillmentOrderReleaseHold(id: $id) { fulfillmentOrder { id status requestStatus } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/FulfillmentOrder/564786110"
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
    mutation fulfillmentOrderReleaseHold($id: ID!) {
      fulfillmentOrderReleaseHold(id: $id) {
        fulfillmentOrder {
          id
          status
          requestStatus
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/FulfillmentOrder/564786110"
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
    mutation fulfillmentOrderReleaseHold($id: ID!) {
      fulfillmentOrderReleaseHold(id: $id) {
        fulfillmentOrder {
          id
          status
          requestStatus
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/FulfillmentOrder/564786110"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation fulfillmentOrderReleaseHold($id: ID!) {
        fulfillmentOrderReleaseHold(id: $id) {
          fulfillmentOrder {
            id
            status
            requestStatus
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/FulfillmentOrder/564786110"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation fulfillmentOrderReleaseHold($id: ID!) {
    fulfillmentOrderReleaseHold(id: $id) {
      fulfillmentOrder {
        id
        status
        requestStatus
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/FulfillmentOrder/564786110"
  }'
  ```

  #### Response

  ```json
  {
    "fulfillmentOrderReleaseHold": {
      "fulfillmentOrder": {
        "id": "gid://shopify/FulfillmentOrder/564786110",
        "status": "OPEN",
        "requestStatus": "UNSUBMITTED"
      },
      "userErrors": []
    }
  }
  ```

* ### Releases the fulfillment hold on a fulfillment order

  #### Description

  An app releases a hold on a fulfillment order.

  #### Query

  ```graphql
  mutation {
    fulfillmentOrderReleaseHold(holdIds: ["gid://shopify/FulfillmentHold/172"], id: "gid://shopify/FulfillmentOrder/564786110") {
      fulfillmentOrder {
        id
        status
        requestStatus
      }
      userErrors {
        field
        message
        code
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
  "query": "mutation { fulfillmentOrderReleaseHold(holdIds: [\"gid://shopify/FulfillmentHold/172\"], id: \"gid://shopify/FulfillmentOrder/564786110\") { fulfillmentOrder { id status requestStatus } userErrors { field message code } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    mutation {
      fulfillmentOrderReleaseHold(holdIds: ["gid://shopify/FulfillmentHold/172"], id: "gid://shopify/FulfillmentOrder/564786110") {
        fulfillmentOrder {
          id
          status
          requestStatus
        }
        userErrors {
          field
          message
          code
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
    mutation {
      fulfillmentOrderReleaseHold(holdIds: ["gid://shopify/FulfillmentHold/172"], id: "gid://shopify/FulfillmentOrder/564786110") {
        fulfillmentOrder {
          id
          status
          requestStatus
        }
        userErrors {
          field
          message
          code
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
    data: `mutation {
      fulfillmentOrderReleaseHold(holdIds: ["gid://shopify/FulfillmentHold/172"], id: "gid://shopify/FulfillmentOrder/564786110") {
        fulfillmentOrder {
          id
          status
          requestStatus
        }
        userErrors {
          field
          message
          code
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation {
    fulfillmentOrderReleaseHold(holdIds: ["gid://shopify/FulfillmentHold/172"], id: "gid://shopify/FulfillmentOrder/564786110") {
      fulfillmentOrder {
        id
        status
        requestStatus
      }
      userErrors {
        field
        message
        code
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "fulfillmentOrderReleaseHold": {
      "fulfillmentOrder": {
        "id": "gid://shopify/FulfillmentOrder/564786110",
        "status": "OPEN",
        "requestStatus": "UNSUBMITTED"
      },
      "userErrors": []
    }
  }
  ```

* ### fulfillmentOrderReleaseHold reference
