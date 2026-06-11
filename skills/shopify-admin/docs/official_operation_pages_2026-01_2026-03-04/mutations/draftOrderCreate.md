---
title: draftOrderCreate - GraphQL Admin
description: >-
  Creates a [draft
  order](https://shopify.dev/docs/api/admin-graphql/latest/objects/DraftOrder)

  with attributes such as customer information, line items, shipping and billing
  addresses, and payment terms.

  Draft orders are useful for merchants that need to:


  - Create new orders for sales made by phone, in person, by chat, or elsewhere.
  When a merchant accepts payment for a draft order, an order is created.

  - Send invoices to customers with a secure checkout link.

  - Use custom items to represent additional costs or products not in inventory.

  - Re-create orders manually from active sales channels.

  - Sell products at discount or wholesale rates.

  - Take pre-orders.


  After creating a draft order, you can:

  - Send an invoice to the customer using the
  [`draftOrderInvoiceSend`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderInvoiceSend)
  mutation.

  - Complete the draft order using the
  [`draftOrderComplete`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderComplete)
  mutation.

  - Update the draft order using the
  [`draftOrderUpdate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderUpdate)
  mutation.

  - Duplicate a draft order using the
  [`draftOrderDuplicate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderDuplicate)
  mutation.

  - Delete the draft order using the
  [`draftOrderDelete`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderDelete)
  mutation.


  > Note:

  > When you create a draft order, you can't [reserve or hold
  inventory](https://shopify.dev/docs/apps/build/orders-fulfillment/inventory-management-apps#inventory-states)
  for the items in the order by default.

  > However, you can reserve inventory using the
  [`reserveInventoryUntil`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderCreate#arguments-input.fields.reserveInventoryUntil)
  input.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderCreate'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderCreate.md
---

# draft​Order​Create

mutation

Requires `write_draft_orders` access scope or `write_quick_sale` access scope. Also: The user must have access to manage draft orders.

Creates a [draft order](https://shopify.dev/docs/api/admin-graphql/latest/objects/DraftOrder) with attributes such as customer information, line items, shipping and billing addresses, and payment terms. Draft orders are useful for merchants that need to:

* Create new orders for sales made by phone, in person, by chat, or elsewhere. When a merchant accepts payment for a draft order, an order is created.
* Send invoices to customers with a secure checkout link.
* Use custom items to represent additional costs or products not in inventory.
* Re-create orders manually from active sales channels.
* Sell products at discount or wholesale rates.
* Take pre-orders.

After creating a draft order, you can:

* Send an invoice to the customer using the [`draftOrderInvoiceSend`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderInvoiceSend) mutation.
* Complete the draft order using the [`draftOrderComplete`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderComplete) mutation.
* Update the draft order using the [`draftOrderUpdate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderUpdate) mutation.
* Duplicate a draft order using the [`draftOrderDuplicate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderDuplicate) mutation.
* Delete the draft order using the [`draftOrderDelete`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderDelete) mutation.

***

**Note:** When you create a draft order, you can\&#39;t \<a href="https://shopify.dev/docs/apps/build/orders-fulfillment/inventory-management-apps#inventory-states">reserve or hold inventory\</a> for the items in the order by default. However, you can reserve inventory using the \<a href="https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderCreate#arguments-input.fields.reserveInventoryUntil">\<code>\<span class="PreventFireFoxApplyingGapToWBR">reserve\<wbr/>Inventory\<wbr/>Until\</span>\</code>\</a> input.

***

## Arguments

* input

  [Draft​Order​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/DraftOrderInput)

  required

  The fields used to create the draft order.

***

## Draft​Order​Create​Payload returns

* draft​Order

  [Draft​Order](https://shopify.dev/docs/api/admin-graphql/latest/objects/DraftOrder)

  The created draft order.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create a draft order

  #### Description

  Create a draft order that combines custom line items with existing products from your store. This example demonstrates creating custom products with manual pricing alongside actual products from your store inventory, using the \[\`appliedDiscount\`]\(https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderCreate#arguments-input.fields.appliedDiscount) field at both the order level and line-item level. Learn more about \[custom attributes]\(https://shopify.dev/docs/apps/build/custom-data/metafields/manage-metafields).

  #### Query

  ```graphql
  mutation draftOrderCreate($input: DraftOrderInput!) {
    draftOrderCreate(input: $input) {
      draftOrder {
        id
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "note": "Test draft order",
      "email": "test.user@shopify.com",
      "taxExempt": true,
      "tags": [
        "foo",
        "bar"
      ],
      "shippingLine": {
        "title": "Custom Shipping",
        "price": 4.55
      },
      "shippingAddress": {
        "address1": "123 Main St",
        "city": "Waterloo",
        "province": "Ontario",
        "country": "Canada",
        "zip": "A1A 1A1"
      },
      "billingAddress": {
        "address1": "456 Main St",
        "city": "Toronto",
        "province": "Ontario",
        "country": "Canada",
        "zip": "Z9Z 9Z9"
      },
      "appliedDiscount": {
        "description": "damaged",
        "value": 5,
        "amount": 5,
        "valueType": "FIXED_AMOUNT",
        "title": "Custom"
      },
      "lineItems": [
        {
          "title": "Custom product",
          "originalUnitPrice": 14.99,
          "quantity": 5,
          "appliedDiscount": {
            "description": "wholesale",
            "value": 5,
            "amount": 3.74,
            "valueType": "PERCENTAGE",
            "title": "Fancy"
          },
          "weight": {
            "value": 1,
            "unit": "KILOGRAMS"
          },
          "customAttributes": [
            {
              "key": "color",
              "value": "Gold"
            },
            {
              "key": "material",
              "value": "Plastic"
            }
          ]
        },
        {
          "variantId": "gid://shopify/ProductVariant/43729076",
          "quantity": 2
        }
      ],
      "customAttributes": [
        {
          "key": "name",
          "value": "Achilles"
        },
        {
          "key": "city",
          "value": "Troy"
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
  "query": "mutation draftOrderCreate($input: DraftOrderInput!) { draftOrderCreate(input: $input) { draftOrder { id } } }",
   "variables": {
      "input": {
        "note": "Test draft order",
        "email": "test.user@shopify.com",
        "taxExempt": true,
        "tags": [
          "foo",
          "bar"
        ],
        "shippingLine": {
          "title": "Custom Shipping",
          "price": 4.55
        },
        "shippingAddress": {
          "address1": "123 Main St",
          "city": "Waterloo",
          "province": "Ontario",
          "country": "Canada",
          "zip": "A1A 1A1"
        },
        "billingAddress": {
          "address1": "456 Main St",
          "city": "Toronto",
          "province": "Ontario",
          "country": "Canada",
          "zip": "Z9Z 9Z9"
        },
        "appliedDiscount": {
          "description": "damaged",
          "value": 5,
          "amount": 5,
          "valueType": "FIXED_AMOUNT",
          "title": "Custom"
        },
        "lineItems": [
          {
            "title": "Custom product",
            "originalUnitPrice": 14.99,
            "quantity": 5,
            "appliedDiscount": {
              "description": "wholesale",
              "value": 5,
              "amount": 3.74,
              "valueType": "PERCENTAGE",
              "title": "Fancy"
            },
            "weight": {
              "value": 1,
              "unit": "KILOGRAMS"
            },
            "customAttributes": [
              {
                "key": "color",
                "value": "Gold"
              },
              {
                "key": "material",
                "value": "Plastic"
              }
            ]
          },
          {
            "variantId": "gid://shopify/ProductVariant/43729076",
            "quantity": 2
          }
        ],
        "customAttributes": [
          {
            "key": "name",
            "value": "Achilles"
          },
          {
            "key": "city",
            "value": "Troy"
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
    mutation draftOrderCreate($input: DraftOrderInput!) {
      draftOrderCreate(input: $input) {
        draftOrder {
          id
        }
      }
    }`,
    {
      variables: {
          "input": {
              "note": "Test draft order",
              "email": "test.user@shopify.com",
              "taxExempt": true,
              "tags": [
                  "foo",
                  "bar"
              ],
              "shippingLine": {
                  "title": "Custom Shipping",
                  "price": 4.55
              },
              "shippingAddress": {
                  "address1": "123 Main St",
                  "city": "Waterloo",
                  "province": "Ontario",
                  "country": "Canada",
                  "zip": "A1A 1A1"
              },
              "billingAddress": {
                  "address1": "456 Main St",
                  "city": "Toronto",
                  "province": "Ontario",
                  "country": "Canada",
                  "zip": "Z9Z 9Z9"
              },
              "appliedDiscount": {
                  "description": "damaged",
                  "value": 5,
                  "amount": 5,
                  "valueType": "FIXED_AMOUNT",
                  "title": "Custom"
              },
              "lineItems": [
                  {
                      "title": "Custom product",
                      "originalUnitPrice": 14.99,
                      "quantity": 5,
                      "appliedDiscount": {
                          "description": "wholesale",
                          "value": 5,
                          "amount": 3.74,
                          "valueType": "PERCENTAGE",
                          "title": "Fancy"
                      },
                      "weight": {
                          "value": 1,
                          "unit": "KILOGRAMS"
                      },
                      "customAttributes": [
                          {
                              "key": "color",
                              "value": "Gold"
                          },
                          {
                              "key": "material",
                              "value": "Plastic"
                          }
                      ]
                  },
                  {
                      "variantId": "gid://shopify/ProductVariant/43729076",
                      "quantity": 2
                  }
              ],
              "customAttributes": [
                  {
                      "key": "name",
                      "value": "Achilles"
                  },
                  {
                      "key": "city",
                      "value": "Troy"
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
    mutation draftOrderCreate($input: DraftOrderInput!) {
      draftOrderCreate(input: $input) {
        draftOrder {
          id
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "note": "Test draft order",
      "email": "test.user@shopify.com",
      "taxExempt": true,
      "tags": [
        "foo",
        "bar"
      ],
      "shippingLine": {
        "title": "Custom Shipping",
        "price": 4.55
      },
      "shippingAddress": {
        "address1": "123 Main St",
        "city": "Waterloo",
        "province": "Ontario",
        "country": "Canada",
        "zip": "A1A 1A1"
      },
      "billingAddress": {
        "address1": "456 Main St",
        "city": "Toronto",
        "province": "Ontario",
        "country": "Canada",
        "zip": "Z9Z 9Z9"
      },
      "appliedDiscount": {
        "description": "damaged",
        "value": 5,
        "amount": 5,
        "valueType": "FIXED_AMOUNT",
        "title": "Custom"
      },
      "lineItems": [
        {
          "title": "Custom product",
          "originalUnitPrice": 14.99,
          "quantity": 5,
          "appliedDiscount": {
            "description": "wholesale",
            "value": 5,
            "amount": 3.74,
            "valueType": "PERCENTAGE",
            "title": "Fancy"
          },
          "weight": {
            "value": 1,
            "unit": "KILOGRAMS"
          },
          "customAttributes": [
            {
              "key": "color",
              "value": "Gold"
            },
            {
              "key": "material",
              "value": "Plastic"
            }
          ]
        },
        {
          "variantId": "gid://shopify/ProductVariant/43729076",
          "quantity": 2
        }
      ],
      "customAttributes": [
        {
          "key": "name",
          "value": "Achilles"
        },
        {
          "key": "city",
          "value": "Troy"
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
      "query": `mutation draftOrderCreate($input: DraftOrderInput!) {
        draftOrderCreate(input: $input) {
          draftOrder {
            id
          }
        }
      }`,
      "variables": {
          "input": {
              "note": "Test draft order",
              "email": "test.user@shopify.com",
              "taxExempt": true,
              "tags": [
                  "foo",
                  "bar"
              ],
              "shippingLine": {
                  "title": "Custom Shipping",
                  "price": 4.55
              },
              "shippingAddress": {
                  "address1": "123 Main St",
                  "city": "Waterloo",
                  "province": "Ontario",
                  "country": "Canada",
                  "zip": "A1A 1A1"
              },
              "billingAddress": {
                  "address1": "456 Main St",
                  "city": "Toronto",
                  "province": "Ontario",
                  "country": "Canada",
                  "zip": "Z9Z 9Z9"
              },
              "appliedDiscount": {
                  "description": "damaged",
                  "value": 5,
                  "amount": 5,
                  "valueType": "FIXED_AMOUNT",
                  "title": "Custom"
              },
              "lineItems": [
                  {
                      "title": "Custom product",
                      "originalUnitPrice": 14.99,
                      "quantity": 5,
                      "appliedDiscount": {
                          "description": "wholesale",
                          "value": 5,
                          "amount": 3.74,
                          "valueType": "PERCENTAGE",
                          "title": "Fancy"
                      },
                      "weight": {
                          "value": 1,
                          "unit": "KILOGRAMS"
                      },
                      "customAttributes": [
                          {
                              "key": "color",
                              "value": "Gold"
                          },
                          {
                              "key": "material",
                              "value": "Plastic"
                          }
                      ]
                  },
                  {
                      "variantId": "gid://shopify/ProductVariant/43729076",
                      "quantity": 2
                  }
              ],
              "customAttributes": [
                  {
                      "key": "name",
                      "value": "Achilles"
                  },
                  {
                      "key": "city",
                      "value": "Troy"
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
  'mutation draftOrderCreate($input: DraftOrderInput!) {
    draftOrderCreate(input: $input) {
      draftOrder {
        id
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "note": "Test draft order",
      "email": "test.user@shopify.com",
      "taxExempt": true,
      "tags": [
        "foo",
        "bar"
      ],
      "shippingLine": {
        "title": "Custom Shipping",
        "price": 4.55
      },
      "shippingAddress": {
        "address1": "123 Main St",
        "city": "Waterloo",
        "province": "Ontario",
        "country": "Canada",
        "zip": "A1A 1A1"
      },
      "billingAddress": {
        "address1": "456 Main St",
        "city": "Toronto",
        "province": "Ontario",
        "country": "Canada",
        "zip": "Z9Z 9Z9"
      },
      "appliedDiscount": {
        "description": "damaged",
        "value": 5,
        "amount": 5,
        "valueType": "FIXED_AMOUNT",
        "title": "Custom"
      },
      "lineItems": [
        {
          "title": "Custom product",
          "originalUnitPrice": 14.99,
          "quantity": 5,
          "appliedDiscount": {
            "description": "wholesale",
            "value": 5,
            "amount": 3.74,
            "valueType": "PERCENTAGE",
            "title": "Fancy"
          },
          "weight": {
            "value": 1,
            "unit": "KILOGRAMS"
          },
          "customAttributes": [
            {
              "key": "color",
              "value": "Gold"
            },
            {
              "key": "material",
              "value": "Plastic"
            }
          ]
        },
        {
          "variantId": "gid://shopify/ProductVariant/43729076",
          "quantity": 2
        }
      ],
      "customAttributes": [
        {
          "key": "name",
          "value": "Achilles"
        },
        {
          "key": "city",
          "value": "Troy"
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "draftOrderCreate": {
      "draftOrder": {
        "id": "gid://shopify/DraftOrder/1069920508"
      }
    }
  }
  ```

* ### Create a draft order with line item components

  #### Description

  Creates a draft order with a line item that has components

  #### Query

  ```graphql
  mutation draftOrderCreate($input: DraftOrderInput!) {
    draftOrderCreate(input: $input) {
      draftOrder {
        id
        lineItems(first: 100) {
          edges {
            node {
              id
              components {
                id
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
    "input": {
      "lineItems": [
        {
          "variantId": "gid://shopify/ProductVariant/799757249",
          "quantity": 1,
          "components": [
            {
              "variantId": "gid://shopify/ProductVariant/149896808",
              "quantity": 1
            },
            {
              "variantId": "gid://shopify/ProductVariant/709406719",
              "quantity": 1
            }
          ]
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
  "query": "mutation draftOrderCreate($input: DraftOrderInput!) { draftOrderCreate(input: $input) { draftOrder { id lineItems(first: 100) { edges { node { id components { id } } } } } } }",
   "variables": {
      "input": {
        "lineItems": [
          {
            "variantId": "gid://shopify/ProductVariant/799757249",
            "quantity": 1,
            "components": [
              {
                "variantId": "gid://shopify/ProductVariant/149896808",
                "quantity": 1
              },
              {
                "variantId": "gid://shopify/ProductVariant/709406719",
                "quantity": 1
              }
            ]
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
    mutation draftOrderCreate($input: DraftOrderInput!) {
      draftOrderCreate(input: $input) {
        draftOrder {
          id
          lineItems(first: 100) {
            edges {
              node {
                id
                components {
                  id
                }
              }
            }
          }
        }
      }
    }`,
    {
      variables: {
          "input": {
              "lineItems": [
                  {
                      "variantId": "gid://shopify/ProductVariant/799757249",
                      "quantity": 1,
                      "components": [
                          {
                              "variantId": "gid://shopify/ProductVariant/149896808",
                              "quantity": 1
                          },
                          {
                              "variantId": "gid://shopify/ProductVariant/709406719",
                              "quantity": 1
                          }
                      ]
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
    mutation draftOrderCreate($input: DraftOrderInput!) {
      draftOrderCreate(input: $input) {
        draftOrder {
          id
          lineItems(first: 100) {
            edges {
              node {
                id
                components {
                  id
                }
              }
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "lineItems": [
        {
          "variantId": "gid://shopify/ProductVariant/799757249",
          "quantity": 1,
          "components": [
            {
              "variantId": "gid://shopify/ProductVariant/149896808",
              "quantity": 1
            },
            {
              "variantId": "gid://shopify/ProductVariant/709406719",
              "quantity": 1
            }
          ]
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
      "query": `mutation draftOrderCreate($input: DraftOrderInput!) {
        draftOrderCreate(input: $input) {
          draftOrder {
            id
            lineItems(first: 100) {
              edges {
                node {
                  id
                  components {
                    id
                  }
                }
              }
            }
          }
        }
      }`,
      "variables": {
          "input": {
              "lineItems": [
                  {
                      "variantId": "gid://shopify/ProductVariant/799757249",
                      "quantity": 1,
                      "components": [
                          {
                              "variantId": "gid://shopify/ProductVariant/149896808",
                              "quantity": 1
                          },
                          {
                              "variantId": "gid://shopify/ProductVariant/709406719",
                              "quantity": 1
                          }
                      ]
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
  'mutation draftOrderCreate($input: DraftOrderInput!) {
    draftOrderCreate(input: $input) {
      draftOrder {
        id
        lineItems(first: 100) {
          edges {
            node {
              id
              components {
                id
              }
            }
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "lineItems": [
        {
          "variantId": "gid://shopify/ProductVariant/799757249",
          "quantity": 1,
          "components": [
            {
              "variantId": "gid://shopify/ProductVariant/149896808",
              "quantity": 1
            },
            {
              "variantId": "gid://shopify/ProductVariant/709406719",
              "quantity": 1
            }
          ]
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "draftOrderCreate": {
      "draftOrder": {
        "id": "gid://shopify/DraftOrder/1069920512",
        "lineItems": {
          "edges": [
            {
              "node": {
                "id": "gid://shopify/DraftOrderLineItem/1066630446",
                "components": [
                  {
                    "id": "gid://shopify/DraftOrderLineItem/1066630447"
                  },
                  {
                    "id": "gid://shopify/DraftOrderLineItem/1066630448"
                  }
                ]
              }
            }
          ]
        }
      }
    }
  }
  ```

* ### Create a draft order with presentment currency

  #### Description

  Create a comprehensive draft order with presentment currency, discounts, custom products, and custom attributes. This example demonstrates setting a customer-facing currency (CAD), mixing custom line-items with existing store products, and adding custom attributes at both order and line-item levels. The \[\`totalPriceSet\`]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/DraftOrder#field-DraftOrder.fields.totalPriceSet) field returns pricing in both shop and presentment currencies. Learn more about \[presentment currencies]\(https://help.shopify.com/manual/international/pricing/exchange-rates).

  #### Query

  ```graphql
  mutation draftOrderCreate($input: DraftOrderInput!) {
    draftOrderCreate(input: $input) {
      draftOrder {
        id
        presentmentCurrencyCode
        totalPriceSet {
          shopMoney {
            amount
            currencyCode
          }
          presentmentMoney {
            amount
            currencyCode
          }
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "note": "Test draft order",
      "email": "test.user@shopify.com",
      "taxExempt": true,
      "tags": [
        "foo",
        "bar"
      ],
      "shippingLine": {
        "title": "Custom Shipping",
        "price": 4.55
      },
      "shippingAddress": {
        "address1": "123 Main St",
        "city": "Waterloo",
        "province": "Ontario",
        "country": "Canada",
        "zip": "A1A 1A1"
      },
      "billingAddress": {
        "address1": "456 Main St",
        "city": "Toronto",
        "province": "Ontario",
        "country": "Canada",
        "zip": "Z9Z 9Z9"
      },
      "appliedDiscount": {
        "description": "damaged",
        "value": 5,
        "amount": 5,
        "valueType": "FIXED_AMOUNT",
        "title": "Custom"
      },
      "lineItems": [
        {
          "title": "Custom product",
          "originalUnitPrice": 14.99,
          "quantity": 5,
          "appliedDiscount": {
            "description": "wholesale",
            "value": 5,
            "amount": 3.74,
            "valueType": "PERCENTAGE",
            "title": "Fancy"
          },
          "weight": {
            "value": 1,
            "unit": "KILOGRAMS"
          },
          "customAttributes": [
            {
              "key": "color",
              "value": "Gold"
            },
            {
              "key": "material",
              "value": "Plastic"
            }
          ]
        },
        {
          "variantId": "gid://shopify/ProductVariant/43729076",
          "quantity": 2
        }
      ],
      "presentmentCurrencyCode": "CAD",
      "customAttributes": [
        {
          "key": "name",
          "value": "Achilles"
        },
        {
          "key": "city",
          "value": "Troy"
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
  "query": "mutation draftOrderCreate($input: DraftOrderInput!) { draftOrderCreate(input: $input) { draftOrder { id presentmentCurrencyCode totalPriceSet { shopMoney { amount currencyCode } presentmentMoney { amount currencyCode } } } } }",
   "variables": {
      "input": {
        "note": "Test draft order",
        "email": "test.user@shopify.com",
        "taxExempt": true,
        "tags": [
          "foo",
          "bar"
        ],
        "shippingLine": {
          "title": "Custom Shipping",
          "price": 4.55
        },
        "shippingAddress": {
          "address1": "123 Main St",
          "city": "Waterloo",
          "province": "Ontario",
          "country": "Canada",
          "zip": "A1A 1A1"
        },
        "billingAddress": {
          "address1": "456 Main St",
          "city": "Toronto",
          "province": "Ontario",
          "country": "Canada",
          "zip": "Z9Z 9Z9"
        },
        "appliedDiscount": {
          "description": "damaged",
          "value": 5,
          "amount": 5,
          "valueType": "FIXED_AMOUNT",
          "title": "Custom"
        },
        "lineItems": [
          {
            "title": "Custom product",
            "originalUnitPrice": 14.99,
            "quantity": 5,
            "appliedDiscount": {
              "description": "wholesale",
              "value": 5,
              "amount": 3.74,
              "valueType": "PERCENTAGE",
              "title": "Fancy"
            },
            "weight": {
              "value": 1,
              "unit": "KILOGRAMS"
            },
            "customAttributes": [
              {
                "key": "color",
                "value": "Gold"
              },
              {
                "key": "material",
                "value": "Plastic"
              }
            ]
          },
          {
            "variantId": "gid://shopify/ProductVariant/43729076",
            "quantity": 2
          }
        ],
        "presentmentCurrencyCode": "CAD",
        "customAttributes": [
          {
            "key": "name",
            "value": "Achilles"
          },
          {
            "key": "city",
            "value": "Troy"
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
    mutation draftOrderCreate($input: DraftOrderInput!) {
      draftOrderCreate(input: $input) {
        draftOrder {
          id
          presentmentCurrencyCode
          totalPriceSet {
            shopMoney {
              amount
              currencyCode
            }
            presentmentMoney {
              amount
              currencyCode
            }
          }
        }
      }
    }`,
    {
      variables: {
          "input": {
              "note": "Test draft order",
              "email": "test.user@shopify.com",
              "taxExempt": true,
              "tags": [
                  "foo",
                  "bar"
              ],
              "shippingLine": {
                  "title": "Custom Shipping",
                  "price": 4.55
              },
              "shippingAddress": {
                  "address1": "123 Main St",
                  "city": "Waterloo",
                  "province": "Ontario",
                  "country": "Canada",
                  "zip": "A1A 1A1"
              },
              "billingAddress": {
                  "address1": "456 Main St",
                  "city": "Toronto",
                  "province": "Ontario",
                  "country": "Canada",
                  "zip": "Z9Z 9Z9"
              },
              "appliedDiscount": {
                  "description": "damaged",
                  "value": 5,
                  "amount": 5,
                  "valueType": "FIXED_AMOUNT",
                  "title": "Custom"
              },
              "lineItems": [
                  {
                      "title": "Custom product",
                      "originalUnitPrice": 14.99,
                      "quantity": 5,
                      "appliedDiscount": {
                          "description": "wholesale",
                          "value": 5,
                          "amount": 3.74,
                          "valueType": "PERCENTAGE",
                          "title": "Fancy"
                      },
                      "weight": {
                          "value": 1,
                          "unit": "KILOGRAMS"
                      },
                      "customAttributes": [
                          {
                              "key": "color",
                              "value": "Gold"
                          },
                          {
                              "key": "material",
                              "value": "Plastic"
                          }
                      ]
                  },
                  {
                      "variantId": "gid://shopify/ProductVariant/43729076",
                      "quantity": 2
                  }
              ],
              "presentmentCurrencyCode": "CAD",
              "customAttributes": [
                  {
                      "key": "name",
                      "value": "Achilles"
                  },
                  {
                      "key": "city",
                      "value": "Troy"
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
    mutation draftOrderCreate($input: DraftOrderInput!) {
      draftOrderCreate(input: $input) {
        draftOrder {
          id
          presentmentCurrencyCode
          totalPriceSet {
            shopMoney {
              amount
              currencyCode
            }
            presentmentMoney {
              amount
              currencyCode
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "note": "Test draft order",
      "email": "test.user@shopify.com",
      "taxExempt": true,
      "tags": [
        "foo",
        "bar"
      ],
      "shippingLine": {
        "title": "Custom Shipping",
        "price": 4.55
      },
      "shippingAddress": {
        "address1": "123 Main St",
        "city": "Waterloo",
        "province": "Ontario",
        "country": "Canada",
        "zip": "A1A 1A1"
      },
      "billingAddress": {
        "address1": "456 Main St",
        "city": "Toronto",
        "province": "Ontario",
        "country": "Canada",
        "zip": "Z9Z 9Z9"
      },
      "appliedDiscount": {
        "description": "damaged",
        "value": 5,
        "amount": 5,
        "valueType": "FIXED_AMOUNT",
        "title": "Custom"
      },
      "lineItems": [
        {
          "title": "Custom product",
          "originalUnitPrice": 14.99,
          "quantity": 5,
          "appliedDiscount": {
            "description": "wholesale",
            "value": 5,
            "amount": 3.74,
            "valueType": "PERCENTAGE",
            "title": "Fancy"
          },
          "weight": {
            "value": 1,
            "unit": "KILOGRAMS"
          },
          "customAttributes": [
            {
              "key": "color",
              "value": "Gold"
            },
            {
              "key": "material",
              "value": "Plastic"
            }
          ]
        },
        {
          "variantId": "gid://shopify/ProductVariant/43729076",
          "quantity": 2
        }
      ],
      "presentmentCurrencyCode": "CAD",
      "customAttributes": [
        {
          "key": "name",
          "value": "Achilles"
        },
        {
          "key": "city",
          "value": "Troy"
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
      "query": `mutation draftOrderCreate($input: DraftOrderInput!) {
        draftOrderCreate(input: $input) {
          draftOrder {
            id
            presentmentCurrencyCode
            totalPriceSet {
              shopMoney {
                amount
                currencyCode
              }
              presentmentMoney {
                amount
                currencyCode
              }
            }
          }
        }
      }`,
      "variables": {
          "input": {
              "note": "Test draft order",
              "email": "test.user@shopify.com",
              "taxExempt": true,
              "tags": [
                  "foo",
                  "bar"
              ],
              "shippingLine": {
                  "title": "Custom Shipping",
                  "price": 4.55
              },
              "shippingAddress": {
                  "address1": "123 Main St",
                  "city": "Waterloo",
                  "province": "Ontario",
                  "country": "Canada",
                  "zip": "A1A 1A1"
              },
              "billingAddress": {
                  "address1": "456 Main St",
                  "city": "Toronto",
                  "province": "Ontario",
                  "country": "Canada",
                  "zip": "Z9Z 9Z9"
              },
              "appliedDiscount": {
                  "description": "damaged",
                  "value": 5,
                  "amount": 5,
                  "valueType": "FIXED_AMOUNT",
                  "title": "Custom"
              },
              "lineItems": [
                  {
                      "title": "Custom product",
                      "originalUnitPrice": 14.99,
                      "quantity": 5,
                      "appliedDiscount": {
                          "description": "wholesale",
                          "value": 5,
                          "amount": 3.74,
                          "valueType": "PERCENTAGE",
                          "title": "Fancy"
                      },
                      "weight": {
                          "value": 1,
                          "unit": "KILOGRAMS"
                      },
                      "customAttributes": [
                          {
                              "key": "color",
                              "value": "Gold"
                          },
                          {
                              "key": "material",
                              "value": "Plastic"
                          }
                      ]
                  },
                  {
                      "variantId": "gid://shopify/ProductVariant/43729076",
                      "quantity": 2
                  }
              ],
              "presentmentCurrencyCode": "CAD",
              "customAttributes": [
                  {
                      "key": "name",
                      "value": "Achilles"
                  },
                  {
                      "key": "city",
                      "value": "Troy"
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
  'mutation draftOrderCreate($input: DraftOrderInput!) {
    draftOrderCreate(input: $input) {
      draftOrder {
        id
        presentmentCurrencyCode
        totalPriceSet {
          shopMoney {
            amount
            currencyCode
          }
          presentmentMoney {
            amount
            currencyCode
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "note": "Test draft order",
      "email": "test.user@shopify.com",
      "taxExempt": true,
      "tags": [
        "foo",
        "bar"
      ],
      "shippingLine": {
        "title": "Custom Shipping",
        "price": 4.55
      },
      "shippingAddress": {
        "address1": "123 Main St",
        "city": "Waterloo",
        "province": "Ontario",
        "country": "Canada",
        "zip": "A1A 1A1"
      },
      "billingAddress": {
        "address1": "456 Main St",
        "city": "Toronto",
        "province": "Ontario",
        "country": "Canada",
        "zip": "Z9Z 9Z9"
      },
      "appliedDiscount": {
        "description": "damaged",
        "value": 5,
        "amount": 5,
        "valueType": "FIXED_AMOUNT",
        "title": "Custom"
      },
      "lineItems": [
        {
          "title": "Custom product",
          "originalUnitPrice": 14.99,
          "quantity": 5,
          "appliedDiscount": {
            "description": "wholesale",
            "value": 5,
            "amount": 3.74,
            "valueType": "PERCENTAGE",
            "title": "Fancy"
          },
          "weight": {
            "value": 1,
            "unit": "KILOGRAMS"
          },
          "customAttributes": [
            {
              "key": "color",
              "value": "Gold"
            },
            {
              "key": "material",
              "value": "Plastic"
            }
          ]
        },
        {
          "variantId": "gid://shopify/ProductVariant/43729076",
          "quantity": 2
        }
      ],
      "presentmentCurrencyCode": "CAD",
      "customAttributes": [
        {
          "key": "name",
          "value": "Achilles"
        },
        {
          "key": "city",
          "value": "Troy"
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "draftOrderCreate": {
      "draftOrder": {
        "id": "gid://shopify/DraftOrder/1069920514",
        "presentmentCurrencyCode": "CAD",
        "totalPriceSet": {
          "shopMoney": {
            "amount": "95.29",
            "currencyCode": "USD"
          },
          "presentmentMoney": {
            "amount": "119.11",
            "currencyCode": "CAD"
          }
        }
      }
    }
  }
  ```

* ### Create a new metafield on a new draft order

  #### Description

  Create a draft order with custom \[metafields]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/DraftOrder#field-DraftOrder.fields.metafields) for storing delivery instructions. This example demonstrates adding structured metadata to draft orders for operational information that doesn't fit standard order fields, such as special delivery instructions, internal notes, or custom fulfillment requirements. Alternatively, refer to the \[\`metafieldsSet\`]\(https://shopify.dev/docs/api/admin-graphql/latest/mutations/metafieldsset) mutation to create or update metafields on draft orders.

  #### Query

  ```graphql
  mutation createDraftOrderMetafields($input: DraftOrderInput!) {
    draftOrderCreate(input: $input) {
      draftOrder {
        id
        metafields(first: 3) {
          edges {
            node {
              id
              namespace
              key
              value
            }
          }
        }
      }
      userErrors {
        message
        field
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "metafields": [
        {
          "namespace": "my_field",
          "key": "delivery_instructions",
          "type": "single_line_text_field",
          "value": "leave on back porch"
        }
      ],
      "lineItems": [
        {
          "title": "small wheel",
          "quantity": 1,
          "originalUnitPrice": "10"
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
  "query": "mutation createDraftOrderMetafields($input: DraftOrderInput!) { draftOrderCreate(input: $input) { draftOrder { id metafields(first: 3) { edges { node { id namespace key value } } } } userErrors { message field } } }",
   "variables": {
      "input": {
        "metafields": [
          {
            "namespace": "my_field",
            "key": "delivery_instructions",
            "type": "single_line_text_field",
            "value": "leave on back porch"
          }
        ],
        "lineItems": [
          {
            "title": "small wheel",
            "quantity": 1,
            "originalUnitPrice": "10"
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
    mutation createDraftOrderMetafields($input: DraftOrderInput!) {
      draftOrderCreate(input: $input) {
        draftOrder {
          id
          metafields(first: 3) {
            edges {
              node {
                id
                namespace
                key
                value
              }
            }
          }
        }
        userErrors {
          message
          field
        }
      }
    }`,
    {
      variables: {
          "input": {
              "metafields": [
                  {
                      "namespace": "my_field",
                      "key": "delivery_instructions",
                      "type": "single_line_text_field",
                      "value": "leave on back porch"
                  }
              ],
              "lineItems": [
                  {
                      "title": "small wheel",
                      "quantity": 1,
                      "originalUnitPrice": "10"
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
    mutation createDraftOrderMetafields($input: DraftOrderInput!) {
      draftOrderCreate(input: $input) {
        draftOrder {
          id
          metafields(first: 3) {
            edges {
              node {
                id
                namespace
                key
                value
              }
            }
          }
        }
        userErrors {
          message
          field
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "metafields": [
        {
          "namespace": "my_field",
          "key": "delivery_instructions",
          "type": "single_line_text_field",
          "value": "leave on back porch"
        }
      ],
      "lineItems": [
        {
          "title": "small wheel",
          "quantity": 1,
          "originalUnitPrice": "10"
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
      "query": `mutation createDraftOrderMetafields($input: DraftOrderInput!) {
        draftOrderCreate(input: $input) {
          draftOrder {
            id
            metafields(first: 3) {
              edges {
                node {
                  id
                  namespace
                  key
                  value
                }
              }
            }
          }
          userErrors {
            message
            field
          }
        }
      }`,
      "variables": {
          "input": {
              "metafields": [
                  {
                      "namespace": "my_field",
                      "key": "delivery_instructions",
                      "type": "single_line_text_field",
                      "value": "leave on back porch"
                  }
              ],
              "lineItems": [
                  {
                      "title": "small wheel",
                      "quantity": 1,
                      "originalUnitPrice": "10"
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
  'mutation createDraftOrderMetafields($input: DraftOrderInput!) {
    draftOrderCreate(input: $input) {
      draftOrder {
        id
        metafields(first: 3) {
          edges {
            node {
              id
              namespace
              key
              value
            }
          }
        }
      }
      userErrors {
        message
        field
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "metafields": [
        {
          "namespace": "my_field",
          "key": "delivery_instructions",
          "type": "single_line_text_field",
          "value": "leave on back porch"
        }
      ],
      "lineItems": [
        {
          "title": "small wheel",
          "quantity": 1,
          "originalUnitPrice": "10"
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "draftOrderCreate": {
      "draftOrder": {
        "id": "gid://shopify/DraftOrder/1069920509",
        "metafields": {
          "edges": [
            {
              "node": {
                "id": "gid://shopify/Metafield/1069228940",
                "namespace": "my_field",
                "key": "delivery_instructions",
                "value": "leave on back porch"
              }
            }
          ]
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Creating a draft order with a company, location and company contact

  #### Description

  Create a B2B draft order with a \[\`purchasingEntity\`]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/DraftOrder#field-DraftOrder.fields.purchasingEntity). This example demonstrates orders for wholesale customers, corporate accounts, or business partners where the buyer represents a company rather than an individual customer. Learn more about \[building B2B draft orders]\(https://shopify.dev/docs/apps/build/b2b/draft-orders).

  #### Query

  ```graphql
  mutation draftOrderCreate($input: DraftOrderInput!) {
    draftOrderCreate(input: $input) {
      draftOrder {
        id
      }
      userErrors {
        message
        field
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "purchasingEntity": {
        "purchasingCompany": {
          "companyId": "gid://shopify/Company/426793626",
          "companyLocationId": "gid://shopify/CompanyLocation/441870438",
          "companyContactId": "gid://shopify/CompanyContact/207808057"
        }
      },
      "note": "Test B2B draft order",
      "email": "test.b2b.user@shopify.com",
      "shippingLine": {
        "title": "Custom Shipping",
        "price": 4.55
      },
      "shippingAddress": {
        "address1": "555 Main St",
        "city": "Waterloo",
        "province": "Ontario",
        "country": "Canada",
        "zip": "B1B 1B1"
      },
      "billingAddress": {
        "address1": "556 Main St",
        "city": "Toronto",
        "province": "Ontario",
        "country": "Canada",
        "zip": "D9D DZD"
      },
      "lineItems": [
        {
          "variantId": "gid://shopify/ProductVariant/43729076",
          "quantity": 5
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
  "query": "mutation draftOrderCreate($input: DraftOrderInput!) { draftOrderCreate(input: $input) { draftOrder { id } userErrors { message field } } }",
   "variables": {
      "input": {
        "purchasingEntity": {
          "purchasingCompany": {
            "companyId": "gid://shopify/Company/426793626",
            "companyLocationId": "gid://shopify/CompanyLocation/441870438",
            "companyContactId": "gid://shopify/CompanyContact/207808057"
          }
        },
        "note": "Test B2B draft order",
        "email": "test.b2b.user@shopify.com",
        "shippingLine": {
          "title": "Custom Shipping",
          "price": 4.55
        },
        "shippingAddress": {
          "address1": "555 Main St",
          "city": "Waterloo",
          "province": "Ontario",
          "country": "Canada",
          "zip": "B1B 1B1"
        },
        "billingAddress": {
          "address1": "556 Main St",
          "city": "Toronto",
          "province": "Ontario",
          "country": "Canada",
          "zip": "D9D DZD"
        },
        "lineItems": [
          {
            "variantId": "gid://shopify/ProductVariant/43729076",
            "quantity": 5
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
    mutation draftOrderCreate($input: DraftOrderInput!) {
      draftOrderCreate(input: $input) {
        draftOrder {
          id
        }
        userErrors {
          message
          field
        }
      }
    }`,
    {
      variables: {
          "input": {
              "purchasingEntity": {
                  "purchasingCompany": {
                      "companyId": "gid://shopify/Company/426793626",
                      "companyLocationId": "gid://shopify/CompanyLocation/441870438",
                      "companyContactId": "gid://shopify/CompanyContact/207808057"
                  }
              },
              "note": "Test B2B draft order",
              "email": "test.b2b.user@shopify.com",
              "shippingLine": {
                  "title": "Custom Shipping",
                  "price": 4.55
              },
              "shippingAddress": {
                  "address1": "555 Main St",
                  "city": "Waterloo",
                  "province": "Ontario",
                  "country": "Canada",
                  "zip": "B1B 1B1"
              },
              "billingAddress": {
                  "address1": "556 Main St",
                  "city": "Toronto",
                  "province": "Ontario",
                  "country": "Canada",
                  "zip": "D9D DZD"
              },
              "lineItems": [
                  {
                      "variantId": "gid://shopify/ProductVariant/43729076",
                      "quantity": 5
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
    mutation draftOrderCreate($input: DraftOrderInput!) {
      draftOrderCreate(input: $input) {
        draftOrder {
          id
        }
        userErrors {
          message
          field
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "purchasingEntity": {
        "purchasingCompany": {
          "companyId": "gid://shopify/Company/426793626",
          "companyLocationId": "gid://shopify/CompanyLocation/441870438",
          "companyContactId": "gid://shopify/CompanyContact/207808057"
        }
      },
      "note": "Test B2B draft order",
      "email": "test.b2b.user@shopify.com",
      "shippingLine": {
        "title": "Custom Shipping",
        "price": 4.55
      },
      "shippingAddress": {
        "address1": "555 Main St",
        "city": "Waterloo",
        "province": "Ontario",
        "country": "Canada",
        "zip": "B1B 1B1"
      },
      "billingAddress": {
        "address1": "556 Main St",
        "city": "Toronto",
        "province": "Ontario",
        "country": "Canada",
        "zip": "D9D DZD"
      },
      "lineItems": [
        {
          "variantId": "gid://shopify/ProductVariant/43729076",
          "quantity": 5
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
      "query": `mutation draftOrderCreate($input: DraftOrderInput!) {
        draftOrderCreate(input: $input) {
          draftOrder {
            id
          }
          userErrors {
            message
            field
          }
        }
      }`,
      "variables": {
          "input": {
              "purchasingEntity": {
                  "purchasingCompany": {
                      "companyId": "gid://shopify/Company/426793626",
                      "companyLocationId": "gid://shopify/CompanyLocation/441870438",
                      "companyContactId": "gid://shopify/CompanyContact/207808057"
                  }
              },
              "note": "Test B2B draft order",
              "email": "test.b2b.user@shopify.com",
              "shippingLine": {
                  "title": "Custom Shipping",
                  "price": 4.55
              },
              "shippingAddress": {
                  "address1": "555 Main St",
                  "city": "Waterloo",
                  "province": "Ontario",
                  "country": "Canada",
                  "zip": "B1B 1B1"
              },
              "billingAddress": {
                  "address1": "556 Main St",
                  "city": "Toronto",
                  "province": "Ontario",
                  "country": "Canada",
                  "zip": "D9D DZD"
              },
              "lineItems": [
                  {
                      "variantId": "gid://shopify/ProductVariant/43729076",
                      "quantity": 5
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
  'mutation draftOrderCreate($input: DraftOrderInput!) {
    draftOrderCreate(input: $input) {
      draftOrder {
        id
      }
      userErrors {
        message
        field
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "purchasingEntity": {
        "purchasingCompany": {
          "companyId": "gid://shopify/Company/426793626",
          "companyLocationId": "gid://shopify/CompanyLocation/441870438",
          "companyContactId": "gid://shopify/CompanyContact/207808057"
        }
      },
      "note": "Test B2B draft order",
      "email": "test.b2b.user@shopify.com",
      "shippingLine": {
        "title": "Custom Shipping",
        "price": 4.55
      },
      "shippingAddress": {
        "address1": "555 Main St",
        "city": "Waterloo",
        "province": "Ontario",
        "country": "Canada",
        "zip": "B1B 1B1"
      },
      "billingAddress": {
        "address1": "556 Main St",
        "city": "Toronto",
        "province": "Ontario",
        "country": "Canada",
        "zip": "D9D DZD"
      },
      "lineItems": [
        {
          "variantId": "gid://shopify/ProductVariant/43729076",
          "quantity": 5
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "draftOrderCreate": {
      "draftOrder": {
        "id": "gid://shopify/DraftOrder/1069920513"
      },
      "userErrors": []
    }
  }
  ```

* ### Creating a draft order with invalid input returns an error

  #### Description

  Create a draft order with invalid input to demonstrate proper error handling. This example shows the \[\`userErrors\`]\(https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderCreate#returns-userErrors) response format when attempting to create an order without any line items, which is required for all draft orders.

  #### Query

  ```graphql
  mutation draftOrderCreate($input: DraftOrderInput!) {
    draftOrderCreate(input: $input) {
      draftOrder {
        id
      }
      userErrors {
        message
        field
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "lineItems": []
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
  "query": "mutation draftOrderCreate($input: DraftOrderInput!) { draftOrderCreate(input: $input) { draftOrder { id } userErrors { message field } } }",
   "variables": {
      "input": {
        "lineItems": []
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
    mutation draftOrderCreate($input: DraftOrderInput!) {
      draftOrderCreate(input: $input) {
        draftOrder {
          id
        }
        userErrors {
          message
          field
        }
      }
    }`,
    {
      variables: {
          "input": {
              "lineItems": []
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
    mutation draftOrderCreate($input: DraftOrderInput!) {
      draftOrderCreate(input: $input) {
        draftOrder {
          id
        }
        userErrors {
          message
          field
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "lineItems": []
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation draftOrderCreate($input: DraftOrderInput!) {
        draftOrderCreate(input: $input) {
          draftOrder {
            id
          }
          userErrors {
            message
            field
          }
        }
      }`,
      "variables": {
          "input": {
              "lineItems": []
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation draftOrderCreate($input: DraftOrderInput!) {
    draftOrderCreate(input: $input) {
      draftOrder {
        id
      }
      userErrors {
        message
        field
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "lineItems": []
    }
  }'
  ```

  #### Response

  ```json
  {
    "draftOrderCreate": {
      "draftOrder": null,
      "userErrors": [
        {
          "message": "Add at least 1 product",
          "field": null
        }
      ]
    }
  }
  ```

* ### draftOrderCreate reference
