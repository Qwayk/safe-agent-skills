---
title: discountAutomaticBasicCreate - GraphQL Admin
description: >-
  Creates an

  [amount off
  discount](https://help.shopify.com/manual/discounts/discount-types/percentage-fixed-amount)

  that's automatically applied on a cart and at checkout.


  > Note:

  > To create code discounts, use the

  [`discountCodeBasicCreate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeBasicCreate)

  mutation.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticBasicCreate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticBasicCreate.md
---

# discount​Automatic​Basic​Create

mutation

Requires Apps must have `write_discounts` access scope.

Creates an [amount off discount](https://help.shopify.com/manual/discounts/discount-types/percentage-fixed-amount) that's automatically applied on a cart and at checkout.

***

**Note:** To create code discounts, use the \<a href="https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeBasicCreate">\<code>\<span class="PreventFireFoxApplyingGapToWBR">discount\<wbr/>Code\<wbr/>Basic\<wbr/>Create\</span>\</code>\</a> mutation.

***

## Arguments

* automatic​Basic​Discount

  [Discount​Automatic​Basic​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/DiscountAutomaticBasicInput)

  required

  The input data used to create the automatic amount off discount.

***

## Discount​Automatic​Basic​Create​Payload returns

* automatic​Discount​Node

  [Discount​Automatic​Node](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountAutomaticNode)

  The automatic discount that was created.

* user​Errors

  [\[Discount​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create a combinable automatic discount

  #### Description

  Create an \[automatic discount]\(https://help.shopify.com/manual/discounts/discount-types#automatic-discounts) that offers $10.00 off on orders over $100.00 and can also be \[combined]\(https://help.shopify.com/manual/discounts/combining-discounts/discount-combinations) with shipping discounts.

  #### Query

  ```graphql
  mutation discountAutomaticBasicCreate($automaticBasicDiscount: DiscountAutomaticBasicInput!) {
    discountAutomaticBasicCreate(automaticBasicDiscount: $automaticBasicDiscount) {
      automaticDiscountNode {
        id
        automaticDiscount {
          ... on DiscountAutomaticBasic {
            title
            startsAt
            combinesWith {
              productDiscounts
              shippingDiscounts
              orderDiscounts
            }
            minimumRequirement {
              ... on DiscountMinimumSubtotal {
                greaterThanOrEqualToSubtotal {
                  amount
                  currencyCode
                }
              }
            }
            customerGets {
              value {
                ... on DiscountAmount {
                  amount {
                    amount
                    currencyCode
                  }
                }
              }
              items {
                ... on AllDiscountItems {
                  allItems
                }
              }
            }
          }
        }
      }
      userErrors {
        field
        code
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "automaticBasicDiscount": {
      "title": "$10 off orders over $100 (combinable with shipping discounts)",
      "startsAt": "2025-07-24T16:19:41-04:00",
      "minimumRequirement": {
        "subtotal": {
          "greaterThanOrEqualToSubtotal": "100.00"
        }
      },
      "customerGets": {
        "value": {
          "discountAmount": {
            "amount": "10.00",
            "appliesOnEachItem": false
          }
        },
        "items": {
          "all": true
        }
      },
      "combinesWith": {
        "productDiscounts": false,
        "shippingDiscounts": true,
        "orderDiscounts": false
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
  "query": "mutation discountAutomaticBasicCreate($automaticBasicDiscount: DiscountAutomaticBasicInput!) { discountAutomaticBasicCreate(automaticBasicDiscount: $automaticBasicDiscount) { automaticDiscountNode { id automaticDiscount { ... on DiscountAutomaticBasic { title startsAt combinesWith { productDiscounts shippingDiscounts orderDiscounts } minimumRequirement { ... on DiscountMinimumSubtotal { greaterThanOrEqualToSubtotal { amount currencyCode } } } customerGets { value { ... on DiscountAmount { amount { amount currencyCode } } } items { ... on AllDiscountItems { allItems } } } } } } userErrors { field code message } } }",
   "variables": {
      "automaticBasicDiscount": {
        "title": "$10 off orders over $100 (combinable with shipping discounts)",
        "startsAt": "2025-07-24T16:19:41-04:00",
        "minimumRequirement": {
          "subtotal": {
            "greaterThanOrEqualToSubtotal": "100.00"
          }
        },
        "customerGets": {
          "value": {
            "discountAmount": {
              "amount": "10.00",
              "appliesOnEachItem": false
            }
          },
          "items": {
            "all": true
          }
        },
        "combinesWith": {
          "productDiscounts": false,
          "shippingDiscounts": true,
          "orderDiscounts": false
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
    mutation discountAutomaticBasicCreate($automaticBasicDiscount: DiscountAutomaticBasicInput!) {
      discountAutomaticBasicCreate(automaticBasicDiscount: $automaticBasicDiscount) {
        automaticDiscountNode {
          id
          automaticDiscount {
            ... on DiscountAutomaticBasic {
              title
              startsAt
              combinesWith {
                productDiscounts
                shippingDiscounts
                orderDiscounts
              }
              minimumRequirement {
                ... on DiscountMinimumSubtotal {
                  greaterThanOrEqualToSubtotal {
                    amount
                    currencyCode
                  }
                }
              }
              customerGets {
                value {
                  ... on DiscountAmount {
                    amount {
                      amount
                      currencyCode
                    }
                  }
                }
                items {
                  ... on AllDiscountItems {
                    allItems
                  }
                }
              }
            }
          }
        }
        userErrors {
          field
          code
          message
        }
      }
    }`,
    {
      variables: {
          "automaticBasicDiscount": {
              "title": "$10 off orders over $100 (combinable with shipping discounts)",
              "startsAt": "2025-07-24T16:19:41-04:00",
              "minimumRequirement": {
                  "subtotal": {
                      "greaterThanOrEqualToSubtotal": "100.00"
                  }
              },
              "customerGets": {
                  "value": {
                      "discountAmount": {
                          "amount": "10.00",
                          "appliesOnEachItem": false
                      }
                  },
                  "items": {
                      "all": true
                  }
              },
              "combinesWith": {
                  "productDiscounts": false,
                  "shippingDiscounts": true,
                  "orderDiscounts": false
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
    mutation discountAutomaticBasicCreate($automaticBasicDiscount: DiscountAutomaticBasicInput!) {
      discountAutomaticBasicCreate(automaticBasicDiscount: $automaticBasicDiscount) {
        automaticDiscountNode {
          id
          automaticDiscount {
            ... on DiscountAutomaticBasic {
              title
              startsAt
              combinesWith {
                productDiscounts
                shippingDiscounts
                orderDiscounts
              }
              minimumRequirement {
                ... on DiscountMinimumSubtotal {
                  greaterThanOrEqualToSubtotal {
                    amount
                    currencyCode
                  }
                }
              }
              customerGets {
                value {
                  ... on DiscountAmount {
                    amount {
                      amount
                      currencyCode
                    }
                  }
                }
                items {
                  ... on AllDiscountItems {
                    allItems
                  }
                }
              }
            }
          }
        }
        userErrors {
          field
          code
          message
        }
      }
    }
  QUERY

  variables = {
    "automaticBasicDiscount": {
      "title": "$10 off orders over $100 (combinable with shipping discounts)",
      "startsAt": "2025-07-24T16:19:41-04:00",
      "minimumRequirement": {
        "subtotal": {
          "greaterThanOrEqualToSubtotal": "100.00"
        }
      },
      "customerGets": {
        "value": {
          "discountAmount": {
            "amount": "10.00",
            "appliesOnEachItem": false
          }
        },
        "items": {
          "all": true
        }
      },
      "combinesWith": {
        "productDiscounts": false,
        "shippingDiscounts": true,
        "orderDiscounts": false
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
      "query": `mutation discountAutomaticBasicCreate($automaticBasicDiscount: DiscountAutomaticBasicInput!) {
        discountAutomaticBasicCreate(automaticBasicDiscount: $automaticBasicDiscount) {
          automaticDiscountNode {
            id
            automaticDiscount {
              ... on DiscountAutomaticBasic {
                title
                startsAt
                combinesWith {
                  productDiscounts
                  shippingDiscounts
                  orderDiscounts
                }
                minimumRequirement {
                  ... on DiscountMinimumSubtotal {
                    greaterThanOrEqualToSubtotal {
                      amount
                      currencyCode
                    }
                  }
                }
                customerGets {
                  value {
                    ... on DiscountAmount {
                      amount {
                        amount
                        currencyCode
                      }
                    }
                  }
                  items {
                    ... on AllDiscountItems {
                      allItems
                    }
                  }
                }
              }
            }
          }
          userErrors {
            field
            code
            message
          }
        }
      }`,
      "variables": {
          "automaticBasicDiscount": {
              "title": "$10 off orders over $100 (combinable with shipping discounts)",
              "startsAt": "2025-07-24T16:19:41-04:00",
              "minimumRequirement": {
                  "subtotal": {
                      "greaterThanOrEqualToSubtotal": "100.00"
                  }
              },
              "customerGets": {
                  "value": {
                      "discountAmount": {
                          "amount": "10.00",
                          "appliesOnEachItem": false
                      }
                  },
                  "items": {
                      "all": true
                  }
              },
              "combinesWith": {
                  "productDiscounts": false,
                  "shippingDiscounts": true,
                  "orderDiscounts": false
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
  'mutation discountAutomaticBasicCreate($automaticBasicDiscount: DiscountAutomaticBasicInput!) {
    discountAutomaticBasicCreate(automaticBasicDiscount: $automaticBasicDiscount) {
      automaticDiscountNode {
        id
        automaticDiscount {
          ... on DiscountAutomaticBasic {
            title
            startsAt
            combinesWith {
              productDiscounts
              shippingDiscounts
              orderDiscounts
            }
            minimumRequirement {
              ... on DiscountMinimumSubtotal {
                greaterThanOrEqualToSubtotal {
                  amount
                  currencyCode
                }
              }
            }
            customerGets {
              value {
                ... on DiscountAmount {
                  amount {
                    amount
                    currencyCode
                  }
                }
              }
              items {
                ... on AllDiscountItems {
                  allItems
                }
              }
            }
          }
        }
      }
      userErrors {
        field
        code
        message
      }
    }
  }' \
  --variables \
  '{
    "automaticBasicDiscount": {
      "title": "$10 off orders over $100 (combinable with shipping discounts)",
      "startsAt": "2025-07-24T16:19:41-04:00",
      "minimumRequirement": {
        "subtotal": {
          "greaterThanOrEqualToSubtotal": "100.00"
        }
      },
      "customerGets": {
        "value": {
          "discountAmount": {
            "amount": "10.00",
            "appliesOnEachItem": false
          }
        },
        "items": {
          "all": true
        }
      },
      "combinesWith": {
        "productDiscounts": false,
        "shippingDiscounts": true,
        "orderDiscounts": false
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "discountAutomaticBasicCreate": {
      "automaticDiscountNode": {
        "id": "gid://shopify/DiscountAutomaticNode/1057856663",
        "automaticDiscount": {
          "title": "$10 off orders over $100 (combinable with shipping discounts)",
          "startsAt": "2025-07-24T20:19:41Z",
          "combinesWith": {
            "productDiscounts": false,
            "shippingDiscounts": true,
            "orderDiscounts": false
          },
          "minimumRequirement": {
            "greaterThanOrEqualToSubtotal": {
              "amount": "100.0",
              "currencyCode": "USD"
            }
          },
          "customerGets": {
            "value": {
              "amount": {
                "amount": "10.0",
                "currencyCode": "USD"
              }
            },
            "items": {
              "allItems": true
            }
          }
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Create a fixed amount off discount

  #### Description

  Create an \[automatic discount]\(https://help.shopify.com/manual/discounts/discount-types#automatic-discounts) that offers $50.00 off on all orders over $200.00. The discount applies to all customers on all items from June through September 2025.

  #### Query

  ```graphql
  mutation discountAutomaticBasicCreate($automaticBasicDiscount: DiscountAutomaticBasicInput!) {
    discountAutomaticBasicCreate(automaticBasicDiscount: $automaticBasicDiscount) {
      automaticDiscountNode {
        id
        automaticDiscount {
          ... on DiscountAutomaticBasic {
            startsAt
            endsAt
            minimumRequirement {
              ... on DiscountMinimumSubtotal {
                greaterThanOrEqualToSubtotal {
                  amount
                  currencyCode
                }
              }
            }
            customerGets {
              value {
                ... on DiscountAmount {
                  amount {
                    amount
                    currencyCode
                  }
                  appliesOnEachItem
                }
              }
              items {
                ... on AllDiscountItems {
                  allItems
                }
              }
            }
          }
        }
      }
      userErrors {
        field
        code
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "automaticBasicDiscount": {
      "title": "$50 off all orders over $200 (June - September 2025)",
      "startsAt": "2025-06-01T00:00:00Z",
      "endsAt": "2025-09-30T00:00:00Z",
      "minimumRequirement": {
        "subtotal": {
          "greaterThanOrEqualToSubtotal": "200.00"
        }
      },
      "customerGets": {
        "value": {
          "discountAmount": {
            "amount": "50.00",
            "appliesOnEachItem": false
          }
        },
        "items": {
          "all": true
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
  "query": "mutation discountAutomaticBasicCreate($automaticBasicDiscount: DiscountAutomaticBasicInput!) { discountAutomaticBasicCreate(automaticBasicDiscount: $automaticBasicDiscount) { automaticDiscountNode { id automaticDiscount { ... on DiscountAutomaticBasic { startsAt endsAt minimumRequirement { ... on DiscountMinimumSubtotal { greaterThanOrEqualToSubtotal { amount currencyCode } } } customerGets { value { ... on DiscountAmount { amount { amount currencyCode } appliesOnEachItem } } items { ... on AllDiscountItems { allItems } } } } } } userErrors { field code message } } }",
   "variables": {
      "automaticBasicDiscount": {
        "title": "$50 off all orders over $200 (June - September 2025)",
        "startsAt": "2025-06-01T00:00:00Z",
        "endsAt": "2025-09-30T00:00:00Z",
        "minimumRequirement": {
          "subtotal": {
            "greaterThanOrEqualToSubtotal": "200.00"
          }
        },
        "customerGets": {
          "value": {
            "discountAmount": {
              "amount": "50.00",
              "appliesOnEachItem": false
            }
          },
          "items": {
            "all": true
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
    mutation discountAutomaticBasicCreate($automaticBasicDiscount: DiscountAutomaticBasicInput!) {
      discountAutomaticBasicCreate(automaticBasicDiscount: $automaticBasicDiscount) {
        automaticDiscountNode {
          id
          automaticDiscount {
            ... on DiscountAutomaticBasic {
              startsAt
              endsAt
              minimumRequirement {
                ... on DiscountMinimumSubtotal {
                  greaterThanOrEqualToSubtotal {
                    amount
                    currencyCode
                  }
                }
              }
              customerGets {
                value {
                  ... on DiscountAmount {
                    amount {
                      amount
                      currencyCode
                    }
                    appliesOnEachItem
                  }
                }
                items {
                  ... on AllDiscountItems {
                    allItems
                  }
                }
              }
            }
          }
        }
        userErrors {
          field
          code
          message
        }
      }
    }`,
    {
      variables: {
          "automaticBasicDiscount": {
              "title": "$50 off all orders over $200 (June - September 2025)",
              "startsAt": "2025-06-01T00:00:00Z",
              "endsAt": "2025-09-30T00:00:00Z",
              "minimumRequirement": {
                  "subtotal": {
                      "greaterThanOrEqualToSubtotal": "200.00"
                  }
              },
              "customerGets": {
                  "value": {
                      "discountAmount": {
                          "amount": "50.00",
                          "appliesOnEachItem": false
                      }
                  },
                  "items": {
                      "all": true
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
    mutation discountAutomaticBasicCreate($automaticBasicDiscount: DiscountAutomaticBasicInput!) {
      discountAutomaticBasicCreate(automaticBasicDiscount: $automaticBasicDiscount) {
        automaticDiscountNode {
          id
          automaticDiscount {
            ... on DiscountAutomaticBasic {
              startsAt
              endsAt
              minimumRequirement {
                ... on DiscountMinimumSubtotal {
                  greaterThanOrEqualToSubtotal {
                    amount
                    currencyCode
                  }
                }
              }
              customerGets {
                value {
                  ... on DiscountAmount {
                    amount {
                      amount
                      currencyCode
                    }
                    appliesOnEachItem
                  }
                }
                items {
                  ... on AllDiscountItems {
                    allItems
                  }
                }
              }
            }
          }
        }
        userErrors {
          field
          code
          message
        }
      }
    }
  QUERY

  variables = {
    "automaticBasicDiscount": {
      "title": "$50 off all orders over $200 (June - September 2025)",
      "startsAt": "2025-06-01T00:00:00Z",
      "endsAt": "2025-09-30T00:00:00Z",
      "minimumRequirement": {
        "subtotal": {
          "greaterThanOrEqualToSubtotal": "200.00"
        }
      },
      "customerGets": {
        "value": {
          "discountAmount": {
            "amount": "50.00",
            "appliesOnEachItem": false
          }
        },
        "items": {
          "all": true
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
      "query": `mutation discountAutomaticBasicCreate($automaticBasicDiscount: DiscountAutomaticBasicInput!) {
        discountAutomaticBasicCreate(automaticBasicDiscount: $automaticBasicDiscount) {
          automaticDiscountNode {
            id
            automaticDiscount {
              ... on DiscountAutomaticBasic {
                startsAt
                endsAt
                minimumRequirement {
                  ... on DiscountMinimumSubtotal {
                    greaterThanOrEqualToSubtotal {
                      amount
                      currencyCode
                    }
                  }
                }
                customerGets {
                  value {
                    ... on DiscountAmount {
                      amount {
                        amount
                        currencyCode
                      }
                      appliesOnEachItem
                    }
                  }
                  items {
                    ... on AllDiscountItems {
                      allItems
                    }
                  }
                }
              }
            }
          }
          userErrors {
            field
            code
            message
          }
        }
      }`,
      "variables": {
          "automaticBasicDiscount": {
              "title": "$50 off all orders over $200 (June - September 2025)",
              "startsAt": "2025-06-01T00:00:00Z",
              "endsAt": "2025-09-30T00:00:00Z",
              "minimumRequirement": {
                  "subtotal": {
                      "greaterThanOrEqualToSubtotal": "200.00"
                  }
              },
              "customerGets": {
                  "value": {
                      "discountAmount": {
                          "amount": "50.00",
                          "appliesOnEachItem": false
                      }
                  },
                  "items": {
                      "all": true
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
  'mutation discountAutomaticBasicCreate($automaticBasicDiscount: DiscountAutomaticBasicInput!) {
    discountAutomaticBasicCreate(automaticBasicDiscount: $automaticBasicDiscount) {
      automaticDiscountNode {
        id
        automaticDiscount {
          ... on DiscountAutomaticBasic {
            startsAt
            endsAt
            minimumRequirement {
              ... on DiscountMinimumSubtotal {
                greaterThanOrEqualToSubtotal {
                  amount
                  currencyCode
                }
              }
            }
            customerGets {
              value {
                ... on DiscountAmount {
                  amount {
                    amount
                    currencyCode
                  }
                  appliesOnEachItem
                }
              }
              items {
                ... on AllDiscountItems {
                  allItems
                }
              }
            }
          }
        }
      }
      userErrors {
        field
        code
        message
      }
    }
  }' \
  --variables \
  '{
    "automaticBasicDiscount": {
      "title": "$50 off all orders over $200 (June - September 2025)",
      "startsAt": "2025-06-01T00:00:00Z",
      "endsAt": "2025-09-30T00:00:00Z",
      "minimumRequirement": {
        "subtotal": {
          "greaterThanOrEqualToSubtotal": "200.00"
        }
      },
      "customerGets": {
        "value": {
          "discountAmount": {
            "amount": "50.00",
            "appliesOnEachItem": false
          }
        },
        "items": {
          "all": true
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "discountAutomaticBasicCreate": {
      "automaticDiscountNode": {
        "id": "gid://shopify/DiscountAutomaticNode/1057856662",
        "automaticDiscount": {
          "startsAt": "2025-06-01T00:00:00Z",
          "endsAt": "2025-09-30T00:00:00Z",
          "minimumRequirement": {
            "greaterThanOrEqualToSubtotal": {
              "amount": "200.0",
              "currencyCode": "USD"
            }
          },
          "customerGets": {
            "value": {
              "amount": {
                "amount": "50.0",
                "currencyCode": "USD"
              },
              "appliesOnEachItem": false
            },
            "items": {
              "allItems": true
            }
          }
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Create a fixed amount off discount for a customer segment

  #### Description

  Create an \[automatic discount]\(https://help.shopify.com/manual/discounts/discount-types#automatic-discounts) that offers $50.00 off on all orders over $200.00. The discount applies to customers from a specific customer segment on all items.

  #### Query

  ```graphql
  mutation discountAutomaticBasicCreate($automaticBasicDiscount: DiscountAutomaticBasicInput!) {
    discountAutomaticBasicCreate(automaticBasicDiscount: $automaticBasicDiscount) {
      automaticDiscountNode {
        id
        automaticDiscount {
          ... on DiscountAutomaticBasic {
            startsAt
            endsAt
            minimumRequirement {
              ... on DiscountMinimumSubtotal {
                greaterThanOrEqualToSubtotal {
                  amount
                  currencyCode
                }
              }
            }
            context {
              ... on DiscountCustomerSegments {
                segments {
                  id
                }
              }
            }
            customerGets {
              value {
                ... on DiscountAmount {
                  amount {
                    amount
                    currencyCode
                  }
                  appliesOnEachItem
                }
              }
              items {
                ... on AllDiscountItems {
                  allItems
                }
              }
            }
          }
        }
      }
      userErrors {
        field
        code
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "automaticBasicDiscount": {
      "title": "$50 off all orders over $200",
      "startsAt": "2025-07-24T16:19:42-04:00",
      "minimumRequirement": {
        "subtotal": {
          "greaterThanOrEqualToSubtotal": "200.00"
        }
      },
      "context": {
        "customerSegments": {
          "add": [
            "gid://shopify/Segment/210588551"
          ]
        }
      },
      "customerGets": {
        "value": {
          "discountAmount": {
            "amount": "50.00",
            "appliesOnEachItem": false
          }
        },
        "items": {
          "all": true
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
  "query": "mutation discountAutomaticBasicCreate($automaticBasicDiscount: DiscountAutomaticBasicInput!) { discountAutomaticBasicCreate(automaticBasicDiscount: $automaticBasicDiscount) { automaticDiscountNode { id automaticDiscount { ... on DiscountAutomaticBasic { startsAt endsAt minimumRequirement { ... on DiscountMinimumSubtotal { greaterThanOrEqualToSubtotal { amount currencyCode } } } context { ... on DiscountCustomerSegments { segments { id } } } customerGets { value { ... on DiscountAmount { amount { amount currencyCode } appliesOnEachItem } } items { ... on AllDiscountItems { allItems } } } } } } userErrors { field code message } } }",
   "variables": {
      "automaticBasicDiscount": {
        "title": "$50 off all orders over $200",
        "startsAt": "2025-07-24T16:19:42-04:00",
        "minimumRequirement": {
          "subtotal": {
            "greaterThanOrEqualToSubtotal": "200.00"
          }
        },
        "context": {
          "customerSegments": {
            "add": [
              "gid://shopify/Segment/210588551"
            ]
          }
        },
        "customerGets": {
          "value": {
            "discountAmount": {
              "amount": "50.00",
              "appliesOnEachItem": false
            }
          },
          "items": {
            "all": true
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
    mutation discountAutomaticBasicCreate($automaticBasicDiscount: DiscountAutomaticBasicInput!) {
      discountAutomaticBasicCreate(automaticBasicDiscount: $automaticBasicDiscount) {
        automaticDiscountNode {
          id
          automaticDiscount {
            ... on DiscountAutomaticBasic {
              startsAt
              endsAt
              minimumRequirement {
                ... on DiscountMinimumSubtotal {
                  greaterThanOrEqualToSubtotal {
                    amount
                    currencyCode
                  }
                }
              }
              context {
                ... on DiscountCustomerSegments {
                  segments {
                    id
                  }
                }
              }
              customerGets {
                value {
                  ... on DiscountAmount {
                    amount {
                      amount
                      currencyCode
                    }
                    appliesOnEachItem
                  }
                }
                items {
                  ... on AllDiscountItems {
                    allItems
                  }
                }
              }
            }
          }
        }
        userErrors {
          field
          code
          message
        }
      }
    }`,
    {
      variables: {
          "automaticBasicDiscount": {
              "title": "$50 off all orders over $200",
              "startsAt": "2025-07-24T16:19:42-04:00",
              "minimumRequirement": {
                  "subtotal": {
                      "greaterThanOrEqualToSubtotal": "200.00"
                  }
              },
              "context": {
                  "customerSegments": {
                      "add": [
                          "gid://shopify/Segment/210588551"
                      ]
                  }
              },
              "customerGets": {
                  "value": {
                      "discountAmount": {
                          "amount": "50.00",
                          "appliesOnEachItem": false
                      }
                  },
                  "items": {
                      "all": true
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
    mutation discountAutomaticBasicCreate($automaticBasicDiscount: DiscountAutomaticBasicInput!) {
      discountAutomaticBasicCreate(automaticBasicDiscount: $automaticBasicDiscount) {
        automaticDiscountNode {
          id
          automaticDiscount {
            ... on DiscountAutomaticBasic {
              startsAt
              endsAt
              minimumRequirement {
                ... on DiscountMinimumSubtotal {
                  greaterThanOrEqualToSubtotal {
                    amount
                    currencyCode
                  }
                }
              }
              context {
                ... on DiscountCustomerSegments {
                  segments {
                    id
                  }
                }
              }
              customerGets {
                value {
                  ... on DiscountAmount {
                    amount {
                      amount
                      currencyCode
                    }
                    appliesOnEachItem
                  }
                }
                items {
                  ... on AllDiscountItems {
                    allItems
                  }
                }
              }
            }
          }
        }
        userErrors {
          field
          code
          message
        }
      }
    }
  QUERY

  variables = {
    "automaticBasicDiscount": {
      "title": "$50 off all orders over $200",
      "startsAt": "2025-07-24T16:19:42-04:00",
      "minimumRequirement": {
        "subtotal": {
          "greaterThanOrEqualToSubtotal": "200.00"
        }
      },
      "context": {
        "customerSegments": {
          "add": [
            "gid://shopify/Segment/210588551"
          ]
        }
      },
      "customerGets": {
        "value": {
          "discountAmount": {
            "amount": "50.00",
            "appliesOnEachItem": false
          }
        },
        "items": {
          "all": true
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
      "query": `mutation discountAutomaticBasicCreate($automaticBasicDiscount: DiscountAutomaticBasicInput!) {
        discountAutomaticBasicCreate(automaticBasicDiscount: $automaticBasicDiscount) {
          automaticDiscountNode {
            id
            automaticDiscount {
              ... on DiscountAutomaticBasic {
                startsAt
                endsAt
                minimumRequirement {
                  ... on DiscountMinimumSubtotal {
                    greaterThanOrEqualToSubtotal {
                      amount
                      currencyCode
                    }
                  }
                }
                context {
                  ... on DiscountCustomerSegments {
                    segments {
                      id
                    }
                  }
                }
                customerGets {
                  value {
                    ... on DiscountAmount {
                      amount {
                        amount
                        currencyCode
                      }
                      appliesOnEachItem
                    }
                  }
                  items {
                    ... on AllDiscountItems {
                      allItems
                    }
                  }
                }
              }
            }
          }
          userErrors {
            field
            code
            message
          }
        }
      }`,
      "variables": {
          "automaticBasicDiscount": {
              "title": "$50 off all orders over $200",
              "startsAt": "2025-07-24T16:19:42-04:00",
              "minimumRequirement": {
                  "subtotal": {
                      "greaterThanOrEqualToSubtotal": "200.00"
                  }
              },
              "context": {
                  "customerSegments": {
                      "add": [
                          "gid://shopify/Segment/210588551"
                      ]
                  }
              },
              "customerGets": {
                  "value": {
                      "discountAmount": {
                          "amount": "50.00",
                          "appliesOnEachItem": false
                      }
                  },
                  "items": {
                      "all": true
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
  'mutation discountAutomaticBasicCreate($automaticBasicDiscount: DiscountAutomaticBasicInput!) {
    discountAutomaticBasicCreate(automaticBasicDiscount: $automaticBasicDiscount) {
      automaticDiscountNode {
        id
        automaticDiscount {
          ... on DiscountAutomaticBasic {
            startsAt
            endsAt
            minimumRequirement {
              ... on DiscountMinimumSubtotal {
                greaterThanOrEqualToSubtotal {
                  amount
                  currencyCode
                }
              }
            }
            context {
              ... on DiscountCustomerSegments {
                segments {
                  id
                }
              }
            }
            customerGets {
              value {
                ... on DiscountAmount {
                  amount {
                    amount
                    currencyCode
                  }
                  appliesOnEachItem
                }
              }
              items {
                ... on AllDiscountItems {
                  allItems
                }
              }
            }
          }
        }
      }
      userErrors {
        field
        code
        message
      }
    }
  }' \
  --variables \
  '{
    "automaticBasicDiscount": {
      "title": "$50 off all orders over $200",
      "startsAt": "2025-07-24T16:19:42-04:00",
      "minimumRequirement": {
        "subtotal": {
          "greaterThanOrEqualToSubtotal": "200.00"
        }
      },
      "context": {
        "customerSegments": {
          "add": [
            "gid://shopify/Segment/210588551"
          ]
        }
      },
      "customerGets": {
        "value": {
          "discountAmount": {
            "amount": "50.00",
            "appliesOnEachItem": false
          }
        },
        "items": {
          "all": true
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "discountAutomaticBasicCreate": {
      "automaticDiscountNode": {
        "id": "gid://shopify/DiscountAutomaticNode/1057856664",
        "automaticDiscount": {
          "startsAt": "2025-07-24T20:19:42Z",
          "endsAt": null,
          "minimumRequirement": {
            "greaterThanOrEqualToSubtotal": {
              "amount": "200.0",
              "currencyCode": "USD"
            }
          },
          "context": {
            "segments": [
              {
                "id": "gid://shopify/Segment/210588551"
              }
            ]
          },
          "customerGets": {
            "value": {
              "amount": {
                "amount": "50.0",
                "currencyCode": "USD"
              },
              "appliesOnEachItem": false
            },
            "items": {
              "allItems": true
            }
          }
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Create a percentage off discount with a minimum purchase

  #### Description

  Create an \[automatic discount]\(https://help.shopify.com/manual/discounts/discount-types#automatic-discounts) that offers 15% off when customers spend $50.00 or more. The discount applies to all items.

  #### Query

  ```graphql
  mutation discountAutomaticBasicCreate($automaticBasicDiscount: DiscountAutomaticBasicInput!) {
    discountAutomaticBasicCreate(automaticBasicDiscount: $automaticBasicDiscount) {
      automaticDiscountNode {
        id
        automaticDiscount {
          ... on DiscountAutomaticBasic {
            title
            startsAt
            minimumRequirement {
              ... on DiscountMinimumSubtotal {
                greaterThanOrEqualToSubtotal {
                  amount
                  currencyCode
                }
              }
            }
            customerGets {
              value {
                ... on DiscountPercentage {
                  percentage
                }
              }
              items {
                ... on AllDiscountItems {
                  allItems
                }
              }
            }
          }
        }
      }
      userErrors {
        field
        code
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "automaticBasicDiscount": {
      "title": "15% off orders over $50",
      "startsAt": "2024-01-01T00:00:00Z",
      "minimumRequirement": {
        "subtotal": {
          "greaterThanOrEqualToSubtotal": "50.00"
        }
      },
      "customerGets": {
        "value": {
          "percentage": 0.15
        },
        "items": {
          "all": true
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
  "query": "mutation discountAutomaticBasicCreate($automaticBasicDiscount: DiscountAutomaticBasicInput!) { discountAutomaticBasicCreate(automaticBasicDiscount: $automaticBasicDiscount) { automaticDiscountNode { id automaticDiscount { ... on DiscountAutomaticBasic { title startsAt minimumRequirement { ... on DiscountMinimumSubtotal { greaterThanOrEqualToSubtotal { amount currencyCode } } } customerGets { value { ... on DiscountPercentage { percentage } } items { ... on AllDiscountItems { allItems } } } } } } userErrors { field code message } } }",
   "variables": {
      "automaticBasicDiscount": {
        "title": "15% off orders over $50",
        "startsAt": "2024-01-01T00:00:00Z",
        "minimumRequirement": {
          "subtotal": {
            "greaterThanOrEqualToSubtotal": "50.00"
          }
        },
        "customerGets": {
          "value": {
            "percentage": 0.15
          },
          "items": {
            "all": true
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
    mutation discountAutomaticBasicCreate($automaticBasicDiscount: DiscountAutomaticBasicInput!) {
      discountAutomaticBasicCreate(automaticBasicDiscount: $automaticBasicDiscount) {
        automaticDiscountNode {
          id
          automaticDiscount {
            ... on DiscountAutomaticBasic {
              title
              startsAt
              minimumRequirement {
                ... on DiscountMinimumSubtotal {
                  greaterThanOrEqualToSubtotal {
                    amount
                    currencyCode
                  }
                }
              }
              customerGets {
                value {
                  ... on DiscountPercentage {
                    percentage
                  }
                }
                items {
                  ... on AllDiscountItems {
                    allItems
                  }
                }
              }
            }
          }
        }
        userErrors {
          field
          code
          message
        }
      }
    }`,
    {
      variables: {
          "automaticBasicDiscount": {
              "title": "15% off orders over $50",
              "startsAt": "2024-01-01T00:00:00Z",
              "minimumRequirement": {
                  "subtotal": {
                      "greaterThanOrEqualToSubtotal": "50.00"
                  }
              },
              "customerGets": {
                  "value": {
                      "percentage": 0.15
                  },
                  "items": {
                      "all": true
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
    mutation discountAutomaticBasicCreate($automaticBasicDiscount: DiscountAutomaticBasicInput!) {
      discountAutomaticBasicCreate(automaticBasicDiscount: $automaticBasicDiscount) {
        automaticDiscountNode {
          id
          automaticDiscount {
            ... on DiscountAutomaticBasic {
              title
              startsAt
              minimumRequirement {
                ... on DiscountMinimumSubtotal {
                  greaterThanOrEqualToSubtotal {
                    amount
                    currencyCode
                  }
                }
              }
              customerGets {
                value {
                  ... on DiscountPercentage {
                    percentage
                  }
                }
                items {
                  ... on AllDiscountItems {
                    allItems
                  }
                }
              }
            }
          }
        }
        userErrors {
          field
          code
          message
        }
      }
    }
  QUERY

  variables = {
    "automaticBasicDiscount": {
      "title": "15% off orders over $50",
      "startsAt": "2024-01-01T00:00:00Z",
      "minimumRequirement": {
        "subtotal": {
          "greaterThanOrEqualToSubtotal": "50.00"
        }
      },
      "customerGets": {
        "value": {
          "percentage": 0.15
        },
        "items": {
          "all": true
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
      "query": `mutation discountAutomaticBasicCreate($automaticBasicDiscount: DiscountAutomaticBasicInput!) {
        discountAutomaticBasicCreate(automaticBasicDiscount: $automaticBasicDiscount) {
          automaticDiscountNode {
            id
            automaticDiscount {
              ... on DiscountAutomaticBasic {
                title
                startsAt
                minimumRequirement {
                  ... on DiscountMinimumSubtotal {
                    greaterThanOrEqualToSubtotal {
                      amount
                      currencyCode
                    }
                  }
                }
                customerGets {
                  value {
                    ... on DiscountPercentage {
                      percentage
                    }
                  }
                  items {
                    ... on AllDiscountItems {
                      allItems
                    }
                  }
                }
              }
            }
          }
          userErrors {
            field
            code
            message
          }
        }
      }`,
      "variables": {
          "automaticBasicDiscount": {
              "title": "15% off orders over $50",
              "startsAt": "2024-01-01T00:00:00Z",
              "minimumRequirement": {
                  "subtotal": {
                      "greaterThanOrEqualToSubtotal": "50.00"
                  }
              },
              "customerGets": {
                  "value": {
                      "percentage": 0.15
                  },
                  "items": {
                      "all": true
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
  'mutation discountAutomaticBasicCreate($automaticBasicDiscount: DiscountAutomaticBasicInput!) {
    discountAutomaticBasicCreate(automaticBasicDiscount: $automaticBasicDiscount) {
      automaticDiscountNode {
        id
        automaticDiscount {
          ... on DiscountAutomaticBasic {
            title
            startsAt
            minimumRequirement {
              ... on DiscountMinimumSubtotal {
                greaterThanOrEqualToSubtotal {
                  amount
                  currencyCode
                }
              }
            }
            customerGets {
              value {
                ... on DiscountPercentage {
                  percentage
                }
              }
              items {
                ... on AllDiscountItems {
                  allItems
                }
              }
            }
          }
        }
      }
      userErrors {
        field
        code
        message
      }
    }
  }' \
  --variables \
  '{
    "automaticBasicDiscount": {
      "title": "15% off orders over $50",
      "startsAt": "2024-01-01T00:00:00Z",
      "minimumRequirement": {
        "subtotal": {
          "greaterThanOrEqualToSubtotal": "50.00"
        }
      },
      "customerGets": {
        "value": {
          "percentage": 0.15
        },
        "items": {
          "all": true
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "discountAutomaticBasicCreate": {
      "automaticDiscountNode": {
        "id": "gid://shopify/DiscountAutomaticNode/1057856665",
        "automaticDiscount": {
          "title": "15% off orders over $50",
          "startsAt": "2024-01-01T00:00:00Z",
          "minimumRequirement": {
            "greaterThanOrEqualToSubtotal": {
              "amount": "50.0",
              "currencyCode": "USD"
            }
          },
          "customerGets": {
            "value": {
              "percentage": 0.15
            },
            "items": {
              "allItems": true
            }
          }
        }
      },
      "userErrors": []
    }
  }
  ```

* ### discountAutomaticBasicCreate reference
