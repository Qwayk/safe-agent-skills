---
title: locationEdit - GraphQL Admin
description: >-
  Updates the properties of an existing
  [`Location`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Location).
  You can modify the location's name, address, whether it fulfills online
  orders, and custom
  [`metafields`](https://shopify.dev/docs/apps/build/custom-data).


  Apps that created a
  [`FulfillmentService`](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentService)
  can edit the associated location to ensure accurate representation of their
  fulfillment network.


  > Note:

  > You can't disable the
  [`fulfillsOnlineOrders`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/locationEdit#arguments-input.fields.fulfillsOnlineOrders)
  setting for fulfillment service locations.


  Learn more about [editing locations for fulfillment
  services](https://shopify.dev/docs/apps/build/orders-fulfillment/fulfillment-service-apps/build-for-fulfillment-services#step-2-edit-locations).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/locationEdit'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/locationEdit.md'
---

# location​Edit

mutation

Requires `write_locations` access scope or `write_fulfillments` access scope. Also: `write_locations`: access scope is required to modify merchant-managed locations. `write_fulfillments`: apps can edit the locations associated with their fulfillment services if they have this scope. Only the app that created the fulfillment service can edit its associated location.

Updates the properties of an existing [`Location`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Location). You can modify the location's name, address, whether it fulfills online orders, and custom [`metafields`](https://shopify.dev/docs/apps/build/custom-data).

Apps that created a [`FulfillmentService`](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentService) can edit the associated location to ensure accurate representation of their fulfillment network.

***

**Note:** You can\&#39;t disable the \<a href="https://shopify.dev/docs/api/admin-graphql/latest/mutations/locationEdit#arguments-input.fields.fulfillsOnlineOrders">\<code>\<span class="PreventFireFoxApplyingGapToWBR">fulfills\<wbr/>Online\<wbr/>Orders\</span>\</code>\</a> setting for fulfillment service locations.

***

Learn more about [editing locations for fulfillment services](https://shopify.dev/docs/apps/build/orders-fulfillment/fulfillment-service-apps/build-for-fulfillment-services#step-2-edit-locations).

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of a location to edit.

* input

  [Location​Edit​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/LocationEditInput)

  required

  The updated properties for the location.

***

## Location​Edit​Payload returns

* location

  [Location](https://shopify.dev/docs/api/admin-graphql/latest/objects/Location)

  The location that was edited.

* user​Errors

  [\[Location​Edit​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/LocationEditUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create a new metafield and update another on an existing location

  #### Description

  Create a new metafield \`my\_field.delivery\_type\` and update an existing metafield \`global.store\_hours\` on a specific location. Alternatively, refer to the \[metafieldsSet]\(https://shopify.dev/api/admin-graphql/latest/mutations/metafieldsset) mutation to create and/or update metafields on location resources.

  #### Query

  ```graphql
  mutation updateLocationMetafields($input: LocationEditInput!, $ownerId: ID!) {
    locationEdit(input: $input, id: $ownerId) {
      location {
        id
        metafields(first: 3) {
          edges {
            node {
              id
              namespace
              key
              value
            }
          }
        }
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
    "input": {
      "metafields": [
        {
          "namespace": "my_field",
          "key": "delivery_type",
          "type": "single_line_text_field",
          "value": "local"
        },
        {
          "id": "gid://shopify/Metafield/1069229306",
          "value": "Open from 7am to 10pm"
        }
      ]
    },
    "ownerId": "gid://shopify/Location/346779380"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation updateLocationMetafields($input: LocationEditInput!, $ownerId: ID!) { locationEdit(input: $input, id: $ownerId) { location { id metafields(first: 3) { edges { node { id namespace key value } } } } userErrors { message field } } }",
   "variables": {
      "input": {
        "metafields": [
          {
            "namespace": "my_field",
            "key": "delivery_type",
            "type": "single_line_text_field",
            "value": "local"
          },
          {
            "id": "gid://shopify/Metafield/1069229306",
            "value": "Open from 7am to 10pm"
          }
        ]
      },
      "ownerId": "gid://shopify/Location/346779380"
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
    mutation updateLocationMetafields($input: LocationEditInput!, $ownerId: ID!) {
      locationEdit(input: $input, id: $ownerId) {
        location {
          id
          metafields(first: 3) {
            edges {
              node {
                id
                namespace
                key
                value
              }
            }
          }
        }
        userErrors {
          message
          field
        }
      }
    }`,
    {
      variables: {
          "input": {
              "metafields": [
                  {
                      "namespace": "my_field",
                      "key": "delivery_type",
                      "type": "single_line_text_field",
                      "value": "local"
                  },
                  {
                      "id": "gid://shopify/Metafield/1069229306",
                      "value": "Open from 7am to 10pm"
                  }
              ]
          },
          "ownerId": "gid://shopify/Location/346779380"
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
    mutation updateLocationMetafields($input: LocationEditInput!, $ownerId: ID!) {
      locationEdit(input: $input, id: $ownerId) {
        location {
          id
          metafields(first: 3) {
            edges {
              node {
                id
                namespace
                key
                value
              }
            }
          }
        }
        userErrors {
          message
          field
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "metafields": [
        {
          "namespace": "my_field",
          "key": "delivery_type",
          "type": "single_line_text_field",
          "value": "local"
        },
        {
          "id": "gid://shopify/Metafield/1069229306",
          "value": "Open from 7am to 10pm"
        }
      ]
    },
    "ownerId": "gid://shopify/Location/346779380"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation updateLocationMetafields($input: LocationEditInput!, $ownerId: ID!) {
        locationEdit(input: $input, id: $ownerId) {
          location {
            id
            metafields(first: 3) {
              edges {
                node {
                  id
                  namespace
                  key
                  value
                }
              }
            }
          }
          userErrors {
            message
            field
          }
        }
      }`,
      "variables": {
          "input": {
              "metafields": [
                  {
                      "namespace": "my_field",
                      "key": "delivery_type",
                      "type": "single_line_text_field",
                      "value": "local"
                  },
                  {
                      "id": "gid://shopify/Metafield/1069229306",
                      "value": "Open from 7am to 10pm"
                  }
              ]
          },
          "ownerId": "gid://shopify/Location/346779380"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation updateLocationMetafields($input: LocationEditInput!, $ownerId: ID!) {
    locationEdit(input: $input, id: $ownerId) {
      location {
        id
        metafields(first: 3) {
          edges {
            node {
              id
              namespace
              key
              value
            }
          }
        }
      }
      userErrors {
        message
        field
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "metafields": [
        {
          "namespace": "my_field",
          "key": "delivery_type",
          "type": "single_line_text_field",
          "value": "local"
        },
        {
          "id": "gid://shopify/Metafield/1069229306",
          "value": "Open from 7am to 10pm"
        }
      ]
    },
    "ownerId": "gid://shopify/Location/346779380"
  }'
  ```

  #### Response

  ```json
  {
    "locationEdit": {
      "location": {
        "id": "gid://shopify/Location/346779380",
        "metafields": {
          "edges": [
            {
              "node": {
                "id": "gid://shopify/Metafield/1069229306",
                "namespace": "global",
                "key": "store_hours",
                "value": "Open from 7am to 10pm"
              }
            },
            {
              "node": {
                "id": "gid://shopify/Metafield/1069229307",
                "namespace": "my_field",
                "key": "delivery_type",
                "value": "local"
              }
            }
          ]
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Edit a location and return the location ID

  #### Description

  Edit a location's name, address and fulfillsOnlineOrders status

  #### Query

  ```graphql
  mutation locationEdit {
    locationEdit(id: "gid://shopify/Location/346779380", input: {name: "Shipping Warehouse", address: {address1: "290 Bremner Blvd", city: "Toronto", zip: "M5V 3L9", provinceCode: "ON", countryCode: CA}, fulfillsOnlineOrders: false}) {
      location {
        id
        name
        address {
          address1
          provinceCode
          countryCode
          zip
        }
        fulfillsOnlineOrders
      }
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
  "query": "mutation locationEdit { locationEdit(id: \"gid://shopify/Location/346779380\", input: {name: \"Shipping Warehouse\", address: {address1: \"290 Bremner Blvd\", city: \"Toronto\", zip: \"M5V 3L9\", provinceCode: \"ON\", countryCode: CA}, fulfillsOnlineOrders: false}) { location { id name address { address1 provinceCode countryCode zip } fulfillsOnlineOrders } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    mutation locationEdit {
      locationEdit(id: "gid://shopify/Location/346779380", input: {name: "Shipping Warehouse", address: {address1: "290 Bremner Blvd", city: "Toronto", zip: "M5V 3L9", provinceCode: "ON", countryCode: CA}, fulfillsOnlineOrders: false}) {
        location {
          id
          name
          address {
            address1
            provinceCode
            countryCode
            zip
          }
          fulfillsOnlineOrders
        }
      }
    }`,
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
    mutation locationEdit {
      locationEdit(id: "gid://shopify/Location/346779380", input: {name: "Shipping Warehouse", address: {address1: "290 Bremner Blvd", city: "Toronto", zip: "M5V 3L9", provinceCode: "ON", countryCode: CA}, fulfillsOnlineOrders: false}) {
        location {
          id
          name
          address {
            address1
            provinceCode
            countryCode
            zip
          }
          fulfillsOnlineOrders
        }
      }
    }
  QUERY

  response = client.query(query: query)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: `mutation locationEdit {
      locationEdit(id: "gid://shopify/Location/346779380", input: {name: "Shipping Warehouse", address: {address1: "290 Bremner Blvd", city: "Toronto", zip: "M5V 3L9", provinceCode: "ON", countryCode: CA}, fulfillsOnlineOrders: false}) {
        location {
          id
          name
          address {
            address1
            provinceCode
            countryCode
            zip
          }
          fulfillsOnlineOrders
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation locationEdit {
    locationEdit(id: "gid://shopify/Location/346779380", input: {name: "Shipping Warehouse", address: {address1: "290 Bremner Blvd", city: "Toronto", zip: "M5V 3L9", provinceCode: "ON", countryCode: CA}, fulfillsOnlineOrders: false}) {
      location {
        id
        name
        address {
          address1
          provinceCode
          countryCode
          zip
        }
        fulfillsOnlineOrders
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "locationEdit": {
      "location": {
        "id": "gid://shopify/Location/346779380",
        "name": "Shipping Warehouse",
        "address": {
          "address1": "290 Bremner Blvd",
          "provinceCode": "ON",
          "countryCode": "CA",
          "zip": "M5V 3L9"
        },
        "fulfillsOnlineOrders": false
      }
    }
  }
  ```

* ### locationEdit reference
