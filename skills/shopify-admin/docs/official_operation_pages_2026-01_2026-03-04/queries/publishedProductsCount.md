---
title: publishedProductsCount - GraphQL Admin
description: >-
  Returns a count of published products by publication ID. Limited to a maximum
  of 10000 by default.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/publishedProductsCount
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/publishedProductsCount.md
---

# published​Products​Count

query

Requires `read_publications` access scope.

Returns a count of published products by publication ID. Limited to a maximum of 10000 by default.

## Arguments

* limit

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  Default:10000

  The maximum number of products to count.

* publication​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the publication that the products are published to.

***

## Possible returns

* Count

  [Count](https://shopify.dev/docs/api/admin-graphql/latest/objects/Count)

  A numeric count with precision information indicating whether the count is exact or an estimate.

  * count

    [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    non-null

    The count of elements.

  * precision

    [Count​Precision!](https://shopify.dev/docs/api/admin-graphql/latest/enums/CountPrecision)

    non-null

    The count's precision, or the exactness of the value.

***

## Examples

* ### Retrieve a count of products that are published to your app

  #### Query

  ```graphql
  query PublishedProductCount($publicationId: ID!) {
    publishedProductsCount(publicationId: $publicationId) {
      count
      precision
    }
  }
  ```

  #### Variables

  ```json
  {
    "publicationId": "gid://shopify/Publication/244171671"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query PublishedProductCount($publicationId: ID!) { publishedProductsCount(publicationId: $publicationId) { count precision } }",
   "variables": {
      "publicationId": "gid://shopify/Publication/244171671"
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
    query PublishedProductCount($publicationId: ID!) {
      publishedProductsCount(publicationId: $publicationId) {
        count
        precision
      }
    }`,
    {
      variables: {
          "publicationId": "gid://shopify/Publication/244171671"
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
    query PublishedProductCount($publicationId: ID!) {
      publishedProductsCount(publicationId: $publicationId) {
        count
        precision
      }
    }
  QUERY

  variables = {
    "publicationId": "gid://shopify/Publication/244171671"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query PublishedProductCount($publicationId: ID!) {
        publishedProductsCount(publicationId: $publicationId) {
          count
          precision
        }
      }`,
      "variables": {
          "publicationId": "gid://shopify/Publication/244171671"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query PublishedProductCount($publicationId: ID!) {
    publishedProductsCount(publicationId: $publicationId) {
      count
      precision
    }
  }' \
  --variables \
  '{
    "publicationId": "gid://shopify/Publication/244171671"
  }'
  ```

  #### Response

  ```json
  {
    "publishedProductsCount": {
      "count": 6,
      "precision": "EXACT"
    }
  }
  ```
