---
title: fulfillmentOrderSubmitFulfillmentRequest - GraphQL Admin
description: >-
  Sends a fulfillment request to the fulfillment service assigned to a
  [`FulfillmentOrder`](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentOrder).
  The fulfillment service must then accept or reject the request before
  processing can begin.


  You can either request fulfillment for all line items or specify individual
  items with quantities for partial fulfillment. When requesting partial
  fulfillment, Shopify splits the original fulfillment order into two: one with
  the submitted items and another with the remaining unsubmitted items. Include
  an optional message to communicate special instructions to the fulfillment
  service, such as gift wrapping or handling requirements.


  Learn more about [managing fulfillment requests as a fulfillment
  service](https://shopify.dev/docs/apps/build/orders-fulfillment/fulfillment-service-apps/build-for-fulfillment-services#step-4-act-on-fulfillment-requests).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/fulfillmentOrderSubmitFulfillmentRequest
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/fulfillmentOrderSubmitFulfillmentRequest.md
---

# fulfillment​Order​Submit​Fulfillment​Request

mutation

Requires `write_third_party_fulfillment_orders` access scope. Also: The user must have fulfill\_and\_ship\_orders permission.

Sends a fulfillment request to the fulfillment service assigned to a [`FulfillmentOrder`](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentOrder). The fulfillment service must then accept or reject the request before processing can begin.

You can either request fulfillment for all line items or specify individual items with quantities for partial fulfillment. When requesting partial fulfillment, Shopify splits the original fulfillment order into two: one with the submitted items and another with the remaining unsubmitted items. Include an optional message to communicate special instructions to the fulfillment service, such as gift wrapping or handling requirements.

Learn more about [managing fulfillment requests as a fulfillment service](https://shopify.dev/docs/apps/build/orders-fulfillment/fulfillment-service-apps/build-for-fulfillment-services#step-4-act-on-fulfillment-requests).

## Arguments

* fulfillment​Order​Line​Items

  [\[Fulfillment​Order​Line​Item​Input!\]](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/FulfillmentOrderLineItemInput)

  The fulfillment order line items to be requested for fulfillment. If left blank, all line items of the fulfillment order are requested for fulfillment.

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the fulfillment order associated with fulfillment request.

* message

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  An optional message for the fulfillment request.

* notify​Customer

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Whether the customer should be notified when fulfillments are created for this fulfillment order.

***

## Fulfillment​Order​Submit​Fulfillment​Request​Payload returns

* original​Fulfillment​Order

  [Fulfillment​Order](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentOrder)

  The original fulfillment order intended to request fulfillment for.

* submitted​Fulfillment​Order

  [Fulfillment​Order](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentOrder)

  The fulfillment order that was submitted to the fulfillment service. This will be the same as the original fulfillment order field. The exception to this is partial fulfillment requests or fulfillment request for cancelled or incomplete fulfillment orders.

* unsubmitted​Fulfillment​Order

  [Fulfillment​Order](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentOrder)

  This field will only be present for partial fulfillment requests. This will represent the new fulfillment order with the remaining line items not submitted to the fulfillment service.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Sends a fulfillment request

  #### Description

  A merchant or order management app requests to fulfill an entire fulfillment order.

  #### Query

  ```graphql
  mutation fulfillmentOrderSubmitFulfillmentRequest($id: ID!) {
    fulfillmentOrderSubmitFulfillmentRequest(id: $id) {
      originalFulfillmentOrder {
        id
        status
        requestStatus
      }
      submittedFulfillmentOrder {
        id
        status
        requestStatus
      }
      unsubmittedFulfillmentOrder {
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
    "id": "gid://shopify/FulfillmentOrder/1046000784"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation fulfillmentOrderSubmitFulfillmentRequest($id: ID!) { fulfillmentOrderSubmitFulfillmentRequest(id: $id) { originalFulfillmentOrder { id status requestStatus } submittedFulfillmentOrder { id status requestStatus } unsubmittedFulfillmentOrder { id status requestStatus } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/FulfillmentOrder/1046000784"
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
    mutation fulfillmentOrderSubmitFulfillmentRequest($id: ID!) {
      fulfillmentOrderSubmitFulfillmentRequest(id: $id) {
        originalFulfillmentOrder {
          id
          status
          requestStatus
        }
        submittedFulfillmentOrder {
          id
          status
          requestStatus
        }
        unsubmittedFulfillmentOrder {
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
          "id": "gid://shopify/FulfillmentOrder/1046000784"
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
    mutation fulfillmentOrderSubmitFulfillmentRequest($id: ID!) {
      fulfillmentOrderSubmitFulfillmentRequest(id: $id) {
        originalFulfillmentOrder {
          id
          status
          requestStatus
        }
        submittedFulfillmentOrder {
          id
          status
          requestStatus
        }
        unsubmittedFulfillmentOrder {
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
    "id": "gid://shopify/FulfillmentOrder/1046000784"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation fulfillmentOrderSubmitFulfillmentRequest($id: ID!) {
        fulfillmentOrderSubmitFulfillmentRequest(id: $id) {
          originalFulfillmentOrder {
            id
            status
            requestStatus
          }
          submittedFulfillmentOrder {
            id
            status
            requestStatus
          }
          unsubmittedFulfillmentOrder {
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
          "id": "gid://shopify/FulfillmentOrder/1046000784"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation fulfillmentOrderSubmitFulfillmentRequest($id: ID!) {
    fulfillmentOrderSubmitFulfillmentRequest(id: $id) {
      originalFulfillmentOrder {
        id
        status
        requestStatus
      }
      submittedFulfillmentOrder {
        id
        status
        requestStatus
      }
      unsubmittedFulfillmentOrder {
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
    "id": "gid://shopify/FulfillmentOrder/1046000784"
  }'
  ```

  #### Response

  ```json
  {
    "fulfillmentOrderSubmitFulfillmentRequest": {
      "originalFulfillmentOrder": {
        "id": "gid://shopify/FulfillmentOrder/1046000784",
        "status": "OPEN",
        "requestStatus": "SUBMITTED"
      },
      "submittedFulfillmentOrder": {
        "id": "gid://shopify/FulfillmentOrder/1046000784",
        "status": "OPEN",
        "requestStatus": "SUBMITTED"
      },
      "unsubmittedFulfillmentOrder": null,
      "userErrors": []
    }
  }
  ```

* ### Split a fulfillment order into a partial fulfillment request

  #### Description

  A merchant or order management app requests to fulfill only specific line items of a fulfillment order.

  #### Query

  ```graphql
  mutation fulfillmentOrderSubmitFulfillmentRequest($id: ID!, $fulfillmentOrderLineItems: [FulfillmentOrderLineItemInput!]) {
    fulfillmentOrderSubmitFulfillmentRequest(id: $id, fulfillmentOrderLineItems: $fulfillmentOrderLineItems) {
      originalFulfillmentOrder {
        id
        status
        requestStatus
      }
      submittedFulfillmentOrder {
        id
        status
        requestStatus
      }
      unsubmittedFulfillmentOrder {
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
    "id": "gid://shopify/FulfillmentOrder/1046000782",
    "fulfillmentOrderLineItems": [
      {
        "id": "gid://shopify/FulfillmentOrderLineItem/1072503280",
        "quantity": 1
      }
    ]
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation fulfillmentOrderSubmitFulfillmentRequest($id: ID!, $fulfillmentOrderLineItems: [FulfillmentOrderLineItemInput!]) { fulfillmentOrderSubmitFulfillmentRequest(id: $id, fulfillmentOrderLineItems: $fulfillmentOrderLineItems) { originalFulfillmentOrder { id status requestStatus } submittedFulfillmentOrder { id status requestStatus } unsubmittedFulfillmentOrder { id status requestStatus } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/FulfillmentOrder/1046000782",
      "fulfillmentOrderLineItems": [
        {
          "id": "gid://shopify/FulfillmentOrderLineItem/1072503280",
          "quantity": 1
        }
      ]
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
    mutation fulfillmentOrderSubmitFulfillmentRequest($id: ID!, $fulfillmentOrderLineItems: [FulfillmentOrderLineItemInput!]) {
      fulfillmentOrderSubmitFulfillmentRequest(id: $id, fulfillmentOrderLineItems: $fulfillmentOrderLineItems) {
        originalFulfillmentOrder {
          id
          status
          requestStatus
        }
        submittedFulfillmentOrder {
          id
          status
          requestStatus
        }
        unsubmittedFulfillmentOrder {
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
          "id": "gid://shopify/FulfillmentOrder/1046000782",
          "fulfillmentOrderLineItems": [
              {
                  "id": "gid://shopify/FulfillmentOrderLineItem/1072503280",
                  "quantity": 1
              }
          ]
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
    mutation fulfillmentOrderSubmitFulfillmentRequest($id: ID!, $fulfillmentOrderLineItems: [FulfillmentOrderLineItemInput!]) {
      fulfillmentOrderSubmitFulfillmentRequest(id: $id, fulfillmentOrderLineItems: $fulfillmentOrderLineItems) {
        originalFulfillmentOrder {
          id
          status
          requestStatus
        }
        submittedFulfillmentOrder {
          id
          status
          requestStatus
        }
        unsubmittedFulfillmentOrder {
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
    "id": "gid://shopify/FulfillmentOrder/1046000782",
    "fulfillmentOrderLineItems": [
      {
        "id": "gid://shopify/FulfillmentOrderLineItem/1072503280",
        "quantity": 1
      }
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation fulfillmentOrderSubmitFulfillmentRequest($id: ID!, $fulfillmentOrderLineItems: [FulfillmentOrderLineItemInput!]) {
        fulfillmentOrderSubmitFulfillmentRequest(id: $id, fulfillmentOrderLineItems: $fulfillmentOrderLineItems) {
          originalFulfillmentOrder {
            id
            status
            requestStatus
          }
          submittedFulfillmentOrder {
            id
            status
            requestStatus
          }
          unsubmittedFulfillmentOrder {
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
          "id": "gid://shopify/FulfillmentOrder/1046000782",
          "fulfillmentOrderLineItems": [
              {
                  "id": "gid://shopify/FulfillmentOrderLineItem/1072503280",
                  "quantity": 1
              }
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation fulfillmentOrderSubmitFulfillmentRequest($id: ID!, $fulfillmentOrderLineItems: [FulfillmentOrderLineItemInput!]) {
    fulfillmentOrderSubmitFulfillmentRequest(id: $id, fulfillmentOrderLineItems: $fulfillmentOrderLineItems) {
      originalFulfillmentOrder {
        id
        status
        requestStatus
      }
      submittedFulfillmentOrder {
        id
        status
        requestStatus
      }
      unsubmittedFulfillmentOrder {
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
    "id": "gid://shopify/FulfillmentOrder/1046000782",
    "fulfillmentOrderLineItems": [
      {
        "id": "gid://shopify/FulfillmentOrderLineItem/1072503280",
        "quantity": 1
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "fulfillmentOrderSubmitFulfillmentRequest": {
      "originalFulfillmentOrder": {
        "id": "gid://shopify/FulfillmentOrder/1046000782",
        "status": "OPEN",
        "requestStatus": "SUBMITTED"
      },
      "submittedFulfillmentOrder": {
        "id": "gid://shopify/FulfillmentOrder/1046000782",
        "status": "OPEN",
        "requestStatus": "SUBMITTED"
      },
      "unsubmittedFulfillmentOrder": {
        "id": "gid://shopify/FulfillmentOrder/1046000783",
        "status": "OPEN",
        "requestStatus": "UNSUBMITTED"
      },
      "userErrors": []
    }
  }
  ```

* ### fulfillmentOrderSubmitFulfillmentRequest reference
