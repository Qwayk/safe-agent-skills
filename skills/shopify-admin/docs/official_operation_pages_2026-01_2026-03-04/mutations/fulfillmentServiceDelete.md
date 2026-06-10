---
title: fulfillmentServiceDelete - GraphQL Admin
description: Deletes a fulfillment service.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/fulfillmentServiceDelete
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/fulfillmentServiceDelete.md
---

# fulfillment​Service​Delete

mutation

Requires `write_fulfillments` access scope. Also: The user must have fulfill\_and\_ship\_orders permission.

Deletes a fulfillment service.

## Arguments

* destination​Location​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of an active merchant managed location where inventory and commitments will be relocated after the fulfillment service is deleted.

  Inventory will only be transferred if the [`TRANSFER`](https://shopify.dev/api/admin-graphql/latest/enums/FulfillmentServiceDeleteInventoryAction#value-transfer) inventory action has been chosen.

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the fulfillment service to delete.

* inventory​Action

  [Fulfillment​Service​Delete​Inventory​Action](https://shopify.dev/docs/api/admin-graphql/latest/enums/FulfillmentServiceDeleteInventoryAction)

  Default:TRANSFER

  The action to take with the location after the fulfillment service is deleted.

***

## Fulfillment​Service​Delete​Payload returns

* deleted​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of the deleted fulfillment service.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Remove an existing FulfillmentService

  #### Description

  Delete a fulfillment service and relocate inventory and commitments to a new location.

  #### Query

  ```graphql
  mutation fulfillmentServiceDelete($id: ID!, $destinationLocationId: ID) {
    fulfillmentServiceDelete(id: $id, destinationLocationId: $destinationLocationId) {
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
    "destinationLocationId": "gid://shopify/Location/124656943",
    "id": "gid://shopify/FulfillmentService/198258461"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation fulfillmentServiceDelete($id: ID!, $destinationLocationId: ID) { fulfillmentServiceDelete(id: $id, destinationLocationId: $destinationLocationId) { deletedId userErrors { field message } } }",
   "variables": {
      "destinationLocationId": "gid://shopify/Location/124656943",
      "id": "gid://shopify/FulfillmentService/198258461"
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
    mutation fulfillmentServiceDelete($id: ID!, $destinationLocationId: ID) {
      fulfillmentServiceDelete(id: $id, destinationLocationId: $destinationLocationId) {
        deletedId
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "destinationLocationId": "gid://shopify/Location/124656943",
          "id": "gid://shopify/FulfillmentService/198258461"
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
    mutation fulfillmentServiceDelete($id: ID!, $destinationLocationId: ID) {
      fulfillmentServiceDelete(id: $id, destinationLocationId: $destinationLocationId) {
        deletedId
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "destinationLocationId": "gid://shopify/Location/124656943",
    "id": "gid://shopify/FulfillmentService/198258461"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation fulfillmentServiceDelete($id: ID!, $destinationLocationId: ID) {
        fulfillmentServiceDelete(id: $id, destinationLocationId: $destinationLocationId) {
          deletedId
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "destinationLocationId": "gid://shopify/Location/124656943",
          "id": "gid://shopify/FulfillmentService/198258461"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation fulfillmentServiceDelete($id: ID!, $destinationLocationId: ID) {
    fulfillmentServiceDelete(id: $id, destinationLocationId: $destinationLocationId) {
      deletedId
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "destinationLocationId": "gid://shopify/Location/124656943",
    "id": "gid://shopify/FulfillmentService/198258461"
  }'
  ```

  #### Response

  ```json
  {
    "fulfillmentServiceDelete": {
      "deletedId": "gid://shopify/FulfillmentService/198258461",
      "userErrors": []
    }
  }
  ```

* ### fulfillmentServiceDelete reference
