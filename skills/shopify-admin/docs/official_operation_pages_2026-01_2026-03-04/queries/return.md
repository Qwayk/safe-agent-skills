---
title: return - GraphQL Admin
description: >-
  Retrieves a return by its ID. A return represents the intent of a buyer to
  ship one or more items from an

  order back to a merchant or a third-party fulfillment location.


  Use the `return` query to retrieve information associated with the following
  workflows:


  - [Managing
  returns](https://shopify.dev/docs/apps/build/orders-fulfillment/returns-apps/build-return-management)

  - [Processing
  exchanges](https://shopify.dev/docs/apps/build/orders-fulfillment/returns-apps/manage-exchanges)

  - [Tracking reverse fulfillment
  orders](https://shopify.dev/docs/apps/build/orders-fulfillment/returns-apps/manage-reverse-fulfillment-orders)


  A return is associated with an

  [order](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order)

  and can include multiple return [line
  items](https://shopify.dev/docs/api/admin-graphql/latest/objects/LineItem).

  Each return has a
  [status](https://shopify.dev/docs/apps/build/orders-fulfillment/returns-apps#return-statuses),

  which indicates the state of the return.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/return'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/return.md'
---

# return

query

Requires `read_returns` access scope or `read_marketplace_returns` access scope.

Retrieves a return by its ID. A return represents the intent of a buyer to ship one or more items from an order back to a merchant or a third-party fulfillment location.

Use the `return` query to retrieve information associated with the following workflows:

* [Managing returns](https://shopify.dev/docs/apps/build/orders-fulfillment/returns-apps/build-return-management)
* [Processing exchanges](https://shopify.dev/docs/apps/build/orders-fulfillment/returns-apps/manage-exchanges)
* [Tracking reverse fulfillment orders](https://shopify.dev/docs/apps/build/orders-fulfillment/returns-apps/manage-reverse-fulfillment-orders)

A return is associated with an [order](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order) and can include multiple return [line items](https://shopify.dev/docs/api/admin-graphql/latest/objects/LineItem). Each return has a [status](https://shopify.dev/docs/apps/build/orders-fulfillment/returns-apps#return-statuses), which indicates the state of the return.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The [globally-unique ID](https://shopify.dev/docs/api/usage/gids) of the return to retrieve.

***

## Possible returns

* Return

  [Return](https://shopify.dev/docs/api/admin-graphql/latest/objects/Return)

  The `Return` object represents the intent of a buyer to ship one or more items from an order back to a merchant or a third-party fulfillment location. A return is associated with an [order](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order) and can include multiple return [line items](https://shopify.dev/docs/api/admin-graphql/latest/objects/LineItem). Each return has a [status](https://shopify.dev/docs/apps/build/orders-fulfillment/returns-apps#return-statuses), which indicates the state of the return.

  Use the `Return` object to capture the financial, logistical, and business intent of a return. For example, you can identify eligible items for a return and issue customers a refund for returned items on behalf of the merchant.

  Learn more about providing a [return management workflow](https://shopify.dev/docs/apps/build/orders-fulfillment/returns-apps/build-return-management) for merchants. You can also manage [exchanges](https://shopify.dev/docs/apps/build/orders-fulfillment/returns-apps/manage-exchanges), [reverse fulfillment orders](https://shopify.dev/docs/apps/build/orders-fulfillment/returns-apps/manage-reverse-fulfillment-orders), and [reverse deliveries](https://shopify.dev/docs/apps/build/orders-fulfillment/returns-apps/manage-reverse-deliveries) on behalf of merchants.

  * closed​At

    [Date​Time](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    The date and time when the return was closed.

  * created​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time when the return was created.

  * decline

    [Return​Decline](https://shopify.dev/docs/api/admin-graphql/latest/objects/ReturnDecline)

    Additional information about the declined return.

  * exchange​Line​Items

    [Exchange​Line​Item​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/ExchangeLineItemConnection)

    non-null

    The exchange line items attached to the return.

    * include​Removed​Items

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Default:false

      ### Arguments

      Include exchange line items that have been removed from the order by an order edit, return, etc. Items that have been removed have a zero ([LineItem.currentQuantity](https://shopify.dev/docs/api/admin-graphql/unstable/objects/LineItem#field-lineitem-currentquantity)).

    * processing​Status

      [Return​Processing​Status​Filter​Input](https://shopify.dev/docs/api/admin-graphql/latest/enums/ReturnProcessingStatusFilterInput)

      Filter exchange line items by processing status.

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * after

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * last

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * before

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * reverse

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Default:false

      Reverse the order of the underlying list.

    ***

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * name

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The name of the return.

  * order

    [Order!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order)

    non-null

    The order that the return belongs to.

  * refunds

    [Refund​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/RefundConnection)

    non-null

    The list of refunds associated with the return.

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      ### Arguments

      The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * after

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * last

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * before

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * reverse

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Default:false

      Reverse the order of the underlying list.

    ***

  * request​Approved​At

    [Date​Time](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    The date and time when the return was approved.

  * return​Line​Items

    [Return​Line​Item​Type​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/ReturnLineItemTypeConnection)

    non-null

    The return line items attached to the return.

    * processing​Status

      [Return​Processing​Status​Filter​Input](https://shopify.dev/docs/api/admin-graphql/latest/enums/ReturnProcessingStatusFilterInput)

      ### Arguments

      Filter return line items by processing status.

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * after

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * last

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * before

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * reverse

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Default:false

      Reverse the order of the underlying list.

    ***

  * return​Shipping​Fees

    [\[Return​Shipping​Fee!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ReturnShippingFee)

    non-null

    The return shipping fees for the return.

  * reverse​Fulfillment​Orders

    [Reverse​Fulfillment​Order​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/ReverseFulfillmentOrderConnection)

    non-null

    The list of reverse fulfillment orders for the return.

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      ### Arguments

      The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * after

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * last

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * before

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * reverse

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Default:false

      Reverse the order of the underlying list.

    ***

  * staff​Member

    [Staff​Member](https://shopify.dev/docs/api/admin-graphql/latest/objects/StaffMember)

    The staff member that created the return.

  * status

    [Return​Status!](https://shopify.dev/docs/api/admin-graphql/latest/enums/ReturnStatus)

    non-null

    The status of the return.

  * suggested​Financial​Outcome

    [Suggested​Return​Financial​Outcome](https://shopify.dev/docs/api/admin-graphql/latest/objects/SuggestedReturnFinancialOutcome)

    A suggested financial outcome for the return.

    * return​Line​Items

      [\[Suggested​Outcome​Return​Line​Item​Input!\]!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/SuggestedOutcomeReturnLineItemInput)

      required

      ### Arguments

      The line items from the return to include in the outcome.

    * exchange​Line​Items

      [\[Suggested​Outcome​Exchange​Line​Item​Input!\]!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/SuggestedOutcomeExchangeLineItemInput)

      required

      The exchange line items from the return to include in the outcome.

    * refund​Shipping

      [Refund​Shipping​Input](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/RefundShippingInput)

      The shipping amount from the associated order to include as a refund.

    * tip​Line​Id

      [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

      ID of the tip line item.

    * refund​Duties

      [\[Refund​Duty​Input!\]](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/RefundDutyInput)

      The duties from the associated order to include as a refund.

    * refund​Method​Allocation

      [Refund​Method​Allocation](https://shopify.dev/docs/api/admin-graphql/latest/enums/RefundMethodAllocation)

      Default:ORIGINAL\_PAYMENT\_METHODS

      Specifies which refund methods to allocate the suggested refund amount to.

    ***

  * total​Quantity

    [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    non-null

    The sum of all return line item quantities for the return.

  * transactions

    [Order​Transaction​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/OrderTransactionConnection)

    non-null

    The order transactions created from the return.

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      ### Arguments

      The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * after

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * last

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * before

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * reverse

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Default:false

      Reverse the order of the underlying list.

    ***

  * suggested​Refund

    [Suggested​Return​Refund](https://shopify.dev/docs/api/admin-graphql/latest/objects/SuggestedReturnRefund)

    Deprecated

    * return​Refund​Line​Items

      [\[Return​Refund​Line​Item​Input!\]!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/ReturnRefundLineItemInput)

      required

      ### Arguments

      The line items from the return to include in the refund.

    * refund​Shipping

      [Refund​Shipping​Input](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/RefundShippingInput)

      The shipping amount from the associated order to include in the refund.

    * refund​Duties

      [\[Refund​Duty​Input!\]](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/RefundDutyInput)

      The duties from to associated order to include in the refund.

    ***

***

## Examples

* ### Query return with return reason definitions

  #### Description

  Retrieve return line items with their associated return reason definitions. This example shows how to access standardized return reasons instead of the deprecated enum.

  #### Query

  ```graphql
  query {
    return(id: "gid://shopify/Return/945000954") {
      id
      name
      returnLineItems(first: 5) {
        edges {
          node {
            id
            quantity
            returnReasonDefinition {
              id
              handle
              name
              deleted
            }
            customerNote
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
  "query": "query { return(id: \"gid://shopify/Return/945000954\") { id name returnLineItems(first: 5) { edges { node { id quantity returnReasonDefinition { id handle name deleted } customerNote } } } } }"
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
      return(id: "gid://shopify/Return/945000954") {
        id
        name
        returnLineItems(first: 5) {
          edges {
            node {
              id
              quantity
              returnReasonDefinition {
                id
                handle
                name
                deleted
              }
              customerNote
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
      return(id: "gid://shopify/Return/945000954") {
        id
        name
        returnLineItems(first: 5) {
          edges {
            node {
              id
              quantity
              returnReasonDefinition {
                id
                handle
                name
                deleted
              }
              customerNote
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
      return(id: "gid://shopify/Return/945000954") {
        id
        name
        returnLineItems(first: 5) {
          edges {
            node {
              id
              quantity
              returnReasonDefinition {
                id
                handle
                name
                deleted
              }
              customerNote
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
    return(id: "gid://shopify/Return/945000954") {
      id
      name
      returnLineItems(first: 5) {
        edges {
          node {
            id
            quantity
            returnReasonDefinition {
              id
              handle
              name
              deleted
            }
            customerNote
          }
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "return": {
      "id": "gid://shopify/Return/945000954",
      "name": "#1001-R1",
      "returnLineItems": {
        "edges": [
          {
            "node": {
              "id": "gid://shopify/ReturnLineItem/57615080",
              "quantity": 1,
              "returnReasonDefinition": {
                "id": "gid://shopify/ReturnReasonDefinition/305697940",
                "handle": "defective",
                "name": "Defective",
                "deleted": false
              },
              "customerNote": null
            }
          }
        ]
      }
    }
  }
  ```

* ### Retrieve a return's exchange line items

  #### Description

  Retrieve the exchange line items associated with a return to access which items are being exchanged as part of a return process. This example shows how to query for the \`exchangeLineItems\` connection, which includes the IDs of the exchange line items. Learn more about \[managing exchanges]\(https://shopify.dev/docs/apps/build/orders-fulfillment/returns-apps/manage-exchanges).

  #### Query

  ```graphql
  query {
    return(id: "gid://shopify/Return/194950309") {
      exchangeLineItems(first: 10) {
        edges {
          node {
            id
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
  "query": "query { return(id: \"gid://shopify/Return/194950309\") { exchangeLineItems(first: 10) { edges { node { id } } } } }"
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
      return(id: "gid://shopify/Return/194950309") {
        exchangeLineItems(first: 10) {
          edges {
            node {
              id
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
      return(id: "gid://shopify/Return/194950309") {
        exchangeLineItems(first: 10) {
          edges {
            node {
              id
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
      return(id: "gid://shopify/Return/194950309") {
        exchangeLineItems(first: 10) {
          edges {
            node {
              id
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
    return(id: "gid://shopify/Return/194950309") {
      exchangeLineItems(first: 10) {
        edges {
          node {
            id
          }
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "return": {
      "exchangeLineItems": {
        "edges": [
          {
            "node": {
              "id": "gid://shopify/ExchangeLineItem/444766497"
            }
          }
        ]
      }
    }
  }
  ```

* ### Retrieve a return's reverse fulfillment orders

  #### Description

  Retrieve the reverse fulfillment orders associated with a return. This example shows how to query the \`reverseFulfillmentOrders\` connection to get the IDs of related reverse fulfillment orders, which are used for tracking the logistics of returned items. Learn more about \[managing reverse fulfillment orders]\(https://shopify.dev/docs/apps/build/orders-fulfillment/returns-apps/manage-reverse-fulfillment-orders).

  #### Query

  ```graphql
  query {
    return(id: "gid://shopify/Return/684888505") {
      reverseFulfillmentOrders(first: 10) {
        edges {
          node {
            id
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
  "query": "query { return(id: \"gid://shopify/Return/684888505\") { reverseFulfillmentOrders(first: 10) { edges { node { id } } } } }"
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
      return(id: "gid://shopify/Return/684888505") {
        reverseFulfillmentOrders(first: 10) {
          edges {
            node {
              id
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
      return(id: "gid://shopify/Return/684888505") {
        reverseFulfillmentOrders(first: 10) {
          edges {
            node {
              id
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
      return(id: "gid://shopify/Return/684888505") {
        reverseFulfillmentOrders(first: 10) {
          edges {
            node {
              id
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
    return(id: "gid://shopify/Return/684888505") {
      reverseFulfillmentOrders(first: 10) {
        edges {
          node {
            id
          }
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "return": {
      "reverseFulfillmentOrders": {
        "edges": [
          {
            "node": {
              "id": "gid://shopify/ReverseFulfillmentOrder/874405546"
            }
          }
        ]
      }
    }
  }
  ```

* ### Retrieve a return's status and line items

  #### Description

  Retrieve the status and the first ten return line items associated with a return. The example shows how to structure the query to access the return's name, order ID, and the relevant attributes of the return line items, such as quantity, return reason, and total weight. The return status is \`OPEN\`, which indicates tha the query was successfully executed. The example uses the \`... on ReturnLineItem\` \[fragment]\(https://shopify.dev/docs/apps/build/graphql/basics/advanced#inline-fragments) to access fields that only exist on the \[\`ReturnLineItem\`]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/ReturnLineItem) object.

  #### Query

  ```graphql
  query {
    return(id: "gid://shopify/Return/945000954") {
      status
      name
      order {
        id
      }
      returnLineItems(first: 10) {
        edges {
          node {
            ... on ReturnLineItem {
              quantity
              returnReason
              returnReasonNote
              fulfillmentLineItem {
                lineItem {
                  name
                }
              }
              totalWeight {
                value
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
  "query": "query { return(id: \"gid://shopify/Return/945000954\") { status name order { id } returnLineItems(first: 10) { edges { node { ... on ReturnLineItem { quantity returnReason returnReasonNote fulfillmentLineItem { lineItem { name } } totalWeight { value } } } } } } }"
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
      return(id: "gid://shopify/Return/945000954") {
        status
        name
        order {
          id
        }
        returnLineItems(first: 10) {
          edges {
            node {
              ... on ReturnLineItem {
                quantity
                returnReason
                returnReasonNote
                fulfillmentLineItem {
                  lineItem {
                    name
                  }
                }
                totalWeight {
                  value
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
      return(id: "gid://shopify/Return/945000954") {
        status
        name
        order {
          id
        }
        returnLineItems(first: 10) {
          edges {
            node {
              ... on ReturnLineItem {
                quantity
                returnReason
                returnReasonNote
                fulfillmentLineItem {
                  lineItem {
                    name
                  }
                }
                totalWeight {
                  value
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
      return(id: "gid://shopify/Return/945000954") {
        status
        name
        order {
          id
        }
        returnLineItems(first: 10) {
          edges {
            node {
              ... on ReturnLineItem {
                quantity
                returnReason
                returnReasonNote
                fulfillmentLineItem {
                  lineItem {
                    name
                  }
                }
                totalWeight {
                  value
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
    return(id: "gid://shopify/Return/945000954") {
      status
      name
      order {
        id
      }
      returnLineItems(first: 10) {
        edges {
          node {
            ... on ReturnLineItem {
              quantity
              returnReason
              returnReasonNote
              fulfillmentLineItem {
                lineItem {
                  name
                }
              }
              totalWeight {
                value
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
    "return": {
      "status": "OPEN",
      "name": "#1001-R1",
      "order": {
        "id": "gid://shopify/Order/625362839"
      },
      "returnLineItems": {
        "edges": [
          {
            "node": {
              "quantity": 1,
              "returnReason": "UNKNOWN",
              "returnReasonNote": "",
              "fulfillmentLineItem": {
                "lineItem": {
                  "name": "Draft - 151cm"
                }
              },
              "totalWeight": {
                "value": 1500
              }
            }
          }
        ]
      }
    }
  }
  ```
