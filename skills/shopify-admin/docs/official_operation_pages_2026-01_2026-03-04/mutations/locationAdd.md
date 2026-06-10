---
title: locationAdd - GraphQL Admin
description: >-
  Adds a new
  [`Location`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Location)
  where you can stock inventory and fulfill orders. Locations represent physical
  places like warehouses, retail stores, or fulfillment centers.


  The location requires a name and address with at least a country code. You can
  specify whether the location fulfills online orders, which determines if its
  inventory is available for online sales. You can also attach custom
  [metafields](https://shopify.dev/docs/apps/build/custom-data) to store
  additional information about the location.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/locationAdd'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/locationAdd.md'
---

# location​Add

mutation

Requires `write_locations` access scope.

Adds a new [`Location`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Location) where you can stock inventory and fulfill orders. Locations represent physical places like warehouses, retail stores, or fulfillment centers.

The location requires a name and address with at least a country code. You can specify whether the location fulfills online orders, which determines if its inventory is available for online sales. You can also attach custom [metafields](https://shopify.dev/docs/apps/build/custom-data) to store additional information about the location.

## Arguments

* input

  [Location​Add​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/LocationAddInput)

  required

  The properties of the location to add.

***

## Location​Add​Payload returns

* location

  [Location](https://shopify.dev/docs/api/admin-graphql/latest/objects/Location)

  The location that was added.

* user​Errors

  [\[Location​Add​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/LocationAddUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Add a location and return the location ID

  #### Description

  Add a new location with a specified name, address and fulfillsOnlineOrders status.

  #### Query

  ```graphql
  mutation {
    locationAdd(input: {name: "New York Warehouses", address: {address1: "101 Liberty Street", city: "New York", provinceCode: "NY", countryCode: US, zip: "10006"}, fulfillsOnlineOrders: true}) {
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
  "query": "mutation { locationAdd(input: {name: \"New York Warehouses\", address: {address1: \"101 Liberty Street\", city: \"New York\", provinceCode: \"NY\", countryCode: US, zip: \"10006\"}, fulfillsOnlineOrders: true}) { location { id name address { address1 provinceCode countryCode zip } fulfillsOnlineOrders } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    mutation {
      locationAdd(input: {name: "New York Warehouses", address: {address1: "101 Liberty Street", city: "New York", provinceCode: "NY", countryCode: US, zip: "10006"}, fulfillsOnlineOrders: true}) {
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
    mutation {
      locationAdd(input: {name: "New York Warehouses", address: {address1: "101 Liberty Street", city: "New York", provinceCode: "NY", countryCode: US, zip: "10006"}, fulfillsOnlineOrders: true}) {
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
    data: `mutation {
      locationAdd(input: {name: "New York Warehouses", address: {address1: "101 Liberty Street", city: "New York", provinceCode: "NY", countryCode: US, zip: "10006"}, fulfillsOnlineOrders: true}) {
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
  'mutation {
    locationAdd(input: {name: "New York Warehouses", address: {address1: "101 Liberty Street", city: "New York", provinceCode: "NY", countryCode: US, zip: "10006"}, fulfillsOnlineOrders: true}) {
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
    "locationAdd": {
      "location": {
        "id": "gid://shopify/Location/1072404546",
        "name": "New York Warehouses",
        "address": {
          "address1": "101 Liberty Street",
          "provinceCode": "NY",
          "countryCode": "US",
          "zip": "10006"
        },
        "fulfillsOnlineOrders": true
      }
    }
  }
  ```

* ### Create a new metafield on a new location

  #### Description

  Create a new metafield \`my\_field.delivery\_type\` on a new location. Alternatively, refer to the \[metafieldsSet]\(https://shopify.dev/api/admin-graphql/latest/mutations/metafieldsset) mutation to create and/or update metafields on location resources.

  #### Query

  ```graphql
  mutation createLocationMetafields($input: LocationAddInput!) {
    locationAdd(input: $input) {
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
        }
      ],
      "name": "Warehouse",
      "address": {
        "countryCode": "CA"
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
  "query": "mutation createLocationMetafields($input: LocationAddInput!) { locationAdd(input: $input) { location { id metafields(first: 3) { edges { node { id namespace key value } } } } userErrors { message field } } }",
   "variables": {
      "input": {
        "metafields": [
          {
            "namespace": "my_field",
            "key": "delivery_type",
            "type": "single_line_text_field",
            "value": "local"
          }
        ],
        "name": "Warehouse",
        "address": {
          "countryCode": "CA"
        }
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
    mutation createLocationMetafields($input: LocationAddInput!) {
      locationAdd(input: $input) {
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
                  }
              ],
              "name": "Warehouse",
              "address": {
                  "countryCode": "CA"
              }
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
    mutation createLocationMetafields($input: LocationAddInput!) {
      locationAdd(input: $input) {
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
        }
      ],
      "name": "Warehouse",
      "address": {
        "countryCode": "CA"
      }
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation createLocationMetafields($input: LocationAddInput!) {
        locationAdd(input: $input) {
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
                  }
              ],
              "name": "Warehouse",
              "address": {
                  "countryCode": "CA"
              }
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation createLocationMetafields($input: LocationAddInput!) {
    locationAdd(input: $input) {
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
        }
      ],
      "name": "Warehouse",
      "address": {
        "countryCode": "CA"
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "locationAdd": {
      "location": {
        "id": "gid://shopify/Location/1072404547",
        "metafields": {
          "edges": [
            {
              "node": {
                "id": "gid://shopify/Metafield/1069229305",
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

* ### locationAdd reference
