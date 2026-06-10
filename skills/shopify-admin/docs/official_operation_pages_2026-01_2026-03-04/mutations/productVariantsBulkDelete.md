---
title: productVariantsBulkDelete - GraphQL Admin
description: >-
  Deletes multiple variants in a single
  [`Product`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product).
  Specify the product ID and an array of variant IDs to remove variants in bulk.
  You can call this mutation directly or through the
  [`bulkOperationRunMutation`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/bulkOperationRunMutation)
  mutation. Returns the updated product and any
  [`UserError`](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)
  objects.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/productVariantsBulkDelete
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/productVariantsBulkDelete.md
---

# product​Variants​Bulk​Delete

mutation

Requires `write_products` access scope. Also: The user must have a permission to delete product variants.

Deletes multiple variants in a single [`Product`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product). Specify the product ID and an array of variant IDs to remove variants in bulk. You can call this mutation directly or through the [`bulkOperationRunMutation`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/bulkOperationRunMutation) mutation. Returns the updated product and any [`UserError`](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError) objects.

## Arguments

* product​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the product with the variants to update.

* variants​Ids

  [\[ID!\]!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  An array of product variants IDs to delete.

***

## Product​Variants​Bulk​Delete​Payload returns

* product

  [Product](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product)

  The updated product object.

* user​Errors

  [\[Product​Variants​Bulk​Delete​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariantsBulkDeleteUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Bulk delete multiple product variants.

  #### Query

  ```graphql
  mutation bulkDeleteProductVariants($productId: ID!, $variantsIds: [ID!]!) {
    productVariantsBulkDelete(productId: $productId, variantsIds: $variantsIds) {
      product {
        id
        title
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
    "productId": "gid://shopify/Product/20995642",
    "variantsIds": [
      "gid://shopify/ProductVariant/30322695",
      "gid://shopify/ProductVariant/113711323"
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
  "query": "mutation bulkDeleteProductVariants($productId: ID!, $variantsIds: [ID!]!) { productVariantsBulkDelete(productId: $productId, variantsIds: $variantsIds) { product { id title } userErrors { field message } } }",
   "variables": {
      "productId": "gid://shopify/Product/20995642",
      "variantsIds": [
        "gid://shopify/ProductVariant/30322695",
        "gid://shopify/ProductVariant/113711323"
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
    mutation bulkDeleteProductVariants($productId: ID!, $variantsIds: [ID!]!) {
      productVariantsBulkDelete(productId: $productId, variantsIds: $variantsIds) {
        product {
          id
          title
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "productId": "gid://shopify/Product/20995642",
          "variantsIds": [
              "gid://shopify/ProductVariant/30322695",
              "gid://shopify/ProductVariant/113711323"
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
    mutation bulkDeleteProductVariants($productId: ID!, $variantsIds: [ID!]!) {
      productVariantsBulkDelete(productId: $productId, variantsIds: $variantsIds) {
        product {
          id
          title
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "productId": "gid://shopify/Product/20995642",
    "variantsIds": [
      "gid://shopify/ProductVariant/30322695",
      "gid://shopify/ProductVariant/113711323"
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation bulkDeleteProductVariants($productId: ID!, $variantsIds: [ID!]!) {
        productVariantsBulkDelete(productId: $productId, variantsIds: $variantsIds) {
          product {
            id
            title
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "productId": "gid://shopify/Product/20995642",
          "variantsIds": [
              "gid://shopify/ProductVariant/30322695",
              "gid://shopify/ProductVariant/113711323"
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation bulkDeleteProductVariants($productId: ID!, $variantsIds: [ID!]!) {
    productVariantsBulkDelete(productId: $productId, variantsIds: $variantsIds) {
      product {
        id
        title
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "productId": "gid://shopify/Product/20995642",
    "variantsIds": [
      "gid://shopify/ProductVariant/30322695",
      "gid://shopify/ProductVariant/113711323"
    ]
  }'
  ```

  #### Response

  ```json
  {
    "productVariantsBulkDelete": {
      "product": {
        "id": "gid://shopify/Product/20995642",
        "title": "Element"
      },
      "userErrors": []
    }
  }
  ```

* ### Remove an existing Product Variant

  #### Query

  ```graphql
  mutation ProductVariantsDelete($productId: ID!, $variantsIds: [ID!]!) {
    productVariantsBulkDelete(productId: $productId, variantsIds: $variantsIds) {
      product {
        id
        title
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
    "productId": "gid://shopify/Product/20995642",
    "variantsIds": [
      "gid://shopify/ProductVariant/30322695",
      "gid://shopify/ProductVariant/113711323"
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
  "query": "mutation ProductVariantsDelete($productId: ID!, $variantsIds: [ID!]!) { productVariantsBulkDelete(productId: $productId, variantsIds: $variantsIds) { product { id title } userErrors { field message } } }",
   "variables": {
      "productId": "gid://shopify/Product/20995642",
      "variantsIds": [
        "gid://shopify/ProductVariant/30322695",
        "gid://shopify/ProductVariant/113711323"
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
    mutation ProductVariantsDelete($productId: ID!, $variantsIds: [ID!]!) {
      productVariantsBulkDelete(productId: $productId, variantsIds: $variantsIds) {
        product {
          id
          title
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "productId": "gid://shopify/Product/20995642",
          "variantsIds": [
              "gid://shopify/ProductVariant/30322695",
              "gid://shopify/ProductVariant/113711323"
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
    mutation ProductVariantsDelete($productId: ID!, $variantsIds: [ID!]!) {
      productVariantsBulkDelete(productId: $productId, variantsIds: $variantsIds) {
        product {
          id
          title
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "productId": "gid://shopify/Product/20995642",
    "variantsIds": [
      "gid://shopify/ProductVariant/30322695",
      "gid://shopify/ProductVariant/113711323"
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation ProductVariantsDelete($productId: ID!, $variantsIds: [ID!]!) {
        productVariantsBulkDelete(productId: $productId, variantsIds: $variantsIds) {
          product {
            id
            title
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "productId": "gid://shopify/Product/20995642",
          "variantsIds": [
              "gid://shopify/ProductVariant/30322695",
              "gid://shopify/ProductVariant/113711323"
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation ProductVariantsDelete($productId: ID!, $variantsIds: [ID!]!) {
    productVariantsBulkDelete(productId: $productId, variantsIds: $variantsIds) {
      product {
        id
        title
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "productId": "gid://shopify/Product/20995642",
    "variantsIds": [
      "gid://shopify/ProductVariant/30322695",
      "gid://shopify/ProductVariant/113711323"
    ]
  }'
  ```

  #### Response

  ```json
  {
    "productVariantsBulkDelete": {
      "product": {
        "id": "gid://shopify/Product/20995642",
        "title": "Element"
      },
      "userErrors": []
    }
  }
  ```

* ### Returns an error if any of the product variants does not belong to the product.

  #### Query

  ```graphql
  mutation bulkDeleteProductVariants($productId: ID!, $variantsIds: [ID!]!) {
    productVariantsBulkDelete(productId: $productId, variantsIds: $variantsIds) {
      product {
        id
        title
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
    "productId": "gid://shopify/Product/20995642",
    "variantsIds": [
      "gid://shopify/ProductVariant/30322695",
      "gid://shopify/ProductVariant/-1"
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
  "query": "mutation bulkDeleteProductVariants($productId: ID!, $variantsIds: [ID!]!) { productVariantsBulkDelete(productId: $productId, variantsIds: $variantsIds) { product { id title } userErrors { field message } } }",
   "variables": {
      "productId": "gid://shopify/Product/20995642",
      "variantsIds": [
        "gid://shopify/ProductVariant/30322695",
        "gid://shopify/ProductVariant/-1"
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
    mutation bulkDeleteProductVariants($productId: ID!, $variantsIds: [ID!]!) {
      productVariantsBulkDelete(productId: $productId, variantsIds: $variantsIds) {
        product {
          id
          title
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "productId": "gid://shopify/Product/20995642",
          "variantsIds": [
              "gid://shopify/ProductVariant/30322695",
              "gid://shopify/ProductVariant/-1"
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
    mutation bulkDeleteProductVariants($productId: ID!, $variantsIds: [ID!]!) {
      productVariantsBulkDelete(productId: $productId, variantsIds: $variantsIds) {
        product {
          id
          title
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "productId": "gid://shopify/Product/20995642",
    "variantsIds": [
      "gid://shopify/ProductVariant/30322695",
      "gid://shopify/ProductVariant/-1"
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation bulkDeleteProductVariants($productId: ID!, $variantsIds: [ID!]!) {
        productVariantsBulkDelete(productId: $productId, variantsIds: $variantsIds) {
          product {
            id
            title
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "productId": "gid://shopify/Product/20995642",
          "variantsIds": [
              "gid://shopify/ProductVariant/30322695",
              "gid://shopify/ProductVariant/-1"
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation bulkDeleteProductVariants($productId: ID!, $variantsIds: [ID!]!) {
    productVariantsBulkDelete(productId: $productId, variantsIds: $variantsIds) {
      product {
        id
        title
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "productId": "gid://shopify/Product/20995642",
    "variantsIds": [
      "gid://shopify/ProductVariant/30322695",
      "gid://shopify/ProductVariant/-1"
    ]
  }'
  ```

  #### Response

  ```json
  {
    "productVariantsBulkDelete": {
      "product": null,
      "userErrors": [
        {
          "field": [
            "variantsIds",
            "1"
          ],
          "message": "At least one variant does not belong to the product"
        }
      ]
    }
  }
  ```

* ### productVariantsBulkDelete reference
