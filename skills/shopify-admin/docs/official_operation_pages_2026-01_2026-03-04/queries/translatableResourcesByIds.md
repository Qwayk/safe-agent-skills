---
title: translatableResourcesByIds - GraphQL Admin
description: >-
  Returns a paginated list of
  [`TranslatableResource`](https://shopify.dev/docs/api/admin-graphql/latest/objects/TranslatableResource)
  objects for the specified resource IDs. Each resource provides translatable
  content and digest values needed for the
  [`translationsRegister`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/translationsRegister)
  mutation.


  Learn more about [managing translated
  content](https://shopify.dev/docs/apps/build/markets/manage-translated-content).
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/translatableResourcesByIds
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/translatableResourcesByIds.md
---

# translatable​Resources​By​Ids

query

Requires `read_translations` access scope.

Returns a paginated list of [`TranslatableResource`](https://shopify.dev/docs/api/admin-graphql/latest/objects/TranslatableResource) objects for the specified resource IDs. Each resource provides translatable content and digest values needed for the [`translationsRegister`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/translationsRegister) mutation.

Learn more about [managing translated content](https://shopify.dev/docs/apps/build/markets/manage-translated-content).

## TranslatableResourceConnection arguments

[TranslatableResourceConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/TranslatableResourceConnection)

* after

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* before

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* first

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* last

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* resource​Ids

  [\[ID!\]!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  Return only resources for given IDs.

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

***

## Possible returns

* edges

  [\[Translatable​Resource​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/TranslatableResourceEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Translatable​Resource!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/TranslatableResource)

  non-null

  A list of nodes that are contained in TranslatableResourceEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### Retrieve translatable content for a product

  #### Description

  Use this query as part of preparing to register translations. The \`digest\` value is required as an input argument when registering a translation. Note that \`first\` or \`last\` argument is still required to run this query.

  #### Query

  ```graphql
  query {
    translatableResourcesByIds(first: 10, resourceIds: ["gid://shopify/Product/20995642"]) {
      edges {
        node {
          resourceId
          translatableContent {
            key
            value
            digest
            locale
          }
        }
      }
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
  "query": "query { translatableResourcesByIds(first: 10, resourceIds: [\"gid://shopify/Product/20995642\"]) { edges { node { resourceId translatableContent { key value digest locale } } } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query {
      translatableResourcesByIds(first: 10, resourceIds: ["gid://shopify/Product/20995642"]) {
        edges {
          node {
            resourceId
            translatableContent {
              key
              value
              digest
              locale
            }
          }
        }
      }
    }`,
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
    query {
      translatableResourcesByIds(first: 10, resourceIds: ["gid://shopify/Product/20995642"]) {
        edges {
          node {
            resourceId
            translatableContent {
              key
              value
              digest
              locale
            }
          }
        }
      }
    }
  QUERY

  response = client.query(query: query)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: `query {
      translatableResourcesByIds(first: 10, resourceIds: ["gid://shopify/Product/20995642"]) {
        edges {
          node {
            resourceId
            translatableContent {
              key
              value
              digest
              locale
            }
          }
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    translatableResourcesByIds(first: 10, resourceIds: ["gid://shopify/Product/20995642"]) {
      edges {
        node {
          resourceId
          translatableContent {
            key
            value
            digest
            locale
          }
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "translatableResourcesByIds": {
      "edges": [
        {
          "node": {
            "resourceId": "gid://shopify/Product/20995642",
            "translatableContent": [
              {
                "key": "title",
                "value": "Element",
                "digest": "4e5b548d6d61f0006840aca106f7464a4b59e5a854317d5b57861b8423901bf6",
                "locale": "en"
              },
              {
                "key": "body_html",
                "value": "<p>bad board</p>",
                "digest": "60cd8aaeeec8e14d9da0dd1ed4cff31c0bb8f9c64255adad9dc1d2140c472f3b",
                "locale": "en"
              },
              {
                "key": "handle",
                "value": "element",
                "digest": "445929267209c034d1e324834c17e0c8305df3dcb21d1710a639ac6ca08c648b",
                "locale": "en"
              },
              {
                "key": "product_type",
                "value": "Snowboards",
                "digest": "3c752b33c3546064f02d47978a3883019e5bef320ddbc48875318b8d76c6154b",
                "locale": "en"
              }
            ]
          }
        }
      ]
    }
  }
  ```
