---
title: quantityRulesAdd - GraphQL Admin
description: >-
  Creates or updates existing quantity rules on a price list.

  You can use the `quantityRulesAdd` mutation to set order level minimums,
  maximumums and increments for specific product variants.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/quantityRulesAdd'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/quantityRulesAdd.md
---

# quantity​Rules​Add

mutation

Requires `write_products` access scope. Also: The user must have permission to create and edit catalogs, and the shop requires B2B features enabled.

Creates or updates existing quantity rules on a price list. You can use the `quantityRulesAdd` mutation to set order level minimums, maximumums and increments for specific product variants.

## Arguments

* price​List​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the price list to which the quantity rules will be added or updated.

* quantity​Rules

  [\[Quantity​Rule​Input!\]!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/QuantityRuleInput)

  required

  The list of quantity rules to add or update in the price list.

***

## Quantity​Rules​Add​Payload returns

* quantity​Rules

  [\[Quantity​Rule!\]](https://shopify.dev/docs/api/admin-graphql/latest/objects/QuantityRule)

  The list of quantity rules that were added to or updated in the price list.

* user​Errors

  [\[Quantity​Rule​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/QuantityRuleUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Add multiple quantity rules to a price list

  #### Description

  Add quantity rules for two product variants

  #### Query

  ```graphql
  mutation quantityRulesAdd($priceListId: ID!, $quantityRules: [QuantityRuleInput!]!) {
    quantityRulesAdd(priceListId: $priceListId, quantityRules: $quantityRules) {
      userErrors {
        field
        code
        message
      }
      quantityRules {
        minimum
        maximum
        increment
        isDefault
        originType
        productVariant {
          id
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "priceListId": "gid://shopify/PriceList/155157792",
    "quantityRules": [
      {
        "variantId": "gid://shopify/ProductVariant/138327650",
        "minimum": 1,
        "maximum": null,
        "increment": 1
      },
      {
        "variantId": "gid://shopify/ProductVariant/113711323",
        "minimum": 5,
        "maximum": 25,
        "increment": 5
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
  "query": "mutation quantityRulesAdd($priceListId: ID!, $quantityRules: [QuantityRuleInput!]!) { quantityRulesAdd(priceListId: $priceListId, quantityRules: $quantityRules) { userErrors { field code message } quantityRules { minimum maximum increment isDefault originType productVariant { id } } } }",
   "variables": {
      "priceListId": "gid://shopify/PriceList/155157792",
      "quantityRules": [
        {
          "variantId": "gid://shopify/ProductVariant/138327650",
          "minimum": 1,
          "maximum": null,
          "increment": 1
        },
        {
          "variantId": "gid://shopify/ProductVariant/113711323",
          "minimum": 5,
          "maximum": 25,
          "increment": 5
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
    mutation quantityRulesAdd($priceListId: ID!, $quantityRules: [QuantityRuleInput!]!) {
      quantityRulesAdd(priceListId: $priceListId, quantityRules: $quantityRules) {
        userErrors {
          field
          code
          message
        }
        quantityRules {
          minimum
          maximum
          increment
          isDefault
          originType
          productVariant {
            id
          }
        }
      }
    }`,
    {
      variables: {
          "priceListId": "gid://shopify/PriceList/155157792",
          "quantityRules": [
              {
                  "variantId": "gid://shopify/ProductVariant/138327650",
                  "minimum": 1,
                  "maximum": null,
                  "increment": 1
              },
              {
                  "variantId": "gid://shopify/ProductVariant/113711323",
                  "minimum": 5,
                  "maximum": 25,
                  "increment": 5
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
    mutation quantityRulesAdd($priceListId: ID!, $quantityRules: [QuantityRuleInput!]!) {
      quantityRulesAdd(priceListId: $priceListId, quantityRules: $quantityRules) {
        userErrors {
          field
          code
          message
        }
        quantityRules {
          minimum
          maximum
          increment
          isDefault
          originType
          productVariant {
            id
          }
        }
      }
    }
  QUERY

  variables = {
    "priceListId": "gid://shopify/PriceList/155157792",
    "quantityRules": [
      {
        "variantId": "gid://shopify/ProductVariant/138327650",
        "minimum": 1,
        "maximum": null,
        "increment": 1
      },
      {
        "variantId": "gid://shopify/ProductVariant/113711323",
        "minimum": 5,
        "maximum": 25,
        "increment": 5
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
      "query": `mutation quantityRulesAdd($priceListId: ID!, $quantityRules: [QuantityRuleInput!]!) {
        quantityRulesAdd(priceListId: $priceListId, quantityRules: $quantityRules) {
          userErrors {
            field
            code
            message
          }
          quantityRules {
            minimum
            maximum
            increment
            isDefault
            originType
            productVariant {
              id
            }
          }
        }
      }`,
      "variables": {
          "priceListId": "gid://shopify/PriceList/155157792",
          "quantityRules": [
              {
                  "variantId": "gid://shopify/ProductVariant/138327650",
                  "minimum": 1,
                  "maximum": null,
                  "increment": 1
              },
              {
                  "variantId": "gid://shopify/ProductVariant/113711323",
                  "minimum": 5,
                  "maximum": 25,
                  "increment": 5
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
  'mutation quantityRulesAdd($priceListId: ID!, $quantityRules: [QuantityRuleInput!]!) {
    quantityRulesAdd(priceListId: $priceListId, quantityRules: $quantityRules) {
      userErrors {
        field
        code
        message
      }
      quantityRules {
        minimum
        maximum
        increment
        isDefault
        originType
        productVariant {
          id
        }
      }
    }
  }' \
  --variables \
  '{
    "priceListId": "gid://shopify/PriceList/155157792",
    "quantityRules": [
      {
        "variantId": "gid://shopify/ProductVariant/138327650",
        "minimum": 1,
        "maximum": null,
        "increment": 1
      },
      {
        "variantId": "gid://shopify/ProductVariant/113711323",
        "minimum": 5,
        "maximum": 25,
        "increment": 5
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "quantityRulesAdd": {
      "userErrors": [],
      "quantityRules": [
        {
          "minimum": 1,
          "maximum": null,
          "increment": 1,
          "isDefault": true,
          "originType": "FIXED",
          "productVariant": {
            "id": "gid://shopify/ProductVariant/138327650"
          }
        },
        {
          "minimum": 5,
          "maximum": 25,
          "increment": 5,
          "isDefault": false,
          "originType": "FIXED",
          "productVariant": {
            "id": "gid://shopify/ProductVariant/113711323"
          }
        }
      ]
    }
  }
  ```

* ### Adding invalid quantity rules returns an error

  #### Description

  Attempt to add quantity rules with invalid values

  #### Query

  ```graphql
  mutation quantityRulesAdd($priceListId: ID!, $quantityRules: [QuantityRuleInput!]!) {
    quantityRulesAdd(priceListId: $priceListId, quantityRules: $quantityRules) {
      userErrors {
        field
        code
        message
      }
      quantityRules {
        minimum
        maximum
        increment
        isDefault
        originType
        productVariant {
          id
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "priceListId": "gid://shopify/PriceList/155157792",
    "quantityRules": [
      {
        "variantId": "gid://shopify/ProductVariant/138327650",
        "minimum": 1,
        "maximum": 5,
        "increment": 2
      },
      {
        "variantId": "gid://shopify/ProductVariant/113711323",
        "minimum": 10,
        "maximum": 5,
        "increment": 5
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
  "query": "mutation quantityRulesAdd($priceListId: ID!, $quantityRules: [QuantityRuleInput!]!) { quantityRulesAdd(priceListId: $priceListId, quantityRules: $quantityRules) { userErrors { field code message } quantityRules { minimum maximum increment isDefault originType productVariant { id } } } }",
   "variables": {
      "priceListId": "gid://shopify/PriceList/155157792",
      "quantityRules": [
        {
          "variantId": "gid://shopify/ProductVariant/138327650",
          "minimum": 1,
          "maximum": 5,
          "increment": 2
        },
        {
          "variantId": "gid://shopify/ProductVariant/113711323",
          "minimum": 10,
          "maximum": 5,
          "increment": 5
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
    mutation quantityRulesAdd($priceListId: ID!, $quantityRules: [QuantityRuleInput!]!) {
      quantityRulesAdd(priceListId: $priceListId, quantityRules: $quantityRules) {
        userErrors {
          field
          code
          message
        }
        quantityRules {
          minimum
          maximum
          increment
          isDefault
          originType
          productVariant {
            id
          }
        }
      }
    }`,
    {
      variables: {
          "priceListId": "gid://shopify/PriceList/155157792",
          "quantityRules": [
              {
                  "variantId": "gid://shopify/ProductVariant/138327650",
                  "minimum": 1,
                  "maximum": 5,
                  "increment": 2
              },
              {
                  "variantId": "gid://shopify/ProductVariant/113711323",
                  "minimum": 10,
                  "maximum": 5,
                  "increment": 5
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
    mutation quantityRulesAdd($priceListId: ID!, $quantityRules: [QuantityRuleInput!]!) {
      quantityRulesAdd(priceListId: $priceListId, quantityRules: $quantityRules) {
        userErrors {
          field
          code
          message
        }
        quantityRules {
          minimum
          maximum
          increment
          isDefault
          originType
          productVariant {
            id
          }
        }
      }
    }
  QUERY

  variables = {
    "priceListId": "gid://shopify/PriceList/155157792",
    "quantityRules": [
      {
        "variantId": "gid://shopify/ProductVariant/138327650",
        "minimum": 1,
        "maximum": 5,
        "increment": 2
      },
      {
        "variantId": "gid://shopify/ProductVariant/113711323",
        "minimum": 10,
        "maximum": 5,
        "increment": 5
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
      "query": `mutation quantityRulesAdd($priceListId: ID!, $quantityRules: [QuantityRuleInput!]!) {
        quantityRulesAdd(priceListId: $priceListId, quantityRules: $quantityRules) {
          userErrors {
            field
            code
            message
          }
          quantityRules {
            minimum
            maximum
            increment
            isDefault
            originType
            productVariant {
              id
            }
          }
        }
      }`,
      "variables": {
          "priceListId": "gid://shopify/PriceList/155157792",
          "quantityRules": [
              {
                  "variantId": "gid://shopify/ProductVariant/138327650",
                  "minimum": 1,
                  "maximum": 5,
                  "increment": 2
              },
              {
                  "variantId": "gid://shopify/ProductVariant/113711323",
                  "minimum": 10,
                  "maximum": 5,
                  "increment": 5
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
  'mutation quantityRulesAdd($priceListId: ID!, $quantityRules: [QuantityRuleInput!]!) {
    quantityRulesAdd(priceListId: $priceListId, quantityRules: $quantityRules) {
      userErrors {
        field
        code
        message
      }
      quantityRules {
        minimum
        maximum
        increment
        isDefault
        originType
        productVariant {
          id
        }
      }
    }
  }' \
  --variables \
  '{
    "priceListId": "gid://shopify/PriceList/155157792",
    "quantityRules": [
      {
        "variantId": "gid://shopify/ProductVariant/138327650",
        "minimum": 1,
        "maximum": 5,
        "increment": 2
      },
      {
        "variantId": "gid://shopify/ProductVariant/113711323",
        "minimum": 10,
        "maximum": 5,
        "increment": 5
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "quantityRulesAdd": {
      "userErrors": [
        {
          "field": [
            "quantityRules",
            "0",
            "increment"
          ],
          "code": "INCREMENT_IS_GREATER_THAN_MINIMUM",
          "message": "Increment must be lower than or equal to the minimum."
        },
        {
          "field": [
            "quantityRules",
            "0",
            "maximum"
          ],
          "code": "MAXIMUM_NOT_MULTIPLE_OF_INCREMENT",
          "message": "Maximum must be a multiple of the increment."
        },
        {
          "field": [
            "quantityRules",
            "0",
            "minimum"
          ],
          "code": "MINIMUM_NOT_MULTIPLE_OF_INCREMENT",
          "message": "Minimum must be a multiple of the increment."
        },
        {
          "field": [
            "quantityRules",
            "1",
            "minimum"
          ],
          "code": "MINIMUM_IS_GREATER_THAN_MAXIMUM",
          "message": "Minimum must be lower than or equal to the maximum."
        }
      ],
      "quantityRules": []
    }
  }
  ```

* ### quantityRulesAdd reference
