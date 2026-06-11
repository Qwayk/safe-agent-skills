---
title: articleTags - GraphQL Admin
description: List of all article tags.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/articleTags'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/articleTags.md'
---

# article​Tags

query

Requires `read_content` access scope or `read_online_store_pages` access scope.

List of all article tags.

## Arguments

* limit

  [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  required

  The maximum number of tags to return.

* sort

  [Article​Tag​Sort](https://shopify.dev/docs/api/admin-graphql/latest/enums/ArticleTagSort)

  Default:ALPHABETICAL

  Type of sort order.

***

## Possible returns

* String

  [\[String!\]!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  Represents textual data as UTF-8 character sequences. This type is most often used by GraphQL to represent free-form human-readable text.

***

## Examples

* ### Retrieves a list of all article tags

  #### Query

  ```graphql
  query ArticleTagsList {
    articleTags(limit: 10, sort: ALPHABETICAL)
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query ArticleTagsList { articleTags(limit: 10, sort: ALPHABETICAL) }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query ArticleTagsList {
      articleTags(limit: 10, sort: ALPHABETICAL)
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
    query ArticleTagsList {
      articleTags(limit: 10, sort: ALPHABETICAL)
    }
  QUERY

  response = client.query(query: query)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: `query ArticleTagsList {
      articleTags(limit: 10, sort: ALPHABETICAL)
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query ArticleTagsList {
    articleTags(limit: 10, sort: ALPHABETICAL)
  }'
  ```

  #### Response

  ```json
  {
    "articleTags": [
      "alpha",
      "important",
      "not_alpha"
    ]
  }
  ```
