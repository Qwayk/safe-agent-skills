---
title: collectionAddProducts - GraphQL Admin
description: >-
  Adds multiple products to an existing collection in a single operation. This
  mutation provides an efficient way to bulk-manage collection membership
  without individual product updates.


  For example, when merchants create seasonal collections, they can add dozens
  of related products at once rather than updating each product individually. A
  clothing store might add all winter jackets to a "Winter Collection" in one
  operation.


  Use `CollectionAddProducts` to:

  - Bulk-add products to collections for efficient catalog management

  - Implement collection building tools in admin interfaces

  - Organize collection membership during bulk product operations

  - Reduce API calls when managing large product sets


  The mutation processes multiple product additions and returns success status
  along with any errors encountered during the operation. Products are added to
  the collection while preserving existing collection settings.


  This operation only works with manual collections where merchants explicitly
  choose which products to include. It will return an error if used with smart
  collections that automatically include products based on conditions.


  Learn more about [collection
  management](https://shopify.dev/docs/api/admin-graphql/latest/objects/Collection).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/collectionAddProducts
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/collectionAddProducts.md
---

# collection​Add​Products

mutation

Requires `write_products` access scope. Also: The store must not be on the Starter or Retail plans and user must have a permission to add products to a collection.

Adds multiple products to an existing collection in a single operation. This mutation provides an efficient way to bulk-manage collection membership without individual product updates.

For example, when merchants create seasonal collections, they can add dozens of related products at once rather than updating each product individually. A clothing store might add all winter jackets to a "Winter Collection" in one operation.

Use `CollectionAddProducts` to:

* Bulk-add products to collections for efficient catalog management
* Implement collection building tools in admin interfaces
* Organize collection membership during bulk product operations
* Reduce API calls when managing large product sets

The mutation processes multiple product additions and returns success status along with any errors encountered during the operation. Products are added to the collection while preserving existing collection settings.

This operation only works with manual collections where merchants explicitly choose which products to include. It will return an error if used with smart collections that automatically include products based on conditions.

Learn more about [collection management](https://shopify.dev/docs/api/admin-graphql/latest/objects/Collection).

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the collection that's being updated. This can't be a smart collection.

* product​Ids

  [\[ID!\]!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The IDs of the products that are being added to the collection. If any of the products is already present in the input collection, then an error is raised and no products are added.

***

## Collection​Add​Products​Payload returns

* collection

  [Collection](https://shopify.dev/docs/api/admin-graphql/latest/objects/Collection)

  The updated collection. Returns `null` if an error is raised.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Add a product to a collection that doesn't exist

  #### Description

  If the input collection doesn't exist, then the mutation returns an error.

  #### Query

  ```graphql
  mutation collectionAddProducts($id: ID!, $productIds: [ID!]!) {
    collectionAddProducts(id: $id, productIds: $productIds) {
      collection {
        id
        title
        products(first: 10) {
          nodes {
            id
            title
          }
        }
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
  "query": "mutation collectionAddProducts($id: ID!, $productIds: [ID!]!) { collectionAddProducts(id: $id, productIds: $productIds) { collection { id title products(first: 10) { nodes { id title } } } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/Collection/-1",
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
    mutation collectionAddProducts($id: ID!, $productIds: [ID!]!) {
      collectionAddProducts(id: $id, productIds: $productIds) {
        collection {
          id
          title
          products(first: 10) {
            nodes {
              id
              title
            }
          }
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
    mutation collectionAddProducts($id: ID!, $productIds: [ID!]!) {
      collectionAddProducts(id: $id, productIds: $productIds) {
        collection {
          id
          title
          products(first: 10) {
            nodes {
              id
              title
            }
          }
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
      "query": `mutation collectionAddProducts($id: ID!, $productIds: [ID!]!) {
        collectionAddProducts(id: $id, productIds: $productIds) {
          collection {
            id
            title
            products(first: 10) {
              nodes {
                id
                title
              }
            }
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
  'mutation collectionAddProducts($id: ID!, $productIds: [ID!]!) {
    collectionAddProducts(id: $id, productIds: $productIds) {
      collection {
        id
        title
        products(first: 10) {
          nodes {
            id
            title
          }
        }
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
      "gid://shopify/Product/108828309"
    ]
  }'
  ```

  #### Response

  ```json
  {
    "collectionAddProducts": {
      "collection": null,
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

* ### Add a product to a smart collection

  #### Description

  Products can't be manually added to a smart collection, so the mutation returns an error.

  #### Query

  ```graphql
  mutation collectionAddProducts($id: ID!, $productIds: [ID!]!) {
    collectionAddProducts(id: $id, productIds: $productIds) {
      collection {
        id
        title
        products(first: 10) {
          nodes {
            id
            title
          }
        }
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
      "gid://shopify/Product/910489600"
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
  "query": "mutation collectionAddProducts($id: ID!, $productIds: [ID!]!) { collectionAddProducts(id: $id, productIds: $productIds) { collection { id title products(first: 10) { nodes { id title } } } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/Collection/142458073",
      "productIds": [
        "gid://shopify/Product/910489600"
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
    mutation collectionAddProducts($id: ID!, $productIds: [ID!]!) {
      collectionAddProducts(id: $id, productIds: $productIds) {
        collection {
          id
          title
          products(first: 10) {
            nodes {
              id
              title
            }
          }
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
              "gid://shopify/Product/910489600"
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
    mutation collectionAddProducts($id: ID!, $productIds: [ID!]!) {
      collectionAddProducts(id: $id, productIds: $productIds) {
        collection {
          id
          title
          products(first: 10) {
            nodes {
              id
              title
            }
          }
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
      "gid://shopify/Product/910489600"
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation collectionAddProducts($id: ID!, $productIds: [ID!]!) {
        collectionAddProducts(id: $id, productIds: $productIds) {
          collection {
            id
            title
            products(first: 10) {
              nodes {
                id
                title
              }
            }
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
              "gid://shopify/Product/910489600"
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation collectionAddProducts($id: ID!, $productIds: [ID!]!) {
    collectionAddProducts(id: $id, productIds: $productIds) {
      collection {
        id
        title
        products(first: 10) {
          nodes {
            id
            title
          }
        }
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
      "gid://shopify/Product/910489600"
    ]
  }'
  ```

  #### Response

  ```json
  {
    "collectionAddProducts": {
      "collection": null,
      "userErrors": [
        {
          "field": [
            "id"
          ],
          "message": "Can't manually add products to a smart collection"
        }
      ]
    }
  }
  ```

* ### Add products that already belong to the specified collection

  #### Description

  An error is returned and no products are added if any of the input products already belong to the input collection.

  #### Query

  ```graphql
  mutation collectionAddProducts($id: ID!, $productIds: [ID!]!) {
    collectionAddProducts(id: $id, productIds: $productIds) {
      collection {
        id
        title
        products(first: 10) {
          nodes {
            id
            title
          }
        }
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
      "gid://shopify/Product/108828309",
      "gid://shopify/Product/632910392",
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
  "query": "mutation collectionAddProducts($id: ID!, $productIds: [ID!]!) { collectionAddProducts(id: $id, productIds: $productIds) { collection { id title products(first: 10) { nodes { id title } } } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/Collection/1007901140",
      "productIds": [
        "gid://shopify/Product/108828309",
        "gid://shopify/Product/632910392",
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
    mutation collectionAddProducts($id: ID!, $productIds: [ID!]!) {
      collectionAddProducts(id: $id, productIds: $productIds) {
        collection {
          id
          title
          products(first: 10) {
            nodes {
              id
              title
            }
          }
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
              "gid://shopify/Product/108828309",
              "gid://shopify/Product/632910392",
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
    mutation collectionAddProducts($id: ID!, $productIds: [ID!]!) {
      collectionAddProducts(id: $id, productIds: $productIds) {
        collection {
          id
          title
          products(first: 10) {
            nodes {
              id
              title
            }
          }
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
      "gid://shopify/Product/108828309",
      "gid://shopify/Product/632910392",
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
      "query": `mutation collectionAddProducts($id: ID!, $productIds: [ID!]!) {
        collectionAddProducts(id: $id, productIds: $productIds) {
          collection {
            id
            title
            products(first: 10) {
              nodes {
                id
                title
              }
            }
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
              "gid://shopify/Product/108828309",
              "gid://shopify/Product/632910392",
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
  'mutation collectionAddProducts($id: ID!, $productIds: [ID!]!) {
    collectionAddProducts(id: $id, productIds: $productIds) {
      collection {
        id
        title
        products(first: 10) {
          nodes {
            id
            title
          }
        }
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
      "gid://shopify/Product/108828309",
      "gid://shopify/Product/632910392",
      "gid://shopify/Product/20995642"
    ]
  }'
  ```

  #### Response

  ```json
  {
    "collectionAddProducts": {
      "collection": null,
      "userErrors": [
        {
          "field": [
            "productIds"
          ],
          "message": "Error adding gid://shopify/Product/108828309,gid://shopify/Product/20995642 to collection"
        }
      ]
    }
  }
  ```

* ### Add products that don't exist to an existing collection

  #### Description

  Products that don't exist are ignored.

  #### Query

  ```graphql
  mutation collectionAddProducts($id: ID!, $productIds: [ID!]!) {
    collectionAddProducts(id: $id, productIds: $productIds) {
      collection {
        id
        title
        products(first: 10) {
          nodes {
            id
            title
          }
        }
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
    "id": "gid://shopify/Collection/636030761",
    "productIds": [
      "gid://shopify/Product/-1",
      "gid://shopify/Product/108828309",
      "gid://shopify/Product/-2"
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
  "query": "mutation collectionAddProducts($id: ID!, $productIds: [ID!]!) { collectionAddProducts(id: $id, productIds: $productIds) { collection { id title products(first: 10) { nodes { id title } } } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/Collection/636030761",
      "productIds": [
        "gid://shopify/Product/-1",
        "gid://shopify/Product/108828309",
        "gid://shopify/Product/-2"
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
    mutation collectionAddProducts($id: ID!, $productIds: [ID!]!) {
      collectionAddProducts(id: $id, productIds: $productIds) {
        collection {
          id
          title
          products(first: 10) {
            nodes {
              id
              title
            }
          }
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/Collection/636030761",
          "productIds": [
              "gid://shopify/Product/-1",
              "gid://shopify/Product/108828309",
              "gid://shopify/Product/-2"
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
    mutation collectionAddProducts($id: ID!, $productIds: [ID!]!) {
      collectionAddProducts(id: $id, productIds: $productIds) {
        collection {
          id
          title
          products(first: 10) {
            nodes {
              id
              title
            }
          }
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/Collection/636030761",
    "productIds": [
      "gid://shopify/Product/-1",
      "gid://shopify/Product/108828309",
      "gid://shopify/Product/-2"
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation collectionAddProducts($id: ID!, $productIds: [ID!]!) {
        collectionAddProducts(id: $id, productIds: $productIds) {
          collection {
            id
            title
            products(first: 10) {
              nodes {
                id
                title
              }
            }
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/Collection/636030761",
          "productIds": [
              "gid://shopify/Product/-1",
              "gid://shopify/Product/108828309",
              "gid://shopify/Product/-2"
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation collectionAddProducts($id: ID!, $productIds: [ID!]!) {
    collectionAddProducts(id: $id, productIds: $productIds) {
      collection {
        id
        title
        products(first: 10) {
          nodes {
            id
            title
          }
        }
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/Collection/636030761",
    "productIds": [
      "gid://shopify/Product/-1",
      "gid://shopify/Product/108828309",
      "gid://shopify/Product/-2"
    ]
  }'
  ```

  #### Response

  ```json
  {
    "collectionAddProducts": {
      "collection": {
        "id": "gid://shopify/Collection/636030761",
        "title": "Unpublished items",
        "products": {
          "nodes": [
            {
              "id": "gid://shopify/Product/108828309",
              "title": "Draft"
            }
          ]
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Add products to an existing collection

  #### Description

  Add two products with specified IDs to the collection.

  #### Query

  ```graphql
  mutation collectionAddProducts($id: ID!, $productIds: [ID!]!) {
    collectionAddProducts(id: $id, productIds: $productIds) {
      collection {
        id
        title
        products(first: 10) {
          nodes {
            id
            title
          }
        }
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
    "id": "gid://shopify/Collection/636030761",
    "productIds": [
      "gid://shopify/Product/121709582",
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
  "query": "mutation collectionAddProducts($id: ID!, $productIds: [ID!]!) { collectionAddProducts(id: $id, productIds: $productIds) { collection { id title products(first: 10) { nodes { id title } } } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/Collection/636030761",
      "productIds": [
        "gid://shopify/Product/121709582",
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
    mutation collectionAddProducts($id: ID!, $productIds: [ID!]!) {
      collectionAddProducts(id: $id, productIds: $productIds) {
        collection {
          id
          title
          products(first: 10) {
            nodes {
              id
              title
            }
          }
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/Collection/636030761",
          "productIds": [
              "gid://shopify/Product/121709582",
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
    mutation collectionAddProducts($id: ID!, $productIds: [ID!]!) {
      collectionAddProducts(id: $id, productIds: $productIds) {
        collection {
          id
          title
          products(first: 10) {
            nodes {
              id
              title
            }
          }
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/Collection/636030761",
    "productIds": [
      "gid://shopify/Product/121709582",
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
      "query": `mutation collectionAddProducts($id: ID!, $productIds: [ID!]!) {
        collectionAddProducts(id: $id, productIds: $productIds) {
          collection {
            id
            title
            products(first: 10) {
              nodes {
                id
                title
              }
            }
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/Collection/636030761",
          "productIds": [
              "gid://shopify/Product/121709582",
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
  'mutation collectionAddProducts($id: ID!, $productIds: [ID!]!) {
    collectionAddProducts(id: $id, productIds: $productIds) {
      collection {
        id
        title
        products(first: 10) {
          nodes {
            id
            title
          }
        }
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/Collection/636030761",
    "productIds": [
      "gid://shopify/Product/121709582",
      "gid://shopify/Product/108828309"
    ]
  }'
  ```

  #### Response

  ```json
  {
    "collectionAddProducts": {
      "collection": {
        "id": "gid://shopify/Collection/636030761",
        "title": "Unpublished items",
        "products": {
          "nodes": [
            {
              "id": "gid://shopify/Product/121709582",
              "title": "Boots"
            },
            {
              "id": "gid://shopify/Product/108828309",
              "title": "Draft"
            }
          ]
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Add products to collections will fail when CollectionsAccess returns false

  #### Description

  CollectionAddProducts mutation will fail for starter plan shops

  #### Query

  ```graphql
  mutation collectionAddProducts($id: ID!, $productIds: [ID!]!) {
    collectionAddProducts(id: $id, productIds: $productIds) {
      collection {
        id
        title
        products(first: 10) {
          nodes {
            id
            title
          }
        }
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
    "id": "gid://shopify/Collection/636030761",
    "productIds": [
      "gid://shopify/Product/121709582",
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
  "query": "mutation collectionAddProducts($id: ID!, $productIds: [ID!]!) { collectionAddProducts(id: $id, productIds: $productIds) { collection { id title products(first: 10) { nodes { id title } } } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/Collection/636030761",
      "productIds": [
        "gid://shopify/Product/121709582",
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
    mutation collectionAddProducts($id: ID!, $productIds: [ID!]!) {
      collectionAddProducts(id: $id, productIds: $productIds) {
        collection {
          id
          title
          products(first: 10) {
            nodes {
              id
              title
            }
          }
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/Collection/636030761",
          "productIds": [
              "gid://shopify/Product/121709582",
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
    mutation collectionAddProducts($id: ID!, $productIds: [ID!]!) {
      collectionAddProducts(id: $id, productIds: $productIds) {
        collection {
          id
          title
          products(first: 10) {
            nodes {
              id
              title
            }
          }
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/Collection/636030761",
    "productIds": [
      "gid://shopify/Product/121709582",
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
      "query": `mutation collectionAddProducts($id: ID!, $productIds: [ID!]!) {
        collectionAddProducts(id: $id, productIds: $productIds) {
          collection {
            id
            title
            products(first: 10) {
              nodes {
                id
                title
              }
            }
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/Collection/636030761",
          "productIds": [
              "gid://shopify/Product/121709582",
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
  'mutation collectionAddProducts($id: ID!, $productIds: [ID!]!) {
    collectionAddProducts(id: $id, productIds: $productIds) {
      collection {
        id
        title
        products(first: 10) {
          nodes {
            id
            title
          }
        }
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/Collection/636030761",
    "productIds": [
      "gid://shopify/Product/121709582",
      "gid://shopify/Product/108828309"
    ]
  }'
  ```

  #### Response

  ```json
  {
    "collectionAddProducts": null
  }
  ```

* ### Adds a product to a custom collection

  #### Query

  ```graphql
  mutation AddToCollection($id: ID!, $productIds: [ID!]!) {
    collectionAddProducts(id: $id, productIds: $productIds) {
      collection {
        id
        title
        products(first: 10) {
          nodes {
            id
            title
          }
        }
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
      "gid://shopify/Product/121709582"
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
  "query": "mutation AddToCollection($id: ID!, $productIds: [ID!]!) { collectionAddProducts(id: $id, productIds: $productIds) { collection { id title products(first: 10) { nodes { id title } } } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/Collection/1007901140",
      "productIds": [
        "gid://shopify/Product/121709582"
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
    mutation AddToCollection($id: ID!, $productIds: [ID!]!) {
      collectionAddProducts(id: $id, productIds: $productIds) {
        collection {
          id
          title
          products(first: 10) {
            nodes {
              id
              title
            }
          }
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
              "gid://shopify/Product/121709582"
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
    mutation AddToCollection($id: ID!, $productIds: [ID!]!) {
      collectionAddProducts(id: $id, productIds: $productIds) {
        collection {
          id
          title
          products(first: 10) {
            nodes {
              id
              title
            }
          }
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
      "gid://shopify/Product/121709582"
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation AddToCollection($id: ID!, $productIds: [ID!]!) {
        collectionAddProducts(id: $id, productIds: $productIds) {
          collection {
            id
            title
            products(first: 10) {
              nodes {
                id
                title
              }
            }
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
              "gid://shopify/Product/121709582"
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation AddToCollection($id: ID!, $productIds: [ID!]!) {
    collectionAddProducts(id: $id, productIds: $productIds) {
      collection {
        id
        title
        products(first: 10) {
          nodes {
            id
            title
          }
        }
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
      "gid://shopify/Product/121709582"
    ]
  }'
  ```

  #### Response

  ```json
  {
    "collectionAddProducts": {
      "collection": {
        "id": "gid://shopify/Collection/1007901140",
        "title": "Featured items",
        "products": {
          "nodes": [
            {
              "id": "gid://shopify/Product/108828309",
              "title": "Draft"
            },
            {
              "id": "gid://shopify/Product/20995642",
              "title": "Element"
            },
            {
              "id": "gid://shopify/Product/121709582",
              "title": "Boots"
            }
          ]
        }
      },
      "userErrors": []
    }
  }
  ```

* ### collectionAddProducts reference
