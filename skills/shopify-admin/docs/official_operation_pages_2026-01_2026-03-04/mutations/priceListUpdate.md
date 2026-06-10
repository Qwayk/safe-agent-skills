---
title: priceListUpdate - GraphQL Admin
description: >-
  Updates a
  [`PriceList`](https://shopify.dev/docs/api/admin-graphql/latest/objects/PriceList)'s
  configuration, including its name, currency,
  [`Catalog`](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/Catalog)
  association, and pricing adjustments.


  Changing the currency removes all fixed prices from the price list. The
  affected
  [`ProductVariant`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant)
  objects revert to prices calculated from the price list's adjustment settings.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/priceListUpdate'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/priceListUpdate.md
---

# price​List​Update

mutation

Requires `write_products` access scope. Also: The user must have permission to create and edit catalogs.

Updates a [`PriceList`](https://shopify.dev/docs/api/admin-graphql/latest/objects/PriceList)'s configuration, including its name, currency, [`Catalog`](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/Catalog) association, and pricing adjustments.

Changing the currency removes all fixed prices from the price list. The affected [`ProductVariant`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant) objects revert to prices calculated from the price list's adjustment settings.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the price list to update.

* input

  [Price​List​Update​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/PriceListUpdateInput)

  required

  The input data used to update the price list.

***

## Price​List​Update​Payload returns

* price​List

  [Price​List](https://shopify.dev/docs/api/admin-graphql/latest/objects/PriceList)

  The updated price list.

* user​Errors

  [\[Price​List​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PriceListUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Update a price list

  #### Description

  Set the existing price list's adjustment to be an increase of 10%.

  #### Query

  ```graphql
  mutation priceListUpdate($id: ID!, $input: PriceListUpdateInput!) {
    priceListUpdate(id: $id, input: $input) {
      priceList {
        id
        parent {
          adjustment {
            type
            value
          }
        }
      }
      userErrors {
        message
        field
        code
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/PriceList/734173888",
    "input": {
      "parent": {
        "adjustment": {
          "value": 10,
          "type": "PERCENTAGE_INCREASE"
        }
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
  "query": "mutation priceListUpdate($id: ID!, $input: PriceListUpdateInput!) { priceListUpdate(id: $id, input: $input) { priceList { id parent { adjustment { type value } } } userErrors { message field code } } }",
   "variables": {
      "id": "gid://shopify/PriceList/734173888",
      "input": {
        "parent": {
          "adjustment": {
            "value": 10,
            "type": "PERCENTAGE_INCREASE"
          }
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
    mutation priceListUpdate($id: ID!, $input: PriceListUpdateInput!) {
      priceListUpdate(id: $id, input: $input) {
        priceList {
          id
          parent {
            adjustment {
              type
              value
            }
          }
        }
        userErrors {
          message
          field
          code
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/PriceList/734173888",
          "input": {
              "parent": {
                  "adjustment": {
                      "value": 10,
                      "type": "PERCENTAGE_INCREASE"
                  }
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
    mutation priceListUpdate($id: ID!, $input: PriceListUpdateInput!) {
      priceListUpdate(id: $id, input: $input) {
        priceList {
          id
          parent {
            adjustment {
              type
              value
            }
          }
        }
        userErrors {
          message
          field
          code
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/PriceList/734173888",
    "input": {
      "parent": {
        "adjustment": {
          "value": 10,
          "type": "PERCENTAGE_INCREASE"
        }
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
      "query": `mutation priceListUpdate($id: ID!, $input: PriceListUpdateInput!) {
        priceListUpdate(id: $id, input: $input) {
          priceList {
            id
            parent {
              adjustment {
                type
                value
              }
            }
          }
          userErrors {
            message
            field
            code
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/PriceList/734173888",
          "input": {
              "parent": {
                  "adjustment": {
                      "value": 10,
                      "type": "PERCENTAGE_INCREASE"
                  }
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
  'mutation priceListUpdate($id: ID!, $input: PriceListUpdateInput!) {
    priceListUpdate(id: $id, input: $input) {
      priceList {
        id
        parent {
          adjustment {
            type
            value
          }
        }
      }
      userErrors {
        message
        field
        code
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/PriceList/734173888",
    "input": {
      "parent": {
        "adjustment": {
          "value": 10,
          "type": "PERCENTAGE_INCREASE"
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "priceListUpdate": {
      "priceList": {
        "id": "gid://shopify/PriceList/734173888",
        "parent": {
          "adjustment": {
            "type": "PERCENTAGE_INCREASE",
            "value": 10
          }
        }
      },
      "userErrors": []
    }
  }
  ```

* ### priceListUpdate reference
