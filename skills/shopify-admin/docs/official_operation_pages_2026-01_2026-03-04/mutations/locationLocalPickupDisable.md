---
title: locationLocalPickupDisable - GraphQL Admin
description: Disables local pickup for a location.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/locationLocalPickupDisable
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/locationLocalPickupDisable.md
---

# location​Local​Pickup​Disable

mutation

Requires Any of `shipping` access scopes or `manage_delivery_settings` user permission.

Disables local pickup for a location.

## Arguments

* location​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the location to disable local pickup for.

***

## Location​Local​Pickup​Disable​Payload returns

* location​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of the location for which local pickup was disabled.

* user​Errors

  [\[Delivery​Location​Local​Pickup​Settings​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliveryLocationLocalPickupSettingsError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Disable local pickup for a location

  #### Description

  Disable local pickup for a valid location.

  #### Query

  ```graphql
  mutation disableLocalPickup($locationId: ID!) {
    locationLocalPickupDisable(locationId: $locationId) {
      locationId
      userErrors {
        code
        field
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "locationId": "gid://shopify/Location/750123840"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation disableLocalPickup($locationId: ID!) { locationLocalPickupDisable(locationId: $locationId) { locationId userErrors { code field message } } }",
   "variables": {
      "locationId": "gid://shopify/Location/750123840"
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
    mutation disableLocalPickup($locationId: ID!) {
      locationLocalPickupDisable(locationId: $locationId) {
        locationId
        userErrors {
          code
          field
          message
        }
      }
    }`,
    {
      variables: {
          "locationId": "gid://shopify/Location/750123840"
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
    mutation disableLocalPickup($locationId: ID!) {
      locationLocalPickupDisable(locationId: $locationId) {
        locationId
        userErrors {
          code
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "locationId": "gid://shopify/Location/750123840"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation disableLocalPickup($locationId: ID!) {
        locationLocalPickupDisable(locationId: $locationId) {
          locationId
          userErrors {
            code
            field
            message
          }
        }
      }`,
      "variables": {
          "locationId": "gid://shopify/Location/750123840"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation disableLocalPickup($locationId: ID!) {
    locationLocalPickupDisable(locationId: $locationId) {
      locationId
      userErrors {
        code
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "locationId": "gid://shopify/Location/750123840"
  }'
  ```

  #### Response

  ```json
  {
    "locationLocalPickupDisable": {
      "locationId": "gid://shopify/Location/750123840",
      "userErrors": []
    }
  }
  ```

* ### Disabling local pickup for an invalid location returns an error

  #### Description

  Disabling local pickup for an invalid location returns an error.

  #### Query

  ```graphql
  mutation disableLocalPickup($locationId: ID!) {
    locationLocalPickupDisable(locationId: $locationId) {
      locationId
      userErrors {
        code
        field
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "locationId": "gid://shopify/Location/123"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation disableLocalPickup($locationId: ID!) { locationLocalPickupDisable(locationId: $locationId) { locationId userErrors { code field message } } }",
   "variables": {
      "locationId": "gid://shopify/Location/123"
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
    mutation disableLocalPickup($locationId: ID!) {
      locationLocalPickupDisable(locationId: $locationId) {
        locationId
        userErrors {
          code
          field
          message
        }
      }
    }`,
    {
      variables: {
          "locationId": "gid://shopify/Location/123"
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
    mutation disableLocalPickup($locationId: ID!) {
      locationLocalPickupDisable(locationId: $locationId) {
        locationId
        userErrors {
          code
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "locationId": "gid://shopify/Location/123"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation disableLocalPickup($locationId: ID!) {
        locationLocalPickupDisable(locationId: $locationId) {
          locationId
          userErrors {
            code
            field
            message
          }
        }
      }`,
      "variables": {
          "locationId": "gid://shopify/Location/123"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation disableLocalPickup($locationId: ID!) {
    locationLocalPickupDisable(locationId: $locationId) {
      locationId
      userErrors {
        code
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "locationId": "gid://shopify/Location/123"
  }'
  ```

  #### Response

  ```json
  {
    "locationLocalPickupDisable": {
      "locationId": null,
      "userErrors": [
        {
          "code": "ACTIVE_LOCATION_NOT_FOUND",
          "field": [
            "locationId"
          ],
          "message": "Unable to find an active location for location ID 123"
        }
      ]
    }
  }
  ```

* ### locationLocalPickupDisable reference
