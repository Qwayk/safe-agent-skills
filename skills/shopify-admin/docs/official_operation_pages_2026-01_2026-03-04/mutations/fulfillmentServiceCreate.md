---
title: fulfillmentServiceCreate - GraphQL Admin
description: >-
  Creates a fulfillment service.


  ## Fulfillment service location


  When creating a fulfillment service, a new location will be automatically
  created on the shop

  and will be associated with this fulfillment service.

  This location will be named after the fulfillment service and inherit the
  shop's address.


  If you are using API version `2023-10` or later, and you need to specify
  custom attributes for the fulfillment service location

  (for example, to change its address to a country different from the shop's
  country),

  use the

  [LocationEdit](https://shopify.dev/api/admin-graphql/latest/mutations/locationEdit)

  mutation after creating the fulfillment service.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/fulfillmentServiceCreate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/fulfillmentServiceCreate.md
---

# fulfillment​Service​Create

mutation

Requires `write_fulfillments` access scope. Also: The user must have fulfill\_and\_ship\_orders permission.

Creates a fulfillment service.

## Fulfillment service location

When creating a fulfillment service, a new location will be automatically created on the shop and will be associated with this fulfillment service. This location will be named after the fulfillment service and inherit the shop's address.

If you are using API version `2023-10` or later, and you need to specify custom attributes for the fulfillment service location (for example, to change its address to a country different from the shop's country), use the [LocationEdit](https://shopify.dev/api/admin-graphql/latest/mutations/locationEdit) mutation after creating the fulfillment service.

## Arguments

* callback​Url

  [URL](https://shopify.dev/docs/api/admin-graphql/latest/scalars/URL)

  The URL to send requests for the fulfillment service.

  If `callbackUrl` is provided:

  * Shopify queries the `callback_url/fetch_tracking_numbers` endpoint to retrieve tracking numbers for orders, if `trackingSupport` is set to `true`.
  * Shopify queries the `callback_url/fetch_stock` endpoint to retrieve inventory levels, if `inventoryManagement` is set to `true`.
  * Shopify uses the `callback_url/fulfillment_order_notification` endpoint to send [fulfillment and cancellation requests](https://shopify.dev/apps/fulfillment/fulfillment-service-apps/manage-fulfillments#step-2-receive-fulfillment-requests-and-cancellations).

  Otherwise, if no `callbackUrl` is provided you need to submit this information via the api:

  * For submitting tracking info and handling fulfillment requests, see our docs on [building for fulfillment services](https://shopify.dev/apps/build/orders-fulfillment/fulfillment-service-apps/build-for-fulfillment-services).
  * For managing inventory quantities, see our docs on [managing inventory quantities and states](https://shopify.dev/apps/build/orders-fulfillment/inventory-management-apps/manage-quantities-states).

* inventory​Management

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Whether the fulfillment service manages product inventory and provides updates to Shopify.

  If `callbackUrl` is provided ([optional as of API version "2026-01"](https://shopify.dev/changelog/fulfillment-service-callback-url-is-now-optional)), Shopify will periodically fetch inventory levels via the callback endpoint.

  If no `callbackUrl` is provided you need to submit this information via the api, see our docs on [managing inventory quantities and states](https://shopify.dev/apps/build/orders-fulfillment/inventory-management-apps/manage-quantities-states).

* name

  [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  required

  The name of the fulfillment service.

* requires​Shipping​Method

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:true

  Whether the fulfillment service requires products to be physically shipped.

* tracking​Support

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Whether the fulfillment service provides tracking numbers for packages.

  If `callbackUrl` is provided ([optional as of API version "2026-01"](https://shopify.dev/changelog/fulfillment-service-callback-url-is-now-optional)), Shopify will periodically fetch tracking numbers via the callback endpoint.

  If no `callbackUrl` is provided you need to submit this information via the api, see our docs on [building for fulfillment services](https://shopify.dev/apps/build/orders-fulfillment/fulfillment-service-apps/build-for-fulfillment-services).

### Deprecated arguments

* fulfillment​Orders​Opt​In

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  DeprecatedDefault:true

* permits​Sku​Sharing

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Deprecated (removal date set)Default:true

***

## Fulfillment​Service​Create​Payload returns

* fulfillment​Service

  [Fulfillment​Service](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentService)

  The created fulfillment service.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create a new FulfillmentService

  #### Description

  A third party app creates a fulfillment service that uses the fulfillment order based workflow.

  #### Query

  ```graphql
  mutation fulfillmentServiceCreate($name: String!, $callbackUrl: URL!) {
    fulfillmentServiceCreate(name: $name, callbackUrl: $callbackUrl) {
      fulfillmentService {
        id
        serviceName
        callbackUrl
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
    "name": "example_fulfillment_service",
    "callbackUrl": "https://callback.org/"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation fulfillmentServiceCreate($name: String!, $callbackUrl: URL!) { fulfillmentServiceCreate(name: $name, callbackUrl: $callbackUrl) { fulfillmentService { id serviceName callbackUrl } userErrors { field message } } }",
   "variables": {
      "name": "example_fulfillment_service",
      "callbackUrl": "https://callback.org/"
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
    mutation fulfillmentServiceCreate($name: String!, $callbackUrl: URL!) {
      fulfillmentServiceCreate(name: $name, callbackUrl: $callbackUrl) {
        fulfillmentService {
          id
          serviceName
          callbackUrl
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "name": "example_fulfillment_service",
          "callbackUrl": "https://callback.org/"
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
    mutation fulfillmentServiceCreate($name: String!, $callbackUrl: URL!) {
      fulfillmentServiceCreate(name: $name, callbackUrl: $callbackUrl) {
        fulfillmentService {
          id
          serviceName
          callbackUrl
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "name": "example_fulfillment_service",
    "callbackUrl": "https://callback.org/"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation fulfillmentServiceCreate($name: String!, $callbackUrl: URL!) {
        fulfillmentServiceCreate(name: $name, callbackUrl: $callbackUrl) {
          fulfillmentService {
            id
            serviceName
            callbackUrl
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "name": "example_fulfillment_service",
          "callbackUrl": "https://callback.org/"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation fulfillmentServiceCreate($name: String!, $callbackUrl: URL!) {
    fulfillmentServiceCreate(name: $name, callbackUrl: $callbackUrl) {
      fulfillmentService {
        id
        serviceName
        callbackUrl
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "name": "example_fulfillment_service",
    "callbackUrl": "https://callback.org/"
  }'
  ```

  #### Response

  ```json
  {
    "fulfillmentServiceCreate": {
      "fulfillmentService": {
        "id": "gid://shopify/FulfillmentService/1061774487?id=true",
        "serviceName": "example_fulfillment_service",
        "callbackUrl": "https://callback.org/"
      },
      "userErrors": []
    }
  }
  ```

* ### fulfillmentServiceCreate reference
