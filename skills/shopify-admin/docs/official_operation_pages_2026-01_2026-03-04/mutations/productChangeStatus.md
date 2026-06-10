---
title: productChangeStatus - GraphQL Admin
description: >-
  Changes the status of a product. This allows you to set the availability of
  the product across all channels.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/productChangeStatus
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/productChangeStatus.md
---

# product​Change​Status

mutation

Requires `write_products` access scope. Also: The user must have a permission to change products status.

Deprecated. Use [productUpdate](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productUpdate) instead.

Changes the status of a product. This allows you to set the availability of the product across all channels.

## Arguments

* product​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the product.

* status

  [Product​Status!](https://shopify.dev/docs/api/admin-graphql/latest/enums/ProductStatus)

  required

  The status to be assigned to the product.

***

## Product​Change​Status​Payload returns

* product

  [Product](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product)

  The product object.

* user​Errors

  [\[Product​Change​Status​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductChangeStatusUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Update a product's status and return its ID and new status

  #### Query

  ```graphql
  mutation productChangeStatus($productId: ID!, $status: ProductStatus!) {
    productChangeStatus(productId: $productId, status: $status) {
      product {
        id
        status
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
    "productId": "gid://shopify/Product/108828309",
    "status": "ARCHIVED"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation productChangeStatus($productId: ID!, $status: ProductStatus!) { productChangeStatus(productId: $productId, status: $status) { product { id status } userErrors { field message } } }",
   "variables": {
      "productId": "gid://shopify/Product/108828309",
      "status": "ARCHIVED"
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
    mutation productChangeStatus($productId: ID!, $status: ProductStatus!) {
      productChangeStatus(productId: $productId, status: $status) {
        product {
          id
          status
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "productId": "gid://shopify/Product/108828309",
          "status": "ARCHIVED"
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
    mutation productChangeStatus($productId: ID!, $status: ProductStatus!) {
      productChangeStatus(productId: $productId, status: $status) {
        product {
          id
          status
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "productId": "gid://shopify/Product/108828309",
    "status": "ARCHIVED"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation productChangeStatus($productId: ID!, $status: ProductStatus!) {
        productChangeStatus(productId: $productId, status: $status) {
          product {
            id
            status
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "productId": "gid://shopify/Product/108828309",
          "status": "ARCHIVED"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation productChangeStatus($productId: ID!, $status: ProductStatus!) {
    productChangeStatus(productId: $productId, status: $status) {
      product {
        id
        status
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "productId": "gid://shopify/Product/108828309",
    "status": "ARCHIVED"
  }'
  ```

  #### Response

  ```json
  {
    "productChangeStatus": {
      "product": {
        "id": "gid://shopify/Product/108828309",
        "status": "ARCHIVED"
      },
      "userErrors": []
    }
  }
  ```

* ### Update the status of a product that doesn't exist

  #### Query

  ```graphql
  mutation productChangeStatus($productId: ID!, $status: ProductStatus!) {
    productChangeStatus(productId: $productId, status: $status) {
      product {
        id
        status
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
    "productId": "gid://shopify/Product/-1",
    "status": "ARCHIVED"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation productChangeStatus($productId: ID!, $status: ProductStatus!) { productChangeStatus(productId: $productId, status: $status) { product { id status } userErrors { field message } } }",
   "variables": {
      "productId": "gid://shopify/Product/-1",
      "status": "ARCHIVED"
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
    mutation productChangeStatus($productId: ID!, $status: ProductStatus!) {
      productChangeStatus(productId: $productId, status: $status) {
        product {
          id
          status
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "productId": "gid://shopify/Product/-1",
          "status": "ARCHIVED"
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
    mutation productChangeStatus($productId: ID!, $status: ProductStatus!) {
      productChangeStatus(productId: $productId, status: $status) {
        product {
          id
          status
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "productId": "gid://shopify/Product/-1",
    "status": "ARCHIVED"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation productChangeStatus($productId: ID!, $status: ProductStatus!) {
        productChangeStatus(productId: $productId, status: $status) {
          product {
            id
            status
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "productId": "gid://shopify/Product/-1",
          "status": "ARCHIVED"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation productChangeStatus($productId: ID!, $status: ProductStatus!) {
    productChangeStatus(productId: $productId, status: $status) {
      product {
        id
        status
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "productId": "gid://shopify/Product/-1",
    "status": "ARCHIVED"
  }'
  ```

  #### Response

  ```json
  {
    "productChangeStatus": {
      "product": null,
      "userErrors": [
        {
          "field": [
            "productId"
          ],
          "message": "Product does not exist"
        }
      ]
    }
  }
  ```

* ### productChangeStatus reference
