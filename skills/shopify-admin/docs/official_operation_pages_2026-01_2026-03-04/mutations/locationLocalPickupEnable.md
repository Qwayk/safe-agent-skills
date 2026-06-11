---
title: locationLocalPickupEnable - GraphQL Admin
description: >-
  Enables local pickup for a location so customers can collect their orders in
  person. Configures the estimated pickup time that customers see at checkout
  and optional instructions for finding or accessing the pickup location.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/locationLocalPickupEnable
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/locationLocalPickupEnable.md
---

# location​Local​Pickup​Enable

mutation

Requires Any of `shipping` access scopes or `manage_delivery_settings` user permission.

Enables local pickup for a location so customers can collect their orders in person. Configures the estimated pickup time that customers see at checkout and optional instructions for finding or accessing the pickup location.

## Arguments

* local​Pickup​Settings

  [Delivery​Location​Local​Pickup​Enable​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/DeliveryLocationLocalPickupEnableInput)

  required

  The settings required to enable local pickup for a location.

***

## Location​Local​Pickup​Enable​Payload returns

* local​Pickup​Settings

  [Delivery​Local​Pickup​Settings](https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliveryLocalPickupSettings)

  The local pickup settings that were enabled.

* user​Errors

  [\[Delivery​Location​Local​Pickup​Settings​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliveryLocationLocalPickupSettingsError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Enable local pickup for a location

  #### Description

  Enable local pickup for a location with a pickup time and instructions.

  #### Query

  ```graphql
  mutation enableLocalPickup($localPickupSettings: DeliveryLocationLocalPickupEnableInput!) {
    locationLocalPickupEnable(localPickupSettings: $localPickupSettings) {
      localPickupSettings {
        pickupTime
        instructions
      }
      userErrors {
        message
        field
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "localPickupSettings": {
      "locationId": "gid://shopify/Location/530388139",
      "pickupTime": "TWENTY_FOUR_HOURS",
      "instructions": "Use side door."
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
  "query": "mutation enableLocalPickup($localPickupSettings: DeliveryLocationLocalPickupEnableInput!) { locationLocalPickupEnable(localPickupSettings: $localPickupSettings) { localPickupSettings { pickupTime instructions } userErrors { message field } } }",
   "variables": {
      "localPickupSettings": {
        "locationId": "gid://shopify/Location/530388139",
        "pickupTime": "TWENTY_FOUR_HOURS",
        "instructions": "Use side door."
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
    mutation enableLocalPickup($localPickupSettings: DeliveryLocationLocalPickupEnableInput!) {
      locationLocalPickupEnable(localPickupSettings: $localPickupSettings) {
        localPickupSettings {
          pickupTime
          instructions
        }
        userErrors {
          message
          field
        }
      }
    }`,
    {
      variables: {
          "localPickupSettings": {
              "locationId": "gid://shopify/Location/530388139",
              "pickupTime": "TWENTY_FOUR_HOURS",
              "instructions": "Use side door."
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
    mutation enableLocalPickup($localPickupSettings: DeliveryLocationLocalPickupEnableInput!) {
      locationLocalPickupEnable(localPickupSettings: $localPickupSettings) {
        localPickupSettings {
          pickupTime
          instructions
        }
        userErrors {
          message
          field
        }
      }
    }
  QUERY

  variables = {
    "localPickupSettings": {
      "locationId": "gid://shopify/Location/530388139",
      "pickupTime": "TWENTY_FOUR_HOURS",
      "instructions": "Use side door."
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation enableLocalPickup($localPickupSettings: DeliveryLocationLocalPickupEnableInput!) {
        locationLocalPickupEnable(localPickupSettings: $localPickupSettings) {
          localPickupSettings {
            pickupTime
            instructions
          }
          userErrors {
            message
            field
          }
        }
      }`,
      "variables": {
          "localPickupSettings": {
              "locationId": "gid://shopify/Location/530388139",
              "pickupTime": "TWENTY_FOUR_HOURS",
              "instructions": "Use side door."
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation enableLocalPickup($localPickupSettings: DeliveryLocationLocalPickupEnableInput!) {
    locationLocalPickupEnable(localPickupSettings: $localPickupSettings) {
      localPickupSettings {
        pickupTime
        instructions
      }
      userErrors {
        message
        field
      }
    }
  }' \
  --variables \
  '{
    "localPickupSettings": {
      "locationId": "gid://shopify/Location/530388139",
      "pickupTime": "TWENTY_FOUR_HOURS",
      "instructions": "Use side door."
    }
  }'
  ```

  #### Response

  ```json
  {
    "locationLocalPickupEnable": {
      "localPickupSettings": {
        "pickupTime": "TWENTY_FOUR_HOURS",
        "instructions": "Use side door."
      },
      "userErrors": []
    }
  }
  ```

* ### Enabling local pickup for an invalid location returns an error

  #### Description

  Enabling local pickup for an invalid location returns an error.

  #### Query

  ```graphql
  mutation enableLocalPickup($localPickupSettings: DeliveryLocationLocalPickupEnableInput!) {
    locationLocalPickupEnable(localPickupSettings: $localPickupSettings) {
      localPickupSettings {
        pickupTime
        instructions
      }
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
    "localPickupSettings": {
      "locationId": "gid://shopify/Location/123",
      "pickupTime": "TWENTY_FOUR_HOURS",
      "instructions": "Use side door."
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
  "query": "mutation enableLocalPickup($localPickupSettings: DeliveryLocationLocalPickupEnableInput!) { locationLocalPickupEnable(localPickupSettings: $localPickupSettings) { localPickupSettings { pickupTime instructions } userErrors { code field message } } }",
   "variables": {
      "localPickupSettings": {
        "locationId": "gid://shopify/Location/123",
        "pickupTime": "TWENTY_FOUR_HOURS",
        "instructions": "Use side door."
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
    mutation enableLocalPickup($localPickupSettings: DeliveryLocationLocalPickupEnableInput!) {
      locationLocalPickupEnable(localPickupSettings: $localPickupSettings) {
        localPickupSettings {
          pickupTime
          instructions
        }
        userErrors {
          code
          field
          message
        }
      }
    }`,
    {
      variables: {
          "localPickupSettings": {
              "locationId": "gid://shopify/Location/123",
              "pickupTime": "TWENTY_FOUR_HOURS",
              "instructions": "Use side door."
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
    mutation enableLocalPickup($localPickupSettings: DeliveryLocationLocalPickupEnableInput!) {
      locationLocalPickupEnable(localPickupSettings: $localPickupSettings) {
        localPickupSettings {
          pickupTime
          instructions
        }
        userErrors {
          code
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "localPickupSettings": {
      "locationId": "gid://shopify/Location/123",
      "pickupTime": "TWENTY_FOUR_HOURS",
      "instructions": "Use side door."
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation enableLocalPickup($localPickupSettings: DeliveryLocationLocalPickupEnableInput!) {
        locationLocalPickupEnable(localPickupSettings: $localPickupSettings) {
          localPickupSettings {
            pickupTime
            instructions
          }
          userErrors {
            code
            field
            message
          }
        }
      }`,
      "variables": {
          "localPickupSettings": {
              "locationId": "gid://shopify/Location/123",
              "pickupTime": "TWENTY_FOUR_HOURS",
              "instructions": "Use side door."
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation enableLocalPickup($localPickupSettings: DeliveryLocationLocalPickupEnableInput!) {
    locationLocalPickupEnable(localPickupSettings: $localPickupSettings) {
      localPickupSettings {
        pickupTime
        instructions
      }
      userErrors {
        code
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "localPickupSettings": {
      "locationId": "gid://shopify/Location/123",
      "pickupTime": "TWENTY_FOUR_HOURS",
      "instructions": "Use side door."
    }
  }'
  ```

  #### Response

  ```json
  {
    "locationLocalPickupEnable": {
      "localPickupSettings": null,
      "userErrors": [
        {
          "code": "ACTIVE_LOCATION_NOT_FOUND",
          "field": [
            "localPickupSettings"
          ],
          "message": "Unable to find an active location for location ID 123"
        }
      ]
    }
  }
  ```

* ### locationLocalPickupEnable reference
