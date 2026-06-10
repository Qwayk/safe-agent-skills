---
title: tagsAdd - GraphQL Admin
description: >-
  Adds tags to a resource in the store. Supported resources include
  [`Order`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order),
  [`DraftOrder`](https://shopify.dev/docs/api/admin-graphql/latest/objects/DraftOrder),
  [`Customer`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer),
  [`Product`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product),
  and
  [`Article`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Article).


  Tags help merchants organize and filter resources. See the
  [`tags`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/tagsAdd#arguments-tags)
  argument for supported input formats.


  Learn more about [using tags to organize subscription
  orders](https://shopify.dev/docs/apps/build/purchase-options/subscriptions/fulfillments/sync-orders-subscriptions#order-tagging).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/tagsAdd'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/tagsAdd.md'
---

# tags​Add

mutation

Adds tags to a resource in the store. Supported resources include [`Order`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order), [`DraftOrder`](https://shopify.dev/docs/api/admin-graphql/latest/objects/DraftOrder), [`Customer`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer), [`Product`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product), and [`Article`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Article).

Tags help merchants organize and filter resources. See the [`tags`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/tagsAdd#arguments-tags) argument for supported input formats.

Learn more about [using tags to organize subscription orders](https://shopify.dev/docs/apps/build/purchase-options/subscriptions/fulfillments/sync-orders-subscriptions#order-tagging).

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of a resource to add tags to.

* tags

  [\[String!\]!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  required

  A list of tags to add to the resource. Can be an array of strings or a single string composed of a comma-separated list of values. Example values: `["tag1", "tag2", "tag3"]`, `"tag1, tag2, tag3"`.

***

## Tags​Add​Payload returns

* node

  [Node](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/Node)

  The object that was updated.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Add tags to a customer

  #### Query

  ```graphql
  mutation addTags($id: ID!, $tags: [String!]!) {
    tagsAdd(id: $id, tags: $tags) {
      node {
        id
      }
      userErrors {
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/Customer/544365967",
    "tags": "one, two, three"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation addTags($id: ID!, $tags: [String!]!) { tagsAdd(id: $id, tags: $tags) { node { id } userErrors { message } } }",
   "variables": {
      "id": "gid://shopify/Customer/544365967",
      "tags": "one, two, three"
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
    mutation addTags($id: ID!, $tags: [String!]!) {
      tagsAdd(id: $id, tags: $tags) {
        node {
          id
        }
        userErrors {
          message
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/Customer/544365967",
          "tags": "one, two, three"
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
    mutation addTags($id: ID!, $tags: [String!]!) {
      tagsAdd(id: $id, tags: $tags) {
        node {
          id
        }
        userErrors {
          message
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/Customer/544365967",
    "tags": "one, two, three"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation addTags($id: ID!, $tags: [String!]!) {
        tagsAdd(id: $id, tags: $tags) {
          node {
            id
          }
          userErrors {
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/Customer/544365967",
          "tags": "one, two, three"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation addTags($id: ID!, $tags: [String!]!) {
    tagsAdd(id: $id, tags: $tags) {
      node {
        id
      }
      userErrors {
        message
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/Customer/544365967",
    "tags": "one, two, three"
  }'
  ```

  #### Response

  ```json
  {
    "tagsAdd": {
      "node": {
        "id": "gid://shopify/Customer/544365967"
      },
      "userErrors": []
    }
  }
  ```

* ### Add tags to a product

  #### Query

  ```graphql
  mutation addTags($id: ID!, $tags: [String!]!) {
    tagsAdd(id: $id, tags: $tags) {
      node {
        id
      }
      userErrors {
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/Product/20995642",
    "tags": "one, two, three"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation addTags($id: ID!, $tags: [String!]!) { tagsAdd(id: $id, tags: $tags) { node { id } userErrors { message } } }",
   "variables": {
      "id": "gid://shopify/Product/20995642",
      "tags": "one, two, three"
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
    mutation addTags($id: ID!, $tags: [String!]!) {
      tagsAdd(id: $id, tags: $tags) {
        node {
          id
        }
        userErrors {
          message
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/Product/20995642",
          "tags": "one, two, three"
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
    mutation addTags($id: ID!, $tags: [String!]!) {
      tagsAdd(id: $id, tags: $tags) {
        node {
          id
        }
        userErrors {
          message
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/Product/20995642",
    "tags": "one, two, three"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation addTags($id: ID!, $tags: [String!]!) {
        tagsAdd(id: $id, tags: $tags) {
          node {
            id
          }
          userErrors {
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/Product/20995642",
          "tags": "one, two, three"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation addTags($id: ID!, $tags: [String!]!) {
    tagsAdd(id: $id, tags: $tags) {
      node {
        id
      }
      userErrors {
        message
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/Product/20995642",
    "tags": "one, two, three"
  }'
  ```

  #### Response

  ```json
  {
    "tagsAdd": {
      "node": {
        "id": "gid://shopify/Product/20995642"
      },
      "userErrors": []
    }
  }
  ```

* ### Attempt to add tags to an product that does not exist

  #### Query

  ```graphql
  mutation addTags($id: ID!, $tags: [String!]!) {
    tagsAdd(id: $id, tags: $tags) {
      node {
        id
      }
      userErrors {
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/Product/12345",
    "tags": "one, two, three"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation addTags($id: ID!, $tags: [String!]!) { tagsAdd(id: $id, tags: $tags) { node { id } userErrors { message } } }",
   "variables": {
      "id": "gid://shopify/Product/12345",
      "tags": "one, two, three"
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
    mutation addTags($id: ID!, $tags: [String!]!) {
      tagsAdd(id: $id, tags: $tags) {
        node {
          id
        }
        userErrors {
          message
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/Product/12345",
          "tags": "one, two, three"
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
    mutation addTags($id: ID!, $tags: [String!]!) {
      tagsAdd(id: $id, tags: $tags) {
        node {
          id
        }
        userErrors {
          message
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/Product/12345",
    "tags": "one, two, three"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation addTags($id: ID!, $tags: [String!]!) {
        tagsAdd(id: $id, tags: $tags) {
          node {
            id
          }
          userErrors {
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/Product/12345",
          "tags": "one, two, three"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation addTags($id: ID!, $tags: [String!]!) {
    tagsAdd(id: $id, tags: $tags) {
      node {
        id
      }
      userErrors {
        message
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/Product/12345",
    "tags": "one, two, three"
  }'
  ```

  #### Response

  ```json
  {
    "tagsAdd": {
      "node": null,
      "userErrors": [
        {
          "message": "Product does not exist"
        }
      ]
    }
  }
  ```

* ### tagsAdd reference
