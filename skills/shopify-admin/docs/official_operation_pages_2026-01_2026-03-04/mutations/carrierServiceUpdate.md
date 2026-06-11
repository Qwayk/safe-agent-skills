---
title: carrierServiceUpdate - GraphQL Admin
description: >-
  Updates a carrier service. Only the app that creates a carrier service can
  update it.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/carrierServiceUpdate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/carrierServiceUpdate.md
---

# carrier​Service​Update

mutation

Requires `write_shipping` access scope.

Updates a carrier service. Only the app that creates a carrier service can update it.

## Arguments

* input

  [Delivery​Carrier​Service​Update​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/DeliveryCarrierServiceUpdateInput)

  required

  The input fields used to update a carrier service.

***

## Carrier​Service​Update​Payload returns

* carrier​Service

  [Delivery​Carrier​Service](https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliveryCarrierService)

  The updated carrier service.

* user​Errors

  [\[Carrier​Service​Update​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CarrierServiceUpdateUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Modify an existing CarrierService

  #### Query

  ```graphql
  mutation CarrierServiceUpdate($input: DeliveryCarrierServiceUpdateInput!) {
    carrierServiceUpdate(input: $input) {
      carrierService {
        id
        name
        callbackUrl
        active
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
    "input": {
      "id": "gid://shopify/DeliveryCarrierService/1036895102",
      "name": "new test carrier service",
      "callbackUrl": "https://new.example.com/",
      "active": true
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
  "query": "mutation CarrierServiceUpdate($input: DeliveryCarrierServiceUpdateInput!) { carrierServiceUpdate(input: $input) { carrierService { id name callbackUrl active } userErrors { field message } } }",
   "variables": {
      "input": {
        "id": "gid://shopify/DeliveryCarrierService/1036895102",
        "name": "new test carrier service",
        "callbackUrl": "https://new.example.com/",
        "active": true
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
    mutation CarrierServiceUpdate($input: DeliveryCarrierServiceUpdateInput!) {
      carrierServiceUpdate(input: $input) {
        carrierService {
          id
          name
          callbackUrl
          active
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "input": {
              "id": "gid://shopify/DeliveryCarrierService/1036895102",
              "name": "new test carrier service",
              "callbackUrl": "https://new.example.com/",
              "active": true
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
    mutation CarrierServiceUpdate($input: DeliveryCarrierServiceUpdateInput!) {
      carrierServiceUpdate(input: $input) {
        carrierService {
          id
          name
          callbackUrl
          active
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "id": "gid://shopify/DeliveryCarrierService/1036895102",
      "name": "new test carrier service",
      "callbackUrl": "https://new.example.com/",
      "active": true
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation CarrierServiceUpdate($input: DeliveryCarrierServiceUpdateInput!) {
        carrierServiceUpdate(input: $input) {
          carrierService {
            id
            name
            callbackUrl
            active
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "input": {
              "id": "gid://shopify/DeliveryCarrierService/1036895102",
              "name": "new test carrier service",
              "callbackUrl": "https://new.example.com/",
              "active": true
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation CarrierServiceUpdate($input: DeliveryCarrierServiceUpdateInput!) {
    carrierServiceUpdate(input: $input) {
      carrierService {
        id
        name
        callbackUrl
        active
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "id": "gid://shopify/DeliveryCarrierService/1036895102",
      "name": "new test carrier service",
      "callbackUrl": "https://new.example.com/",
      "active": true
    }
  }'
  ```

  #### Response

  ```json
  {
    "carrierServiceUpdate": {
      "carrierService": {
        "id": "gid://shopify/DeliveryCarrierService/1036895102",
        "name": "new test carrier service",
        "callbackUrl": "https://new.example.com/",
        "active": true
      },
      "userErrors": []
    }
  }
  ```

* ### carrierServiceUpdate reference
