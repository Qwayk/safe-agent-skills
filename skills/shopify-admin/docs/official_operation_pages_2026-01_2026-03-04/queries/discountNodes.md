---
title: discountNodes - GraphQL Admin
description: Returns a list of discounts.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/discountNodes'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/discountNodes.md'
---

# discount​Nodes

query

Requires Apps must have `read_discounts` access scope.

Returns a list of discounts.

## DiscountNodeConnection arguments

[DiscountNodeConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/DiscountNodeConnection)

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

    * code

      string

    * combines\_with

      string

    * created\_at

      time

    * discount\_class

      string

    * discount\_type

      string

    * ends\_at

      time

    * id

      id

    * method

      string

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

      Filter by the discount code. Not supported for bulk discounts.

    - Example:

      * `code:WELCOME10`

      Filter by the [Shopify Functions discount classes](https://shopify.dev/docs/apps/build/discounts#discount-classes) that the [discount type](https://shopify.dev/docs/api/admin-graphql/latest/queries/discountnodes#argument-query-filter-discount_type) can combine with. Supports multiple values separated by commas (e.g., combines\_with:product\_discounts,order\_discounts).

    - Valid values:

      * `order_discounts`
      * `product_discounts`
      * `shipping_discounts`

      Example:

      * `combines_with:product_discounts`
      * `combines_with:product_discounts,order_discounts`

      Filter by the date and time, in the shop's timezone, when the discount was created.

    - Example:

      * `created_at:>'2020-10-21T23:39:20Z'`
      * `created_at:<now`
      * `created_at:<='2024'`

      Filter by the [discount class](https://shopify.dev/docs/apps/build/discounts#discount-classes). Supports multiple classes separated by commas (e.g., discount\_class:product,order).

    - Valid values:

      * `order`
      * `product`
      * `shipping`

      Example:

      * `discount_class:product`
      * `discount_class:product,order`

      Filter by the [discount type](https://help.shopify.com/manual/discounts/discount-types). Supports multiple types separated by commas (e.g., discount\_type:percentage,fixed\_amount).

    - Valid values:

      * `app`
      * `bogo`
      * `fixed_amount`
      * `free_shipping`
      * `percentage`

      Example:

      * `discount_type:fixed_amount`
      * `discount_type:percentage,fixed_amount`

      Filter by the date and time, in the shop's timezone, when the discount ends.

    - Example:

      * `ends_at:>'2020-10-21T23:39:20Z'`
      * `ends_at:<now`
      * `ends_at:<='2024'`

      Filter by `id` range.

    - Example:

      * `id:1234`
      * `id:>=1234`
      * `id:<=1234`

      Filter by the [discount method](https://shopify.dev/docs/apps/build/discounts#discount-methods). Supports multiple methods separated by commas (e.g., method:code,automatic).

    - Valid values:

      * `automatic`
      * `code`

      Example:

      * `method:code`
      * `method:code,automatic`

      Filter by the date and time, in the shop's timezone, when the discount becomes active and is available for customer use.

    - Example:

      * `starts_at:>'2020-10-21T23:39:20Z'`
      * `starts_at:<now`
      * `starts_at:<='2024'`

      Filter by the status of the discount. Supports multiple statuses separated by commas (e.g., status:active,scheduled).

    - Valid values:

      * `active`
      * `expired`
      * `scheduled`

      Example:

      * `status:scheduled`
      * `status:active,scheduled`

      Filter by the number of times the discount has been used. For example, if a "Buy 3, Get 1 Free" t-shirt discount is automatically applied in 200 transactions, then the discount has been used 200 times.\
      \
      This value is updated asynchronously. As a result, it might be different than the actual usage count.

    - Example:

      * `times_used:0`
      * `times_used:>150`
      * `times_used:>=200`

      Filter by the discount name that displays to merchants in the Shopify admin and to customers.

    - Example:

      * `title:Black Friday Sale`

      Filter by the [discount type](https://help.shopify.com/manual/discounts/discount-types). Supports multiple types separated by commas (e.g., type:percentage,fixed\_amount).

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
      * `type:percentage,fixed_amount`

      Filter by the date and time, in the shop's timezone, when the discount was last updated.

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

  [Discount​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/DiscountSortKeys)

  Default:ID

  Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

***

## Possible returns

* edges

  [\[Discount​Node​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountNodeEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Discount​Node!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountNode)

  non-null

  A list of nodes that are contained in DiscountNodeEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### Retrieve a list of combinable discounts

  #### Description

  Retrieve a list of discounts that can be combined with other discounts. This query returns discounts that can be \[combined]\(https://help.shopify.com/manual/discounts/combining-discounts/discount-combinations) with product discounts.

  #### Query

  ```graphql
  query {
    discountNodes(query: "combines_with:product_discounts", first: 10) {
      edges {
        node {
          id
          discount {
            ... on DiscountCodeBasic {
              title
              status
              combinesWith {
                productDiscounts
              }
            }
            ... on DiscountCodeFreeShipping {
              title
              status
              combinesWith {
                productDiscounts
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
  "query": "query { discountNodes(query: \"combines_with:product_discounts\", first: 10) { edges { node { id discount { ... on DiscountCodeBasic { title status combinesWith { productDiscounts } } ... on DiscountCodeFreeShipping { title status combinesWith { productDiscounts } } } } } } }"
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
      discountNodes(query: "combines_with:product_discounts", first: 10) {
        edges {
          node {
            id
            discount {
              ... on DiscountCodeBasic {
                title
                status
                combinesWith {
                  productDiscounts
                }
              }
              ... on DiscountCodeFreeShipping {
                title
                status
                combinesWith {
                  productDiscounts
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
      discountNodes(query: "combines_with:product_discounts", first: 10) {
        edges {
          node {
            id
            discount {
              ... on DiscountCodeBasic {
                title
                status
                combinesWith {
                  productDiscounts
                }
              }
              ... on DiscountCodeFreeShipping {
                title
                status
                combinesWith {
                  productDiscounts
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
      discountNodes(query: "combines_with:product_discounts", first: 10) {
        edges {
          node {
            id
            discount {
              ... on DiscountCodeBasic {
                title
                status
                combinesWith {
                  productDiscounts
                }
              }
              ... on DiscountCodeFreeShipping {
                title
                status
                combinesWith {
                  productDiscounts
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
    discountNodes(query: "combines_with:product_discounts", first: 10) {
      edges {
        node {
          id
          discount {
            ... on DiscountCodeBasic {
              title
              status
              combinesWith {
                productDiscounts
              }
            }
            ... on DiscountCodeFreeShipping {
              title
              status
              combinesWith {
                productDiscounts
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
    "discountNodes": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/DiscountCodeNode/700447567",
            "discount": {
              "title": "COMBINABLEFREESHIPPING",
              "status": "ACTIVE",
              "combinesWith": {
                "productDiscounts": true
              }
            }
          }
        },
        {
          "node": {
            "id": "gid://shopify/DiscountCodeNode/988849754",
            "discount": {
              "title": "combinable_cart_amount",
              "status": "EXPIRED",
              "combinesWith": {
                "productDiscounts": true
              }
            }
          }
        }
      ]
    }
  }
  ```

* ### Retrieve a list of discounts

  #### Description

  Retrieve the first five discounts for a shop. You can retrieve \[discount types]\(https://help.shopify.com/manual/discounts/discount-types) that offer buy X get Y (BXGY), amount off, and free shipping. You can also retrieve discounts that are managed by an app that's using \[Shopify Functions]\(https://shopify.dev/docs/apps/build/functions).

  #### Query

  ```graphql
  query {
    discountNodes(first: 5) {
      edges {
        node {
          id
          __typename
          discount {
            ... on DiscountCodeBasic {
              title
              summary
              status
            }
            ... on DiscountAutomaticBasic {
              title
              summary
              status
            }
            ... on DiscountCodeBxgy {
              title
              summary
              status
            }
            ... on DiscountAutomaticBxgy {
              title
              summary
              status
            }
            ... on DiscountCodeFreeShipping {
              title
              summary
              status
            }
            ... on DiscountAutomaticApp {
              title
              status
              appDiscountType {
                functionId
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
  "query": "query { discountNodes(first: 5) { edges { node { id __typename discount { ... on DiscountCodeBasic { title summary status } ... on DiscountAutomaticBasic { title summary status } ... on DiscountCodeBxgy { title summary status } ... on DiscountAutomaticBxgy { title summary status } ... on DiscountCodeFreeShipping { title summary status } ... on DiscountAutomaticApp { title status appDiscountType { functionId } } } } } } }"
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
      discountNodes(first: 5) {
        edges {
          node {
            id
            __typename
            discount {
              ... on DiscountCodeBasic {
                title
                summary
                status
              }
              ... on DiscountAutomaticBasic {
                title
                summary
                status
              }
              ... on DiscountCodeBxgy {
                title
                summary
                status
              }
              ... on DiscountAutomaticBxgy {
                title
                summary
                status
              }
              ... on DiscountCodeFreeShipping {
                title
                summary
                status
              }
              ... on DiscountAutomaticApp {
                title
                status
                appDiscountType {
                  functionId
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
      discountNodes(first: 5) {
        edges {
          node {
            id
            __typename
            discount {
              ... on DiscountCodeBasic {
                title
                summary
                status
              }
              ... on DiscountAutomaticBasic {
                title
                summary
                status
              }
              ... on DiscountCodeBxgy {
                title
                summary
                status
              }
              ... on DiscountAutomaticBxgy {
                title
                summary
                status
              }
              ... on DiscountCodeFreeShipping {
                title
                summary
                status
              }
              ... on DiscountAutomaticApp {
                title
                status
                appDiscountType {
                  functionId
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
      discountNodes(first: 5) {
        edges {
          node {
            id
            __typename
            discount {
              ... on DiscountCodeBasic {
                title
                summary
                status
              }
              ... on DiscountAutomaticBasic {
                title
                summary
                status
              }
              ... on DiscountCodeBxgy {
                title
                summary
                status
              }
              ... on DiscountAutomaticBxgy {
                title
                summary
                status
              }
              ... on DiscountCodeFreeShipping {
                title
                summary
                status
              }
              ... on DiscountAutomaticApp {
                title
                status
                appDiscountType {
                  functionId
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
    discountNodes(first: 5) {
      edges {
        node {
          id
          __typename
          discount {
            ... on DiscountCodeBasic {
              title
              summary
              status
            }
            ... on DiscountAutomaticBasic {
              title
              summary
              status
            }
            ... on DiscountCodeBxgy {
              title
              summary
              status
            }
            ... on DiscountAutomaticBxgy {
              title
              summary
              status
            }
            ... on DiscountCodeFreeShipping {
              title
              summary
              status
            }
            ... on DiscountAutomaticApp {
              title
              status
              appDiscountType {
                functionId
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
    "discountNodes": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/DiscountCodeNode/2429471",
            "__typename": "DiscountNode",
            "discount": {
              "title": "cart_amount",
              "summary": "$10.00 off one-time purchase products",
              "status": "EXPIRED"
            }
          }
        },
        {
          "node": {
            "id": "gid://shopify/DiscountAutomaticNode/52422887",
            "__typename": "DiscountNode",
            "discount": {
              "title": "Percentage off (by Automatic App Discount)",
              "status": "EXPIRED",
              "appDiscountType": {
                "functionId": "9476d0af-de36-4159-a6cd-b68165c2deac"
              }
            }
          }
        },
        {
          "node": {
            "id": "gid://shopify/DiscountAutomaticNode/198286294",
            "__typename": "DiscountNode",
            "discount": {
              "title": "My automatic bogo",
              "summary": "Buy 1 item, get 1 item free",
              "status": "EXPIRED"
            }
          }
        },
        {
          "node": {
            "id": "gid://shopify/DiscountAutomaticNode/299501151",
            "__typename": "DiscountNode",
            "discount": {
              "title": "My automatic discount",
              "summary": "$100.00 off entire order • Minimum quantity of 1",
              "status": "SCHEDULED"
            }
          }
        },
        {
          "node": {
            "id": "gid://shopify/DiscountCodeNode/299564956",
            "__typename": "DiscountNode",
            "discount": {
              "title": "product_bogo",
              "summary": "Buy 1 item, get 1 item free",
              "status": "EXPIRED"
            }
          }
        }
      ]
    }
  }
  ```
