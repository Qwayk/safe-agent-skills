---
title: collectionReorderProducts - GraphQL Admin
description: >-
  Asynchronously reorders products within a specified collection. Instead of
  returning an updated collection, this mutation returns a job, which should be
  [polled](https://shopify.dev/api/admin-graphql/latest/queries/job). The
  [`Collection.sortOrder`](https://shopify.dev/api/admin-graphql/latest/objects/Collection#field-collection-sortorder)
  must be `MANUAL`.


  How to use this mutation:

  - Provide only the products that actually moved in the `moves` list; do not
  send the entire product list. For example: to move the product at index 1 to
  index N, send a single move for that product with `newPosition: N`.

  - Each move is applied sequentially in the order provided.

  - `newPosition` is a zero-based index within the collection at the moment the
  move is applied (after any prior moves in the list).

  - Products not included in `moves` keep their relative order, aside from any
  displacement caused by the moves.

  - If `newPosition` is greater than or equal to the number of products, the
  product is placed at the end.


  Example:

  - Initial order: [A, B, C, D, E] (indices 0..4)

  - Moves (applied in order):
    - E -> newPosition: 1
    - C -> newPosition: 4
  - Result: [A, E, B, D, C]


  Displaced products will have their position altered in a consistent manner
  with no gaps.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/collectionReorderProducts
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/collectionReorderProducts.md
---

# collection​Reorder​Products

mutation

Requires `write_products` access scope. Also: The user must have a permission to reorder products within a collection.

Asynchronously reorders products within a specified collection. Instead of returning an updated collection, this mutation returns a job, which should be [polled](https://shopify.dev/api/admin-graphql/latest/queries/job). The [`Collection.sortOrder`](https://shopify.dev/api/admin-graphql/latest/objects/Collection#field-collection-sortorder) must be `MANUAL`.

How to use this mutation:

* Provide only the products that actually moved in the `moves` list; do not send the entire product list. For example: to move the product at index 1 to index N, send a single move for that product with `newPosition: N`.
* Each move is applied sequentially in the order provided.
* `newPosition` is a zero-based index within the collection at the moment the move is applied (after any prior moves in the list).
* Products not included in `moves` keep their relative order, aside from any displacement caused by the moves.
* If `newPosition` is greater than or equal to the number of products, the product is placed at the end.

Example:

* Initial order: \[A, B, C, D, E] (indices 0..4)

* Moves (applied in order):

  * E -> newPosition: 1
  * C -> newPosition: 4

* Result: \[A, E, B, D, C]

Displaced products will have their position altered in a consistent manner with no gaps.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the collection on which to reorder products.

* moves

  [\[Move​Input!\]!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/MoveInput)

  required

  A list of moves to perform, evaluated in order. Provide only products whose positions changed; do not send the full list. `newPosition` is a zero-based index evaluated at the time each move is applied (after any prior moves). `newPosition` values do not need to be unique, and if a value is greater than or equal to the number of products, the product is moved to the end. Up to 250 moves are supported.

***

## Collection​Reorder​Products​Payload returns

* job

  [Job](https://shopify.dev/docs/api/admin-graphql/latest/objects/Job)

  The asynchronous job reordering the products.

* user​Errors

  [\[Collection​Reorder​Products​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CollectionReorderProductsUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Move a product to the top of a collection

  #### Description

  Moving a product to the top of a collection will return a job ID. All other product positions will be updated and incremented by 1 during processing.

  #### Query

  ```graphql
  mutation collectionReorderProducts($id: ID!, $moves: [MoveInput!]!) {
    collectionReorderProducts(id: $id, moves: $moves) {
      job {
        id
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
    "id": "gid://shopify/Collection/79210309",
    "moves": {
      "id": "gid://shopify/Product/20995642",
      "newPosition": "0"
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
  "query": "mutation collectionReorderProducts($id: ID!, $moves: [MoveInput!]!) { collectionReorderProducts(id: $id, moves: $moves) { job { id } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/Collection/79210309",
      "moves": {
        "id": "gid://shopify/Product/20995642",
        "newPosition": "0"
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
    mutation collectionReorderProducts($id: ID!, $moves: [MoveInput!]!) {
      collectionReorderProducts(id: $id, moves: $moves) {
        job {
          id
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/Collection/79210309",
          "moves": {
              "id": "gid://shopify/Product/20995642",
              "newPosition": "0"
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
    mutation collectionReorderProducts($id: ID!, $moves: [MoveInput!]!) {
      collectionReorderProducts(id: $id, moves: $moves) {
        job {
          id
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/Collection/79210309",
    "moves": {
      "id": "gid://shopify/Product/20995642",
      "newPosition": "0"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation collectionReorderProducts($id: ID!, $moves: [MoveInput!]!) {
        collectionReorderProducts(id: $id, moves: $moves) {
          job {
            id
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/Collection/79210309",
          "moves": {
              "id": "gid://shopify/Product/20995642",
              "newPosition": "0"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation collectionReorderProducts($id: ID!, $moves: [MoveInput!]!) {
    collectionReorderProducts(id: $id, moves: $moves) {
      job {
        id
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/Collection/79210309",
    "moves": {
      "id": "gid://shopify/Product/20995642",
      "newPosition": "0"
    }
  }'
  ```

  #### Response

  ```json
  {
    "collectionReorderProducts": {
      "job": {
        "id": "gid://shopify/Job/af3cb206-d472-4a54-902b-f34df6af4eb5"
      },
      "userErrors": []
    }
  }
  ```

* ### Move a product to the top of a sorted collection

  #### Description

  Attempting to move a product within a non-manually sorted collection will return a user error.

  #### Query

  ```graphql
  mutation collectionReorderProducts($id: ID!, $moves: [MoveInput!]!) {
    collectionReorderProducts(id: $id, moves: $moves) {
      job {
        id
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
    "id": "gid://shopify/Collection/1063001310",
    "moves": {
      "id": "gid://shopify/Product/108828309",
      "newPosition": "0"
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
  "query": "mutation collectionReorderProducts($id: ID!, $moves: [MoveInput!]!) { collectionReorderProducts(id: $id, moves: $moves) { job { id } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/Collection/1063001310",
      "moves": {
        "id": "gid://shopify/Product/108828309",
        "newPosition": "0"
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
    mutation collectionReorderProducts($id: ID!, $moves: [MoveInput!]!) {
      collectionReorderProducts(id: $id, moves: $moves) {
        job {
          id
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/Collection/1063001310",
          "moves": {
              "id": "gid://shopify/Product/108828309",
              "newPosition": "0"
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
    mutation collectionReorderProducts($id: ID!, $moves: [MoveInput!]!) {
      collectionReorderProducts(id: $id, moves: $moves) {
        job {
          id
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/Collection/1063001310",
    "moves": {
      "id": "gid://shopify/Product/108828309",
      "newPosition": "0"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation collectionReorderProducts($id: ID!, $moves: [MoveInput!]!) {
        collectionReorderProducts(id: $id, moves: $moves) {
          job {
            id
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/Collection/1063001310",
          "moves": {
              "id": "gid://shopify/Product/108828309",
              "newPosition": "0"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation collectionReorderProducts($id: ID!, $moves: [MoveInput!]!) {
    collectionReorderProducts(id: $id, moves: $moves) {
      job {
        id
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/Collection/1063001310",
    "moves": {
      "id": "gid://shopify/Product/108828309",
      "newPosition": "0"
    }
  }'
  ```

  #### Response

  ```json
  {
    "collectionReorderProducts": {
      "job": null,
      "userErrors": [
        {
          "field": [
            "id"
          ],
          "message": "Can't reorder products unless collection is manually sorted"
        }
      ]
    }
  }
  ```

* ### Updates the ordering type of products in a smart collection

  #### Query

  ```graphql
  mutation UpdateCollectionSortOrder($id: ID!, $sortOrder: CollectionSortOrder!) {
    collectionUpdate(input: {id: $id, sortOrder: $sortOrder}) {
      collection {
        id
        sortOrder
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
    "id": "gid://shopify/Collection/1063001310",
    "sortOrder": "MANUAL"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation UpdateCollectionSortOrder($id: ID!, $sortOrder: CollectionSortOrder!) { collectionUpdate(input: {id: $id, sortOrder: $sortOrder}) { collection { id sortOrder } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/Collection/1063001310",
      "sortOrder": "MANUAL"
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
    mutation UpdateCollectionSortOrder($id: ID!, $sortOrder: CollectionSortOrder!) {
      collectionUpdate(input: {id: $id, sortOrder: $sortOrder}) {
        collection {
          id
          sortOrder
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/Collection/1063001310",
          "sortOrder": "MANUAL"
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
    mutation UpdateCollectionSortOrder($id: ID!, $sortOrder: CollectionSortOrder!) {
      collectionUpdate(input: {id: $id, sortOrder: $sortOrder}) {
        collection {
          id
          sortOrder
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/Collection/1063001310",
    "sortOrder": "MANUAL"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation UpdateCollectionSortOrder($id: ID!, $sortOrder: CollectionSortOrder!) {
        collectionUpdate(input: {id: $id, sortOrder: $sortOrder}) {
          collection {
            id
            sortOrder
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/Collection/1063001310",
          "sortOrder": "MANUAL"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation UpdateCollectionSortOrder($id: ID!, $sortOrder: CollectionSortOrder!) {
    collectionUpdate(input: {id: $id, sortOrder: $sortOrder}) {
      collection {
        id
        sortOrder
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/Collection/1063001310",
    "sortOrder": "MANUAL"
  }'
  ```

  #### Response

  ```json
  {
    "collectionUpdate": {
      "collection": {
        "id": "gid://shopify/Collection/1063001310",
        "sortOrder": "MANUAL"
      },
      "userErrors": []
    }
  }
  ```

* ### collectionReorderProducts reference
