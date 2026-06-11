---
title: quantityRulesDelete - GraphQL Admin
description: >-
  Deletes specific quantity rules from a price list using a product variant ID.

  You can use the `quantityRulesDelete` mutation to delete a set of quantity
  rules from a price list.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/quantityRulesDelete
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/quantityRulesDelete.md
---

# quantity​Rules​Delete

mutation

Requires `write_products` access scope. Also: The user must have permission to create and edit catalogs, and the shop requires B2B features enabled.

Deletes specific quantity rules from a price list using a product variant ID. You can use the `quantityRulesDelete` mutation to delete a set of quantity rules from a price list.

## Arguments

* price​List​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the price list from which the quantity rules will be deleted.

* variant​Ids

  [\[ID!\]!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  A list of product variant IDs whose quantity rules will be removed from the price list.

***

## Quantity​Rules​Delete​Payload returns

* deleted​Quantity​Rules​Variant​Ids

  [\[ID!\]](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  A list of product variant IDs whose quantity rules were removed from the price list.

* user​Errors

  [\[Quantity​Rule​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/QuantityRuleUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Delete multiple quantity rules from a price list

  #### Description

  Delete quantity rules for two product variants

  #### Query

  ```graphql
  mutation quantityRulesDelete($priceListId: ID!, $variantIds: [ID!]!) {
    quantityRulesDelete(priceListId: $priceListId, variantIds: $variantIds) {
      deletedQuantityRulesVariantIds
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
    "priceListId": "gid://shopify/PriceList/225060712",
    "variantIds": [
      "gid://shopify/ProductVariant/43729076",
      "gid://shopify/ProductVariant/138327650"
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
  "query": "mutation quantityRulesDelete($priceListId: ID!, $variantIds: [ID!]!) { quantityRulesDelete(priceListId: $priceListId, variantIds: $variantIds) { deletedQuantityRulesVariantIds userErrors { field code message } } }",
   "variables": {
      "priceListId": "gid://shopify/PriceList/225060712",
      "variantIds": [
        "gid://shopify/ProductVariant/43729076",
        "gid://shopify/ProductVariant/138327650"
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
    mutation quantityRulesDelete($priceListId: ID!, $variantIds: [ID!]!) {
      quantityRulesDelete(priceListId: $priceListId, variantIds: $variantIds) {
        deletedQuantityRulesVariantIds
        userErrors {
          field
          code
          message
        }
      }
    }`,
    {
      variables: {
          "priceListId": "gid://shopify/PriceList/225060712",
          "variantIds": [
              "gid://shopify/ProductVariant/43729076",
              "gid://shopify/ProductVariant/138327650"
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
    mutation quantityRulesDelete($priceListId: ID!, $variantIds: [ID!]!) {
      quantityRulesDelete(priceListId: $priceListId, variantIds: $variantIds) {
        deletedQuantityRulesVariantIds
        userErrors {
          field
          code
          message
        }
      }
    }
  QUERY

  variables = {
    "priceListId": "gid://shopify/PriceList/225060712",
    "variantIds": [
      "gid://shopify/ProductVariant/43729076",
      "gid://shopify/ProductVariant/138327650"
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation quantityRulesDelete($priceListId: ID!, $variantIds: [ID!]!) {
        quantityRulesDelete(priceListId: $priceListId, variantIds: $variantIds) {
          deletedQuantityRulesVariantIds
          userErrors {
            field
            code
            message
          }
        }
      }`,
      "variables": {
          "priceListId": "gid://shopify/PriceList/225060712",
          "variantIds": [
              "gid://shopify/ProductVariant/43729076",
              "gid://shopify/ProductVariant/138327650"
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation quantityRulesDelete($priceListId: ID!, $variantIds: [ID!]!) {
    quantityRulesDelete(priceListId: $priceListId, variantIds: $variantIds) {
      deletedQuantityRulesVariantIds
      userErrors {
        field
        code
        message
      }
    }
  }' \
  --variables \
  '{
    "priceListId": "gid://shopify/PriceList/225060712",
    "variantIds": [
      "gid://shopify/ProductVariant/43729076",
      "gid://shopify/ProductVariant/138327650"
    ]
  }'
  ```

  #### Response

  ```json
  {
    "quantityRulesDelete": {
      "deletedQuantityRulesVariantIds": [
        "gid://shopify/ProductVariant/43729076",
        "gid://shopify/ProductVariant/138327650"
      ],
      "userErrors": []
    }
  }
  ```

* ### quantityRulesDelete reference
