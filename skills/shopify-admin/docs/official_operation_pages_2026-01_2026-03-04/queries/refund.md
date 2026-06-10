---
title: refund - GraphQL Admin
description: >-
  Retrieves a
  [refund](https://shopify.dev/docs/api/admin-graphql/latest/objects/Refund) by
  its ID.

  A refund represents a financial record of money returned to a customer from an
  order.

  It provides a comprehensive view of all refunded amounts, transactions, and
  restocking

  instructions associated with returning products or correcting order issues.


  Use the `refund` query to retrieve information associated with the following
  workflows:


  - Displaying refund details in order management interfaces

  - Building customer service tools for reviewing refund history

  - Creating reports on refunded amounts and reasons

  - Auditing refund transactions and payment gateway records

  - Tracking inventory impacts from refunded items


  A refund is associated with an

  [order](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order)

  and includes [refund line
  items](https://shopify.dev/docs/api/admin-graphql/latest/objects/RefundLineItem)

  that specify which items were refunded. Each refund processes through

  [order
  transactions](https://shopify.dev/docs/api/admin-graphql/latest/objects/OrderTransaction)

  that handle the actual money transfer back to the customer.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/refund'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/refund.md'
---

# refund

query

Requires `read_orders` access scope or `read_marketplace_orders` access scope.

Retrieves a [refund](https://shopify.dev/docs/api/admin-graphql/latest/objects/Refund) by its ID. A refund represents a financial record of money returned to a customer from an order. It provides a comprehensive view of all refunded amounts, transactions, and restocking instructions associated with returning products or correcting order issues.

Use the `refund` query to retrieve information associated with the following workflows:

* Displaying refund details in order management interfaces
* Building customer service tools for reviewing refund history
* Creating reports on refunded amounts and reasons
* Auditing refund transactions and payment gateway records
* Tracking inventory impacts from refunded items

A refund is associated with an [order](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order) and includes [refund line items](https://shopify.dev/docs/api/admin-graphql/latest/objects/RefundLineItem) that specify which items were refunded. Each refund processes through [order transactions](https://shopify.dev/docs/api/admin-graphql/latest/objects/OrderTransaction) that handle the actual money transfer back to the customer.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the Refund to return.

***

## Possible returns

* Refund

  [Refund](https://shopify.dev/docs/api/admin-graphql/latest/objects/Refund)

  The `Refund` object represents a financial record of money returned to a customer from an order. It provides a comprehensive view of all refunded amounts, transactions, and restocking instructions associated with returning products or correcting order issues.

  The `Refund` object provides information to:

  * Process customer returns and issue payments back to customers
  * Handle partial or full refunds for line items with optional inventory restocking
  * Refund shipping costs, duties, and additional fees
  * Issue store credit refunds as an alternative to original payment method returns
  * Track and reconcile all financial transactions related to refunds

  Each `Refund` object maintains detailed records of what was refunded, how much was refunded, which payment transactions were involved, and any inventory restocking that occurred. The refund can include multiple components such as product line items, shipping charges, taxes, duties, and additional fees, all calculated with proper currency handling for international orders.

  Refunds are always associated with an [order](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order) and can optionally be linked to a [return](https://shopify.dev/docs/api/admin-graphql/latest/objects/Return) if the refund was initiated through the returns process. The refund tracks both the presentment currency (what the customer sees) and the shop currency for accurate financial reporting.

  ***

  **Note:** The existence of a \<code>Refund\</code> object doesn\&#39;t guarantee that the money has been returned to the customer. The actual financial processing happens through associated \<a href="https://shopify.dev/docs/api/admin-graphql/latest/objects/OrderTransaction">\<code>\<span class="PreventFireFoxApplyingGapToWBR">Order\<wbr/>Transaction\</span>\</code>\</a> objects, which can be in various states, such as pending, processing, success, or failure. To determine if money has actually been refunded, check the \<a href="https://shopify.dev/docs/api/admin-graphql/latest/objects/OrderTransaction#field-OrderTransaction.fields.status">status\</a> of the associated transactions.

  ***

  Learn more about [managing returns](https://shopify.dev/docs/apps/build/orders-fulfillment/returns-apps/build-return-management), [refunding duties](https://shopify.dev/docs/apps/build/orders-fulfillment/returns-apps/view-and-refund-duties), and [processing refunds](https://shopify.dev/docs/api/admin-graphql/latest/mutations/refundCreate).

  * created​At

    [Date​Time](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    The date and time when the refund was created.

  * duties

    [\[Refund​Duty!\]](https://shopify.dev/docs/api/admin-graphql/latest/objects/RefundDuty)

    A list of the refunded duties as part of this refund.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * legacy​Resource​Id

    [Unsigned​Int64!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/UnsignedInt64)

    non-null

    The ID of the corresponding resource in the REST Admin API.

  * note

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The optional note associated with the refund.

  * order

    [Order!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order)

    non-null

    The order associated with the refund.

  * order​Adjustments

    [Order​Adjustment​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/OrderAdjustmentConnection)

    non-null

    The order adjustments that are attached with the refund.

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

  * processed​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time when the refund was processed.

  * refund​Line​Items

    [Refund​Line​Item​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/RefundLineItemConnection)

    non-null

    The `RefundLineItem` resources attached to the refund.

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

  * refund​Shipping​Lines

    [Refund​Shipping​Line​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/RefundShippingLineConnection)

    non-null

    The `RefundShippingLine` resources attached to the refund.

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

  * return

    [Return](https://shopify.dev/docs/api/admin-graphql/latest/objects/Return)

    The return associated with the refund.

  * staff​Member

    [Staff​Member](https://shopify.dev/docs/api/admin-graphql/latest/objects/StaffMember)

    The staff member who created the refund.

  * total​Refunded​Set

    [Money​Bag!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyBag)

    non-null

    The total amount across all transactions for the refund, in shop and presentment currencies.

  * transactions

    [Order​Transaction​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/OrderTransactionConnection)

    non-null

    The transactions associated with the refund.

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

  * updated​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time when the refund was updated.

  * total​Refunded

    [Money​V2!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyV2)

    non-nullDeprecated

***

## Examples

* ### Get refund duties

  #### Description

  The following query retrieves a refund by its ID and returns the refund duties.

  #### Query

  ```graphql
  query refund($input: ID!) {
    refund(id: $input) {
      duties {
        originalDuty {
          countryCodeOfOrigin
        }
        amountSet {
          shopMoney {
            amount
          }
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": "gid://shopify/Refund/850600470"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query refund($input: ID!) { refund(id: $input) { duties { originalDuty { countryCodeOfOrigin } amountSet { shopMoney { amount } } } } }",
   "variables": {
      "input": "gid://shopify/Refund/850600470"
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
    query refund($input: ID!) {
      refund(id: $input) {
        duties {
          originalDuty {
            countryCodeOfOrigin
          }
          amountSet {
            shopMoney {
              amount
            }
          }
        }
      }
    }`,
    {
      variables: {
          "input": "gid://shopify/Refund/850600470"
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
    query refund($input: ID!) {
      refund(id: $input) {
        duties {
          originalDuty {
            countryCodeOfOrigin
          }
          amountSet {
            shopMoney {
              amount
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "input": "gid://shopify/Refund/850600470"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query refund($input: ID!) {
        refund(id: $input) {
          duties {
            originalDuty {
              countryCodeOfOrigin
            }
            amountSet {
              shopMoney {
                amount
              }
            }
          }
        }
      }`,
      "variables": {
          "input": "gid://shopify/Refund/850600470"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query refund($input: ID!) {
    refund(id: $input) {
      duties {
        originalDuty {
          countryCodeOfOrigin
        }
        amountSet {
          shopMoney {
            amount
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "input": "gid://shopify/Refund/850600470"
  }'
  ```

  #### Response

  ```json
  {
    "refund": {
      "duties": [
        {
          "originalDuty": {
            "countryCodeOfOrigin": "US"
          },
          "amountSet": {
            "shopMoney": {
              "amount": "6.0"
            }
          }
        }
      ]
    }
  }
  ```

* ### Get the total refunded amount

  #### Description

  The following query retrieves a refund by its ID and returns the total refunded amount.

  #### Query

  ```graphql
  query refund($input: ID!) {
    refund(id: $input) {
      totalRefundedSet {
        shopMoney {
          amount
          currencyCode
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": "gid://shopify/Refund/196417871"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query refund($input: ID!) { refund(id: $input) { totalRefundedSet { shopMoney { amount currencyCode } } } }",
   "variables": {
      "input": "gid://shopify/Refund/196417871"
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
    query refund($input: ID!) {
      refund(id: $input) {
        totalRefundedSet {
          shopMoney {
            amount
            currencyCode
          }
        }
      }
    }`,
    {
      variables: {
          "input": "gid://shopify/Refund/196417871"
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
    query refund($input: ID!) {
      refund(id: $input) {
        totalRefundedSet {
          shopMoney {
            amount
            currencyCode
          }
        }
      }
    }
  QUERY

  variables = {
    "input": "gid://shopify/Refund/196417871"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query refund($input: ID!) {
        refund(id: $input) {
          totalRefundedSet {
            shopMoney {
              amount
              currencyCode
            }
          }
        }
      }`,
      "variables": {
          "input": "gid://shopify/Refund/196417871"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query refund($input: ID!) {
    refund(id: $input) {
      totalRefundedSet {
        shopMoney {
          amount
          currencyCode
        }
      }
    }
  }' \
  --variables \
  '{
    "input": "gid://shopify/Refund/196417871"
  }'
  ```

  #### Response

  ```json
  {
    "refund": {
      "totalRefundedSet": {
        "shopMoney": {
          "amount": "5.75",
          "currencyCode": "USD"
        }
      }
    }
  }
  ```

* ### Retrieves a specific refund

  #### Query

  ```graphql
  query RefundShow($id: ID!) {
    refund(id: $id) {
      id
      note
      totalRefundedSet {
        presentmentMoney {
          amount
          currencyCode
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/Refund/196417871"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query RefundShow($id: ID!) { refund(id: $id) { id note totalRefundedSet { presentmentMoney { amount currencyCode } } } }",
   "variables": {
      "id": "gid://shopify/Refund/196417871"
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
    query RefundShow($id: ID!) {
      refund(id: $id) {
        id
        note
        totalRefundedSet {
          presentmentMoney {
            amount
            currencyCode
          }
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/Refund/196417871"
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
    query RefundShow($id: ID!) {
      refund(id: $id) {
        id
        note
        totalRefundedSet {
          presentmentMoney {
            amount
            currencyCode
          }
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/Refund/196417871"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query RefundShow($id: ID!) {
        refund(id: $id) {
          id
          note
          totalRefundedSet {
            presentmentMoney {
              amount
              currencyCode
            }
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/Refund/196417871"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query RefundShow($id: ID!) {
    refund(id: $id) {
      id
      note
      totalRefundedSet {
        presentmentMoney {
          amount
          currencyCode
        }
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/Refund/196417871"
  }'
  ```

  #### Response

  ```json
  {
    "refund": {
      "id": "gid://shopify/Refund/196417871",
      "note": "free shipping",
      "totalRefundedSet": {
        "presentmentMoney": {
          "amount": "5.75",
          "currencyCode": "USD"
        }
      }
    }
  }
  ```
