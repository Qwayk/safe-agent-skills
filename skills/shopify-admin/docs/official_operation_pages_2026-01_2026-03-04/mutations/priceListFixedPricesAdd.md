---
title: priceListFixedPricesAdd - GraphQL Admin
description: >-
  Creates or updates fixed prices on a
  [`PriceList`](https://shopify.dev/docs/api/admin-graphql/latest/objects/PriceList).
  Use this mutation to set specific prices for
  [`ProductVariant`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant)
  objects that override the price list's default percentage-based adjustments.


  When you add fixed prices, the mutation replaces any existing fixed prices for
  those variants on the price list.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/priceListFixedPricesAdd
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/priceListFixedPricesAdd.md
---

# price​List​Fixed​Prices​Add

mutation

Requires `write_products` access scope. Also: The user must have permission to create and edit catalogs.

Creates or updates fixed prices on a [`PriceList`](https://shopify.dev/docs/api/admin-graphql/latest/objects/PriceList). Use this mutation to set specific prices for [`ProductVariant`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant) objects that override the price list's default percentage-based adjustments.

When you add fixed prices, the mutation replaces any existing fixed prices for those variants on the price list.

## Arguments

* price​List​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the price list to which the fixed prices will be added or updated.

* prices

  [\[Price​List​Price​Input!\]!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/PriceListPriceInput)

  required

  The list of fixed prices to add or update in the price list.

***

## Price​List​Fixed​Prices​Add​Payload returns

* prices

  [\[Price​List​Price!\]](https://shopify.dev/docs/api/admin-graphql/latest/objects/PriceListPrice)

  The list of fixed prices that were added to or updated in the price list.

* user​Errors

  [\[Price​List​Price​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PriceListPriceUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Add multiple fixed prices to a price list

  #### Description

  Add fixed prices for two product variants in Canadian currency.

  #### Query

  ```graphql
  mutation priceListFixedPricesAdd($priceListId: ID!, $prices: [PriceListPriceInput!]!) {
    priceListFixedPricesAdd(priceListId: $priceListId, prices: $prices) {
      prices {
        compareAtPrice {
          amount
          currencyCode
        }
        price {
          amount
          currencyCode
        }
      }
      userErrors {
        field
        code
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "priceListId": "gid://shopify/PriceList/115567603",
    "prices": [
      {
        "compareAtPrice": {
          "amount": "125.50",
          "currencyCode": "CAD"
        },
        "price": {
          "amount": "100",
          "currencyCode": "CAD"
        },
        "variantId": "gid://shopify/ProductVariant/43729076"
      },
      {
        "compareAtPrice": {
          "amount": "6.99",
          "currencyCode": "CAD"
        },
        "price": {
          "amount": "4",
          "currencyCode": "CAD"
        },
        "variantId": "gid://shopify/ProductVariant/138327650"
      }
    ]
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation priceListFixedPricesAdd($priceListId: ID!, $prices: [PriceListPriceInput!]!) { priceListFixedPricesAdd(priceListId: $priceListId, prices: $prices) { prices { compareAtPrice { amount currencyCode } price { amount currencyCode } } userErrors { field code message } } }",
   "variables": {
      "priceListId": "gid://shopify/PriceList/115567603",
      "prices": [
        {
          "compareAtPrice": {
            "amount": "125.50",
            "currencyCode": "CAD"
          },
          "price": {
            "amount": "100",
            "currencyCode": "CAD"
          },
          "variantId": "gid://shopify/ProductVariant/43729076"
        },
        {
          "compareAtPrice": {
            "amount": "6.99",
            "currencyCode": "CAD"
          },
          "price": {
            "amount": "4",
            "currencyCode": "CAD"
          },
          "variantId": "gid://shopify/ProductVariant/138327650"
        }
      ]
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
    mutation priceListFixedPricesAdd($priceListId: ID!, $prices: [PriceListPriceInput!]!) {
      priceListFixedPricesAdd(priceListId: $priceListId, prices: $prices) {
        prices {
          compareAtPrice {
            amount
            currencyCode
          }
          price {
            amount
            currencyCode
          }
        }
        userErrors {
          field
          code
          message
        }
      }
    }`,
    {
      variables: {
          "priceListId": "gid://shopify/PriceList/115567603",
          "prices": [
              {
                  "compareAtPrice": {
                      "amount": "125.50",
                      "currencyCode": "CAD"
                  },
                  "price": {
                      "amount": "100",
                      "currencyCode": "CAD"
                  },
                  "variantId": "gid://shopify/ProductVariant/43729076"
              },
              {
                  "compareAtPrice": {
                      "amount": "6.99",
                      "currencyCode": "CAD"
                  },
                  "price": {
                      "amount": "4",
                      "currencyCode": "CAD"
                  },
                  "variantId": "gid://shopify/ProductVariant/138327650"
              }
          ]
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
    mutation priceListFixedPricesAdd($priceListId: ID!, $prices: [PriceListPriceInput!]!) {
      priceListFixedPricesAdd(priceListId: $priceListId, prices: $prices) {
        prices {
          compareAtPrice {
            amount
            currencyCode
          }
          price {
            amount
            currencyCode
          }
        }
        userErrors {
          field
          code
          message
        }
      }
    }
  QUERY

  variables = {
    "priceListId": "gid://shopify/PriceList/115567603",
    "prices": [
      {
        "compareAtPrice": {
          "amount": "125.50",
          "currencyCode": "CAD"
        },
        "price": {
          "amount": "100",
          "currencyCode": "CAD"
        },
        "variantId": "gid://shopify/ProductVariant/43729076"
      },
      {
        "compareAtPrice": {
          "amount": "6.99",
          "currencyCode": "CAD"
        },
        "price": {
          "amount": "4",
          "currencyCode": "CAD"
        },
        "variantId": "gid://shopify/ProductVariant/138327650"
      }
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation priceListFixedPricesAdd($priceListId: ID!, $prices: [PriceListPriceInput!]!) {
        priceListFixedPricesAdd(priceListId: $priceListId, prices: $prices) {
          prices {
            compareAtPrice {
              amount
              currencyCode
            }
            price {
              amount
              currencyCode
            }
          }
          userErrors {
            field
            code
            message
          }
        }
      }`,
      "variables": {
          "priceListId": "gid://shopify/PriceList/115567603",
          "prices": [
              {
                  "compareAtPrice": {
                      "amount": "125.50",
                      "currencyCode": "CAD"
                  },
                  "price": {
                      "amount": "100",
                      "currencyCode": "CAD"
                  },
                  "variantId": "gid://shopify/ProductVariant/43729076"
              },
              {
                  "compareAtPrice": {
                      "amount": "6.99",
                      "currencyCode": "CAD"
                  },
                  "price": {
                      "amount": "4",
                      "currencyCode": "CAD"
                  },
                  "variantId": "gid://shopify/ProductVariant/138327650"
              }
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation priceListFixedPricesAdd($priceListId: ID!, $prices: [PriceListPriceInput!]!) {
    priceListFixedPricesAdd(priceListId: $priceListId, prices: $prices) {
      prices {
        compareAtPrice {
          amount
          currencyCode
        }
        price {
          amount
          currencyCode
        }
      }
      userErrors {
        field
        code
        message
      }
    }
  }' \
  --variables \
  '{
    "priceListId": "gid://shopify/PriceList/115567603",
    "prices": [
      {
        "compareAtPrice": {
          "amount": "125.50",
          "currencyCode": "CAD"
        },
        "price": {
          "amount": "100",
          "currencyCode": "CAD"
        },
        "variantId": "gid://shopify/ProductVariant/43729076"
      },
      {
        "compareAtPrice": {
          "amount": "6.99",
          "currencyCode": "CAD"
        },
        "price": {
          "amount": "4",
          "currencyCode": "CAD"
        },
        "variantId": "gid://shopify/ProductVariant/138327650"
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "priceListFixedPricesAdd": {
      "prices": [
        {
          "compareAtPrice": {
            "amount": "125.5",
            "currencyCode": "CAD"
          },
          "price": {
            "amount": "100.0",
            "currencyCode": "CAD"
          }
        },
        {
          "compareAtPrice": {
            "amount": "6.99",
            "currencyCode": "CAD"
          },
          "price": {
            "amount": "4.0",
            "currencyCode": "CAD"
          }
        }
      ],
      "userErrors": []
    }
  }
  ```

* ### Adding a fixed price using a currency that isn't supported by the price list returns a currency mismatch error

  #### Description

  Attempt to add a fixed price using the Euro currency on a price list that only supports Canadian currency.

  #### Query

  ```graphql
  mutation priceListFixedPricesAdd($priceListId: ID!, $prices: [PriceListPriceInput!]!) {
    priceListFixedPricesAdd(priceListId: $priceListId, prices: $prices) {
      prices {
        compareAtPrice {
          amount
          currencyCode
        }
        price {
          amount
          currencyCode
        }
      }
      userErrors {
        field
        code
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "priceListId": "gid://shopify/PriceList/115567603",
    "prices": [
      {
        "compareAtPrice": {
          "amount": "125.50",
          "currencyCode": "EUR"
        },
        "price": {
          "amount": "100",
          "currencyCode": "EUR"
        },
        "variantId": "gid://shopify/ProductVariant/43729076"
      }
    ]
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation priceListFixedPricesAdd($priceListId: ID!, $prices: [PriceListPriceInput!]!) { priceListFixedPricesAdd(priceListId: $priceListId, prices: $prices) { prices { compareAtPrice { amount currencyCode } price { amount currencyCode } } userErrors { field code message } } }",
   "variables": {
      "priceListId": "gid://shopify/PriceList/115567603",
      "prices": [
        {
          "compareAtPrice": {
            "amount": "125.50",
            "currencyCode": "EUR"
          },
          "price": {
            "amount": "100",
            "currencyCode": "EUR"
          },
          "variantId": "gid://shopify/ProductVariant/43729076"
        }
      ]
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
    mutation priceListFixedPricesAdd($priceListId: ID!, $prices: [PriceListPriceInput!]!) {
      priceListFixedPricesAdd(priceListId: $priceListId, prices: $prices) {
        prices {
          compareAtPrice {
            amount
            currencyCode
          }
          price {
            amount
            currencyCode
          }
        }
        userErrors {
          field
          code
          message
        }
      }
    }`,
    {
      variables: {
          "priceListId": "gid://shopify/PriceList/115567603",
          "prices": [
              {
                  "compareAtPrice": {
                      "amount": "125.50",
                      "currencyCode": "EUR"
                  },
                  "price": {
                      "amount": "100",
                      "currencyCode": "EUR"
                  },
                  "variantId": "gid://shopify/ProductVariant/43729076"
              }
          ]
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
    mutation priceListFixedPricesAdd($priceListId: ID!, $prices: [PriceListPriceInput!]!) {
      priceListFixedPricesAdd(priceListId: $priceListId, prices: $prices) {
        prices {
          compareAtPrice {
            amount
            currencyCode
          }
          price {
            amount
            currencyCode
          }
        }
        userErrors {
          field
          code
          message
        }
      }
    }
  QUERY

  variables = {
    "priceListId": "gid://shopify/PriceList/115567603",
    "prices": [
      {
        "compareAtPrice": {
          "amount": "125.50",
          "currencyCode": "EUR"
        },
        "price": {
          "amount": "100",
          "currencyCode": "EUR"
        },
        "variantId": "gid://shopify/ProductVariant/43729076"
      }
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation priceListFixedPricesAdd($priceListId: ID!, $prices: [PriceListPriceInput!]!) {
        priceListFixedPricesAdd(priceListId: $priceListId, prices: $prices) {
          prices {
            compareAtPrice {
              amount
              currencyCode
            }
            price {
              amount
              currencyCode
            }
          }
          userErrors {
            field
            code
            message
          }
        }
      }`,
      "variables": {
          "priceListId": "gid://shopify/PriceList/115567603",
          "prices": [
              {
                  "compareAtPrice": {
                      "amount": "125.50",
                      "currencyCode": "EUR"
                  },
                  "price": {
                      "amount": "100",
                      "currencyCode": "EUR"
                  },
                  "variantId": "gid://shopify/ProductVariant/43729076"
              }
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation priceListFixedPricesAdd($priceListId: ID!, $prices: [PriceListPriceInput!]!) {
    priceListFixedPricesAdd(priceListId: $priceListId, prices: $prices) {
      prices {
        compareAtPrice {
          amount
          currencyCode
        }
        price {
          amount
          currencyCode
        }
      }
      userErrors {
        field
        code
        message
      }
    }
  }' \
  --variables \
  '{
    "priceListId": "gid://shopify/PriceList/115567603",
    "prices": [
      {
        "compareAtPrice": {
          "amount": "125.50",
          "currencyCode": "EUR"
        },
        "price": {
          "amount": "100",
          "currencyCode": "EUR"
        },
        "variantId": "gid://shopify/ProductVariant/43729076"
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "priceListFixedPricesAdd": {
      "prices": [],
      "userErrors": [
        {
          "field": [
            "prices",
            "0",
            "price",
            "currencyCode"
          ],
          "code": "PRICE_LIST_CURRENCY_MISMATCH",
          "message": "The specified currency does not match the price list's currency."
        },
        {
          "field": [
            "prices",
            "0",
            "compareAtPrice",
            "currencyCode"
          ],
          "code": "PRICE_LIST_CURRENCY_MISMATCH",
          "message": "The specified currency does not match the price list's currency."
        }
      ]
    }
  }
  ```

* ### priceListFixedPricesAdd reference
