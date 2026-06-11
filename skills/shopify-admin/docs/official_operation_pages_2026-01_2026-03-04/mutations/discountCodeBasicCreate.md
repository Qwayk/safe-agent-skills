---
title: discountCodeBasicCreate - GraphQL Admin
description: >-
  Creates an [amount off
  discount](https://help.shopify.com/manual/discounts/discount-types/percentage-fixed-amount)
  that's applied on a cart and at checkout when a customer enters a code. Amount
  off discounts can be a percentage off or a fixed amount off.


  > Note:

  > To create discounts that are automatically applied on a cart and at
  checkout, use the
  [`discountAutomaticBasicCreate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticBasicCreate)
  mutation.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeBasicCreate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeBasicCreate.md
---

# discount​Code​Basic​Create

mutation

Requires Apps must have `write_discounts` access scope.

Creates an [amount off discount](https://help.shopify.com/manual/discounts/discount-types/percentage-fixed-amount) that's applied on a cart and at checkout when a customer enters a code. Amount off discounts can be a percentage off or a fixed amount off.

***

**Note:** To create discounts that are automatically applied on a cart and at checkout, use the \<a href="https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticBasicCreate">\<code>\<span class="PreventFireFoxApplyingGapToWBR">discount\<wbr/>Automatic\<wbr/>Basic\<wbr/>Create\</span>\</code>\</a> mutation.

***

## Arguments

* basic​Code​Discount

  [Discount​Code​Basic​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/DiscountCodeBasicInput)

  required

  The input data used to create the discount code.

***

## Discount​Code​Basic​Create​Payload returns

* code​Discount​Node

  [Discount​Code​Node](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountCodeNode)

  The discount code that was created.

* user​Errors

  [\[Discount​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create a discount code with a customer segment

  #### Description

  Create an \[amount off discount]\(https://help.shopify.com/manual/discounts/discount-types/percentage-fixed-amount) that's applied on a cart and at checkout when customers enter a code. This example shows how to create a code that takes $20 off all items and applies only to a specific customer segment.

  #### Query

  ```graphql
  mutation CreateSegmentDiscountCode($basicCodeDiscount: DiscountCodeBasicInput!) {
    discountCodeBasicCreate(basicCodeDiscount: $basicCodeDiscount) {
      codeDiscountNode {
        id
        codeDiscount {
          ... on DiscountCodeBasic {
            title
            codes(first: 10) {
              nodes {
                code
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
            }
          }
        }
      }
      userErrors {
        field
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "basicCodeDiscount": {
      "title": "$20 off for VIP customers",
      "code": "VIP20OFF",
      "startsAt": "2025-07-24T16:16:22-04:00",
      "endsAt": null,
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
            "amount": "20.00",
            "appliesOnEachItem": false
          }
        },
        "items": {
          "all": true
        }
      },
      "appliesOncePerCustomer": true
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
  "query": "mutation CreateSegmentDiscountCode($basicCodeDiscount: DiscountCodeBasicInput!) { discountCodeBasicCreate(basicCodeDiscount: $basicCodeDiscount) { codeDiscountNode { id codeDiscount { ... on DiscountCodeBasic { title codes(first: 10) { nodes { code } } context { ... on DiscountCustomerSegments { segments { id } } } customerGets { value { ... on DiscountAmount { amount { amount currencyCode } appliesOnEachItem } } } } } } userErrors { field message } } }",
   "variables": {
      "basicCodeDiscount": {
        "title": "$20 off for VIP customers",
        "code": "VIP20OFF",
        "startsAt": "2025-07-24T16:16:22-04:00",
        "endsAt": null,
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
              "amount": "20.00",
              "appliesOnEachItem": false
            }
          },
          "items": {
            "all": true
          }
        },
        "appliesOncePerCustomer": true
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
    mutation CreateSegmentDiscountCode($basicCodeDiscount: DiscountCodeBasicInput!) {
      discountCodeBasicCreate(basicCodeDiscount: $basicCodeDiscount) {
        codeDiscountNode {
          id
          codeDiscount {
            ... on DiscountCodeBasic {
              title
              codes(first: 10) {
                nodes {
                  code
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
              }
            }
          }
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "basicCodeDiscount": {
              "title": "$20 off for VIP customers",
              "code": "VIP20OFF",
              "startsAt": "2025-07-24T16:16:22-04:00",
              "endsAt": null,
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
                          "amount": "20.00",
                          "appliesOnEachItem": false
                      }
                  },
                  "items": {
                      "all": true
                  }
              },
              "appliesOncePerCustomer": true
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
    mutation CreateSegmentDiscountCode($basicCodeDiscount: DiscountCodeBasicInput!) {
      discountCodeBasicCreate(basicCodeDiscount: $basicCodeDiscount) {
        codeDiscountNode {
          id
          codeDiscount {
            ... on DiscountCodeBasic {
              title
              codes(first: 10) {
                nodes {
                  code
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
              }
            }
          }
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "basicCodeDiscount": {
      "title": "$20 off for VIP customers",
      "code": "VIP20OFF",
      "startsAt": "2025-07-24T16:16:22-04:00",
      "endsAt": null,
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
            "amount": "20.00",
            "appliesOnEachItem": false
          }
        },
        "items": {
          "all": true
        }
      },
      "appliesOncePerCustomer": true
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation CreateSegmentDiscountCode($basicCodeDiscount: DiscountCodeBasicInput!) {
        discountCodeBasicCreate(basicCodeDiscount: $basicCodeDiscount) {
          codeDiscountNode {
            id
            codeDiscount {
              ... on DiscountCodeBasic {
                title
                codes(first: 10) {
                  nodes {
                    code
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
                }
              }
            }
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "basicCodeDiscount": {
              "title": "$20 off for VIP customers",
              "code": "VIP20OFF",
              "startsAt": "2025-07-24T16:16:22-04:00",
              "endsAt": null,
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
                          "amount": "20.00",
                          "appliesOnEachItem": false
                      }
                  },
                  "items": {
                      "all": true
                  }
              },
              "appliesOncePerCustomer": true
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation CreateSegmentDiscountCode($basicCodeDiscount: DiscountCodeBasicInput!) {
    discountCodeBasicCreate(basicCodeDiscount: $basicCodeDiscount) {
      codeDiscountNode {
        id
        codeDiscount {
          ... on DiscountCodeBasic {
            title
            codes(first: 10) {
              nodes {
                code
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
            }
          }
        }
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "basicCodeDiscount": {
      "title": "$20 off for VIP customers",
      "code": "VIP20OFF",
      "startsAt": "2025-07-24T16:16:22-04:00",
      "endsAt": null,
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
            "amount": "20.00",
            "appliesOnEachItem": false
          }
        },
        "items": {
          "all": true
        }
      },
      "appliesOncePerCustomer": true
    }
  }'
  ```

  #### Response

  ```json
  {
    "discountCodeBasicCreate": {
      "codeDiscountNode": {
        "id": "gid://shopify/DiscountCodeNode/1057856653",
        "codeDiscount": {
          "title": "$20 off for VIP customers",
          "codes": {
            "nodes": [
              {
                "code": "VIP20OFF"
              }
            ]
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
                "amount": "20.0",
                "currencyCode": "USD"
              },
              "appliesOnEachItem": false
            }
          }
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Create a percentage off discount code with a minimum purchase requirement

  #### Description

  Create an \[amount off discount]\(https://help.shopify.com/manual/discounts/discount-types/percentage-fixed-amount) that's applied on a cart and at checkout when customers enter a code. This example shows how to create a code that offers a 10% discount on all items to a customer after they spend $50. The discount is limited to one use for each customer.

  #### Query

  ```graphql
  mutation CreateDiscountCode($basicCodeDiscount: DiscountCodeBasicInput!) {
    discountCodeBasicCreate(basicCodeDiscount: $basicCodeDiscount) {
      codeDiscountNode {
        id
        codeDiscount {
          ... on DiscountCodeBasic {
            title
            startsAt
            endsAt
            customerSelection {
              ... on DiscountCustomers {
                customers {
                  id
                }
              }
            }
            customerGets {
              value {
                ... on DiscountPercentage {
                  percentage
                }
              }
            }
          }
        }
      }
      userErrors {
        field
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "basicCodeDiscount": {
      "title": "10% off selected items",
      "code": "10FORYOU",
      "startsAt": "2025-01-01T00:00:00Z",
      "endsAt": "2025-12-31T23:59:59Z",
      "customerSelection": {
        "customers": {
          "add": [
            "gid://shopify/Customer/624407574"
          ]
        }
      },
      "customerGets": {
        "value": {
          "percentage": 0.1
        },
        "items": {
          "all": true
        }
      },
      "minimumRequirement": {
        "subtotal": {
          "greaterThanOrEqualToSubtotal": "50.0"
        }
      },
      "usageLimit": 100,
      "appliesOncePerCustomer": true
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
  "query": "mutation CreateDiscountCode($basicCodeDiscount: DiscountCodeBasicInput!) { discountCodeBasicCreate(basicCodeDiscount: $basicCodeDiscount) { codeDiscountNode { id codeDiscount { ... on DiscountCodeBasic { title startsAt endsAt customerSelection { ... on DiscountCustomers { customers { id } } } customerGets { value { ... on DiscountPercentage { percentage } } } } } } userErrors { field message } } }",
   "variables": {
      "basicCodeDiscount": {
        "title": "10% off selected items",
        "code": "10FORYOU",
        "startsAt": "2025-01-01T00:00:00Z",
        "endsAt": "2025-12-31T23:59:59Z",
        "customerSelection": {
          "customers": {
            "add": [
              "gid://shopify/Customer/624407574"
            ]
          }
        },
        "customerGets": {
          "value": {
            "percentage": 0.1
          },
          "items": {
            "all": true
          }
        },
        "minimumRequirement": {
          "subtotal": {
            "greaterThanOrEqualToSubtotal": "50.0"
          }
        },
        "usageLimit": 100,
        "appliesOncePerCustomer": true
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
    mutation CreateDiscountCode($basicCodeDiscount: DiscountCodeBasicInput!) {
      discountCodeBasicCreate(basicCodeDiscount: $basicCodeDiscount) {
        codeDiscountNode {
          id
          codeDiscount {
            ... on DiscountCodeBasic {
              title
              startsAt
              endsAt
              customerSelection {
                ... on DiscountCustomers {
                  customers {
                    id
                  }
                }
              }
              customerGets {
                value {
                  ... on DiscountPercentage {
                    percentage
                  }
                }
              }
            }
          }
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "basicCodeDiscount": {
              "title": "10% off selected items",
              "code": "10FORYOU",
              "startsAt": "2025-01-01T00:00:00Z",
              "endsAt": "2025-12-31T23:59:59Z",
              "customerSelection": {
                  "customers": {
                      "add": [
                          "gid://shopify/Customer/624407574"
                      ]
                  }
              },
              "customerGets": {
                  "value": {
                      "percentage": 0.1
                  },
                  "items": {
                      "all": true
                  }
              },
              "minimumRequirement": {
                  "subtotal": {
                      "greaterThanOrEqualToSubtotal": "50.0"
                  }
              },
              "usageLimit": 100,
              "appliesOncePerCustomer": true
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
    mutation CreateDiscountCode($basicCodeDiscount: DiscountCodeBasicInput!) {
      discountCodeBasicCreate(basicCodeDiscount: $basicCodeDiscount) {
        codeDiscountNode {
          id
          codeDiscount {
            ... on DiscountCodeBasic {
              title
              startsAt
              endsAt
              customerSelection {
                ... on DiscountCustomers {
                  customers {
                    id
                  }
                }
              }
              customerGets {
                value {
                  ... on DiscountPercentage {
                    percentage
                  }
                }
              }
            }
          }
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "basicCodeDiscount": {
      "title": "10% off selected items",
      "code": "10FORYOU",
      "startsAt": "2025-01-01T00:00:00Z",
      "endsAt": "2025-12-31T23:59:59Z",
      "customerSelection": {
        "customers": {
          "add": [
            "gid://shopify/Customer/624407574"
          ]
        }
      },
      "customerGets": {
        "value": {
          "percentage": 0.1
        },
        "items": {
          "all": true
        }
      },
      "minimumRequirement": {
        "subtotal": {
          "greaterThanOrEqualToSubtotal": "50.0"
        }
      },
      "usageLimit": 100,
      "appliesOncePerCustomer": true
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation CreateDiscountCode($basicCodeDiscount: DiscountCodeBasicInput!) {
        discountCodeBasicCreate(basicCodeDiscount: $basicCodeDiscount) {
          codeDiscountNode {
            id
            codeDiscount {
              ... on DiscountCodeBasic {
                title
                startsAt
                endsAt
                customerSelection {
                  ... on DiscountCustomers {
                    customers {
                      id
                    }
                  }
                }
                customerGets {
                  value {
                    ... on DiscountPercentage {
                      percentage
                    }
                  }
                }
              }
            }
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "basicCodeDiscount": {
              "title": "10% off selected items",
              "code": "10FORYOU",
              "startsAt": "2025-01-01T00:00:00Z",
              "endsAt": "2025-12-31T23:59:59Z",
              "customerSelection": {
                  "customers": {
                      "add": [
                          "gid://shopify/Customer/624407574"
                      ]
                  }
              },
              "customerGets": {
                  "value": {
                      "percentage": 0.1
                  },
                  "items": {
                      "all": true
                  }
              },
              "minimumRequirement": {
                  "subtotal": {
                      "greaterThanOrEqualToSubtotal": "50.0"
                  }
              },
              "usageLimit": 100,
              "appliesOncePerCustomer": true
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation CreateDiscountCode($basicCodeDiscount: DiscountCodeBasicInput!) {
    discountCodeBasicCreate(basicCodeDiscount: $basicCodeDiscount) {
      codeDiscountNode {
        id
        codeDiscount {
          ... on DiscountCodeBasic {
            title
            startsAt
            endsAt
            customerSelection {
              ... on DiscountCustomers {
                customers {
                  id
                }
              }
            }
            customerGets {
              value {
                ... on DiscountPercentage {
                  percentage
                }
              }
            }
          }
        }
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "basicCodeDiscount": {
      "title": "10% off selected items",
      "code": "10FORYOU",
      "startsAt": "2025-01-01T00:00:00Z",
      "endsAt": "2025-12-31T23:59:59Z",
      "customerSelection": {
        "customers": {
          "add": [
            "gid://shopify/Customer/624407574"
          ]
        }
      },
      "customerGets": {
        "value": {
          "percentage": 0.1
        },
        "items": {
          "all": true
        }
      },
      "minimumRequirement": {
        "subtotal": {
          "greaterThanOrEqualToSubtotal": "50.0"
        }
      },
      "usageLimit": 100,
      "appliesOncePerCustomer": true
    }
  }'
  ```

  #### Response

  ```json
  {
    "discountCodeBasicCreate": {
      "codeDiscountNode": {
        "id": "gid://shopify/DiscountCodeNode/1057856652",
        "codeDiscount": {
          "title": "10% off selected items",
          "startsAt": "2025-01-01T00:00:00Z",
          "endsAt": "2025-12-31T23:59:59Z",
          "customerSelection": {
            "customers": [
              {
                "id": "gid://shopify/Customer/624407574"
              }
            ]
          },
          "customerGets": {
            "value": {
              "percentage": 0.1
            }
          }
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Create an amount off discount code with an end date

  #### Description

  Create an \[amount off discount]\(https://help.shopify.com/manual/discounts/discount-types/percentage-fixed-amount) that's applied on a cart and at checkout when customers enter a code. This example shows how to create a code that offers a $20 off discount on all items from June 21st to September 21st. The discount is limited to one use for each customer.

  #### Query

  ```graphql
  mutation CreateSummerDiscount($input: DiscountCodeBasicInput!) {
    discountCodeBasicCreate(basicCodeDiscount: $input) {
      codeDiscountNode {
        id
        codeDiscount {
          ... on DiscountCodeBasic {
            title
            codes(first: 10) {
              nodes {
                code
              }
            }
            startsAt
            endsAt
          }
        }
      }
      userErrors {
        field
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "title": "Limited time discount off all items",
      "code": "BUYNOW20",
      "startsAt": "2024-06-21T00:00:00Z",
      "endsAt": "2024-09-21T00:00:00Z",
      "customerSelection": {
        "all": true
      },
      "customerGets": {
        "value": {
          "discountAmount": {
            "amount": 20,
            "appliesOnEachItem": false
          }
        },
        "items": {
          "all": true
        }
      },
      "appliesOncePerCustomer": true
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
  "query": "mutation CreateSummerDiscount($input: DiscountCodeBasicInput!) { discountCodeBasicCreate(basicCodeDiscount: $input) { codeDiscountNode { id codeDiscount { ... on DiscountCodeBasic { title codes(first: 10) { nodes { code } } startsAt endsAt } } } userErrors { field message } } }",
   "variables": {
      "input": {
        "title": "Limited time discount off all items",
        "code": "BUYNOW20",
        "startsAt": "2024-06-21T00:00:00Z",
        "endsAt": "2024-09-21T00:00:00Z",
        "customerSelection": {
          "all": true
        },
        "customerGets": {
          "value": {
            "discountAmount": {
              "amount": 20,
              "appliesOnEachItem": false
            }
          },
          "items": {
            "all": true
          }
        },
        "appliesOncePerCustomer": true
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
    mutation CreateSummerDiscount($input: DiscountCodeBasicInput!) {
      discountCodeBasicCreate(basicCodeDiscount: $input) {
        codeDiscountNode {
          id
          codeDiscount {
            ... on DiscountCodeBasic {
              title
              codes(first: 10) {
                nodes {
                  code
                }
              }
              startsAt
              endsAt
            }
          }
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "input": {
              "title": "Limited time discount off all items",
              "code": "BUYNOW20",
              "startsAt": "2024-06-21T00:00:00Z",
              "endsAt": "2024-09-21T00:00:00Z",
              "customerSelection": {
                  "all": true
              },
              "customerGets": {
                  "value": {
                      "discountAmount": {
                          "amount": 20,
                          "appliesOnEachItem": false
                      }
                  },
                  "items": {
                      "all": true
                  }
              },
              "appliesOncePerCustomer": true
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
    mutation CreateSummerDiscount($input: DiscountCodeBasicInput!) {
      discountCodeBasicCreate(basicCodeDiscount: $input) {
        codeDiscountNode {
          id
          codeDiscount {
            ... on DiscountCodeBasic {
              title
              codes(first: 10) {
                nodes {
                  code
                }
              }
              startsAt
              endsAt
            }
          }
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "title": "Limited time discount off all items",
      "code": "BUYNOW20",
      "startsAt": "2024-06-21T00:00:00Z",
      "endsAt": "2024-09-21T00:00:00Z",
      "customerSelection": {
        "all": true
      },
      "customerGets": {
        "value": {
          "discountAmount": {
            "amount": 20,
            "appliesOnEachItem": false
          }
        },
        "items": {
          "all": true
        }
      },
      "appliesOncePerCustomer": true
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation CreateSummerDiscount($input: DiscountCodeBasicInput!) {
        discountCodeBasicCreate(basicCodeDiscount: $input) {
          codeDiscountNode {
            id
            codeDiscount {
              ... on DiscountCodeBasic {
                title
                codes(first: 10) {
                  nodes {
                    code
                  }
                }
                startsAt
                endsAt
              }
            }
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "input": {
              "title": "Limited time discount off all items",
              "code": "BUYNOW20",
              "startsAt": "2024-06-21T00:00:00Z",
              "endsAt": "2024-09-21T00:00:00Z",
              "customerSelection": {
                  "all": true
              },
              "customerGets": {
                  "value": {
                      "discountAmount": {
                          "amount": 20,
                          "appliesOnEachItem": false
                      }
                  },
                  "items": {
                      "all": true
                  }
              },
              "appliesOncePerCustomer": true
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation CreateSummerDiscount($input: DiscountCodeBasicInput!) {
    discountCodeBasicCreate(basicCodeDiscount: $input) {
      codeDiscountNode {
        id
        codeDiscount {
          ... on DiscountCodeBasic {
            title
            codes(first: 10) {
              nodes {
                code
              }
            }
            startsAt
            endsAt
          }
        }
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "title": "Limited time discount off all items",
      "code": "BUYNOW20",
      "startsAt": "2024-06-21T00:00:00Z",
      "endsAt": "2024-09-21T00:00:00Z",
      "customerSelection": {
        "all": true
      },
      "customerGets": {
        "value": {
          "discountAmount": {
            "amount": 20,
            "appliesOnEachItem": false
          }
        },
        "items": {
          "all": true
        }
      },
      "appliesOncePerCustomer": true
    }
  }'
  ```

  #### Response

  ```json
  {
    "discountCodeBasicCreate": {
      "codeDiscountNode": {
        "id": "gid://shopify/DiscountCodeNode/1057856654",
        "codeDiscount": {
          "title": "Limited time discount off all items",
          "codes": {
            "nodes": [
              {
                "code": "BUYNOW20"
              }
            ]
          },
          "startsAt": "2024-06-21T00:00:00Z",
          "endsAt": "2024-09-21T00:00:00Z"
        }
      },
      "userErrors": []
    }
  }
  ```

* ### discountCodeBasicCreate reference
