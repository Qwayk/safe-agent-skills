---
title: productVariantsCount - GraphQL Admin
description: Count of product variants. Limited to a maximum of 10000 by default.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/productVariantsCount
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/productVariantsCount.md
---

# product​Variants​Count

query

Requires `read_products` access scope.

Count of product variants. Limited to a maximum of 10000 by default.

## Arguments

* limit

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  Default:10000

  The upper bound on count value before returning a result. Use `null` to have no limit.

* query

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  No supported search fields.

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

* ### Receive a count of all Product Variants

  #### Query

  ```graphql
  query ProductVariantsCount {
    productVariantsCount {
      count
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
  "query": "query ProductVariantsCount { productVariantsCount { count } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query ProductVariantsCount {
      productVariantsCount {
        count
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
    query ProductVariantsCount {
      productVariantsCount {
        count
      }
    }
  QUERY

  response = client.query(query: query)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: `query ProductVariantsCount {
      productVariantsCount {
        count
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query ProductVariantsCount {
    productVariantsCount {
      count
    }
  }'
  ```

  #### Response

  ```json
  {
    "productVariantsCount": {
      "count": 12
    }
  }
  ```
