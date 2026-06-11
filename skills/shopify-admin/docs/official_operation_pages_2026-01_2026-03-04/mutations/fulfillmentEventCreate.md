---
title: fulfillmentEventCreate - GraphQL Admin
description: >-
  Creates a
  [`FulfillmentEvent`](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentEvent)
  to track the shipment status and location of items that have shipped. Events
  capture status updates like carrier pickup, in transit, out for delivery, or
  delivered.


  Each event records the timestamp and current status of the
  [`Fulfillment`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Fulfillment).
  You can include optional details such as the location where the event
  occurred, estimated arrival time, and messages for tracking purposes.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/fulfillmentEventCreate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/fulfillmentEventCreate.md
---

# fulfillment​Event​Create

mutation

Requires `write_fulfillments` access scope. Also: The user must have fulfill\_and\_ship\_orders permission.

Creates a [`FulfillmentEvent`](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentEvent) to track the shipment status and location of items that have shipped. Events capture status updates like carrier pickup, in transit, out for delivery, or delivered.

Each event records the timestamp and current status of the [`Fulfillment`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Fulfillment). You can include optional details such as the location where the event occurred, estimated arrival time, and messages for tracking purposes.

## Arguments

* fulfillment​Event

  [Fulfillment​Event​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/FulfillmentEventInput)

  required

  The input fields used to create a fulfillment event for a fulfillment.

***

## Fulfillment​Event​Create​Payload returns

* fulfillment​Event

  [Fulfillment​Event](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentEvent)

  The created fulfillment event.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create fulfillment event when a package is out for delivery

  #### Description

  Create a fulfillment event when the items in a fulfillment are sent out for delivery.

  #### Query

  ```graphql
  mutation fulfillmentEventCreate($fulfillmentEvent: FulfillmentEventInput!) {
    fulfillmentEventCreate(fulfillmentEvent: $fulfillmentEvent) {
      fulfillmentEvent {
        id
        status
        message
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
    "fulfillmentEvent": {
      "fulfillmentId": "gid://shopify/Fulfillment/237894043",
      "address1": "151 O'Connor St",
      "city": "Ottawa",
      "province": "Ontario",
      "country": "Canada",
      "zip": "K2P 2L8",
      "latitude": 45.4191176,
      "longitude": 75.6966166,
      "happenedAt": "2024-03-07T15:50:00Z",
      "estimatedDeliveryAt": "2024-03-07T16:50:00Z",
      "message": "This package is now out for delivery!",
      "status": "OUT_FOR_DELIVERY"
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
  "query": "mutation fulfillmentEventCreate($fulfillmentEvent: FulfillmentEventInput!) { fulfillmentEventCreate(fulfillmentEvent: $fulfillmentEvent) { fulfillmentEvent { id status message } userErrors { field message } } }",
   "variables": {
      "fulfillmentEvent": {
        "fulfillmentId": "gid://shopify/Fulfillment/237894043",
        "address1": "151 O'\''Connor St",
        "city": "Ottawa",
        "province": "Ontario",
        "country": "Canada",
        "zip": "K2P 2L8",
        "latitude": 45.4191176,
        "longitude": 75.6966166,
        "happenedAt": "2024-03-07T15:50:00Z",
        "estimatedDeliveryAt": "2024-03-07T16:50:00Z",
        "message": "This package is now out for delivery!",
        "status": "OUT_FOR_DELIVERY"
      }
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
    mutation fulfillmentEventCreate($fulfillmentEvent: FulfillmentEventInput!) {
      fulfillmentEventCreate(fulfillmentEvent: $fulfillmentEvent) {
        fulfillmentEvent {
          id
          status
          message
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "fulfillmentEvent": {
              "fulfillmentId": "gid://shopify/Fulfillment/237894043",
              "address1": "151 O'Connor St",
              "city": "Ottawa",
              "province": "Ontario",
              "country": "Canada",
              "zip": "K2P 2L8",
              "latitude": 45.4191176,
              "longitude": 75.6966166,
              "happenedAt": "2024-03-07T15:50:00Z",
              "estimatedDeliveryAt": "2024-03-07T16:50:00Z",
              "message": "This package is now out for delivery!",
              "status": "OUT_FOR_DELIVERY"
          }
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
    mutation fulfillmentEventCreate($fulfillmentEvent: FulfillmentEventInput!) {
      fulfillmentEventCreate(fulfillmentEvent: $fulfillmentEvent) {
        fulfillmentEvent {
          id
          status
          message
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "fulfillmentEvent": {
      "fulfillmentId": "gid://shopify/Fulfillment/237894043",
      "address1": "151 O'Connor St",
      "city": "Ottawa",
      "province": "Ontario",
      "country": "Canada",
      "zip": "K2P 2L8",
      "latitude": 45.4191176,
      "longitude": 75.6966166,
      "happenedAt": "2024-03-07T15:50:00Z",
      "estimatedDeliveryAt": "2024-03-07T16:50:00Z",
      "message": "This package is now out for delivery!",
      "status": "OUT_FOR_DELIVERY"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation fulfillmentEventCreate($fulfillmentEvent: FulfillmentEventInput!) {
        fulfillmentEventCreate(fulfillmentEvent: $fulfillmentEvent) {
          fulfillmentEvent {
            id
            status
            message
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "fulfillmentEvent": {
              "fulfillmentId": "gid://shopify/Fulfillment/237894043",
              "address1": "151 O'Connor St",
              "city": "Ottawa",
              "province": "Ontario",
              "country": "Canada",
              "zip": "K2P 2L8",
              "latitude": 45.4191176,
              "longitude": 75.6966166,
              "happenedAt": "2024-03-07T15:50:00Z",
              "estimatedDeliveryAt": "2024-03-07T16:50:00Z",
              "message": "This package is now out for delivery!",
              "status": "OUT_FOR_DELIVERY"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation fulfillmentEventCreate($fulfillmentEvent: FulfillmentEventInput!) {
    fulfillmentEventCreate(fulfillmentEvent: $fulfillmentEvent) {
      fulfillmentEvent {
        id
        status
        message
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "fulfillmentEvent": {
      "fulfillmentId": "gid://shopify/Fulfillment/237894043",
      "address1": "151 O'Connor St",
      "city": "Ottawa",
      "province": "Ontario",
      "country": "Canada",
      "zip": "K2P 2L8",
      "latitude": 45.4191176,
      "longitude": 75.6966166,
      "happenedAt": "2024-03-07T15:50:00Z",
      "estimatedDeliveryAt": "2024-03-07T16:50:00Z",
      "message": "This package is now out for delivery!",
      "status": "OUT_FOR_DELIVERY"
    }
  }'
  ```

  #### Response

  ```json
  {
    "fulfillmentEventCreate": {
      "fulfillmentEvent": {
        "id": "gid://shopify/FulfillmentEvent/944956426",
        "status": "OUT_FOR_DELIVERY",
        "message": "This package is now out for delivery!"
      },
      "userErrors": []
    }
  }
  ```

* ### Creates a fulfillment event

  #### Query

  ```graphql
  mutation fulfillmentEventCreate($fulfillmentEvent: FulfillmentEventInput!) {
    fulfillmentEventCreate(fulfillmentEvent: $fulfillmentEvent) {
      fulfillmentEvent {
        address1
        city
        country
        estimatedDeliveryAt
        happenedAt
        latitude
        longitude
        message
        province
        status
        zip
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
    "fulfillmentEvent": {
      "fulfillmentId": "gid://shopify/Fulfillment/237894043",
      "address1": "150 Elgin St.",
      "city": "Ottawa",
      "country": "Canada",
      "estimatedDeliveryAt": "2024-11-15T23:40:59Z",
      "happenedAt": "2024-11-15T23:40:49Z",
      "latitude": 1.234,
      "longitude": 9.876,
      "message": "In transit",
      "province": "Ontario",
      "status": "IN_TRANSIT",
      "zip": "K2P1L4"
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
  "query": "mutation fulfillmentEventCreate($fulfillmentEvent: FulfillmentEventInput!) { fulfillmentEventCreate(fulfillmentEvent: $fulfillmentEvent) { fulfillmentEvent { address1 city country estimatedDeliveryAt happenedAt latitude longitude message province status zip } userErrors { field message } } }",
   "variables": {
      "fulfillmentEvent": {
        "fulfillmentId": "gid://shopify/Fulfillment/237894043",
        "address1": "150 Elgin St.",
        "city": "Ottawa",
        "country": "Canada",
        "estimatedDeliveryAt": "2024-11-15T23:40:59Z",
        "happenedAt": "2024-11-15T23:40:49Z",
        "latitude": 1.234,
        "longitude": 9.876,
        "message": "In transit",
        "province": "Ontario",
        "status": "IN_TRANSIT",
        "zip": "K2P1L4"
      }
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
    mutation fulfillmentEventCreate($fulfillmentEvent: FulfillmentEventInput!) {
      fulfillmentEventCreate(fulfillmentEvent: $fulfillmentEvent) {
        fulfillmentEvent {
          address1
          city
          country
          estimatedDeliveryAt
          happenedAt
          latitude
          longitude
          message
          province
          status
          zip
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "fulfillmentEvent": {
              "fulfillmentId": "gid://shopify/Fulfillment/237894043",
              "address1": "150 Elgin St.",
              "city": "Ottawa",
              "country": "Canada",
              "estimatedDeliveryAt": "2024-11-15T23:40:59Z",
              "happenedAt": "2024-11-15T23:40:49Z",
              "latitude": 1.234,
              "longitude": 9.876,
              "message": "In transit",
              "province": "Ontario",
              "status": "IN_TRANSIT",
              "zip": "K2P1L4"
          }
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
    mutation fulfillmentEventCreate($fulfillmentEvent: FulfillmentEventInput!) {
      fulfillmentEventCreate(fulfillmentEvent: $fulfillmentEvent) {
        fulfillmentEvent {
          address1
          city
          country
          estimatedDeliveryAt
          happenedAt
          latitude
          longitude
          message
          province
          status
          zip
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "fulfillmentEvent": {
      "fulfillmentId": "gid://shopify/Fulfillment/237894043",
      "address1": "150 Elgin St.",
      "city": "Ottawa",
      "country": "Canada",
      "estimatedDeliveryAt": "2024-11-15T23:40:59Z",
      "happenedAt": "2024-11-15T23:40:49Z",
      "latitude": 1.234,
      "longitude": 9.876,
      "message": "In transit",
      "province": "Ontario",
      "status": "IN_TRANSIT",
      "zip": "K2P1L4"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation fulfillmentEventCreate($fulfillmentEvent: FulfillmentEventInput!) {
        fulfillmentEventCreate(fulfillmentEvent: $fulfillmentEvent) {
          fulfillmentEvent {
            address1
            city
            country
            estimatedDeliveryAt
            happenedAt
            latitude
            longitude
            message
            province
            status
            zip
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "fulfillmentEvent": {
              "fulfillmentId": "gid://shopify/Fulfillment/237894043",
              "address1": "150 Elgin St.",
              "city": "Ottawa",
              "country": "Canada",
              "estimatedDeliveryAt": "2024-11-15T23:40:59Z",
              "happenedAt": "2024-11-15T23:40:49Z",
              "latitude": 1.234,
              "longitude": 9.876,
              "message": "In transit",
              "province": "Ontario",
              "status": "IN_TRANSIT",
              "zip": "K2P1L4"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation fulfillmentEventCreate($fulfillmentEvent: FulfillmentEventInput!) {
    fulfillmentEventCreate(fulfillmentEvent: $fulfillmentEvent) {
      fulfillmentEvent {
        address1
        city
        country
        estimatedDeliveryAt
        happenedAt
        latitude
        longitude
        message
        province
        status
        zip
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "fulfillmentEvent": {
      "fulfillmentId": "gid://shopify/Fulfillment/237894043",
      "address1": "150 Elgin St.",
      "city": "Ottawa",
      "country": "Canada",
      "estimatedDeliveryAt": "2024-11-15T23:40:59Z",
      "happenedAt": "2024-11-15T23:40:49Z",
      "latitude": 1.234,
      "longitude": 9.876,
      "message": "In transit",
      "province": "Ontario",
      "status": "IN_TRANSIT",
      "zip": "K2P1L4"
    }
  }'
  ```

  #### Response

  ```json
  {
    "fulfillmentEventCreate": {
      "fulfillmentEvent": {
        "address1": "150 Elgin St.",
        "city": "Ottawa",
        "country": "Canada",
        "estimatedDeliveryAt": "2024-11-15T23:40:59Z",
        "happenedAt": "2024-11-15T23:40:49Z",
        "latitude": 1.234,
        "longitude": 9.876,
        "message": "In transit",
        "province": "Ontario",
        "status": "IN_TRANSIT",
        "zip": "K2P1L4"
      },
      "userErrors": []
    }
  }
  ```

* ### fulfillmentEventCreate reference
