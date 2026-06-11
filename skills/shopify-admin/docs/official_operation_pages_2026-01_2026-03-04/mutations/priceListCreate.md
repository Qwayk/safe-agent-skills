---
title: priceListCreate - GraphQL Admin
description: >-
  Creates a
  [`PriceList`](https://shopify.dev/docs/api/admin-graphql/latest/objects/PriceList).
  Price lists enable contextual pricing by defining fixed prices or
  percentage-based adjustments.


  The price list requires a unique name, currency for fixed prices, and parent
  adjustment settings that determine how the system calculates prices relative
  to base prices. To apply contextual pricing, link the price list to a
  [`Catalog`](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/Catalog).
  When that catalog's context is matched, customers receive the price list's
  prices.


  Learn more about [building catalogs with price
  lists](https://shopify.dev/docs/apps/build/markets/build-catalog#step-2-associate-a-price-list-with-the-catalog).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/priceListCreate'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/priceListCreate.md
---

# price​List​Create

mutation

Requires `write_products` access scope. Also: The user must have permission to create and edit catalogs.

Creates a [`PriceList`](https://shopify.dev/docs/api/admin-graphql/latest/objects/PriceList). Price lists enable contextual pricing by defining fixed prices or percentage-based adjustments.

The price list requires a unique name, currency for fixed prices, and parent adjustment settings that determine how the system calculates prices relative to base prices. To apply contextual pricing, link the price list to a [`Catalog`](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/Catalog). When that catalog's context is matched, customers receive the price list's prices.

Learn more about [building catalogs with price lists](https://shopify.dev/docs/apps/build/markets/build-catalog#step-2-associate-a-price-list-with-the-catalog).

## Arguments

* input

  [Price​List​Create​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/PriceListCreateInput)

  required

  The properties of the new price list.

***

## Price​List​Create​Payload returns

* price​List

  [Price​List](https://shopify.dev/docs/api/admin-graphql/latest/objects/PriceList)

  The newly created price list.

* user​Errors

  [\[Price​List​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PriceListUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create a price list with a percentage adjustment.

  #### Description

  Create a price list that applies a 10% price increase.

  #### Query

  ```graphql
  mutation PriceListCreate($input: PriceListCreateInput!) {
    priceListCreate(input: $input) {
      userErrors {
        field
        message
      }
      priceList {
        id
        name
        currency
        parent {
          adjustment {
            type
            value
          }
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "name": "Price List",
      "currency": "USD",
      "parent": {
        "adjustment": {
          "type": "PERCENTAGE_INCREASE",
          "value": 10
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
  "query": "mutation PriceListCreate($input: PriceListCreateInput!) { priceListCreate(input: $input) { userErrors { field message } priceList { id name currency parent { adjustment { type value } } } } }",
   "variables": {
      "input": {
        "name": "Price List",
        "currency": "USD",
        "parent": {
          "adjustment": {
            "type": "PERCENTAGE_INCREASE",
            "value": 10
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
    mutation PriceListCreate($input: PriceListCreateInput!) {
      priceListCreate(input: $input) {
        userErrors {
          field
          message
        }
        priceList {
          id
          name
          currency
          parent {
            adjustment {
              type
              value
            }
          }
        }
      }
    }`,
    {
      variables: {
          "input": {
              "name": "Price List",
              "currency": "USD",
              "parent": {
                  "adjustment": {
                      "type": "PERCENTAGE_INCREASE",
                      "value": 10
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
    mutation PriceListCreate($input: PriceListCreateInput!) {
      priceListCreate(input: $input) {
        userErrors {
          field
          message
        }
        priceList {
          id
          name
          currency
          parent {
            adjustment {
              type
              value
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "name": "Price List",
      "currency": "USD",
      "parent": {
        "adjustment": {
          "type": "PERCENTAGE_INCREASE",
          "value": 10
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
      "query": `mutation PriceListCreate($input: PriceListCreateInput!) {
        priceListCreate(input: $input) {
          userErrors {
            field
            message
          }
          priceList {
            id
            name
            currency
            parent {
              adjustment {
                type
                value
              }
            }
          }
        }
      }`,
      "variables": {
          "input": {
              "name": "Price List",
              "currency": "USD",
              "parent": {
                  "adjustment": {
                      "type": "PERCENTAGE_INCREASE",
                      "value": 10
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
  'mutation PriceListCreate($input: PriceListCreateInput!) {
    priceListCreate(input: $input) {
      userErrors {
        field
        message
      }
      priceList {
        id
        name
        currency
        parent {
          adjustment {
            type
            value
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "name": "Price List",
      "currency": "USD",
      "parent": {
        "adjustment": {
          "type": "PERCENTAGE_INCREASE",
          "value": 10
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "priceListCreate": {
      "userErrors": [],
      "priceList": {
        "id": "gid://shopify/PriceList/1014716633",
        "name": "Price List",
        "currency": "USD",
        "parent": {
          "adjustment": {
            "type": "PERCENTAGE_INCREASE",
            "value": 10
          }
        }
      }
    }
  }
  ```

* ### priceListCreate reference
