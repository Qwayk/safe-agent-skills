---
title: fulfillmentServiceUpdate - GraphQL Admin
description: >-
  Updates the
  [`FulfillmentService`](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentService)
  configuration, including its name, callback URL, and operational settings.


  The mutation modifies how the fulfillment service handles inventory tracking,
  shipping requirements, and package tracking support.


  > Note:

  > To update the physical address or other location details of the fulfillment
  service, use the
  [`locationEdit`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/locationEdit)
  mutation instead.


  Learn more about [editing fulfillment service
  locations](https://shopify.dev/docs/apps/build/orders-fulfillment/fulfillment-service-apps/build-for-fulfillment-services#step-2-edit-locations).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/fulfillmentServiceUpdate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/fulfillmentServiceUpdate.md
---

# fulfillment​Service​Update

mutation

Requires `write_fulfillments` access scope. Also: The user must have fulfill\_and\_ship\_orders permission.

Updates the [`FulfillmentService`](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentService) configuration, including its name, callback URL, and operational settings.

The mutation modifies how the fulfillment service handles inventory tracking, shipping requirements, and package tracking support.

***

**Note:** To update the physical address or other location details of the fulfillment service, use the \<a href="https://shopify.dev/docs/api/admin-graphql/latest/mutations/locationEdit">\<code>\<span class="PreventFireFoxApplyingGapToWBR">location\<wbr/>Edit\</span>\</code>\</a> mutation instead.

***

Learn more about [editing fulfillment service locations](https://shopify.dev/docs/apps/build/orders-fulfillment/fulfillment-service-apps/build-for-fulfillment-services#step-2-edit-locations).

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

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The id of the fulfillment service.

* inventory​Management

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Whether the fulfillment service manages product inventory and provides updates to Shopify.

  If `callbackUrl` is provided, Shopify will periodically fetch inventory levels via the callback endpoint.

  If no `callbackUrl` is provided you need to submit this information via the api, see our docs on [managing inventory quantities and states](https://shopify.dev/apps/build/orders-fulfillment/inventory-management-apps/manage-quantities-states).

* name

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The name of the fulfillment service.

* requires​Shipping​Method

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:true

  Whether the fulfillment service requires products to be physically shipped.

* tracking​Support

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Whether the fulfillment service provides tracking numbers for packages.

  If `callbackUrl` is provided, Shopify will periodically fetch tracking numbers via the callback endpoint.

  If no `callbackUrl` is provided you need to submit this information via the api, see our docs on [building for fulfillment services](https://shopify.dev/apps/build/orders-fulfillment/fulfillment-service-apps/build-for-fulfillment-services).

### Deprecated arguments

* fulfillment​Orders​Opt​In

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Deprecated

* permits​Sku​Sharing

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Deprecated (removal date set)

***

## Fulfillment​Service​Update​Payload returns

* fulfillment​Service

  [Fulfillment​Service](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentService)

  The updated fulfillment service.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Modify an existing FulfillmentService

  #### Description

  A fulfillment service app updates the name of its fulfillment service.

  #### Query

  ```graphql
  mutation fulfillmentServiceUpdate($id: ID!, $name: String!) {
    fulfillmentServiceUpdate(id: $id, name: $name) {
      fulfillmentService {
        id
        serviceName
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
    "id": "gid://shopify/FulfillmentService/198258461",
    "name": "My Updated Fulfillment Warehouse"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation fulfillmentServiceUpdate($id: ID!, $name: String!) { fulfillmentServiceUpdate(id: $id, name: $name) { fulfillmentService { id serviceName } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/FulfillmentService/198258461",
      "name": "My Updated Fulfillment Warehouse"
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
    mutation fulfillmentServiceUpdate($id: ID!, $name: String!) {
      fulfillmentServiceUpdate(id: $id, name: $name) {
        fulfillmentService {
          id
          serviceName
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/FulfillmentService/198258461",
          "name": "My Updated Fulfillment Warehouse"
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
    mutation fulfillmentServiceUpdate($id: ID!, $name: String!) {
      fulfillmentServiceUpdate(id: $id, name: $name) {
        fulfillmentService {
          id
          serviceName
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/FulfillmentService/198258461",
    "name": "My Updated Fulfillment Warehouse"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation fulfillmentServiceUpdate($id: ID!, $name: String!) {
        fulfillmentServiceUpdate(id: $id, name: $name) {
          fulfillmentService {
            id
            serviceName
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/FulfillmentService/198258461",
          "name": "My Updated Fulfillment Warehouse"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation fulfillmentServiceUpdate($id: ID!, $name: String!) {
    fulfillmentServiceUpdate(id: $id, name: $name) {
      fulfillmentService {
        id
        serviceName
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/FulfillmentService/198258461",
    "name": "My Updated Fulfillment Warehouse"
  }'
  ```

  #### Response

  ```json
  {
    "fulfillmentServiceUpdate": {
      "fulfillmentService": {
        "id": "gid://shopify/FulfillmentService/198258461?id=true",
        "serviceName": "My Updated Fulfillment Warehouse"
      },
      "userErrors": []
    }
  }
  ```

* ### fulfillmentServiceUpdate reference
