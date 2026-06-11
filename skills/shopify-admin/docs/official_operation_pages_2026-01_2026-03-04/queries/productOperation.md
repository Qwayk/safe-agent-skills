---
title: productOperation - GraphQL Admin
description: >-
  Returns a ProductOperation resource by ID.


  This can be used to query the

  [ProductSetOperation](/docs/api/admin-graphql/2026-01/objects/ProductSetOperation),
  using

  the ID that was returned

  [when the product was created or
  updated](https://shopify.dev/api/admin/migrate/new-product-model/sync-data#create-a-product-with-variants-and-options-asynchronously)

  by the

  [ProductSet](/docs/api/admin-graphql/2026-01/mutations/productSet) mutation.


  The `status` field indicates whether the operation is `CREATED`, `ACTIVE`, or
  `COMPLETE`.


  The `product` field provides the details of the created or updated product.


  For the

  [ProductSetOperation](/docs/api/admin-graphql/2026-01/objects/ProductSetOperation),
  the

  `userErrors` field provides mutation errors that occurred during the
  operation.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/productOperation'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/productOperation.md
---

# product​Operation

query

Returns a ProductOperation resource by ID.

This can be used to query the [ProductSetOperation](https://shopify.dev/docs/api/admin-graphql/2026-01/objects/ProductSetOperation), using the ID that was returned [when the product was created or updated](https://shopify.dev/api/admin/migrate/new-product-model/sync-data#create-a-product-with-variants-and-options-asynchronously) by the [ProductSet](https://shopify.dev/docs/api/admin-graphql/2026-01/mutations/productSet) mutation.

The `status` field indicates whether the operation is `CREATED`, `ACTIVE`, or `COMPLETE`.

The `product` field provides the details of the created or updated product.

For the [ProductSetOperation](https://shopify.dev/docs/api/admin-graphql/2026-01/objects/ProductSetOperation), the `userErrors` field provides mutation errors that occurred during the operation.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the `ProductOperation` to return.

***

## Possible returns

* Product​Operation

  [Product​Operation](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/ProductOperation)

  An interface representing asynchronous operations on products. Tracks the status and details of background product mutations like `productSet`, `productDelete`, `productDuplicate`, and `productBundle` operations. Provides status field (CREATED, ACTIVE, COMPLETE) and product field to monitor long-running product operations.

  * product

    [Product](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product)

    The product on which the operation is being performed.

  * status

    [Product​Operation​Status!](https://shopify.dev/docs/api/admin-graphql/latest/enums/ProductOperationStatus)

    non-null

    The status of this operation.

***

## Examples

* ### View the status of an asynchronous product delete operation

  #### Query

  ```graphql
  query ProductDeleteOperation($id: ID!) {
    productOperation(id: $id) {
      ... on ProductDeleteOperation {
        id
        status
        deletedProductId
        product {
          id
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/ProductDeleteOperation/843567278"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query ProductDeleteOperation($id: ID!) { productOperation(id: $id) { ... on ProductDeleteOperation { id status deletedProductId product { id } } } }",
   "variables": {
      "id": "gid://shopify/ProductDeleteOperation/843567278"
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
    query ProductDeleteOperation($id: ID!) {
      productOperation(id: $id) {
        ... on ProductDeleteOperation {
          id
          status
          deletedProductId
          product {
            id
          }
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/ProductDeleteOperation/843567278"
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
    query ProductDeleteOperation($id: ID!) {
      productOperation(id: $id) {
        ... on ProductDeleteOperation {
          id
          status
          deletedProductId
          product {
            id
          }
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/ProductDeleteOperation/843567278"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query ProductDeleteOperation($id: ID!) {
        productOperation(id: $id) {
          ... on ProductDeleteOperation {
            id
            status
            deletedProductId
            product {
              id
            }
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/ProductDeleteOperation/843567278"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query ProductDeleteOperation($id: ID!) {
    productOperation(id: $id) {
      ... on ProductDeleteOperation {
        id
        status
        deletedProductId
        product {
          id
        }
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/ProductDeleteOperation/843567278"
  }'
  ```

  #### Response

  ```json
  {
    "productOperation": {
      "id": "gid://shopify/ProductDeleteOperation/843567278",
      "status": "COMPLETE",
      "deletedProductId": "gid://shopify/Product/20995642",
      "product": null
    }
  }
  ```

* ### View the status of an asynchronous product duplicate operation

  #### Query

  ```graphql
  query ProductDuplicateOperation($operationId: ID!) {
    productOperation(id: $operationId) {
      ... on ProductDuplicateOperation {
        id
        status
        newProduct {
          id
          title
        }
        userErrors {
          field
          message
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "operationId": "gid://shopify/ProductDuplicateOperation/893212316"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query ProductDuplicateOperation($operationId: ID!) { productOperation(id: $operationId) { ... on ProductDuplicateOperation { id status newProduct { id title } userErrors { field message } } } }",
   "variables": {
      "operationId": "gid://shopify/ProductDuplicateOperation/893212316"
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
    query ProductDuplicateOperation($operationId: ID!) {
      productOperation(id: $operationId) {
        ... on ProductDuplicateOperation {
          id
          status
          newProduct {
            id
            title
          }
          userErrors {
            field
            message
          }
        }
      }
    }`,
    {
      variables: {
          "operationId": "gid://shopify/ProductDuplicateOperation/893212316"
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
    query ProductDuplicateOperation($operationId: ID!) {
      productOperation(id: $operationId) {
        ... on ProductDuplicateOperation {
          id
          status
          newProduct {
            id
            title
          }
          userErrors {
            field
            message
          }
        }
      }
    }
  QUERY

  variables = {
    "operationId": "gid://shopify/ProductDuplicateOperation/893212316"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query ProductDuplicateOperation($operationId: ID!) {
        productOperation(id: $operationId) {
          ... on ProductDuplicateOperation {
            id
            status
            newProduct {
              id
              title
            }
            userErrors {
              field
              message
            }
          }
        }
      }`,
      "variables": {
          "operationId": "gid://shopify/ProductDuplicateOperation/893212316"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query ProductDuplicateOperation($operationId: ID!) {
    productOperation(id: $operationId) {
      ... on ProductDuplicateOperation {
        id
        status
        newProduct {
          id
          title
        }
        userErrors {
          field
          message
        }
      }
    }
  }' \
  --variables \
  '{
    "operationId": "gid://shopify/ProductDuplicateOperation/893212316"
  }'
  ```

  #### Response

  ```json
  {
    "productOperation": {
      "id": "gid://shopify/ProductDuplicateOperation/893212316",
      "status": "COMPLETE",
      "newProduct": {
        "id": "gid://shopify/Product/108828309",
        "title": "Draft (Copy)"
      },
      "userErrors": []
    }
  }
  ```

* ### View the status of an asynchronous product set operation

  #### Query

  ```graphql
  query productSetOperation($id: ID!) {
    productOperation(id: $id) {
      ... on ProductSetOperation {
        id
        status
        product {
          id
        }
        userErrors {
          field
          message
          code
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/ProductSetOperation/824846712"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query productSetOperation($id: ID!) { productOperation(id: $id) { ... on ProductSetOperation { id status product { id } userErrors { field message code } } } }",
   "variables": {
      "id": "gid://shopify/ProductSetOperation/824846712"
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
    query productSetOperation($id: ID!) {
      productOperation(id: $id) {
        ... on ProductSetOperation {
          id
          status
          product {
            id
          }
          userErrors {
            field
            message
            code
          }
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/ProductSetOperation/824846712"
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
    query productSetOperation($id: ID!) {
      productOperation(id: $id) {
        ... on ProductSetOperation {
          id
          status
          product {
            id
          }
          userErrors {
            field
            message
            code
          }
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/ProductSetOperation/824846712"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query productSetOperation($id: ID!) {
        productOperation(id: $id) {
          ... on ProductSetOperation {
            id
            status
            product {
              id
            }
            userErrors {
              field
              message
              code
            }
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/ProductSetOperation/824846712"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query productSetOperation($id: ID!) {
    productOperation(id: $id) {
      ... on ProductSetOperation {
        id
        status
        product {
          id
        }
        userErrors {
          field
          message
          code
        }
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/ProductSetOperation/824846712"
  }'
  ```

  #### Response

  ```json
  {
    "productOperation": {
      "id": "gid://shopify/ProductSetOperation/824846712",
      "status": "COMPLETE",
      "product": {
        "id": "gid://shopify/Product/20995642"
      },
      "userErrors": []
    }
  }
  ```
