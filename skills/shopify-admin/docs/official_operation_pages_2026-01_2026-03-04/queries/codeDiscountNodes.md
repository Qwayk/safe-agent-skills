---
title: codeDiscountNodes - GraphQL Admin
description: >-
  Returns a list of [code-based
  discounts](https://help.shopify.com/manual/discounts/discount-types#discount-codes).
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/codeDiscountNodes'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/codeDiscountNodes.md
---

# code​Discount​Nodes

query

Requires Apps must have `read_discounts` access scope.

Deprecated. Use [discountNodes](https://shopify.dev/docs/api/admin-graphql/latest/queries/discountNodes) instead.

Returns a list of [code-based discounts](https://help.shopify.com/manual/discounts/discount-types#discount-codes).

## DiscountCodeNodeConnection arguments

[DiscountCodeNodeConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/DiscountCodeNodeConnection)

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

* query

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  A filter made up of terms, connectives, modifiers, and comparators. You can apply one or more filters to a query. Learn more about [Shopify API search syntax](https://shopify.dev/api/usage/search-syntax).

  * * default

      string

    * combines\_with

      string

    * created\_at

      time

    * discount\_type

      string

    * ends\_at

      time

    * id

      id

    * starts\_at

      time

    * status

      string

    * times\_used

      integer

    * title

      string

    * type

      string

    * updated\_at

      time

    - Filter by a case-insensitive search of multiple fields in a document.

    - Example:

      * `query=Bob Norman`
      * `query=title:green hoodie`

      Filter by the [discount classes](https://help.shopify.com/manual/discounts/combining-discounts/discount-combinations) that you can use in combination with [Shopify discount types](https://help.shopify.com/manual/discounts/discount-types).

    - Valid values:

      * `order_discounts`
      * `product_discounts`
      * `shipping_discounts`

      Example:

      * `combines_with:product_discounts`

      Filter by the date and time when the discount was created.

    - Example:

      * `created_at:>'2020-10-21T23:39:20Z'`
      * `created_at:<now`
      * `created_at:<='2024'`

      Filter by the [discount type](https://help.shopify.com/manual/discounts/discount-types).

    - Valid values:

      * `app`
      * `bogo`
      * `fixed_amount`
      * `free_shipping`
      * `percentage`

      Example:

      * `discount_type:fixed_amount`

      Filter by the date and time when the discount expires and is no longer available for customer use.

    - Example:

      * `ends_at:>'2020-10-21T23:39:20Z'`
      * `ends_at:<now`
      * `ends_at:<='2024'`

      Filter by `id` range.

    - Example:

      * `id:1234`
      * `id:>=1234`
      * `id:<=1234`

      Filter by the date and time, in the shop's timezone, when the discount becomes active and is available for customer use.

    - Example:

      * `starts_at:>'2020-10-21T23:39:20Z'`
      * `starts_at:<now`
      * `starts_at:<='2024'`

      Filter by the status of the discount.

    - Valid values:

      * `active`
      * `expired`
      * `scheduled`

      Example:

      * `status:scheduled`

      Filter by the number of times the discount has been used. For example, if a "Buy 3, Get 1 Free" t-shirt discount is automatically applied in 200 transactions, then the discount has been used 200 times.\
      \
      This value is updated asynchronously. As a result, it might be different than the actual usage count.

    - Example:

      * `times_used:0`
      * `times_used:>150`
      * `times_used:>=200`

      Filter by the discount name that displays to customers.

    - Example:

      * `title:Black Friday Sale`

      Filter by the [discount type](https://help.shopify.com/manual/discounts/discount-types).

    - Valid values:

      * `all`
      * `all_with_app`
      * `app`
      * `bxgy`
      * `fixed_amount`
      * `free_shipping`
      * `percentage`

      Example:

      * `type:percentage`

      Filter by the date and time when the discount was last updated.

      Example:

      * `updated_at:>'2020-10-21T23:39:20Z'`
      * `updated_at:<now`
      * `updated_at:<='2024'`

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

* saved​Search​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of a [saved search](https://shopify.dev/api/admin-graphql/latest/objects/savedsearch#field-id). The search’s query string is used as the query argument.

* sort​Key

  [Code​Discount​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/CodeDiscountSortKeys)

  Default:ID

  Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

***

## Possible returns

* edges

  [\[Discount​Code​Node​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountCodeNodeEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Discount​Code​Node!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountCodeNode)

  non-null

  A list of nodes that are contained in DiscountCodeNodeEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### Retrieve a list of code discounts

  #### Description

  Retrieve the first 3 \[code discounts]\(https://help.shopify.com/manual/discounts/discount-types#discount-codes) that are applied on a cart and at checkout when a customer enters a code.

  #### Query

  ```graphql
  query {
    codeDiscountNodes(first: 3) {
      nodes {
        id
        codeDiscount {
          ... on DiscountCodeBasic {
            title
            summary
          }
          ... on DiscountCodeBxgy {
            title
            codesCount {
              count
            }
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
  "query": "query { codeDiscountNodes(first: 3) { nodes { id codeDiscount { ... on DiscountCodeBasic { title summary } ... on DiscountCodeBxgy { title codesCount { count } } } } } }"
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
      codeDiscountNodes(first: 3) {
        nodes {
          id
          codeDiscount {
            ... on DiscountCodeBasic {
              title
              summary
            }
            ... on DiscountCodeBxgy {
              title
              codesCount {
                count
              }
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
      codeDiscountNodes(first: 3) {
        nodes {
          id
          codeDiscount {
            ... on DiscountCodeBasic {
              title
              summary
            }
            ... on DiscountCodeBxgy {
              title
              codesCount {
                count
              }
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
      codeDiscountNodes(first: 3) {
        nodes {
          id
          codeDiscount {
            ... on DiscountCodeBasic {
              title
              summary
            }
            ... on DiscountCodeBxgy {
              title
              codesCount {
                count
              }
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
    codeDiscountNodes(first: 3) {
      nodes {
        id
        codeDiscount {
          ... on DiscountCodeBasic {
            title
            summary
          }
          ... on DiscountCodeBxgy {
            title
            codesCount {
              count
            }
          }
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "codeDiscountNodes": {
      "nodes": [
        {
          "id": "gid://shopify/DiscountCodeNode/1057371281",
          "codeDiscount": {
            "title": "10% off one-time",
            "summary": "10% off one-time purchase products"
          }
        },
        {
          "id": "gid://shopify/DiscountCodeNode/1057371282",
          "codeDiscount": {
            "title": "60% off one-time",
            "summary": "60% off one-time purchase products"
          }
        },
        {
          "id": "gid://shopify/DiscountCodeNode/1057371283",
          "codeDiscount": {
            "title": "BXGY Raincoats",
            "codesCount": {
              "count": 1
            }
          }
        }
      ]
    }
  }
  ```

* ### Retrieve code discounts by discount type

  #### Description

  This example shows how to retrieve code discounts that offer a fixed amount off products in an order.

  #### Query

  ```graphql
  query {
    codeDiscountNodes(first: 1, query: "value_type:fixed_amount") {
      nodes {
        id
        codeDiscount {
          ... on DiscountCodeBasic {
            title
            codes(first: 1) {
              nodes {
                code
              }
            }
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
  "query": "query { codeDiscountNodes(first: 1, query: \"value_type:fixed_amount\") { nodes { id codeDiscount { ... on DiscountCodeBasic { title codes(first: 1) { nodes { code } } } } } } }"
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
      codeDiscountNodes(first: 1, query: "value_type:fixed_amount") {
        nodes {
          id
          codeDiscount {
            ... on DiscountCodeBasic {
              title
              codes(first: 1) {
                nodes {
                  code
                }
              }
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
      codeDiscountNodes(first: 1, query: "value_type:fixed_amount") {
        nodes {
          id
          codeDiscount {
            ... on DiscountCodeBasic {
              title
              codes(first: 1) {
                nodes {
                  code
                }
              }
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
      codeDiscountNodes(first: 1, query: "value_type:fixed_amount") {
        nodes {
          id
          codeDiscount {
            ... on DiscountCodeBasic {
              title
              codes(first: 1) {
                nodes {
                  code
                }
              }
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
    codeDiscountNodes(first: 1, query: "value_type:fixed_amount") {
      nodes {
        id
        codeDiscount {
          ... on DiscountCodeBasic {
            title
            codes(first: 1) {
              nodes {
                code
              }
            }
          }
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "codeDiscountNodes": {
      "nodes": [
        {
          "id": "gid://shopify/DiscountCodeNode/1057371284",
          "codeDiscount": {
            "title": "Fixed amount off",
            "codes": {
              "nodes": [
                {
                  "code": "FIXEDOFF"
                }
              ]
            }
          }
        }
      ]
    }
  }
  ```
