---
title: orderCreate - GraphQL Admin
description: >-
  Creates an order with attributes such as customer information, line items, and
  shipping and billing addresses.


  Use the `orderCreate` mutation to programmatically generate orders in
  scenarios where

  orders aren't created through the standard checkout process, such as when
  importing orders from an external

  system or creating orders for wholesale customers.


  The `orderCreate` mutation doesn't support applying multiple discounts, such
  as discounts on line items.

  Automatic discounts won't be applied unless you replicate the logic of those
  discounts in your custom

  implementation. You can [apply a discount
  code](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/OrderCreateDiscountCodeInput),

  but only one discount code can be set for each order.


  > Note:

  > If you're using the `orderCreate` mutation with a

  >
  [trial](https://help.shopify.com/manual/intro-to-shopify/pricing-plans/free-trial)
  or

  > [development store](https://shopify.dev/docs/api/development-stores), then
  you can create a

  > maximum of five new orders per minute.


  After you create an order, you can make subsequent edits to the order using
  one of the following mutations:

  *
  [`orderUpdate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderUpdate):

  Used for simple updates to an order, such as changing the order's note, tags,
  or customer information.

  *
  [`orderEditBegin`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderEditBegin):

  Used when you need to make significant updates to an order, such as adding or
  removing line items, changing

  quantities, or modifying discounts. The `orderEditBegin` mutation initiates an
  order editing session,

  allowing you to make multiple changes before finalizing them. Learn more about
  using the `orderEditBegin`

  mutation to [edit existing
  orders](https://shopify.dev/docs/apps/build/orders-fulfillment/order-management-apps/edit-orders).


  Learn how to build apps that integrate with

  [order management and fulfillment
  processes](https://shopify.dev/docs/apps/build/orders-fulfillment).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderCreate'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderCreate.md'
---

# order​Create

mutation

Requires `write_orders` access scope. Also: This mutation is only accessible to apps authenticated using [offline tokens](https://shopify.dev/docs/apps/build/authentication-authorization/access-tokens/offline-access-tokens).

Creates an order with attributes such as customer information, line items, and shipping and billing addresses.

Use the `orderCreate` mutation to programmatically generate orders in scenarios where orders aren't created through the standard checkout process, such as when importing orders from an external system or creating orders for wholesale customers.

The `orderCreate` mutation doesn't support applying multiple discounts, such as discounts on line items. Automatic discounts won't be applied unless you replicate the logic of those discounts in your custom implementation. You can [apply a discount code](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/OrderCreateDiscountCodeInput), but only one discount code can be set for each order.

***

**Note:** If you\&#39;re using the \<code>\<span class="PreventFireFoxApplyingGapToWBR">order\<wbr/>Create\</span>\</code> mutation with a \<a href="https://help.shopify.com/manual/intro-to-shopify/pricing-plans/free-trial">trial\</a> or \<a href="https://shopify.dev/docs/api/development-stores">development store\</a>, then you can create a maximum of five new orders per minute.

***

After you create an order, you can make subsequent edits to the order using one of the following mutations:

* [`orderUpdate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderUpdate): Used for simple updates to an order, such as changing the order's note, tags, or customer information.
* [`orderEditBegin`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderEditBegin): Used when you need to make significant updates to an order, such as adding or removing line items, changing quantities, or modifying discounts. The `orderEditBegin` mutation initiates an order editing session, allowing you to make multiple changes before finalizing them. Learn more about using the `orderEditBegin` mutation to [edit existing orders](https://shopify.dev/docs/apps/build/orders-fulfillment/order-management-apps/edit-orders).

Learn how to build apps that integrate with [order management and fulfillment processes](https://shopify.dev/docs/apps/build/orders-fulfillment).

## Arguments

* options

  [Order​Create​Options​Input](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/OrderCreateOptionsInput)

  The strategies for updating inventory and whether to send shipping and order confirmations to customers.

* order

  [Order​Create​Order​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/OrderCreateOrderInput)

  required

  The attributes of the new order.

***

## Order​Create​Payload returns

* order

  [Order](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order)

  The order that was created.

* user​Errors

  [\[Order​Create​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/OrderCreateUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create a comprehensive order

  #### Description

  This mutation creates an order with pricing in EUR. It includes a single line item with custom pricing and line item level taxes. It also shows a successfully completed transaction with payment details. The response includes the order's total tax amount.

  #### Query

  ```graphql
  mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
    orderCreate(order: $order, options: $options) {
      userErrors {
        field
        message
      }
      order {
        id
        totalTaxSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        lineItems(first: 5) {
          nodes {
            variant {
              id
            }
            id
            title
            quantity
            taxLines {
              title
              rate
              priceSet {
                shopMoney {
                  amount
                  currencyCode
                }
              }
            }
          }
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "order": {
      "currency": "EUR",
      "lineItems": [
        {
          "title": "Big Brown Bear Boots",
          "priceSet": {
            "shopMoney": {
              "amount": 74.99,
              "currencyCode": "EUR"
            }
          },
          "quantity": 3,
          "taxLines": [
            {
              "priceSet": {
                "shopMoney": {
                  "amount": 13.5,
                  "currencyCode": "EUR"
                }
              },
              "rate": 0.06,
              "title": "State tax"
            }
          ]
        }
      ],
      "transactions": [
        {
          "kind": "SALE",
          "status": "SUCCESS",
          "amountSet": {
            "shopMoney": {
              "amount": 238.47,
              "currencyCode": "EUR"
            }
          }
        }
      ]
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
  "query": "mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) { orderCreate(order: $order, options: $options) { userErrors { field message } order { id totalTaxSet { shopMoney { amount currencyCode } } lineItems(first: 5) { nodes { variant { id } id title quantity taxLines { title rate priceSet { shopMoney { amount currencyCode } } } } } } } }",
   "variables": {
      "order": {
        "currency": "EUR",
        "lineItems": [
          {
            "title": "Big Brown Bear Boots",
            "priceSet": {
              "shopMoney": {
                "amount": 74.99,
                "currencyCode": "EUR"
              }
            },
            "quantity": 3,
            "taxLines": [
              {
                "priceSet": {
                  "shopMoney": {
                    "amount": 13.5,
                    "currencyCode": "EUR"
                  }
                },
                "rate": 0.06,
                "title": "State tax"
              }
            ]
          }
        ],
        "transactions": [
          {
            "kind": "SALE",
            "status": "SUCCESS",
            "amountSet": {
              "shopMoney": {
                "amount": 238.47,
                "currencyCode": "EUR"
              }
            }
          }
        ]
      }
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
    mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
      orderCreate(order: $order, options: $options) {
        userErrors {
          field
          message
        }
        order {
          id
          totalTaxSet {
            shopMoney {
              amount
              currencyCode
            }
          }
          lineItems(first: 5) {
            nodes {
              variant {
                id
              }
              id
              title
              quantity
              taxLines {
                title
                rate
                priceSet {
                  shopMoney {
                    amount
                    currencyCode
                  }
                }
              }
            }
          }
        }
      }
    }`,
    {
      variables: {
          "order": {
              "currency": "EUR",
              "lineItems": [
                  {
                      "title": "Big Brown Bear Boots",
                      "priceSet": {
                          "shopMoney": {
                              "amount": 74.99,
                              "currencyCode": "EUR"
                          }
                      },
                      "quantity": 3,
                      "taxLines": [
                          {
                              "priceSet": {
                                  "shopMoney": {
                                      "amount": 13.5,
                                      "currencyCode": "EUR"
                                  }
                              },
                              "rate": 0.06,
                              "title": "State tax"
                          }
                      ]
                  }
              ],
              "transactions": [
                  {
                      "kind": "SALE",
                      "status": "SUCCESS",
                      "amountSet": {
                          "shopMoney": {
                              "amount": 238.47,
                              "currencyCode": "EUR"
                          }
                      }
                  }
              ]
          }
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
    mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
      orderCreate(order: $order, options: $options) {
        userErrors {
          field
          message
        }
        order {
          id
          totalTaxSet {
            shopMoney {
              amount
              currencyCode
            }
          }
          lineItems(first: 5) {
            nodes {
              variant {
                id
              }
              id
              title
              quantity
              taxLines {
                title
                rate
                priceSet {
                  shopMoney {
                    amount
                    currencyCode
                  }
                }
              }
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "order": {
      "currency": "EUR",
      "lineItems": [
        {
          "title": "Big Brown Bear Boots",
          "priceSet": {
            "shopMoney": {
              "amount": 74.99,
              "currencyCode": "EUR"
            }
          },
          "quantity": 3,
          "taxLines": [
            {
              "priceSet": {
                "shopMoney": {
                  "amount": 13.5,
                  "currencyCode": "EUR"
                }
              },
              "rate": 0.06,
              "title": "State tax"
            }
          ]
        }
      ],
      "transactions": [
        {
          "kind": "SALE",
          "status": "SUCCESS",
          "amountSet": {
            "shopMoney": {
              "amount": 238.47,
              "currencyCode": "EUR"
            }
          }
        }
      ]
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
        orderCreate(order: $order, options: $options) {
          userErrors {
            field
            message
          }
          order {
            id
            totalTaxSet {
              shopMoney {
                amount
                currencyCode
              }
            }
            lineItems(first: 5) {
              nodes {
                variant {
                  id
                }
                id
                title
                quantity
                taxLines {
                  title
                  rate
                  priceSet {
                    shopMoney {
                      amount
                      currencyCode
                    }
                  }
                }
              }
            }
          }
        }
      }`,
      "variables": {
          "order": {
              "currency": "EUR",
              "lineItems": [
                  {
                      "title": "Big Brown Bear Boots",
                      "priceSet": {
                          "shopMoney": {
                              "amount": 74.99,
                              "currencyCode": "EUR"
                          }
                      },
                      "quantity": 3,
                      "taxLines": [
                          {
                              "priceSet": {
                                  "shopMoney": {
                                      "amount": 13.5,
                                      "currencyCode": "EUR"
                                  }
                              },
                              "rate": 0.06,
                              "title": "State tax"
                          }
                      ]
                  }
              ],
              "transactions": [
                  {
                      "kind": "SALE",
                      "status": "SUCCESS",
                      "amountSet": {
                          "shopMoney": {
                              "amount": 238.47,
                              "currencyCode": "EUR"
                          }
                      }
                  }
              ]
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
    orderCreate(order: $order, options: $options) {
      userErrors {
        field
        message
      }
      order {
        id
        totalTaxSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        lineItems(first: 5) {
          nodes {
            variant {
              id
            }
            id
            title
            quantity
            taxLines {
              title
              rate
              priceSet {
                shopMoney {
                  amount
                  currencyCode
                }
              }
            }
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "order": {
      "currency": "EUR",
      "lineItems": [
        {
          "title": "Big Brown Bear Boots",
          "priceSet": {
            "shopMoney": {
              "amount": 74.99,
              "currencyCode": "EUR"
            }
          },
          "quantity": 3,
          "taxLines": [
            {
              "priceSet": {
                "shopMoney": {
                  "amount": 13.5,
                  "currencyCode": "EUR"
                }
              },
              "rate": 0.06,
              "title": "State tax"
            }
          ]
        }
      ],
      "transactions": [
        {
          "kind": "SALE",
          "status": "SUCCESS",
          "amountSet": {
            "shopMoney": {
              "amount": 238.47,
              "currencyCode": "EUR"
            }
          }
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "orderCreate": {
      "userErrors": [],
      "order": {
        "id": "gid://shopify/Order/1073459971",
        "totalTaxSet": {
          "shopMoney": {
            "amount": "13.5",
            "currencyCode": "EUR"
          }
        },
        "lineItems": {
          "nodes": [
            {
              "variant": null,
              "id": "gid://shopify/LineItem/1071823181",
              "title": "Big Brown Bear Boots",
              "quantity": 3,
              "taxLines": [
                {
                  "title": "State tax",
                  "rate": 0.06,
                  "priceSet": {
                    "shopMoney": {
                      "amount": "13.5",
                      "currencyCode": "EUR"
                    }
                  }
                }
              ]
            }
          ]
        }
      }
    }
  }
  ```

* ### Create a paid order and update customer details

  #### Description

  This mutation creates an order for an existing customer and updates the customer's first name, last name, and email. The financial status is kept as paid.

  #### Query

  ```graphql
  mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
    orderCreate(order: $order, options: $options) {
      userErrors {
        field
        message
      }
      order {
        id
        displayFinancialStatus
        customer {
          email
          firstName
          lastName
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "order": {
      "lineItems": [
        {
          "variantId": "gid://shopify/ProductVariant/43729076",
          "quantity": 1
        }
      ],
      "customer": {
        "toUpsert": {
          "email": "foo.bar@shopify.com",
          "firstName": "Foo",
          "lastName": "Bar"
        }
      },
      "financialStatus": "PAID"
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
  "query": "mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) { orderCreate(order: $order, options: $options) { userErrors { field message } order { id displayFinancialStatus customer { email firstName lastName } } } }",
   "variables": {
      "order": {
        "lineItems": [
          {
            "variantId": "gid://shopify/ProductVariant/43729076",
            "quantity": 1
          }
        ],
        "customer": {
          "toUpsert": {
            "email": "foo.bar@shopify.com",
            "firstName": "Foo",
            "lastName": "Bar"
          }
        },
        "financialStatus": "PAID"
      }
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
    mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
      orderCreate(order: $order, options: $options) {
        userErrors {
          field
          message
        }
        order {
          id
          displayFinancialStatus
          customer {
            email
            firstName
            lastName
          }
        }
      }
    }`,
    {
      variables: {
          "order": {
              "lineItems": [
                  {
                      "variantId": "gid://shopify/ProductVariant/43729076",
                      "quantity": 1
                  }
              ],
              "customer": {
                  "toUpsert": {
                      "email": "foo.bar@shopify.com",
                      "firstName": "Foo",
                      "lastName": "Bar"
                  }
              },
              "financialStatus": "PAID"
          }
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
    mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
      orderCreate(order: $order, options: $options) {
        userErrors {
          field
          message
        }
        order {
          id
          displayFinancialStatus
          customer {
            email
            firstName
            lastName
          }
        }
      }
    }
  QUERY

  variables = {
    "order": {
      "lineItems": [
        {
          "variantId": "gid://shopify/ProductVariant/43729076",
          "quantity": 1
        }
      ],
      "customer": {
        "toUpsert": {
          "email": "foo.bar@shopify.com",
          "firstName": "Foo",
          "lastName": "Bar"
        }
      },
      "financialStatus": "PAID"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
        orderCreate(order: $order, options: $options) {
          userErrors {
            field
            message
          }
          order {
            id
            displayFinancialStatus
            customer {
              email
              firstName
              lastName
            }
          }
        }
      }`,
      "variables": {
          "order": {
              "lineItems": [
                  {
                      "variantId": "gid://shopify/ProductVariant/43729076",
                      "quantity": 1
                  }
              ],
              "customer": {
                  "toUpsert": {
                      "email": "foo.bar@shopify.com",
                      "firstName": "Foo",
                      "lastName": "Bar"
                  }
              },
              "financialStatus": "PAID"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
    orderCreate(order: $order, options: $options) {
      userErrors {
        field
        message
      }
      order {
        id
        displayFinancialStatus
        customer {
          email
          firstName
          lastName
        }
      }
    }
  }' \
  --variables \
  '{
    "order": {
      "lineItems": [
        {
          "variantId": "gid://shopify/ProductVariant/43729076",
          "quantity": 1
        }
      ],
      "customer": {
        "toUpsert": {
          "email": "foo.bar@shopify.com",
          "firstName": "Foo",
          "lastName": "Bar"
        }
      },
      "financialStatus": "PAID"
    }
  }'
  ```

  #### Response

  ```json
  {
    "orderCreate": {
      "userErrors": [],
      "order": {
        "id": "gid://shopify/Order/1073459972",
        "displayFinancialStatus": "PAID",
        "customer": {
          "email": "foo.bar@shopify.com",
          "firstName": "Foo",
          "lastName": "Bar"
        }
      }
    }
  }
  ```

* ### Create a pending order for an existing customer

  #### Description

  This mutation creates an order for an existing customer, adds new shipping and billing addresses, and sets the order's financial status to pending.

  #### Query

  ```graphql
  mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
    orderCreate(order: $order, options: $options) {
      userErrors {
        field
        message
      }
      order {
        id
        displayFinancialStatus
        shippingAddress {
          lastName
          address1
          city
          provinceCode
          countryCode
          zip
        }
        billingAddress {
          lastName
          address1
          city
          provinceCode
          countryCode
          zip
        }
        customer {
          id
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "order": {
      "lineItems": [
        {
          "variantId": "gid://shopify/ProductVariant/43729076",
          "quantity": 1
        }
      ],
      "customer": {
        "toAssociate": {
          "id": "gid://shopify/Customer/544365967"
        }
      },
      "financialStatus": "PENDING",
      "shippingAddress": {
        "lastName": "James",
        "address1": "123 Main St",
        "city": "Ottawa",
        "countryCode": "CA",
        "provinceCode": "ON",
        "zip": "K1P 1J1"
      },
      "billingAddress": {
        "lastName": "James",
        "address1": "321 Secondary St",
        "city": "Ottawa",
        "countryCode": "CA",
        "provinceCode": "ON",
        "zip": "K1P 1J1"
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
  "query": "mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) { orderCreate(order: $order, options: $options) { userErrors { field message } order { id displayFinancialStatus shippingAddress { lastName address1 city provinceCode countryCode zip } billingAddress { lastName address1 city provinceCode countryCode zip } customer { id } } } }",
   "variables": {
      "order": {
        "lineItems": [
          {
            "variantId": "gid://shopify/ProductVariant/43729076",
            "quantity": 1
          }
        ],
        "customer": {
          "toAssociate": {
            "id": "gid://shopify/Customer/544365967"
          }
        },
        "financialStatus": "PENDING",
        "shippingAddress": {
          "lastName": "James",
          "address1": "123 Main St",
          "city": "Ottawa",
          "countryCode": "CA",
          "provinceCode": "ON",
          "zip": "K1P 1J1"
        },
        "billingAddress": {
          "lastName": "James",
          "address1": "321 Secondary St",
          "city": "Ottawa",
          "countryCode": "CA",
          "provinceCode": "ON",
          "zip": "K1P 1J1"
        }
      }
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
    mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
      orderCreate(order: $order, options: $options) {
        userErrors {
          field
          message
        }
        order {
          id
          displayFinancialStatus
          shippingAddress {
            lastName
            address1
            city
            provinceCode
            countryCode
            zip
          }
          billingAddress {
            lastName
            address1
            city
            provinceCode
            countryCode
            zip
          }
          customer {
            id
          }
        }
      }
    }`,
    {
      variables: {
          "order": {
              "lineItems": [
                  {
                      "variantId": "gid://shopify/ProductVariant/43729076",
                      "quantity": 1
                  }
              ],
              "customer": {
                  "toAssociate": {
                      "id": "gid://shopify/Customer/544365967"
                  }
              },
              "financialStatus": "PENDING",
              "shippingAddress": {
                  "lastName": "James",
                  "address1": "123 Main St",
                  "city": "Ottawa",
                  "countryCode": "CA",
                  "provinceCode": "ON",
                  "zip": "K1P 1J1"
              },
              "billingAddress": {
                  "lastName": "James",
                  "address1": "321 Secondary St",
                  "city": "Ottawa",
                  "countryCode": "CA",
                  "provinceCode": "ON",
                  "zip": "K1P 1J1"
              }
          }
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
    mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
      orderCreate(order: $order, options: $options) {
        userErrors {
          field
          message
        }
        order {
          id
          displayFinancialStatus
          shippingAddress {
            lastName
            address1
            city
            provinceCode
            countryCode
            zip
          }
          billingAddress {
            lastName
            address1
            city
            provinceCode
            countryCode
            zip
          }
          customer {
            id
          }
        }
      }
    }
  QUERY

  variables = {
    "order": {
      "lineItems": [
        {
          "variantId": "gid://shopify/ProductVariant/43729076",
          "quantity": 1
        }
      ],
      "customer": {
        "toAssociate": {
          "id": "gid://shopify/Customer/544365967"
        }
      },
      "financialStatus": "PENDING",
      "shippingAddress": {
        "lastName": "James",
        "address1": "123 Main St",
        "city": "Ottawa",
        "countryCode": "CA",
        "provinceCode": "ON",
        "zip": "K1P 1J1"
      },
      "billingAddress": {
        "lastName": "James",
        "address1": "321 Secondary St",
        "city": "Ottawa",
        "countryCode": "CA",
        "provinceCode": "ON",
        "zip": "K1P 1J1"
      }
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
        orderCreate(order: $order, options: $options) {
          userErrors {
            field
            message
          }
          order {
            id
            displayFinancialStatus
            shippingAddress {
              lastName
              address1
              city
              provinceCode
              countryCode
              zip
            }
            billingAddress {
              lastName
              address1
              city
              provinceCode
              countryCode
              zip
            }
            customer {
              id
            }
          }
        }
      }`,
      "variables": {
          "order": {
              "lineItems": [
                  {
                      "variantId": "gid://shopify/ProductVariant/43729076",
                      "quantity": 1
                  }
              ],
              "customer": {
                  "toAssociate": {
                      "id": "gid://shopify/Customer/544365967"
                  }
              },
              "financialStatus": "PENDING",
              "shippingAddress": {
                  "lastName": "James",
                  "address1": "123 Main St",
                  "city": "Ottawa",
                  "countryCode": "CA",
                  "provinceCode": "ON",
                  "zip": "K1P 1J1"
              },
              "billingAddress": {
                  "lastName": "James",
                  "address1": "321 Secondary St",
                  "city": "Ottawa",
                  "countryCode": "CA",
                  "provinceCode": "ON",
                  "zip": "K1P 1J1"
              }
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
    orderCreate(order: $order, options: $options) {
      userErrors {
        field
        message
      }
      order {
        id
        displayFinancialStatus
        shippingAddress {
          lastName
          address1
          city
          provinceCode
          countryCode
          zip
        }
        billingAddress {
          lastName
          address1
          city
          provinceCode
          countryCode
          zip
        }
        customer {
          id
        }
      }
    }
  }' \
  --variables \
  '{
    "order": {
      "lineItems": [
        {
          "variantId": "gid://shopify/ProductVariant/43729076",
          "quantity": 1
        }
      ],
      "customer": {
        "toAssociate": {
          "id": "gid://shopify/Customer/544365967"
        }
      },
      "financialStatus": "PENDING",
      "shippingAddress": {
        "lastName": "James",
        "address1": "123 Main St",
        "city": "Ottawa",
        "countryCode": "CA",
        "provinceCode": "ON",
        "zip": "K1P 1J1"
      },
      "billingAddress": {
        "lastName": "James",
        "address1": "321 Secondary St",
        "city": "Ottawa",
        "countryCode": "CA",
        "provinceCode": "ON",
        "zip": "K1P 1J1"
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "orderCreate": {
      "userErrors": [],
      "order": {
        "id": "gid://shopify/Order/1073459970",
        "displayFinancialStatus": "PENDING",
        "shippingAddress": {
          "lastName": "James",
          "address1": "123 Main St",
          "city": "Ottawa",
          "provinceCode": "ON",
          "countryCode": "CA",
          "zip": "K1P 1J1"
        },
        "billingAddress": {
          "lastName": "James",
          "address1": "321 Secondary St",
          "city": "Ottawa",
          "provinceCode": "ON",
          "countryCode": "CA",
          "zip": "K1P 1J1"
        },
        "customer": {
          "id": "gid://shopify/Customer/544365967"
        }
      }
    }
  }
  ```

* ### Create an order and send email confirmations

  #### Description

  This mutation creates an order with minimal fulfillment details. By setting the \`sendReceipt\` and \`sendFulfillmentReceipt\` options to \`true\`, the customer receives email confirmations for both the order and shipment.

  #### Query

  ```graphql
  mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
    orderCreate(order: $order, options: $options) {
      userErrors {
        field
        message
      }
      order {
        id
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "order": {
      "lineItems": [
        {
          "variantId": "gid://shopify/ProductVariant/43729076",
          "quantity": 1
        }
      ],
      "email": "foo@shopify.com",
      "fulfillmentStatus": "FULFILLED"
    },
    "options": {
      "sendReceipt": true,
      "sendFulfillmentReceipt": true
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
  "query": "mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) { orderCreate(order: $order, options: $options) { userErrors { field message } order { id } } }",
   "variables": {
      "order": {
        "lineItems": [
          {
            "variantId": "gid://shopify/ProductVariant/43729076",
            "quantity": 1
          }
        ],
        "email": "foo@shopify.com",
        "fulfillmentStatus": "FULFILLED"
      },
      "options": {
        "sendReceipt": true,
        "sendFulfillmentReceipt": true
      }
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
    mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
      orderCreate(order: $order, options: $options) {
        userErrors {
          field
          message
        }
        order {
          id
        }
      }
    }`,
    {
      variables: {
          "order": {
              "lineItems": [
                  {
                      "variantId": "gid://shopify/ProductVariant/43729076",
                      "quantity": 1
                  }
              ],
              "email": "foo@shopify.com",
              "fulfillmentStatus": "FULFILLED"
          },
          "options": {
              "sendReceipt": true,
              "sendFulfillmentReceipt": true
          }
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
    mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
      orderCreate(order: $order, options: $options) {
        userErrors {
          field
          message
        }
        order {
          id
        }
      }
    }
  QUERY

  variables = {
    "order": {
      "lineItems": [
        {
          "variantId": "gid://shopify/ProductVariant/43729076",
          "quantity": 1
        }
      ],
      "email": "foo@shopify.com",
      "fulfillmentStatus": "FULFILLED"
    },
    "options": {
      "sendReceipt": true,
      "sendFulfillmentReceipt": true
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
        orderCreate(order: $order, options: $options) {
          userErrors {
            field
            message
          }
          order {
            id
          }
        }
      }`,
      "variables": {
          "order": {
              "lineItems": [
                  {
                      "variantId": "gid://shopify/ProductVariant/43729076",
                      "quantity": 1
                  }
              ],
              "email": "foo@shopify.com",
              "fulfillmentStatus": "FULFILLED"
          },
          "options": {
              "sendReceipt": true,
              "sendFulfillmentReceipt": true
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
    orderCreate(order: $order, options: $options) {
      userErrors {
        field
        message
      }
      order {
        id
      }
    }
  }' \
  --variables \
  '{
    "order": {
      "lineItems": [
        {
          "variantId": "gid://shopify/ProductVariant/43729076",
          "quantity": 1
        }
      ],
      "email": "foo@shopify.com",
      "fulfillmentStatus": "FULFILLED"
    },
    "options": {
      "sendReceipt": true,
      "sendFulfillmentReceipt": true
    }
  }'
  ```

  #### Response

  ```json
  {
    "orderCreate": {
      "userErrors": [],
      "order": {
        "id": "gid://shopify/Order/1073459974"
      }
    }
  }
  ```

* ### Create an order using a product variant ID

  #### Description

  This mutation creates an order using the supplied ID of a product variant. The response includes the created order's ID and associated line items.

  #### Query

  ```graphql
  mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
    orderCreate(order: $order, options: $options) {
      userErrors {
        field
        message
      }
      order {
        id
        lineItems(first: 5) {
          nodes {
            id
            title
            quantity
            variant {
              id
            }
          }
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "order": {
      "lineItems": [
        {
          "variantId": "gid://shopify/ProductVariant/43729076",
          "quantity": 1
        }
      ]
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
  "query": "mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) { orderCreate(order: $order, options: $options) { userErrors { field message } order { id lineItems(first: 5) { nodes { id title quantity variant { id } } } } } }",
   "variables": {
      "order": {
        "lineItems": [
          {
            "variantId": "gid://shopify/ProductVariant/43729076",
            "quantity": 1
          }
        ]
      }
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
    mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
      orderCreate(order: $order, options: $options) {
        userErrors {
          field
          message
        }
        order {
          id
          lineItems(first: 5) {
            nodes {
              id
              title
              quantity
              variant {
                id
              }
            }
          }
        }
      }
    }`,
    {
      variables: {
          "order": {
              "lineItems": [
                  {
                      "variantId": "gid://shopify/ProductVariant/43729076",
                      "quantity": 1
                  }
              ]
          }
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
    mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
      orderCreate(order: $order, options: $options) {
        userErrors {
          field
          message
        }
        order {
          id
          lineItems(first: 5) {
            nodes {
              id
              title
              quantity
              variant {
                id
              }
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "order": {
      "lineItems": [
        {
          "variantId": "gid://shopify/ProductVariant/43729076",
          "quantity": 1
        }
      ]
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
        orderCreate(order: $order, options: $options) {
          userErrors {
            field
            message
          }
          order {
            id
            lineItems(first: 5) {
              nodes {
                id
                title
                quantity
                variant {
                  id
                }
              }
            }
          }
        }
      }`,
      "variables": {
          "order": {
              "lineItems": [
                  {
                      "variantId": "gid://shopify/ProductVariant/43729076",
                      "quantity": 1
                  }
              ]
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
    orderCreate(order: $order, options: $options) {
      userErrors {
        field
        message
      }
      order {
        id
        lineItems(first: 5) {
          nodes {
            id
            title
            quantity
            variant {
              id
            }
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "order": {
      "lineItems": [
        {
          "variantId": "gid://shopify/ProductVariant/43729076",
          "quantity": 1
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "orderCreate": {
      "userErrors": [],
      "order": {
        "id": "gid://shopify/Order/1073459975",
        "lineItems": {
          "nodes": [
            {
              "id": "gid://shopify/LineItem/1071823185",
              "title": "Draft",
              "quantity": 1,
              "variant": {
                "id": "gid://shopify/ProductVariant/43729076"
              }
            }
          ]
        }
      }
    }
  }
  ```

* ### Create an order with a fixed amount off discount

  #### Description

  This mutation creates an order with a \[fixed amount off discount]\(https://help.shopify.com/manual/discounts/discount-types/percentage-fixed-amount) that's applied on a cart and at checkout when a customer enters a code. The discount is applied in both the shop's currency (USD) and the presentment currency (CAD) to demonstrate support for handling multiple currencies.

  #### Query

  ```graphql
  mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
    orderCreate(order: $order, options: $options) {
      userErrors {
        field
        message
      }
      order {
        totalDiscountsSet {
          shopMoney {
            amount
            currencyCode
          }
          presentmentMoney {
            amount
            currencyCode
          }
        }
        discountCodes
        discountApplications(first: 5) {
          nodes {
            value {
              ... on MoneyV2 {
                amount
                currencyCode
              }
            }
          }
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "order": {
      "lineItems": [
        {
          "variantId": "gid://shopify/ProductVariant/43729076",
          "quantity": 1,
          "priceSet": {
            "shopMoney": {
              "amount": 100,
              "currencyCode": "USD"
            },
            "presentmentMoney": {
              "amount": 75,
              "currencyCode": "CAD"
            }
          }
        }
      ],
      "presentmentCurrency": "CAD",
      "discountCode": {
        "itemFixedDiscountCode": {
          "amountSet": {
            "shopMoney": {
              "amount": 5,
              "currencyCode": "USD"
            },
            "presentmentMoney": {
              "amount": 9,
              "currencyCode": "CAD"
            }
          },
          "code": "BESTSALE"
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
  "query": "mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) { orderCreate(order: $order, options: $options) { userErrors { field message } order { totalDiscountsSet { shopMoney { amount currencyCode } presentmentMoney { amount currencyCode } } discountCodes discountApplications(first: 5) { nodes { value { ... on MoneyV2 { amount currencyCode } } } } } } }",
   "variables": {
      "order": {
        "lineItems": [
          {
            "variantId": "gid://shopify/ProductVariant/43729076",
            "quantity": 1,
            "priceSet": {
              "shopMoney": {
                "amount": 100,
                "currencyCode": "USD"
              },
              "presentmentMoney": {
                "amount": 75,
                "currencyCode": "CAD"
              }
            }
          }
        ],
        "presentmentCurrency": "CAD",
        "discountCode": {
          "itemFixedDiscountCode": {
            "amountSet": {
              "shopMoney": {
                "amount": 5,
                "currencyCode": "USD"
              },
              "presentmentMoney": {
                "amount": 9,
                "currencyCode": "CAD"
              }
            },
            "code": "BESTSALE"
          }
        }
      }
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
    mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
      orderCreate(order: $order, options: $options) {
        userErrors {
          field
          message
        }
        order {
          totalDiscountsSet {
            shopMoney {
              amount
              currencyCode
            }
            presentmentMoney {
              amount
              currencyCode
            }
          }
          discountCodes
          discountApplications(first: 5) {
            nodes {
              value {
                ... on MoneyV2 {
                  amount
                  currencyCode
                }
              }
            }
          }
        }
      }
    }`,
    {
      variables: {
          "order": {
              "lineItems": [
                  {
                      "variantId": "gid://shopify/ProductVariant/43729076",
                      "quantity": 1,
                      "priceSet": {
                          "shopMoney": {
                              "amount": 100,
                              "currencyCode": "USD"
                          },
                          "presentmentMoney": {
                              "amount": 75,
                              "currencyCode": "CAD"
                          }
                      }
                  }
              ],
              "presentmentCurrency": "CAD",
              "discountCode": {
                  "itemFixedDiscountCode": {
                      "amountSet": {
                          "shopMoney": {
                              "amount": 5,
                              "currencyCode": "USD"
                          },
                          "presentmentMoney": {
                              "amount": 9,
                              "currencyCode": "CAD"
                          }
                      },
                      "code": "BESTSALE"
                  }
              }
          }
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
    mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
      orderCreate(order: $order, options: $options) {
        userErrors {
          field
          message
        }
        order {
          totalDiscountsSet {
            shopMoney {
              amount
              currencyCode
            }
            presentmentMoney {
              amount
              currencyCode
            }
          }
          discountCodes
          discountApplications(first: 5) {
            nodes {
              value {
                ... on MoneyV2 {
                  amount
                  currencyCode
                }
              }
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "order": {
      "lineItems": [
        {
          "variantId": "gid://shopify/ProductVariant/43729076",
          "quantity": 1,
          "priceSet": {
            "shopMoney": {
              "amount": 100,
              "currencyCode": "USD"
            },
            "presentmentMoney": {
              "amount": 75,
              "currencyCode": "CAD"
            }
          }
        }
      ],
      "presentmentCurrency": "CAD",
      "discountCode": {
        "itemFixedDiscountCode": {
          "amountSet": {
            "shopMoney": {
              "amount": 5,
              "currencyCode": "USD"
            },
            "presentmentMoney": {
              "amount": 9,
              "currencyCode": "CAD"
            }
          },
          "code": "BESTSALE"
        }
      }
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
        orderCreate(order: $order, options: $options) {
          userErrors {
            field
            message
          }
          order {
            totalDiscountsSet {
              shopMoney {
                amount
                currencyCode
              }
              presentmentMoney {
                amount
                currencyCode
              }
            }
            discountCodes
            discountApplications(first: 5) {
              nodes {
                value {
                  ... on MoneyV2 {
                    amount
                    currencyCode
                  }
                }
              }
            }
          }
        }
      }`,
      "variables": {
          "order": {
              "lineItems": [
                  {
                      "variantId": "gid://shopify/ProductVariant/43729076",
                      "quantity": 1,
                      "priceSet": {
                          "shopMoney": {
                              "amount": 100,
                              "currencyCode": "USD"
                          },
                          "presentmentMoney": {
                              "amount": 75,
                              "currencyCode": "CAD"
                          }
                      }
                  }
              ],
              "presentmentCurrency": "CAD",
              "discountCode": {
                  "itemFixedDiscountCode": {
                      "amountSet": {
                          "shopMoney": {
                              "amount": 5,
                              "currencyCode": "USD"
                          },
                          "presentmentMoney": {
                              "amount": 9,
                              "currencyCode": "CAD"
                          }
                      },
                      "code": "BESTSALE"
                  }
              }
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
    orderCreate(order: $order, options: $options) {
      userErrors {
        field
        message
      }
      order {
        totalDiscountsSet {
          shopMoney {
            amount
            currencyCode
          }
          presentmentMoney {
            amount
            currencyCode
          }
        }
        discountCodes
        discountApplications(first: 5) {
          nodes {
            value {
              ... on MoneyV2 {
                amount
                currencyCode
              }
            }
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "order": {
      "lineItems": [
        {
          "variantId": "gid://shopify/ProductVariant/43729076",
          "quantity": 1,
          "priceSet": {
            "shopMoney": {
              "amount": 100,
              "currencyCode": "USD"
            },
            "presentmentMoney": {
              "amount": 75,
              "currencyCode": "CAD"
            }
          }
        }
      ],
      "presentmentCurrency": "CAD",
      "discountCode": {
        "itemFixedDiscountCode": {
          "amountSet": {
            "shopMoney": {
              "amount": 5,
              "currencyCode": "USD"
            },
            "presentmentMoney": {
              "amount": 9,
              "currencyCode": "CAD"
            }
          },
          "code": "BESTSALE"
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "orderCreate": {
      "userErrors": [],
      "order": {
        "totalDiscountsSet": {
          "shopMoney": {
            "amount": "5.0",
            "currencyCode": "USD"
          },
          "presentmentMoney": {
            "amount": "9.0",
            "currencyCode": "CAD"
          }
        },
        "discountCodes": [
          "BESTSALE"
        ],
        "discountApplications": {
          "nodes": [
            {
              "value": {
                "amount": "5.0",
                "currencyCode": "USD"
              }
            }
          ]
        }
      }
    }
  }
  ```

* ### Create an order with a percentage discount

  #### Description

  This mutation creates an order with a \[percentage discount]\(https://help.shopify.com/manual/discounts/discount-types/percentage-fixed-amount) that's applied on a cart and at checkout when a customer enters a code.

  #### Query

  ```graphql
  mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
    orderCreate(order: $order, options: $options) {
      userErrors {
        field
        message
      }
      order {
        totalDiscountsSet {
          shopMoney {
            amount
            currencyCode
          }
          presentmentMoney {
            amount
            currencyCode
          }
        }
        discountCodes
        discountApplications(first: 5) {
          nodes {
            value {
              ... on MoneyV2 {
                amount
                currencyCode
              }
              ... on PricingPercentageValue {
                percentage
              }
            }
          }
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "order": {
      "lineItems": [
        {
          "variantId": "gid://shopify/ProductVariant/43729076",
          "quantity": 1
        }
      ],
      "discountCode": {
        "itemPercentageDiscountCode": {
          "percentage": 10,
          "code": "SUMMER SALE"
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
  "query": "mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) { orderCreate(order: $order, options: $options) { userErrors { field message } order { totalDiscountsSet { shopMoney { amount currencyCode } presentmentMoney { amount currencyCode } } discountCodes discountApplications(first: 5) { nodes { value { ... on MoneyV2 { amount currencyCode } ... on PricingPercentageValue { percentage } } } } } } }",
   "variables": {
      "order": {
        "lineItems": [
          {
            "variantId": "gid://shopify/ProductVariant/43729076",
            "quantity": 1
          }
        ],
        "discountCode": {
          "itemPercentageDiscountCode": {
            "percentage": 10,
            "code": "SUMMER SALE"
          }
        }
      }
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
    mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
      orderCreate(order: $order, options: $options) {
        userErrors {
          field
          message
        }
        order {
          totalDiscountsSet {
            shopMoney {
              amount
              currencyCode
            }
            presentmentMoney {
              amount
              currencyCode
            }
          }
          discountCodes
          discountApplications(first: 5) {
            nodes {
              value {
                ... on MoneyV2 {
                  amount
                  currencyCode
                }
                ... on PricingPercentageValue {
                  percentage
                }
              }
            }
          }
        }
      }
    }`,
    {
      variables: {
          "order": {
              "lineItems": [
                  {
                      "variantId": "gid://shopify/ProductVariant/43729076",
                      "quantity": 1
                  }
              ],
              "discountCode": {
                  "itemPercentageDiscountCode": {
                      "percentage": 10,
                      "code": "SUMMER SALE"
                  }
              }
          }
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
    mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
      orderCreate(order: $order, options: $options) {
        userErrors {
          field
          message
        }
        order {
          totalDiscountsSet {
            shopMoney {
              amount
              currencyCode
            }
            presentmentMoney {
              amount
              currencyCode
            }
          }
          discountCodes
          discountApplications(first: 5) {
            nodes {
              value {
                ... on MoneyV2 {
                  amount
                  currencyCode
                }
                ... on PricingPercentageValue {
                  percentage
                }
              }
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "order": {
      "lineItems": [
        {
          "variantId": "gid://shopify/ProductVariant/43729076",
          "quantity": 1
        }
      ],
      "discountCode": {
        "itemPercentageDiscountCode": {
          "percentage": 10,
          "code": "SUMMER SALE"
        }
      }
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
        orderCreate(order: $order, options: $options) {
          userErrors {
            field
            message
          }
          order {
            totalDiscountsSet {
              shopMoney {
                amount
                currencyCode
              }
              presentmentMoney {
                amount
                currencyCode
              }
            }
            discountCodes
            discountApplications(first: 5) {
              nodes {
                value {
                  ... on MoneyV2 {
                    amount
                    currencyCode
                  }
                  ... on PricingPercentageValue {
                    percentage
                  }
                }
              }
            }
          }
        }
      }`,
      "variables": {
          "order": {
              "lineItems": [
                  {
                      "variantId": "gid://shopify/ProductVariant/43729076",
                      "quantity": 1
                  }
              ],
              "discountCode": {
                  "itemPercentageDiscountCode": {
                      "percentage": 10,
                      "code": "SUMMER SALE"
                  }
              }
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
    orderCreate(order: $order, options: $options) {
      userErrors {
        field
        message
      }
      order {
        totalDiscountsSet {
          shopMoney {
            amount
            currencyCode
          }
          presentmentMoney {
            amount
            currencyCode
          }
        }
        discountCodes
        discountApplications(first: 5) {
          nodes {
            value {
              ... on MoneyV2 {
                amount
                currencyCode
              }
              ... on PricingPercentageValue {
                percentage
              }
            }
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "order": {
      "lineItems": [
        {
          "variantId": "gid://shopify/ProductVariant/43729076",
          "quantity": 1
        }
      ],
      "discountCode": {
        "itemPercentageDiscountCode": {
          "percentage": 10,
          "code": "SUMMER SALE"
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "orderCreate": {
      "userErrors": [],
      "order": {
        "totalDiscountsSet": {
          "shopMoney": {
            "amount": "1.0",
            "currencyCode": "USD"
          },
          "presentmentMoney": {
            "amount": "1.0",
            "currencyCode": "USD"
          }
        },
        "discountCodes": [
          "SUMMER SALE"
        ],
        "discountApplications": {
          "nodes": [
            {
              "value": {
                "percentage": 10
              }
            }
          ]
        }
      }
    }
  }
  ```

* ### Create an order with fulfillment details

  #### Description

  This mutation creates an order with \[fulfillment]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/Fulfillment) details, including the shipping address and tracking information. The \`notifyCustomer\` field is set to \`true\` to send an email notification to the customer about the shipment.

  #### Query

  ```graphql
  mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
    orderCreate(order: $order, options: $options) {
      userErrors {
        field
        message
      }
      order {
        id
        fulfillments(first: 5) {
          id
          status
          location {
            id
          }
          originAddress {
            address1
            city
            countryCode
            provinceCode
            zip
          }
          trackingInfo {
            company
            number
          }
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "order": {
      "lineItems": [
        {
          "variantId": "gid://shopify/ProductVariant/43729076",
          "quantity": 1
        }
      ],
      "fulfillment": {
        "locationId": "gid://shopify/Location/124656943",
        "originAddress": {
          "address1": "123 Main St",
          "city": "Ottawa",
          "countryCode": "CA",
          "provinceCode": "ON",
          "zip": "K1P 1J1"
        },
        "trackingCompany": "Canada Post",
        "trackingNumber": "1234567890",
        "shipmentStatus": "DELIVERED",
        "notifyCustomer": true
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
  "query": "mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) { orderCreate(order: $order, options: $options) { userErrors { field message } order { id fulfillments(first: 5) { id status location { id } originAddress { address1 city countryCode provinceCode zip } trackingInfo { company number } } } } }",
   "variables": {
      "order": {
        "lineItems": [
          {
            "variantId": "gid://shopify/ProductVariant/43729076",
            "quantity": 1
          }
        ],
        "fulfillment": {
          "locationId": "gid://shopify/Location/124656943",
          "originAddress": {
            "address1": "123 Main St",
            "city": "Ottawa",
            "countryCode": "CA",
            "provinceCode": "ON",
            "zip": "K1P 1J1"
          },
          "trackingCompany": "Canada Post",
          "trackingNumber": "1234567890",
          "shipmentStatus": "DELIVERED",
          "notifyCustomer": true
        }
      }
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
    mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
      orderCreate(order: $order, options: $options) {
        userErrors {
          field
          message
        }
        order {
          id
          fulfillments(first: 5) {
            id
            status
            location {
              id
            }
            originAddress {
              address1
              city
              countryCode
              provinceCode
              zip
            }
            trackingInfo {
              company
              number
            }
          }
        }
      }
    }`,
    {
      variables: {
          "order": {
              "lineItems": [
                  {
                      "variantId": "gid://shopify/ProductVariant/43729076",
                      "quantity": 1
                  }
              ],
              "fulfillment": {
                  "locationId": "gid://shopify/Location/124656943",
                  "originAddress": {
                      "address1": "123 Main St",
                      "city": "Ottawa",
                      "countryCode": "CA",
                      "provinceCode": "ON",
                      "zip": "K1P 1J1"
                  },
                  "trackingCompany": "Canada Post",
                  "trackingNumber": "1234567890",
                  "shipmentStatus": "DELIVERED",
                  "notifyCustomer": true
              }
          }
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
    mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
      orderCreate(order: $order, options: $options) {
        userErrors {
          field
          message
        }
        order {
          id
          fulfillments(first: 5) {
            id
            status
            location {
              id
            }
            originAddress {
              address1
              city
              countryCode
              provinceCode
              zip
            }
            trackingInfo {
              company
              number
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "order": {
      "lineItems": [
        {
          "variantId": "gid://shopify/ProductVariant/43729076",
          "quantity": 1
        }
      ],
      "fulfillment": {
        "locationId": "gid://shopify/Location/124656943",
        "originAddress": {
          "address1": "123 Main St",
          "city": "Ottawa",
          "countryCode": "CA",
          "provinceCode": "ON",
          "zip": "K1P 1J1"
        },
        "trackingCompany": "Canada Post",
        "trackingNumber": "1234567890",
        "shipmentStatus": "DELIVERED",
        "notifyCustomer": true
      }
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
        orderCreate(order: $order, options: $options) {
          userErrors {
            field
            message
          }
          order {
            id
            fulfillments(first: 5) {
              id
              status
              location {
                id
              }
              originAddress {
                address1
                city
                countryCode
                provinceCode
                zip
              }
              trackingInfo {
                company
                number
              }
            }
          }
        }
      }`,
      "variables": {
          "order": {
              "lineItems": [
                  {
                      "variantId": "gid://shopify/ProductVariant/43729076",
                      "quantity": 1
                  }
              ],
              "fulfillment": {
                  "locationId": "gid://shopify/Location/124656943",
                  "originAddress": {
                      "address1": "123 Main St",
                      "city": "Ottawa",
                      "countryCode": "CA",
                      "provinceCode": "ON",
                      "zip": "K1P 1J1"
                  },
                  "trackingCompany": "Canada Post",
                  "trackingNumber": "1234567890",
                  "shipmentStatus": "DELIVERED",
                  "notifyCustomer": true
              }
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
    orderCreate(order: $order, options: $options) {
      userErrors {
        field
        message
      }
      order {
        id
        fulfillments(first: 5) {
          id
          status
          location {
            id
          }
          originAddress {
            address1
            city
            countryCode
            provinceCode
            zip
          }
          trackingInfo {
            company
            number
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "order": {
      "lineItems": [
        {
          "variantId": "gid://shopify/ProductVariant/43729076",
          "quantity": 1
        }
      ],
      "fulfillment": {
        "locationId": "gid://shopify/Location/124656943",
        "originAddress": {
          "address1": "123 Main St",
          "city": "Ottawa",
          "countryCode": "CA",
          "provinceCode": "ON",
          "zip": "K1P 1J1"
        },
        "trackingCompany": "Canada Post",
        "trackingNumber": "1234567890",
        "shipmentStatus": "DELIVERED",
        "notifyCustomer": true
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "orderCreate": {
      "userErrors": [],
      "order": {
        "id": "gid://shopify/Order/1073459978",
        "fulfillments": [
          {
            "id": "gid://shopify/Fulfillment/1069019871",
            "status": "SUCCESS",
            "location": {
              "id": "gid://shopify/Location/124656943"
            },
            "originAddress": {
              "address1": "123 Main St",
              "city": "Ottawa",
              "countryCode": "CA",
              "provinceCode": "ON",
              "zip": "K1P 1J1"
            },
            "trackingInfo": [
              {
                "company": "Canada Post",
                "number": "1234567890"
              }
            ]
          }
        ]
      }
    }
  }
  ```

* ### Create an order with tax lines

  #### Description

  This mutation creates an order with \[tax lines]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/TaxLine). The order has a mix of taxable and non-taxable line items, and the total tax amount is split among the taxable line items proportionally based on price.

  #### Query

  ```graphql
  mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
    orderCreate(order: $order, options: $options) {
      userErrors {
        field
        message
      }
      order {
        id
        totalTaxSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        lineItems(first: 5) {
          nodes {
            id
            title
            quantity
            variant {
              id
            }
            taxLines {
              title
              rate
              priceSet {
                shopMoney {
                  amount
                  currencyCode
                }
              }
            }
          }
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "order": {
      "lineItems": [
        {
          "title": "Red Leather Coat",
          "priceSet": {
            "shopMoney": {
              "amount": 129.99,
              "currencyCode": "USD"
            }
          },
          "quantity": 1
        },
        {
          "title": "Blue Suede Shoes",
          "priceSet": {
            "shopMoney": {
              "amount": 85.95,
              "currencyCode": "USD"
            }
          },
          "quantity": 1,
          "taxable": false
        },
        {
          "title": "Raspberry Beret",
          "priceSet": {
            "shopMoney": {
              "amount": 19.99,
              "currencyCode": "USD"
            }
          },
          "quantity": 2
        }
      ],
      "taxLines": [
        {
          "priceSet": {
            "shopMoney": {
              "amount": 10.2,
              "currencyCode": "USD"
            }
          },
          "title": "State tax",
          "rate": 0.04
        },
        {
          "priceSet": {
            "shopMoney": {
              "amount": 4.25,
              "currencyCode": "USD"
            }
          },
          "title": "County tax",
          "rate": 0.02
        }
      ]
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
  "query": "mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) { orderCreate(order: $order, options: $options) { userErrors { field message } order { id totalTaxSet { shopMoney { amount currencyCode } } lineItems(first: 5) { nodes { id title quantity variant { id } taxLines { title rate priceSet { shopMoney { amount currencyCode } } } } } } } }",
   "variables": {
      "order": {
        "lineItems": [
          {
            "title": "Red Leather Coat",
            "priceSet": {
              "shopMoney": {
                "amount": 129.99,
                "currencyCode": "USD"
              }
            },
            "quantity": 1
          },
          {
            "title": "Blue Suede Shoes",
            "priceSet": {
              "shopMoney": {
                "amount": 85.95,
                "currencyCode": "USD"
              }
            },
            "quantity": 1,
            "taxable": false
          },
          {
            "title": "Raspberry Beret",
            "priceSet": {
              "shopMoney": {
                "amount": 19.99,
                "currencyCode": "USD"
              }
            },
            "quantity": 2
          }
        ],
        "taxLines": [
          {
            "priceSet": {
              "shopMoney": {
                "amount": 10.2,
                "currencyCode": "USD"
              }
            },
            "title": "State tax",
            "rate": 0.04
          },
          {
            "priceSet": {
              "shopMoney": {
                "amount": 4.25,
                "currencyCode": "USD"
              }
            },
            "title": "County tax",
            "rate": 0.02
          }
        ]
      }
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
    mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
      orderCreate(order: $order, options: $options) {
        userErrors {
          field
          message
        }
        order {
          id
          totalTaxSet {
            shopMoney {
              amount
              currencyCode
            }
          }
          lineItems(first: 5) {
            nodes {
              id
              title
              quantity
              variant {
                id
              }
              taxLines {
                title
                rate
                priceSet {
                  shopMoney {
                    amount
                    currencyCode
                  }
                }
              }
            }
          }
        }
      }
    }`,
    {
      variables: {
          "order": {
              "lineItems": [
                  {
                      "title": "Red Leather Coat",
                      "priceSet": {
                          "shopMoney": {
                              "amount": 129.99,
                              "currencyCode": "USD"
                          }
                      },
                      "quantity": 1
                  },
                  {
                      "title": "Blue Suede Shoes",
                      "priceSet": {
                          "shopMoney": {
                              "amount": 85.95,
                              "currencyCode": "USD"
                          }
                      },
                      "quantity": 1,
                      "taxable": false
                  },
                  {
                      "title": "Raspberry Beret",
                      "priceSet": {
                          "shopMoney": {
                              "amount": 19.99,
                              "currencyCode": "USD"
                          }
                      },
                      "quantity": 2
                  }
              ],
              "taxLines": [
                  {
                      "priceSet": {
                          "shopMoney": {
                              "amount": 10.2,
                              "currencyCode": "USD"
                          }
                      },
                      "title": "State tax",
                      "rate": 0.04
                  },
                  {
                      "priceSet": {
                          "shopMoney": {
                              "amount": 4.25,
                              "currencyCode": "USD"
                          }
                      },
                      "title": "County tax",
                      "rate": 0.02
                  }
              ]
          }
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
    mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
      orderCreate(order: $order, options: $options) {
        userErrors {
          field
          message
        }
        order {
          id
          totalTaxSet {
            shopMoney {
              amount
              currencyCode
            }
          }
          lineItems(first: 5) {
            nodes {
              id
              title
              quantity
              variant {
                id
              }
              taxLines {
                title
                rate
                priceSet {
                  shopMoney {
                    amount
                    currencyCode
                  }
                }
              }
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "order": {
      "lineItems": [
        {
          "title": "Red Leather Coat",
          "priceSet": {
            "shopMoney": {
              "amount": 129.99,
              "currencyCode": "USD"
            }
          },
          "quantity": 1
        },
        {
          "title": "Blue Suede Shoes",
          "priceSet": {
            "shopMoney": {
              "amount": 85.95,
              "currencyCode": "USD"
            }
          },
          "quantity": 1,
          "taxable": false
        },
        {
          "title": "Raspberry Beret",
          "priceSet": {
            "shopMoney": {
              "amount": 19.99,
              "currencyCode": "USD"
            }
          },
          "quantity": 2
        }
      ],
      "taxLines": [
        {
          "priceSet": {
            "shopMoney": {
              "amount": 10.2,
              "currencyCode": "USD"
            }
          },
          "title": "State tax",
          "rate": 0.04
        },
        {
          "priceSet": {
            "shopMoney": {
              "amount": 4.25,
              "currencyCode": "USD"
            }
          },
          "title": "County tax",
          "rate": 0.02
        }
      ]
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
        orderCreate(order: $order, options: $options) {
          userErrors {
            field
            message
          }
          order {
            id
            totalTaxSet {
              shopMoney {
                amount
                currencyCode
              }
            }
            lineItems(first: 5) {
              nodes {
                id
                title
                quantity
                variant {
                  id
                }
                taxLines {
                  title
                  rate
                  priceSet {
                    shopMoney {
                      amount
                      currencyCode
                    }
                  }
                }
              }
            }
          }
        }
      }`,
      "variables": {
          "order": {
              "lineItems": [
                  {
                      "title": "Red Leather Coat",
                      "priceSet": {
                          "shopMoney": {
                              "amount": 129.99,
                              "currencyCode": "USD"
                          }
                      },
                      "quantity": 1
                  },
                  {
                      "title": "Blue Suede Shoes",
                      "priceSet": {
                          "shopMoney": {
                              "amount": 85.95,
                              "currencyCode": "USD"
                          }
                      },
                      "quantity": 1,
                      "taxable": false
                  },
                  {
                      "title": "Raspberry Beret",
                      "priceSet": {
                          "shopMoney": {
                              "amount": 19.99,
                              "currencyCode": "USD"
                          }
                      },
                      "quantity": 2
                  }
              ],
              "taxLines": [
                  {
                      "priceSet": {
                          "shopMoney": {
                              "amount": 10.2,
                              "currencyCode": "USD"
                          }
                      },
                      "title": "State tax",
                      "rate": 0.04
                  },
                  {
                      "priceSet": {
                          "shopMoney": {
                              "amount": 4.25,
                              "currencyCode": "USD"
                          }
                      },
                      "title": "County tax",
                      "rate": 0.02
                  }
              ]
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
    orderCreate(order: $order, options: $options) {
      userErrors {
        field
        message
      }
      order {
        id
        totalTaxSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        lineItems(first: 5) {
          nodes {
            id
            title
            quantity
            variant {
              id
            }
            taxLines {
              title
              rate
              priceSet {
                shopMoney {
                  amount
                  currencyCode
                }
              }
            }
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "order": {
      "lineItems": [
        {
          "title": "Red Leather Coat",
          "priceSet": {
            "shopMoney": {
              "amount": 129.99,
              "currencyCode": "USD"
            }
          },
          "quantity": 1
        },
        {
          "title": "Blue Suede Shoes",
          "priceSet": {
            "shopMoney": {
              "amount": 85.95,
              "currencyCode": "USD"
            }
          },
          "quantity": 1,
          "taxable": false
        },
        {
          "title": "Raspberry Beret",
          "priceSet": {
            "shopMoney": {
              "amount": 19.99,
              "currencyCode": "USD"
            }
          },
          "quantity": 2
        }
      ],
      "taxLines": [
        {
          "priceSet": {
            "shopMoney": {
              "amount": 10.2,
              "currencyCode": "USD"
            }
          },
          "title": "State tax",
          "rate": 0.04
        },
        {
          "priceSet": {
            "shopMoney": {
              "amount": 4.25,
              "currencyCode": "USD"
            }
          },
          "title": "County tax",
          "rate": 0.02
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "orderCreate": {
      "userErrors": [],
      "order": {
        "id": "gid://shopify/Order/1073459977",
        "totalTaxSet": {
          "shopMoney": {
            "amount": "14.45",
            "currencyCode": "USD"
          }
        },
        "lineItems": {
          "nodes": [
            {
              "id": "gid://shopify/LineItem/1071823187",
              "title": "Red Leather Coat",
              "quantity": 1,
              "variant": null,
              "taxLines": [
                {
                  "title": "State tax",
                  "rate": 0.04,
                  "priceSet": {
                    "shopMoney": {
                      "amount": "7.81",
                      "currencyCode": "USD"
                    }
                  }
                },
                {
                  "title": "County tax",
                  "rate": 0.02,
                  "priceSet": {
                    "shopMoney": {
                      "amount": "3.26",
                      "currencyCode": "USD"
                    }
                  }
                }
              ]
            },
            {
              "id": "gid://shopify/LineItem/1071823188",
              "title": "Blue Suede Shoes",
              "quantity": 1,
              "variant": null,
              "taxLines": []
            },
            {
              "id": "gid://shopify/LineItem/1071823189",
              "title": "Raspberry Beret",
              "quantity": 2,
              "variant": null,
              "taxLines": [
                {
                  "title": "State tax",
                  "rate": 0.04,
                  "priceSet": {
                    "shopMoney": {
                      "amount": "2.39",
                      "currencyCode": "USD"
                    }
                  }
                },
                {
                  "title": "County tax",
                  "rate": 0.02,
                  "priceSet": {
                    "shopMoney": {
                      "amount": "0.99",
                      "currencyCode": "USD"
                    }
                  }
                }
              ]
            }
          ]
        }
      }
    }
  }
  ```

* ### Create an order without sending email confirmations

  #### Description

  This mutation creates an order with minimal fulfillment details. The \`sendReceipt\` and \`sendFulfillmentReceipt\` options aren't included in the request, so the customer doesn't receive any email confirmations for the order or shipment.

  #### Query

  ```graphql
  mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
    orderCreate(order: $order, options: $options) {
      userErrors {
        field
        message
      }
      order {
        id
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "order": {
      "lineItems": [
        {
          "variantId": "gid://shopify/ProductVariant/43729076",
          "quantity": 1
        }
      ],
      "email": "foo@shopify.com",
      "fulfillmentStatus": "FULFILLED"
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
  "query": "mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) { orderCreate(order: $order, options: $options) { userErrors { field message } order { id } } }",
   "variables": {
      "order": {
        "lineItems": [
          {
            "variantId": "gid://shopify/ProductVariant/43729076",
            "quantity": 1
          }
        ],
        "email": "foo@shopify.com",
        "fulfillmentStatus": "FULFILLED"
      }
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
    mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
      orderCreate(order: $order, options: $options) {
        userErrors {
          field
          message
        }
        order {
          id
        }
      }
    }`,
    {
      variables: {
          "order": {
              "lineItems": [
                  {
                      "variantId": "gid://shopify/ProductVariant/43729076",
                      "quantity": 1
                  }
              ],
              "email": "foo@shopify.com",
              "fulfillmentStatus": "FULFILLED"
          }
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
    mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
      orderCreate(order: $order, options: $options) {
        userErrors {
          field
          message
        }
        order {
          id
        }
      }
    }
  QUERY

  variables = {
    "order": {
      "lineItems": [
        {
          "variantId": "gid://shopify/ProductVariant/43729076",
          "quantity": 1
        }
      ],
      "email": "foo@shopify.com",
      "fulfillmentStatus": "FULFILLED"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
        orderCreate(order: $order, options: $options) {
          userErrors {
            field
            message
          }
          order {
            id
          }
        }
      }`,
      "variables": {
          "order": {
              "lineItems": [
                  {
                      "variantId": "gid://shopify/ProductVariant/43729076",
                      "quantity": 1
                  }
              ],
              "email": "foo@shopify.com",
              "fulfillmentStatus": "FULFILLED"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
    orderCreate(order: $order, options: $options) {
      userErrors {
        field
        message
      }
      order {
        id
      }
    }
  }' \
  --variables \
  '{
    "order": {
      "lineItems": [
        {
          "variantId": "gid://shopify/ProductVariant/43729076",
          "quantity": 1
        }
      ],
      "email": "foo@shopify.com",
      "fulfillmentStatus": "FULFILLED"
    }
  }'
  ```

  #### Response

  ```json
  {
    "orderCreate": {
      "userErrors": [],
      "order": {
        "id": "gid://shopify/Order/1073459969"
      }
    }
  }
  ```

* ### orderCreate reference
