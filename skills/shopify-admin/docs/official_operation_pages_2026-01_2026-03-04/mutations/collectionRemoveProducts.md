---
title: collectionRemoveProducts - GraphQL Admin
description: >-
  Removes multiple products from a collection in a single operation. This
  mutation can process large product sets (up to 250 products) and may take
  significant time to complete for collections with many products.


  For example, when ending a seasonal promotion, merchants can remove all sale
  items from a "Summer Clearance" collection at once rather than editing each
  product individually.


  Use `CollectionRemoveProducts` to:

  - Bulk-remove products from collections efficiently

  - Clean up collection membership during catalog updates

  - Implement automated collection management workflows


  The operation processes asynchronously to avoid timeouts and performance
  issues, especially for large product sets.


  Learn more about [collection
  management](https://shopify.dev/docs/api/admin-graphql/latest/objects/Collection).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/collectionRemoveProducts
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/collectionRemoveProducts.md
---

# collection​Remove​Products

mutation

Requires `write_products` access scope. Also: The user must have a permission to remove products from a collection.

Removes multiple products from a collection in a single operation. This mutation can process large product sets (up to 250 products) and may take significant time to complete for collections with many products.

For example, when ending a seasonal promotion, merchants can remove all sale items from a "Summer Clearance" collection at once rather than editing each product individually.

Use `CollectionRemoveProducts` to:

* Bulk-remove products from collections efficiently
* Clean up collection membership during catalog updates
* Implement automated collection management workflows

The operation processes asynchronously to avoid timeouts and performance issues, especially for large product sets.

Learn more about [collection management](https://shopify.dev/docs/api/admin-graphql/latest/objects/Collection).

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the collection to remove products from. The ID must reference an existing manual collection.

* product​Ids

  [\[ID!\]!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The IDs of products to remove from the collection. The mutation doesn't validate that the products belong to the collection or whether the products exist.

***

## Collection​Remove​Products​Payload returns

* job

  [Job](https://shopify.dev/docs/api/admin-graphql/latest/objects/Job)

  The asynchronous job removing the products.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Remove a product from a manual collection

  #### Description

  Removing a product from a manual collection returns a job ID.

  #### Query

  ```graphql
  mutation collectionRemoveProducts($id: ID!, $productIds: [ID!]!) {
    collectionRemoveProducts(id: $id, productIds: $productIds) {
      job {
        done
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
    "id": "gid://shopify/Collection/1007901140",
    "productIds": [
      "gid://shopify/Product/20995642"
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
  "query": "mutation collectionRemoveProducts($id: ID!, $productIds: [ID!]!) { collectionRemoveProducts(id: $id, productIds: $productIds) { job { done id } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/Collection/1007901140",
      "productIds": [
        "gid://shopify/Product/20995642"
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
    mutation collectionRemoveProducts($id: ID!, $productIds: [ID!]!) {
      collectionRemoveProducts(id: $id, productIds: $productIds) {
        job {
          done
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
          "id": "gid://shopify/Collection/1007901140",
          "productIds": [
              "gid://shopify/Product/20995642"
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
    mutation collectionRemoveProducts($id: ID!, $productIds: [ID!]!) {
      collectionRemoveProducts(id: $id, productIds: $productIds) {
        job {
          done
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
    "id": "gid://shopify/Collection/1007901140",
    "productIds": [
      "gid://shopify/Product/20995642"
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation collectionRemoveProducts($id: ID!, $productIds: [ID!]!) {
        collectionRemoveProducts(id: $id, productIds: $productIds) {
          job {
            done
            id
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/Collection/1007901140",
          "productIds": [
              "gid://shopify/Product/20995642"
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation collectionRemoveProducts($id: ID!, $productIds: [ID!]!) {
    collectionRemoveProducts(id: $id, productIds: $productIds) {
      job {
        done
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
    "id": "gid://shopify/Collection/1007901140",
    "productIds": [
      "gid://shopify/Product/20995642"
    ]
  }'
  ```

  #### Response

  ```json
  {
    "collectionRemoveProducts": {
      "job": {
        "done": false,
        "id": "gid://shopify/Job/0d9c63ab-d903-4f1e-b9b1-6ddf55948dfb"
      },
      "userErrors": []
    }
  }
  ```

* ### Remove a product from a non-existent collection

  #### Description

  Trying to remove a product from a non-existent collection returns a user error.

  #### Query

  ```graphql
  mutation collectionRemoveProducts($id: ID!, $productIds: [ID!]!) {
    collectionRemoveProducts(id: $id, productIds: $productIds) {
      job {
        done
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
    "id": "gid://shopify/Collection/-1",
    "productIds": [
      "gid://shopify/Product/20995642"
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
  "query": "mutation collectionRemoveProducts($id: ID!, $productIds: [ID!]!) { collectionRemoveProducts(id: $id, productIds: $productIds) { job { done id } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/Collection/-1",
      "productIds": [
        "gid://shopify/Product/20995642"
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
    mutation collectionRemoveProducts($id: ID!, $productIds: [ID!]!) {
      collectionRemoveProducts(id: $id, productIds: $productIds) {
        job {
          done
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
          "id": "gid://shopify/Collection/-1",
          "productIds": [
              "gid://shopify/Product/20995642"
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
    mutation collectionRemoveProducts($id: ID!, $productIds: [ID!]!) {
      collectionRemoveProducts(id: $id, productIds: $productIds) {
        job {
          done
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
    "id": "gid://shopify/Collection/-1",
    "productIds": [
      "gid://shopify/Product/20995642"
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation collectionRemoveProducts($id: ID!, $productIds: [ID!]!) {
        collectionRemoveProducts(id: $id, productIds: $productIds) {
          job {
            done
            id
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/Collection/-1",
          "productIds": [
              "gid://shopify/Product/20995642"
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation collectionRemoveProducts($id: ID!, $productIds: [ID!]!) {
    collectionRemoveProducts(id: $id, productIds: $productIds) {
      job {
        done
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
    "id": "gid://shopify/Collection/-1",
    "productIds": [
      "gid://shopify/Product/20995642"
    ]
  }'
  ```

  #### Response

  ```json
  {
    "collectionRemoveProducts": {
      "job": null,
      "userErrors": [
        {
          "field": [
            "id"
          ],
          "message": "Collection does not exist"
        }
      ]
    }
  }
  ```

* ### Remove a product from a smart collection

  #### Description

  Trying to manually remove a product from a smart collection returns a user error.

  #### Query

  ```graphql
  mutation collectionRemoveProducts($id: ID!, $productIds: [ID!]!) {
    collectionRemoveProducts(id: $id, productIds: $productIds) {
      job {
        done
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
    "id": "gid://shopify/Collection/142458073",
    "productIds": [
      "gid://shopify/Product/108828309"
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
  "query": "mutation collectionRemoveProducts($id: ID!, $productIds: [ID!]!) { collectionRemoveProducts(id: $id, productIds: $productIds) { job { done id } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/Collection/142458073",
      "productIds": [
        "gid://shopify/Product/108828309"
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
    mutation collectionRemoveProducts($id: ID!, $productIds: [ID!]!) {
      collectionRemoveProducts(id: $id, productIds: $productIds) {
        job {
          done
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
          "id": "gid://shopify/Collection/142458073",
          "productIds": [
              "gid://shopify/Product/108828309"
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
    mutation collectionRemoveProducts($id: ID!, $productIds: [ID!]!) {
      collectionRemoveProducts(id: $id, productIds: $productIds) {
        job {
          done
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
    "id": "gid://shopify/Collection/142458073",
    "productIds": [
      "gid://shopify/Product/108828309"
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation collectionRemoveProducts($id: ID!, $productIds: [ID!]!) {
        collectionRemoveProducts(id: $id, productIds: $productIds) {
          job {
            done
            id
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/Collection/142458073",
          "productIds": [
              "gid://shopify/Product/108828309"
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation collectionRemoveProducts($id: ID!, $productIds: [ID!]!) {
    collectionRemoveProducts(id: $id, productIds: $productIds) {
      job {
        done
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
    "id": "gid://shopify/Collection/142458073",
    "productIds": [
      "gid://shopify/Product/108828309"
    ]
  }'
  ```

  #### Response

  ```json
  {
    "collectionRemoveProducts": {
      "job": null,
      "userErrors": [
        {
          "field": [
            "id"
          ],
          "message": "Can't manually remove products from a smart collection"
        }
      ]
    }
  }
  ```

* ### Removes a product from a collection

  #### Query

  ```graphql
  mutation RemoveFromCollection($id: ID!, $productIds: [ID!]!) {
    collectionRemoveProducts(id: $id, productIds: $productIds) {
      job {
        done
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
    "id": "gid://shopify/Collection/1007901140",
    "productIds": [
      "gid://shopify/Product/20995642"
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
  "query": "mutation RemoveFromCollection($id: ID!, $productIds: [ID!]!) { collectionRemoveProducts(id: $id, productIds: $productIds) { job { done id } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/Collection/1007901140",
      "productIds": [
        "gid://shopify/Product/20995642"
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
    mutation RemoveFromCollection($id: ID!, $productIds: [ID!]!) {
      collectionRemoveProducts(id: $id, productIds: $productIds) {
        job {
          done
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
          "id": "gid://shopify/Collection/1007901140",
          "productIds": [
              "gid://shopify/Product/20995642"
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
    mutation RemoveFromCollection($id: ID!, $productIds: [ID!]!) {
      collectionRemoveProducts(id: $id, productIds: $productIds) {
        job {
          done
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
    "id": "gid://shopify/Collection/1007901140",
    "productIds": [
      "gid://shopify/Product/20995642"
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation RemoveFromCollection($id: ID!, $productIds: [ID!]!) {
        collectionRemoveProducts(id: $id, productIds: $productIds) {
          job {
            done
            id
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/Collection/1007901140",
          "productIds": [
              "gid://shopify/Product/20995642"
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation RemoveFromCollection($id: ID!, $productIds: [ID!]!) {
    collectionRemoveProducts(id: $id, productIds: $productIds) {
      job {
        done
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
    "id": "gid://shopify/Collection/1007901140",
    "productIds": [
      "gid://shopify/Product/20995642"
    ]
  }'
  ```

  #### Response

  ```json
  {
    "collectionRemoveProducts": {
      "job": {
        "done": false,
        "id": "gid://shopify/Job/8b553d69-6076-4dee-bc21-8c2d52457a36"
      },
      "userErrors": []
    }
  }
  ```

* ### collectionRemoveProducts reference
