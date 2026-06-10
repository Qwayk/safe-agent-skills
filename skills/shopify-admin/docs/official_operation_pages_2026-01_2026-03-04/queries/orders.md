---
title: orders - GraphQL Admin
description: >-
  Returns a list of
  [orders](https://shopify.dev/api/admin-graphql/latest/objects/Order) placed in
  the store, including data such as order status, customer, and line item
  details.

  Use the `orders` query to build reports, analyze sales performance, or
  automate fulfillment workflows. The `orders` query supports
  [pagination](https://shopify.dev/docs/api/usage/pagination-graphql),

  [sorting](https://shopify.dev/docs/api/admin-graphql/latest/queries/orders#arguments-sortKey),
  and
  [filtering](https://shopify.dev/docs/api/admin-graphql/latest/queries/orders#arguments-query).
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/orders'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/orders.md'
---

# orders

query

Returns a list of [orders](https://shopify.dev/api/admin-graphql/latest/objects/Order) placed in the store, including data such as order status, customer, and line item details. Use the `orders` query to build reports, analyze sales performance, or automate fulfillment workflows. The `orders` query supports [pagination](https://shopify.dev/docs/api/usage/pagination-graphql), [sorting](https://shopify.dev/docs/api/admin-graphql/latest/queries/orders#arguments-sortKey), and [filtering](https://shopify.dev/docs/api/admin-graphql/latest/queries/orders#arguments-query).

## OrderConnection arguments

[OrderConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/OrderConnection)

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

    * cart\_token

      string

    * channel

      string

    * channel\_id

      id

    * chargeback\_status

      string

    * checkout\_token

      string

    * confirmation\_number

      string

    * created\_at

      time

    * credit\_card\_last4

      string

    * current\_total\_price

      float

    * customer\_id

      id

    * delivery\_method

      string

    * discount\_code

      string

    * email

      string

    * financial\_status

      string

    * fraud\_protection\_level

      string

    * fulfillment\_location\_id

      id

    * fulfillment\_status

      string

    * gateway

      string

    * id

      id

    * location\_id

      id

    * metafields.{namespace}.{key}

      mixed

    * name

      string

    * payment\_id

      string

    * payment\_provider\_id

      id

    * po\_number

      string

    * processed\_at

      time

    * reference\_location\_id

      id

    * return\_status

      string

    * risk\_level

      string

    * sales\_channel

      string

    * sku

      string

    * source\_identifier

      string

    * source\_name

      string

    * status

      string

    * subtotal\_line\_items\_quantity

      string

    * tag

      string

    * tag\_not

      string

    * test

      boolean

    * total\_weight

      string

    * updated\_at

      time

    - Filter by a case-insensitive search of multiple fields in a document.

    - Example:

      * `query=Bob Norman`
      * `query=title:green hoodie`

      Filter by the cart token's unique value to track abandoned cart conversions or troubleshoot checkout issues. The token references the cart that's associated with an order.

    - Example:

      * `cart_token:abc123`

      Filter by the channel information [`handle`](https://shopify.dev/api/admin-graphql/latest/objects/ChannelInformation#field-ChannelInformation.fields.channelDefinition.handle) (`ChannelInformation.channelDefinition.handle`) field.

    - Example:

      * `channel:web`
      * `channel:web,pos`

      Filter by the channel [`id`](https://shopify.dev/api/admin-graphql/latest/objects/Channel#field-Channel.fields.id) field.

    - Example:

      * `channel_id:123`

      Filter by the order's chargeback status. A chargeback occurs when a customer questions the legitimacy of a charge with their financial institution.

    - Valid values:

      * `accepted`
      * `charge_refunded`
      * `lost`
      * `needs_response`
      * `under_review`
      * `won`

      Example:

      * `chargeback_status:accepted`

      Filter by the checkout token's unique value to analyze conversion funnels or resolve payment issues. The checkout token's value references the checkout that's associated with an order.

    - Example:

      * `checkout_token:abc123`

      Filter by the randomly generated alpha-numeric identifier for an order that can be displayed to the customer instead of the sequential order name. This value isn't guaranteed to be unique.

    - Example:

      * `confirmation_number:ABC123`

      Filter by the date and time when the order was created in Shopify's system.

    - Example:

      * `created_at:2020-10-21T23:39:20Z`
      * `created_at:<now`
      * `created_at:<=2024`

      Filter by the last four digits of the payment card that was used to pay for the order. This filter matches only the last four digits of the card for heightened security.

    - Example:

      * `credit_card_last4:1234`

      Filter by the current total price of the order in the shop currency, including any returns/refunds/removals. This filter supports both exact values and ranges.

    - Example:

      * `current_total_price:10`
      * `current_total_price:>=5.00 current_total_price:<=20.99`

      Filter orders by the customer [`id`](https://shopify.dev/api/admin-graphql/latest/objects/Customer#field-Customer.fields.id) field.

    - Example:

      * `customer_id:123`

      Filter by the delivery [`methodType`](https://shopify.dev/api/admin-graphql/2024-07/objects/DeliveryMethod#field-DeliveryMethod.fields.methodType) field.

    - Valid values:

      * `shipping`
      * `pick-up`
      * `retail`
      * `local`
      * `pickup-point`
      * `none`

      Example:

      * `delivery_method:shipping`

      Filter by the case-insensitive discount code that was applied to the order at checkout. Limited to the first discount code used on an order. Maximum characters: 255.

    - Example:

      * `discount_code:ABC123`

      Filter by the email address that's associated with the order to provide customer support or analyze purchasing patterns.

    - Example:

      * `email:example@shopify.com`

      Filter by the order [`displayFinancialStatus`](https://shopify.dev/api/admin-graphql/latest/objects/Order#field-Order.fields.displayFinancialStatus) field.

    - Valid values:

      * `paid`
      * `pending`
      * `authorized`
      * `partially_paid`
      * `partially_refunded`
      * `refunded`
      * `voided`
      * `expired`

      Example:

      * `financial_status:authorized`

      Filter by the level of fraud protection that's applied to the order. Use this filter to manage risk or handle disputes.

    - Valid values:

      * `fully_protected`
      * `partially_protected`
      * `not_protected`
      * `pending`
      * `not_eligible`
      * `not_available`

      Example:

      * `fraud_protection_level:fully_protected`

      Filter by the fulfillment location [`id`](https://shopify.dev/api/admin-graphql/latest/objects/Fulfillment#field-Fulfillment.fields.location.id) (`Fulfillment.location.id`) field.

    - Example:

      * `fulfillment_location_id:123`

      Filter by the [`displayFulfillmentStatus`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order#field-Order.fields.displayFulfillmentStatus) field to prioritize shipments or monitor order processing.

    - Valid values:

      * `unshipped`
      * `shipped`
      * `fulfilled`
      * `partial`
      * `scheduled`
      * `on_hold`
      * `unfulfilled`
      * `request_declined`

      Example:

      * `fulfillment_status:fulfilled`

      Filter by the [`paymentGatewayNames`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order#field-Order.fields.paymentGatewayNames) field. Use this filter to find orders that were processed through specific payment providers like Shopify Payments, PayPal, or other custom payment gateways.

    - Example:

      * `gateway:shopify_payments`

      Filter by `id` range.

    - Example:

      * `id:1234`
      * `id:>=1234`
      * `id:<=1234`

      Filter by the location [`id`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Location#field-Location.fields.id) that's associated with the order to view and manage orders for specific locations. For POS orders, locations must be defined in the Shopify admin under **Settings** > **Locations**. If no ID is provided, then the primary location of the shop is returned.

    - Example:

      * `location_id:123`

      Filters resources by metafield value. Format: `metafields.{namespace}.{key}:{value}`. Learn more about [querying by metafield value](https://shopify.dev/apps/build/custom-data/metafields/query-by-metafield-value).

    - Example:

      * `metafields.custom.on_sale:true`
      * `metafields.product.material:"gid://shopify/Metaobject/43458085"`

      Filter by the order [`name`](https://shopify.dev/api/admin-graphql/latest/objects/Order#field-name) field.

    - Example:

      * `name:1001-A`

      Filter by the payment ID that's associated with the order to reconcile financial records or troubleshoot payment issues.

    - Example:

      * `payment_id:abc123`

      Filter by the ID of the payment provider that's associated with the order to manage payment methods or troubleshoot transactions.

    - Example:

      * `payment_provider_id:123`

      Filter by the order [`poNumber`](https://shopify.dev/api/admin-graphql/latest/objects/order#field-Order.fields.poNumber) field.

    - Example:

      * `po_number:P01001`

      Filter by the order [`processedAt`](https://shopify.dev/api/admin-graphql/latest/objects/order#field-Order.fields.processedAt) field.

    - Example:

      * `processed_at:2021-01-01T00:00:00Z`

      Filter by the ID of a location that's associated with the order, such as locations from fulfillments, refunds, or the shop's primary location.

    - Example:

      * `reference_location_id:123`

      Filter by the order's [`returnStatus`](https://shopify.dev/api/admin-graphql/latest/objects/Order#field-Order.fields.returnStatus) to monitor returns processing and track which orders have active returns.

    - Valid values:

      * `return_requested`
      * `in_progress`
      * `inspection_complete`
      * `returned`
      * `return_failed`
      * `no_return`

      Example:

      * `return_status:in_progress`

      Filter by the order risk assessment [`riskLevel`](https://shopify.dev/api/admin-graphql/latest/objects/OrderRiskAssessment#field-OrderRiskAssessment.fields.riskLevel) field.

    - Valid values:

      * `high`
      * `medium`
      * `low`
      * `none`
      * `pending`

      Example:

      * `risk_level:high`

      Filter by the [sales channel](https://shopify.dev/docs/apps/build/sales-channels) where the order was made to analyze performance or manage fulfillment processes.

    - Example:

      * `sales_channel: some_sales_channel`

      Filter by the product variant [`sku`](https://shopify.dev/api/admin-graphql/latest/objects/ProductVariant#field-ProductVariant.fields.sku) field. [Learn more about SKUs](https://help.shopify.com/manual/products/details/sku).

    - Example:

      * `sku:ABC123`

      Filter by the ID of the order placed on the originating platform, such as a unique POS or third-party identifier. This value doesn't correspond to the Shopify ID that's generated from a completed draft order.

    - Example:

      * `source_identifier:1234-12-1000`

      Filter by the platform where the order was placed to distinguish between web orders, POS sales, draft orders, or third-party channels. Use this filter to analyze sales performance across different ordering methods.

    - Example:

      * `source_name:web`
      * `source_name:shopify_draft_order`

      Filter by the order's status to manage workflows or analyze the order lifecycle.

    - Valid values:

      * `open`
      * `closed`
      * `cancelled`
      * `not_closed`

      Example:

      * `status:open`

      Filter by the total number of items across all line items in an order. This filter supports both exact values and ranges, and is useful for identifying bulk orders or analyzing purchase volume patterns.

    - Example:

      * `subtotal_line_items_quantity:10`
      * `subtotal_line_items_quantity:5..20`

      Filter objects by the `tag` field.

    - Example:

      * `tag:my_tag`

      Filter by objects that don’t have the specified tag.

    - Example:

      * `tag_not:my_tag`

      Filter by test orders. Test orders are made using the [Shopify Bogus Gateway](https://help.shopify.com/manual/checkout-settings/test-orders/payments-test-mode#bogus-gateway) or a payment provider with test mode enabled.

    - Example:

      * `test:true`

      Filter by the order weight. This filter supports both exact values and ranges, and is to be used to filter orders by the total weight of all items (excluding packaging). It takes a unit of measurement as a suffix. It accepts the following units: g, kg, lb, oz.

    - Example:

      * `total_weight:10.5kg`
      * `total_weight:>=5g total_weight:<=20g`
      * `total_weight:.5 lb`

      Filter by the date and time when the order was last updated in Shopify's system.

      Example:

      * `updated_at:2020-10-21T23:39:20Z`
      * `updated_at:<now`
      * `updated_at:<=2024`

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

* saved​Search​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of a [saved search](https://shopify.dev/api/admin-graphql/latest/objects/savedsearch#field-id). The search’s query string is used as the query argument.

* sort​Key

  [Order​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/OrderSortKeys)

  Default:PROCESSED\_AT

  Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

***

## Possible returns

* edges

  [\[Order​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/OrderEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Order!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order)

  non-null

  A list of nodes that are contained in OrderEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### Retrieve a list of orders

  #### Description

  This query retrieves the first 10 \[\`orders\`]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/Order) using \[pagination]\(https://shopify.dev/docs/api/usage/pagination-graphql) and returns order IDs.

  #### Query

  ```graphql
  query {
    orders(first: 10) {
      edges {
        cursor
        node {
          id
        }
      }
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
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
  "query": "query { orders(first: 10) { edges { cursor node { id } } pageInfo { hasNextPage hasPreviousPage startCursor endCursor } } }"
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
      orders(first: 10) {
        edges {
          cursor
          node {
            id
          }
        }
        pageInfo {
          hasNextPage
          hasPreviousPage
          startCursor
          endCursor
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
      orders(first: 10) {
        edges {
          cursor
          node {
            id
          }
        }
        pageInfo {
          hasNextPage
          hasPreviousPage
          startCursor
          endCursor
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
      orders(first: 10) {
        edges {
          cursor
          node {
            id
          }
        }
        pageInfo {
          hasNextPage
          hasPreviousPage
          startCursor
          endCursor
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
    orders(first: 10) {
      edges {
        cursor
        node {
          id
        }
      }
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "orders": {
      "edges": [
        {
          "cursor": "eyJsYXN0X2lkIjoxMjYyMTY1MTYsImxhc3RfdmFsdWUiOiIyMDA1LTA3LTMxIDE1OjU3OjExLjAwMDAwMCJ9",
          "node": {
            "id": "gid://shopify/Order/126216516"
          }
        },
        {
          "cursor": "eyJsYXN0X2lkIjoxNDg5Nzc3NzYsImxhc3RfdmFsdWUiOiIyMDA1LTA3LTMxIDE1OjU3OjExLjAwMDAwMCJ9",
          "node": {
            "id": "gid://shopify/Order/148977776"
          }
        },
        {
          "cursor": "eyJsYXN0X2lkIjoyMzUyNDAzMDIsImxhc3RfdmFsdWUiOiIyMDA1LTA3LTMxIDE1OjU3OjExLjAwMDAwMCJ9",
          "node": {
            "id": "gid://shopify/Order/235240302"
          }
        },
        {
          "cursor": "eyJsYXN0X2lkIjozNTc5NDQ4NTQsImxhc3RfdmFsdWUiOiIyMDA1LTA3LTMxIDE1OjU3OjExLjAwMDAwMCJ9",
          "node": {
            "id": "gid://shopify/Order/357944854"
          }
        },
        {
          "cursor": "eyJsYXN0X2lkIjo0MDQ0ODE1NzUsImxhc3RfdmFsdWUiOiIyMDA1LTA3LTMxIDE1OjU3OjExLjAwMDAwMCJ9",
          "node": {
            "id": "gid://shopify/Order/404481575"
          }
        },
        {
          "cursor": "eyJsYXN0X2lkIjo0MDkyMTQzNjMsImxhc3RfdmFsdWUiOiIyMDA1LTA3LTMxIDE1OjU3OjExLjAwMDAwMCJ9",
          "node": {
            "id": "gid://shopify/Order/409214363"
          }
        },
        {
          "cursor": "eyJsYXN0X2lkIjo0NzE4NjExMjksImxhc3RfdmFsdWUiOiIyMDA1LTA3LTMxIDE1OjU3OjExLjAwMDAwMCJ9",
          "node": {
            "id": "gid://shopify/Order/471861129"
          }
        },
        {
          "cursor": "eyJsYXN0X2lkIjo0ODA3OTYxODksImxhc3RfdmFsdWUiOiIyMDA1LTA3LTMxIDE1OjU3OjExLjAwMDAwMCJ9",
          "node": {
            "id": "gid://shopify/Order/480796189"
          }
        },
        {
          "cursor": "eyJsYXN0X2lkIjo1MjcyMjkyODksImxhc3RfdmFsdWUiOiIyMDA1LTA3LTMxIDE1OjU3OjExLjAwMDAwMCJ9",
          "node": {
            "id": "gid://shopify/Order/527229289"
          }
        },
        {
          "cursor": "eyJsYXN0X2lkIjo1NTY1Mjc2MzgsImxhc3RfdmFsdWUiOiIyMDA1LTA3LTMxIDE1OjU3OjExLjAwMDAwMCJ9",
          "node": {
            "id": "gid://shopify/Order/556527638"
          }
        }
      ],
      "pageInfo": {
        "hasNextPage": true,
        "hasPreviousPage": false,
        "startCursor": "eyJsYXN0X2lkIjoxMjYyMTY1MTYsImxhc3RfdmFsdWUiOiIyMDA1LTA3LTMxIDE1OjU3OjExLjAwMDAwMCJ9",
        "endCursor": "eyJsYXN0X2lkIjo1NTY1Mjc2MzgsImxhc3RfdmFsdWUiOiIyMDA1LTA3LTMxIDE1OjU3OjExLjAwMDAwMCJ9"
      }
    }
  }
  ```

* ### Retrieve a list of orders using their IDs and GraphQL aliases

  #### Description

  This query demonstrates GraphQL aliases such as \`order1\` and \`order2\` to fetch multiple orders in a single query. Without aliases, requesting the same field twice would cause an error due to duplicate response keys.

  #### Query

  ```graphql
  query {
    order1: order(id: "gid://shopify/Order/148977776") {
      name
    }
    order2: order(id: "gid://shopify/Order/1073459961") {
      name
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
  "query": "query { order1: order(id: \"gid://shopify/Order/148977776\") { name } order2: order(id: \"gid://shopify/Order/1073459961\") { name } }"
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
      order1: order(id: "gid://shopify/Order/148977776") {
        name
      }
      order2: order(id: "gid://shopify/Order/1073459961") {
        name
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
      order1: order(id: "gid://shopify/Order/148977776") {
        name
      }
      order2: order(id: "gid://shopify/Order/1073459961") {
        name
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
      order1: order(id: "gid://shopify/Order/148977776") {
        name
      }
      order2: order(id: "gid://shopify/Order/1073459961") {
        name
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    order1: order(id: "gid://shopify/Order/148977776") {
      name
    }
    order2: order(id: "gid://shopify/Order/1073459961") {
      name
    }
  }'
  ```

  #### Response

  ```json
  {
    "order1": {
      "name": "#1001"
    },
    "order2": {
      "name": "#1018"
    }
  }
  ```

* ### Retrieve specific order details

  #### Description

  This query retrieves the first five \[\`orders\`]\(https://shopify.dev/api/admin-graphql/latest/objects/Order), including status information, financial data, and a list of \[line items]\(https://shopify.dev/api/admin-graphql/latest/objects/LineItem). This query is useful for order processing, fulfillment, and financial reporting.

  #### Query

  ```graphql
  query {
    orders(first: 5) {
      edges {
        node {
          id
          name
          createdAt
          displayFinancialStatus
          displayFulfillmentStatus
          totalPriceSet {
            shopMoney {
              amount
              currencyCode
            }
          }
          subtotalPriceSet {
            shopMoney {
              amount
              currencyCode
            }
          }
          email
          shippingAddress {
            address1
            city
            provinceCode
            zip
          }
          lineItems(first: 5) {
            edges {
              node {
                name
                quantity
                sku
                variant {
                  id
                  title
                }
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
  "query": "query { orders(first: 5) { edges { node { id name createdAt displayFinancialStatus displayFulfillmentStatus totalPriceSet { shopMoney { amount currencyCode } } subtotalPriceSet { shopMoney { amount currencyCode } } email shippingAddress { address1 city provinceCode zip } lineItems(first: 5) { edges { node { name quantity sku variant { id title } } } } } } } }"
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
      orders(first: 5) {
        edges {
          node {
            id
            name
            createdAt
            displayFinancialStatus
            displayFulfillmentStatus
            totalPriceSet {
              shopMoney {
                amount
                currencyCode
              }
            }
            subtotalPriceSet {
              shopMoney {
                amount
                currencyCode
              }
            }
            email
            shippingAddress {
              address1
              city
              provinceCode
              zip
            }
            lineItems(first: 5) {
              edges {
                node {
                  name
                  quantity
                  sku
                  variant {
                    id
                    title
                  }
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
      orders(first: 5) {
        edges {
          node {
            id
            name
            createdAt
            displayFinancialStatus
            displayFulfillmentStatus
            totalPriceSet {
              shopMoney {
                amount
                currencyCode
              }
            }
            subtotalPriceSet {
              shopMoney {
                amount
                currencyCode
              }
            }
            email
            shippingAddress {
              address1
              city
              provinceCode
              zip
            }
            lineItems(first: 5) {
              edges {
                node {
                  name
                  quantity
                  sku
                  variant {
                    id
                    title
                  }
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
      orders(first: 5) {
        edges {
          node {
            id
            name
            createdAt
            displayFinancialStatus
            displayFulfillmentStatus
            totalPriceSet {
              shopMoney {
                amount
                currencyCode
              }
            }
            subtotalPriceSet {
              shopMoney {
                amount
                currencyCode
              }
            }
            email
            shippingAddress {
              address1
              city
              provinceCode
              zip
            }
            lineItems(first: 5) {
              edges {
                node {
                  name
                  quantity
                  sku
                  variant {
                    id
                    title
                  }
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
    orders(first: 5) {
      edges {
        node {
          id
          name
          createdAt
          displayFinancialStatus
          displayFulfillmentStatus
          totalPriceSet {
            shopMoney {
              amount
              currencyCode
            }
          }
          subtotalPriceSet {
            shopMoney {
              amount
              currencyCode
            }
          }
          email
          shippingAddress {
            address1
            city
            provinceCode
            zip
          }
          lineItems(first: 5) {
            edges {
              node {
                name
                quantity
                sku
                variant {
                  id
                  title
                }
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
    "orders": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/Order/158040885",
            "name": "#2000",
            "createdAt": "2024-01-01T00:00:00Z",
            "displayFinancialStatus": "PAID",
            "displayFulfillmentStatus": "UNFULFILLED",
            "totalPriceSet": {
              "shopMoney": {
                "amount": "2000.0",
                "currencyCode": "CAD"
              }
            },
            "subtotalPriceSet": {
              "shopMoney": {
                "amount": "2000.0",
                "currencyCode": "CAD"
              }
            },
            "email": "bob@example.com",
            "shippingAddress": null,
            "lineItems": {
              "edges": [
                {
                  "node": {
                    "name": "Draft - 151cm",
                    "quantity": 10,
                    "sku": "draft-151",
                    "variant": {
                      "id": "gid://shopify/ProductVariant/168923715",
                      "title": "151cm"
                    }
                  }
                }
              ]
            }
          }
        },
        {
          "node": {
            "id": "gid://shopify/Order/199007853",
            "name": "#2006",
            "createdAt": "2024-01-01T00:00:00Z",
            "displayFinancialStatus": "PAID",
            "displayFulfillmentStatus": "UNFULFILLED",
            "totalPriceSet": {
              "shopMoney": {
                "amount": "2000.0",
                "currencyCode": "CAD"
              }
            },
            "subtotalPriceSet": {
              "shopMoney": {
                "amount": "2000.0",
                "currencyCode": "CAD"
              }
            },
            "email": "bob@example.com",
            "shippingAddress": null,
            "lineItems": {
              "edges": []
            }
          }
        },
        {
          "node": {
            "id": "gid://shopify/Order/212949620",
            "name": "#2002",
            "createdAt": "2024-01-01T00:00:00Z",
            "displayFinancialStatus": "PAID",
            "displayFulfillmentStatus": "UNFULFILLED",
            "totalPriceSet": {
              "shopMoney": {
                "amount": "2000.0",
                "currencyCode": "CAD"
              }
            },
            "subtotalPriceSet": {
              "shopMoney": {
                "amount": "2000.0",
                "currencyCode": "CAD"
              }
            },
            "email": "bob@example.com",
            "shippingAddress": null,
            "lineItems": {
              "edges": []
            }
          }
        },
        {
          "node": {
            "id": "gid://shopify/Order/294238686",
            "name": "#2009",
            "createdAt": "2024-01-01T00:00:00Z",
            "displayFinancialStatus": "PAID",
            "displayFulfillmentStatus": "UNFULFILLED",
            "totalPriceSet": {
              "shopMoney": {
                "amount": "2000.0",
                "currencyCode": "CAD"
              }
            },
            "subtotalPriceSet": {
              "shopMoney": {
                "amount": "2000.0",
                "currencyCode": "CAD"
              }
            },
            "email": "bob@example.com",
            "shippingAddress": null,
            "lineItems": {
              "edges": []
            }
          }
        },
        {
          "node": {
            "id": "gid://shopify/Order/316002265",
            "name": "#2003",
            "createdAt": "2024-01-01T00:00:00Z",
            "displayFinancialStatus": "PAID",
            "displayFulfillmentStatus": "UNFULFILLED",
            "totalPriceSet": {
              "shopMoney": {
                "amount": "2000.0",
                "currencyCode": "CAD"
              }
            },
            "subtotalPriceSet": {
              "shopMoney": {
                "amount": "2000.0",
                "currencyCode": "CAD"
              }
            },
            "email": "bob@example.com",
            "shippingAddress": null,
            "lineItems": {
              "edges": []
            }
          }
        }
      ]
    }
  }
  ```

* ### Retrieve the first 10 orders updated after December 1, 2019

  #### Description

  This query retrieves the first 10 \[\`orders\`]\(https://shopify.dev/api/admin-graphql/latest/objects/Order) updated after December 1, 2019. The example shows how to use the \[\`updated\_at\`]\(https://shopify.dev/docs/api/admin-graphql/latest/queries/orders#argument-query-filter-updated\_at) parameter to determine the orders that were updated after the specified date. Refer to \[pagination]\(https://shopify.dev/api/usage/pagination-graphql) for best practices on handling larger result sets.

  #### Query

  ```graphql
  query {
    orders(first: 10, query: "updated_at:>2019-12-01") {
      edges {
        node {
          id
          updatedAt
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
  "query": "query { orders(first: 10, query: \"updated_at:>2019-12-01\") { edges { node { id updatedAt } } } }"
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
      orders(first: 10, query: "updated_at:>2019-12-01") {
        edges {
          node {
            id
            updatedAt
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
      orders(first: 10, query: "updated_at:>2019-12-01") {
        edges {
          node {
            id
            updatedAt
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
      orders(first: 10, query: "updated_at:>2019-12-01") {
        edges {
          node {
            id
            updatedAt
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
    orders(first: 10, query: "updated_at:>2019-12-01") {
      edges {
        node {
          id
          updatedAt
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "orders": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/Order/158040885",
            "updatedAt": "2024-01-01T12:34:43Z"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Order/199007853",
            "updatedAt": "2024-01-01T12:34:43Z"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Order/212949620",
            "updatedAt": "2024-01-01T12:34:43Z"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Order/294238686",
            "updatedAt": "2024-01-01T12:34:43Z"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Order/316002265",
            "updatedAt": "2024-01-01T12:34:43Z"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Order/459506686",
            "updatedAt": "2024-01-01T12:34:43Z"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Order/634584900",
            "updatedAt": "2024-01-01T12:34:43Z"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Order/744797037",
            "updatedAt": "2024-01-01T12:34:43Z"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Order/1001810659",
            "updatedAt": "2024-01-01T12:34:43Z"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Order/1021030140",
            "updatedAt": "2024-01-01T12:34:43Z"
          }
        }
      ]
    }
  }
  ```

* ### Retrieve the first 10 orders with authorized payments

  #### Description

  This query retrieves the first 10 \[orders]\(https://shopify.dev/api/admin-graphql/latest/objects/Order) with authorized payments. For individual payment verification, refer to the \[\`orderPaymentStatus\`]\(https://shopify.dev/api/admin-graphql/latest/queries/orderPaymentStatus) query.

  #### Query

  ```graphql
  query {
    orders(first: 10, query: "financial_status:authorized") {
      edges {
        node {
          id
          displayFinancialStatus
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
  "query": "query { orders(first: 10, query: \"financial_status:authorized\") { edges { node { id displayFinancialStatus } } } }"
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
      orders(first: 10, query: "financial_status:authorized") {
        edges {
          node {
            id
            displayFinancialStatus
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
      orders(first: 10, query: "financial_status:authorized") {
        edges {
          node {
            id
            displayFinancialStatus
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
      orders(first: 10, query: "financial_status:authorized") {
        edges {
          node {
            id
            displayFinancialStatus
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
    orders(first: 10, query: "financial_status:authorized") {
      edges {
        node {
          id
          displayFinancialStatus
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "orders": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/Order/471861129",
            "displayFinancialStatus": "AUTHORIZED"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Order/527229289",
            "displayFinancialStatus": "AUTHORIZED"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Order/751082136",
            "displayFinancialStatus": "AUTHORIZED"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Order/431501862",
            "displayFinancialStatus": "AUTHORIZED"
          }
        }
      ]
    }
  }
  ```
