---
title: translatableResources - GraphQL Admin
description: >-
  Returns a paginated list of
  [`TranslatableResource`](https://shopify.dev/docs/api/admin-graphql/latest/objects/TranslatableResource)
  objects for a specific resource type. Each resource provides translatable
  content and digest values needed for the
  [`translationsRegister`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/translationsRegister)
  mutation.


  Learn more about [managing translated
  content](https://shopify.dev/docs/apps/build/markets/manage-translated-content).

          Learn more about [managing translated content](https://shopify.dev/docs/apps/build/markets/manage-translated-content).
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/translatableResources
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/translatableResources.md
---

# translatable​Resources

query

Requires `read_translations` access scope.

Returns a paginated list of [`TranslatableResource`](https://shopify.dev/docs/api/admin-graphql/latest/objects/TranslatableResource) objects for a specific resource type. Each resource provides translatable content and digest values needed for the [`translationsRegister`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/translationsRegister) mutation.

Learn more about [managing translated content](https://shopify.dev/docs/apps/build/markets/manage-translated-content).

Learn more about \[managing translated content]\(https://shopify.dev/docs/apps/build/markets/manage-translated-content).

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

* resource​Type

  [Translatable​Resource​Type!](https://shopify.dev/docs/api/admin-graphql/latest/enums/TranslatableResourceType)

  required

  Return only resources of a type.

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

* ### Retrieve translatable content for the first 5 products

  #### Description

  Use this query as part of preparing to register translations. The \`digest\` value is required as an input argument when registering a translation.

  #### Query

  ```graphql
  query {
    translatableResources(first: 5, resourceType: PRODUCT) {
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
  "query": "query { translatableResources(first: 5, resourceType: PRODUCT) { edges { node { resourceId translatableContent { key value digest locale } } } } }"
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
      translatableResources(first: 5, resourceType: PRODUCT) {
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
      translatableResources(first: 5, resourceType: PRODUCT) {
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
      translatableResources(first: 5, resourceType: PRODUCT) {
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
    translatableResources(first: 5, resourceType: PRODUCT) {
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
    "translatableResources": {
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
        },
        {
          "node": {
            "resourceId": "gid://shopify/Product/108828309",
            "translatableContent": [
              {
                "key": "title",
                "value": "Draft",
                "digest": "ebf12ef47cf575b3ba9a3cc019c5310146fdac88f6d1be6618d6e91158c2f174",
                "locale": "en"
              },
              {
                "key": "body_html",
                "value": "<p>good board</p>",
                "digest": "6e634d476ca1dde2a0992fd6f57fc48b5979c8a4ee19117044a054f9f601ae56",
                "locale": "en"
              },
              {
                "key": "handle",
                "value": "draft",
                "digest": "7743ce348d9284d677a185f33295b92266cc435a5b5f775029b300066d26693a",
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
        },
        {
          "node": {
            "resourceId": "gid://shopify/Product/121709582",
            "translatableContent": [
              {
                "key": "title",
                "value": "Boots",
                "digest": "929433e4be1dbd23ffc6b076da2e6f3854ccc5fe606a1e59419110b71fe0a833",
                "locale": "en"
              },
              {
                "key": "body_html",
                "value": "<p>some boots</p>",
                "digest": "8e6907bdb64ea435ccc2874160eaa35db63c95bb5804d93ea460c3a72a68c00c",
                "locale": "en"
              },
              {
                "key": "handle",
                "value": "boots",
                "digest": "40cafc18e93464f86d5d304e726df74311237955bcf7d99909bcef3f0bcb90bb",
                "locale": "en"
              },
              {
                "key": "product_type",
                "value": "Boots",
                "digest": "929433e4be1dbd23ffc6b076da2e6f3854ccc5fe606a1e59419110b71fe0a833",
                "locale": "en"
              }
            ]
          }
        },
        {
          "node": {
            "resourceId": "gid://shopify/Product/440089423",
            "translatableContent": [
              {
                "key": "title",
                "value": "IPod Nano - 8GB",
                "digest": "4ce3c71c164cd0ddc7c95e7d554d9b028e6a6ed4abff8a71ad714c6f2f1a7e4a",
                "locale": "en"
              },
              {
                "key": "body_html",
                "value": "<p>It's the small iPod with one very big idea: Video. Now the world's most popular music player, available in 4GB and 8GB models, lets you enjoy TV shows, movies, video podcasts, and more. The larger, brighter display means amazing picture quality. In six eye-catching colors, iPod nano is stunning all around. And with models starting at just $149, little speaks volumes.</p>",
                "digest": "d3378109cc15e6d88148c52661e687203c692141fe837dbe983fd02e9b095803",
                "locale": "en"
              },
              {
                "key": "handle",
                "value": "ipod-nano",
                "digest": "226259c06fdbf95cd3b681de6db73d0346c7dae4d381f0472c0e405b73cf57e0",
                "locale": "en"
              },
              {
                "key": "product_type",
                "value": "Cult Products",
                "digest": "be736be3f50f1755fdc2f5bc96b10251d56cd1888a51889321cb96d605078c42",
                "locale": "en"
              }
            ]
          }
        },
        {
          "node": {
            "resourceId": "gid://shopify/Product/558169081",
            "translatableContent": [
              {
                "key": "title",
                "value": "Unpublished Boots",
                "digest": "1654ceb776b32b1bf3298e88ce86829478d3be20669887faebc98daf88ebabc0",
                "locale": "en"
              },
              {
                "key": "body_html",
                "value": "<p>some boots</p>",
                "digest": "8e6907bdb64ea435ccc2874160eaa35db63c95bb5804d93ea460c3a72a68c00c",
                "locale": "en"
              },
              {
                "key": "handle",
                "value": "unpublished_boots",
                "digest": "8fa116cf72ed66775134127295e199c727b3756c676b13699b2060db2f19d78c",
                "locale": "en"
              },
              {
                "key": "product_type",
                "value": "Boots",
                "digest": "929433e4be1dbd23ffc6b076da2e6f3854ccc5fe606a1e59419110b71fe0a833",
                "locale": "en"
              }
            ]
          }
        }
      ]
    }
  }
  ```
