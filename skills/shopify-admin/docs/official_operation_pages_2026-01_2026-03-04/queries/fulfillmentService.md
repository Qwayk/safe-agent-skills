---
title: fulfillmentService - GraphQL Admin
description: >-
  Returns a
  [`FulfillmentService`](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentService)
  by its ID. The service can manage inventory, process fulfillment requests, and
  provide tracking details through callback endpoints or directly calling
  Shopify's APIs.


  When you register a fulfillment service, Shopify automatically creates an
  associated
  [`Location`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Location)
  where fulfillment order's can be assigned to be processed.


  Learn more about [building fulfillment service
  apps](https://shopify.dev/docs/apps/build/orders-fulfillment/fulfillment-service-apps/build-for-fulfillment-services).
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/fulfillmentService'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/fulfillmentService.md
---

# fulfillment​Service

query

Returns a [`FulfillmentService`](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentService) by its ID. The service can manage inventory, process fulfillment requests, and provide tracking details through callback endpoints or directly calling Shopify's APIs.

When you register a fulfillment service, Shopify automatically creates an associated [`Location`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Location) where fulfillment order's can be assigned to be processed.

Learn more about [building fulfillment service apps](https://shopify.dev/docs/apps/build/orders-fulfillment/fulfillment-service-apps/build-for-fulfillment-services).

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the FulfillmentService to return.

***

## Possible returns

* Fulfillment​Service

  [Fulfillment​Service](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentService)

  A **Fulfillment Service** is a third party warehouse that prepares and ships orders on behalf of the store owner. Fulfillment services charge a fee to package and ship items and update product inventory levels. Some well known fulfillment services with Shopify integrations include: Amazon, Shipwire, and Rakuten. When an app registers a new `FulfillmentService` on a store, Shopify automatically creates a `Location` that's associated to the fulfillment service. To learn more about fulfillment services, refer to [Manage fulfillments as a fulfillment service app](https://shopify.dev/apps/fulfillment/fulfillment-service-apps) guide.

  ## Mutations

  You can work with the `FulfillmentService` object with the [fulfillmentServiceCreate](https://shopify.dev/api/admin-graphql/latest/mutations/fulfillmentServiceCreate), [fulfillmentServiceUpdate](https://shopify.dev/api/admin-graphql/latest/mutations/fulfillmentServiceUpdate), and [fulfillmentServiceDelete](https://shopify.dev/api/admin-graphql/latest/mutations/fulfillmentServiceDelete) mutations.

  ## Hosted endpoints

  Fulfillment service providers integrate with Shopify by providing Shopify with a set of hosted endpoints that Shopify can query on certain conditions. These endpoints must have a common prefix, and this prefix should be supplied in the `callbackUrl` parameter in the [fulfillmentServiceCreate](https://shopify.dev/api/admin-graphql/latest/mutations/fulfillmentServiceCreate) mutation.

  * Shopify sends POST requests to the `<callbackUrl>/fulfillment_order_notification` endpoint to notify the fulfillment service about fulfillment requests and fulfillment cancellation requests.

  For more information, refer to [Receive fulfillment requests and cancellations](https://shopify.dev/apps/fulfillment/fulfillment-service-apps/manage-fulfillments#step-2-receive-fulfillment-requests-and-cancellations).

  * Shopify sends GET requests to the `<callbackUrl>/fetch_tracking_numbers` endpoint to retrieve tracking numbers for orders if `trackingSupport` is set to `true`.

  For more information, refer to [Enable tracking support](https://shopify.dev/apps/fulfillment/fulfillment-service-apps/manage-fulfillments#step-8-enable-tracking-support-optional).

  Fulfillment services can also update tracking information using the [fulfillmentTrackingInfoUpdate](https://shopify.dev/api/admin-graphql/latest/mutations/fulfillmentTrackingInfoUpdate) mutation, rather than waiting for Shopify to ask for tracking numbers.

  * Shopify sends GET requests to the `<callbackUrl>/fetch_stock` endpoint to retrieve on hand inventory levels for the fulfillment service location if `inventoryManagement` is set to `true`.

  For more information, refer to [Sharing inventory levels with Shopify](https://shopify.dev/apps/build/orders-fulfillment/fulfillment-service-apps/build-for-fulfillment-services#step-10-optional-share-inventory-levels-with-shopify).

  To make sure you have everything set up correctly, you can test the `callbackUrl`-prefixed endpoints in your development store.

  ## Resources and webhooks

  There are a variety of objects and webhooks that enable a fulfillment service to work. To exchange fulfillment information with Shopify, fulfillment services use the [FulfillmentOrder](https://shopify.dev/api/admin-graphql/latest/objects/FulfillmentOrder), [Fulfillment](https://shopify.dev/api/admin-graphql/latest/objects/Fulfillment) and [Order](https://shopify.dev/api/admin-graphql/latest/objects/Order) objects and related mutations. To act on fulfillment process events that happen on the Shopify side, besides awaiting calls to `callbackUrl`-prefixed endpoints, fulfillment services can subscribe to the [fulfillment order](https://shopify.dev/apps/fulfillment/fulfillment-service-apps/manage-fulfillments#webhooks) and [order](https://shopify.dev/api/admin-rest/latest/resources/webhook) webhooks.

  * callback​Url

    [URL](https://shopify.dev/docs/api/admin-graphql/latest/scalars/URL)

    The callback URL that the fulfillment service has registered for requests. The following considerations apply:

    * Shopify queries the `<callbackUrl>/fetch_tracking_numbers` endpoint to retrieve tracking numbers for orders, if `trackingSupport` is set to `true`.
    * Shopify queries the `<callbackUrl>/fetch_stock` endpoint to retrieve inventory levels, if `inventoryManagement` is set to `true`.
    * Shopify uses the `<callbackUrl>/fulfillment_order_notification` endpoint to send [fulfillment and cancellation requests](https://shopify.dev/apps/build/orders-fulfillment/fulfillment-service-apps/build-for-fulfillment-services#step-9-optional-enable-tracking-support).

  * handle

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    Human-readable unique identifier for this fulfillment service.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    The ID of the fulfillment service.

  * inventory​Management

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the fulfillment service tracks product inventory and provides updates to Shopify.

  * location

    [Location](https://shopify.dev/docs/api/admin-graphql/latest/objects/Location)

    Location associated with the fulfillment service.

  * requires​Shipping​Method

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the fulfillment service requires products to be physically shipped.

  * service​Name

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The name of the fulfillment service as seen by merchants.

  * tracking​Support

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the fulfillment service implemented the /fetch\_tracking\_numbers endpoint.

  * type

    [Fulfillment​Service​Type!](https://shopify.dev/docs/api/admin-graphql/latest/enums/FulfillmentServiceType)

    non-null

    Type associated with the fulfillment service.

  * fulfillment​Orders​Opt​In

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-nullDeprecated

  * permits​Sku​Sharing

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-nullDeprecated (removal date set)

***

## Examples

* ### Receive a single FulfillmentService

  #### Query

  ```graphql
  query FulfillmentServiceShow($id: ID!) {
    fulfillmentService(id: $id) {
      id
      callbackUrl
      fulfillmentOrdersOptIn
      permitsSkuSharing
      handle
      inventoryManagement
      serviceName
      location {
        legacyResourceId
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/FulfillmentService/18961920"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query FulfillmentServiceShow($id: ID!) { fulfillmentService(id: $id) { id callbackUrl fulfillmentOrdersOptIn permitsSkuSharing handle inventoryManagement serviceName location { legacyResourceId } } }",
   "variables": {
      "id": "gid://shopify/FulfillmentService/18961920"
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
    query FulfillmentServiceShow($id: ID!) {
      fulfillmentService(id: $id) {
        id
        callbackUrl
        fulfillmentOrdersOptIn
        permitsSkuSharing
        handle
        inventoryManagement
        serviceName
        location {
          legacyResourceId
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/FulfillmentService/18961920"
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
    query FulfillmentServiceShow($id: ID!) {
      fulfillmentService(id: $id) {
        id
        callbackUrl
        fulfillmentOrdersOptIn
        permitsSkuSharing
        handle
        inventoryManagement
        serviceName
        location {
          legacyResourceId
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/FulfillmentService/18961920"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query FulfillmentServiceShow($id: ID!) {
        fulfillmentService(id: $id) {
          id
          callbackUrl
          fulfillmentOrdersOptIn
          permitsSkuSharing
          handle
          inventoryManagement
          serviceName
          location {
            legacyResourceId
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/FulfillmentService/18961920"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query FulfillmentServiceShow($id: ID!) {
    fulfillmentService(id: $id) {
      id
      callbackUrl
      fulfillmentOrdersOptIn
      permitsSkuSharing
      handle
      inventoryManagement
      serviceName
      location {
        legacyResourceId
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/FulfillmentService/18961920"
  }'
  ```

  #### Response

  ```json
  {
    "fulfillmentService": {
      "id": "gid://shopify/FulfillmentService/18961920?id=true",
      "callbackUrl": "http://shipwire.com",
      "fulfillmentOrdersOptIn": true,
      "permitsSkuSharing": true,
      "handle": "shipwire",
      "inventoryManagement": false,
      "serviceName": "Shipwire",
      "location": {
        "legacyResourceId": "215093630"
      }
    }
  }
  ```
