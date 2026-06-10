---
title: fulfillmentOrderAcceptFulfillmentRequest - GraphQL Admin
description: >-
  Accepts a fulfillment request that the fulfillment service has received for a
  [`FulfillmentOrder`](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentOrder)
  which signals that the fulfillment service will process and fulfill the order.
  The fulfillment service can optionally provide a message to the merchant and
  an estimated shipped date when accepting the request.


  Learn more about [accepting fulfillment
  requests](https://shopify.dev/docs/apps/build/orders-fulfillment/fulfillment-service-apps/build-for-fulfillment-services#accept-a-fulfillment-request).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/fulfillmentOrderAcceptFulfillmentRequest
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/fulfillmentOrderAcceptFulfillmentRequest.md
---

# fulfillment​Order​Accept​Fulfillment​Request

mutation

Requires `write_assigned_fulfillment_orders` access scope. Also: The user must have fulfill\_and\_ship\_orders permission.

Accepts a fulfillment request that the fulfillment service has received for a [`FulfillmentOrder`](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentOrder) which signals that the fulfillment service will process and fulfill the order. The fulfillment service can optionally provide a message to the merchant and an estimated shipped date when accepting the request.

Learn more about [accepting fulfillment requests](https://shopify.dev/docs/apps/build/orders-fulfillment/fulfillment-service-apps/build-for-fulfillment-services#accept-a-fulfillment-request).

## Arguments

* estimated​Shipped​At

  [Date​Time](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

  The estimated date and time when the fulfillment order will be shipped.

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the fulfillment order associated with the fulfillment request.

* message

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  An optional reason for accepting the fulfillment request.

***

## Fulfillment​Order​Accept​Fulfillment​Request​Payload returns

* fulfillment​Order

  [Fulfillment​Order](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentOrder)

  The fulfillment order whose fulfillment request was accepted.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Accepts a fulfillment request

  #### Description

  A fulfillment service accepts a fulfillment request for a fulfillment order.

  #### Query

  ```graphql
  mutation fulfillmentOrderAcceptFulfillmentRequest($id: ID!, $message: String) {
    fulfillmentOrderAcceptFulfillmentRequest(id: $id, message: $message) {
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
    "id": "gid://shopify/FulfillmentOrder/1046000778",
    "message": "Fragile"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation fulfillmentOrderAcceptFulfillmentRequest($id: ID!, $message: String) { fulfillmentOrderAcceptFulfillmentRequest(id: $id, message: $message) { fulfillmentOrder { id status requestStatus } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/FulfillmentOrder/1046000778",
      "message": "Fragile"
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
    mutation fulfillmentOrderAcceptFulfillmentRequest($id: ID!, $message: String) {
      fulfillmentOrderAcceptFulfillmentRequest(id: $id, message: $message) {
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
          "id": "gid://shopify/FulfillmentOrder/1046000778",
          "message": "Fragile"
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
    mutation fulfillmentOrderAcceptFulfillmentRequest($id: ID!, $message: String) {
      fulfillmentOrderAcceptFulfillmentRequest(id: $id, message: $message) {
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
    "id": "gid://shopify/FulfillmentOrder/1046000778",
    "message": "Fragile"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation fulfillmentOrderAcceptFulfillmentRequest($id: ID!, $message: String) {
        fulfillmentOrderAcceptFulfillmentRequest(id: $id, message: $message) {
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
          "id": "gid://shopify/FulfillmentOrder/1046000778",
          "message": "Fragile"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation fulfillmentOrderAcceptFulfillmentRequest($id: ID!, $message: String) {
    fulfillmentOrderAcceptFulfillmentRequest(id: $id, message: $message) {
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
    "id": "gid://shopify/FulfillmentOrder/1046000778",
    "message": "Fragile"
  }'
  ```

  #### Response

  ```json
  {
    "fulfillmentOrderAcceptFulfillmentRequest": {
      "fulfillmentOrder": {
        "id": "gid://shopify/FulfillmentOrder/1046000778",
        "status": "IN_PROGRESS",
        "requestStatus": "ACCEPTED"
      },
      "userErrors": []
    }
  }
  ```

* ### fulfillmentOrderAcceptFulfillmentRequest reference
