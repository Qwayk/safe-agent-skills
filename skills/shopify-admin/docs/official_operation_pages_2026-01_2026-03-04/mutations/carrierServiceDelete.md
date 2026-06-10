---
title: carrierServiceDelete - GraphQL Admin
description: Removes an existing carrier service.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/carrierServiceDelete
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/carrierServiceDelete.md
---

# carrier​Service​Delete

mutation

Requires `write_shipping` access scope.

Removes an existing carrier service.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The global ID of the carrier service to delete.

***

## Carrier​Service​Delete​Payload returns

* deleted​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of the deleted carrier service.

* user​Errors

  [\[Carrier​Service​Delete​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CarrierServiceDeleteUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Remove an existing CarrierService

  #### Query

  ```graphql
  mutation CarrierServiceDelete($id: ID!) {
    carrierServiceDelete(id: $id) {
      deletedId
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
    "id": "gid://shopify/DeliveryCarrierService/1036895097"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation CarrierServiceDelete($id: ID!) { carrierServiceDelete(id: $id) { deletedId userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/DeliveryCarrierService/1036895097"
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
    mutation CarrierServiceDelete($id: ID!) {
      carrierServiceDelete(id: $id) {
        deletedId
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/DeliveryCarrierService/1036895097"
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
    mutation CarrierServiceDelete($id: ID!) {
      carrierServiceDelete(id: $id) {
        deletedId
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/DeliveryCarrierService/1036895097"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation CarrierServiceDelete($id: ID!) {
        carrierServiceDelete(id: $id) {
          deletedId
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/DeliveryCarrierService/1036895097"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation CarrierServiceDelete($id: ID!) {
    carrierServiceDelete(id: $id) {
      deletedId
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/DeliveryCarrierService/1036895097"
  }'
  ```

  #### Response

  ```json
  {
    "carrierServiceDelete": {
      "deletedId": "gid://shopify/DeliveryCarrierService/1036895097",
      "userErrors": []
    }
  }
  ```

* ### carrierServiceDelete reference
