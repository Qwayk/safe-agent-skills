---
title: fulfillmentOrderClose - GraphQL Admin
description: >-
  Marks an in-progress fulfillment order as incomplete,

  indicating the fulfillment service is unable to ship any remaining items,

  and closes the fulfillment request.


  This mutation can only be called for fulfillment orders that meet the
  following criteria:
    - Assigned to a fulfillment service location,
    - The fulfillment request has been accepted,
    - The fulfillment order status is `IN_PROGRESS`.

  This mutation can only be called by the fulfillment service app that accepted
  the fulfillment request.

  Calling this mutation returns the control of the fulfillment order to the
  merchant, allowing them to

  move the fulfillment order line items to another location and fulfill from
  there,

  remove and refund the line items, or to request fulfillment from the same
  fulfillment service again.


  Closing a fulfillment order is explained in

  [the fulfillment service
  guide](https://shopify.dev/apps/build/orders-fulfillment/fulfillment-service-apps/build-for-fulfillment-services#step-7-optional-close-a-fulfillment-order).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/fulfillmentOrderClose
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/fulfillmentOrderClose.md
---

# fulfillment​Order​Close

mutation

Requires `write_assigned_fulfillment_orders` access scope. Also: The user must have fulfill\_and\_ship\_orders permission.

Marks an in-progress fulfillment order as incomplete, indicating the fulfillment service is unable to ship any remaining items, and closes the fulfillment request.

This mutation can only be called for fulfillment orders that meet the following criteria:

* Assigned to a fulfillment service location,
* The fulfillment request has been accepted,
* The fulfillment order status is `IN_PROGRESS`.

This mutation can only be called by the fulfillment service app that accepted the fulfillment request. Calling this mutation returns the control of the fulfillment order to the merchant, allowing them to move the fulfillment order line items to another location and fulfill from there, remove and refund the line items, or to request fulfillment from the same fulfillment service again.

Closing a fulfillment order is explained in [the fulfillment service guide](https://shopify.dev/apps/build/orders-fulfillment/fulfillment-service-apps/build-for-fulfillment-services#step-7-optional-close-a-fulfillment-order).

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the fulfillment order to mark as incomplete.

* message

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  An optional reason for marking the fulfillment order as incomplete.

***

## Fulfillment​Order​Close​Payload returns

* fulfillment​Order

  [Fulfillment​Order](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentOrder)

  The fulfillment order that was marked as incomplete.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Marks a fulfillment order as incomplete

  #### Description

  A fulfillment app marks an accepted fulfillment order as incomplete.

  #### Query

  ```graphql
  mutation fulfillmentOrderClose($id: ID!, $message: String) {
    fulfillmentOrderClose(id: $id, message: $message) {
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
    "id": "gid://shopify/FulfillmentOrder/1046000779",
    "message": "Out of Stock"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation fulfillmentOrderClose($id: ID!, $message: String) { fulfillmentOrderClose(id: $id, message: $message) { fulfillmentOrder { id status requestStatus } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/FulfillmentOrder/1046000779",
      "message": "Out of Stock"
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
    mutation fulfillmentOrderClose($id: ID!, $message: String) {
      fulfillmentOrderClose(id: $id, message: $message) {
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
          "id": "gid://shopify/FulfillmentOrder/1046000779",
          "message": "Out of Stock"
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
    mutation fulfillmentOrderClose($id: ID!, $message: String) {
      fulfillmentOrderClose(id: $id, message: $message) {
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
    "id": "gid://shopify/FulfillmentOrder/1046000779",
    "message": "Out of Stock"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation fulfillmentOrderClose($id: ID!, $message: String) {
        fulfillmentOrderClose(id: $id, message: $message) {
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
          "id": "gid://shopify/FulfillmentOrder/1046000779",
          "message": "Out of Stock"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation fulfillmentOrderClose($id: ID!, $message: String) {
    fulfillmentOrderClose(id: $id, message: $message) {
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
    "id": "gid://shopify/FulfillmentOrder/1046000779",
    "message": "Out of Stock"
  }'
  ```

  #### Response

  ```json
  {
    "fulfillmentOrderClose": {
      "fulfillmentOrder": {
        "id": "gid://shopify/FulfillmentOrder/1046000779",
        "status": "INCOMPLETE",
        "requestStatus": "CLOSED"
      },
      "userErrors": []
    }
  }
  ```

* ### fulfillmentOrderClose reference
