---
title: sellingPlanGroupCreate - GraphQL Admin
description: >-
  Creates a selling plan group that defines how products can be sold and
  purchased. A selling plan group represents a selling method such as "Subscribe
  and save", "Pre-order", or "Try before you buy" and contains one or more
  selling plans with specific billing, delivery, and pricing policies.


  Use the
  [`resources`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/sellingPlanGroupCreate#arguments-resources)
  argument to associate products or product variants with the group during
  creation. You can also add products later using
  [`sellingPlanGroupAddProducts`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/sellingPlanGroupAddProducts)
  or
  [`sellingPlanGroupAddProductVariants`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/sellingPlanGroupAddProductVariants).


  Learn more about [building selling plan
  groups](https://shopify.dev/docs/apps/build/purchase-options/subscriptions/selling-plans/build-a-selling-plan#step-1-create-a-selling-plan-group)
  or explore [examples of creating TBYB and other selling plan
  groups](https://shopify.dev/docs/api/admin-graphql/latest/mutations/sellingPlanGroupCreate?example=create-a-tbyb-selling-plan-group).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/sellingPlanGroupCreate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/sellingPlanGroupCreate.md
---

# selling​Plan​Group​Create

mutation

Requires `write_products` access scope as well as any of `write_own_subscription_contracts`, `write_purchase_options` access scopes. Also: The user must have `manage_orders_information` permissions.

Creates a selling plan group that defines how products can be sold and purchased. A selling plan group represents a selling method such as "Subscribe and save", "Pre-order", or "Try before you buy" and contains one or more selling plans with specific billing, delivery, and pricing policies.

Use the [`resources`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/sellingPlanGroupCreate#arguments-resources) argument to associate products or product variants with the group during creation. You can also add products later using [`sellingPlanGroupAddProducts`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/sellingPlanGroupAddProducts) or [`sellingPlanGroupAddProductVariants`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/sellingPlanGroupAddProductVariants).

Learn more about [building selling plan groups](https://shopify.dev/docs/apps/build/purchase-options/subscriptions/selling-plans/build-a-selling-plan#step-1-create-a-selling-plan-group) or explore [examples of creating TBYB and other selling plan groups](https://shopify.dev/docs/api/admin-graphql/latest/mutations/sellingPlanGroupCreate?example=create-a-tbyb-selling-plan-group).

## Arguments

* input

  [Selling​Plan​Group​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/SellingPlanGroupInput)

  required

  The properties of the new Selling Plan Group.

* resources

  [Selling​Plan​Group​Resource​Input](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/SellingPlanGroupResourceInput)

  The resources this Selling Plan Group should be applied to.

***

## Selling​Plan​Group​Create​Payload returns

* selling​Plan​Group

  [Selling​Plan​Group](https://shopify.dev/docs/api/admin-graphql/latest/objects/SellingPlanGroup)

  The created selling plan group object.

* user​Errors

  [\[Selling​Plan​Group​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/SellingPlanGroupUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create a TBYB selling plan group

  #### Query

  ```graphql
  mutation createSellingPlanGroup($input: SellingPlanGroupInput!, $resources: SellingPlanGroupResourceInput) {
    sellingPlanGroupCreate(input: $input, resources: $resources) {
      sellingPlanGroup {
        id
        sellingPlans(first: 1) {
          edges {
            node {
              id
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
    "input": {
      "name": "TBYB",
      "merchantCode": "tbyb",
      "options": [
        "Try before you buy"
      ],
      "sellingPlansToCreate": [
        {
          "name": "TBYB",
          "options": "Try free for 14 days",
          "category": "TRY_BEFORE_YOU_BUY",
          "billingPolicy": {
            "fixed": {
              "checkoutCharge": {
                "type": "PRICE",
                "value": {
                  "fixedValue": 0
                }
              },
              "remainingBalanceChargeTrigger": "TIME_AFTER_CHECKOUT",
              "remainingBalanceChargeTimeAfterCheckout": "P14D"
            }
          },
          "inventoryPolicy": {
            "reserve": "ON_SALE"
          },
          "deliveryPolicy": {
            "fixed": {
              "fulfillmentTrigger": "ASAP"
            }
          }
        }
      ]
    },
    "resources": {
      "productIds": [
        "gid://shopify/Product/121709582"
      ],
      "productVariantIds": []
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
  "query": "mutation createSellingPlanGroup($input: SellingPlanGroupInput!, $resources: SellingPlanGroupResourceInput) { sellingPlanGroupCreate(input: $input, resources: $resources) { sellingPlanGroup { id sellingPlans(first: 1) { edges { node { id } } } } userErrors { field message } } }",
   "variables": {
      "input": {
        "name": "TBYB",
        "merchantCode": "tbyb",
        "options": [
          "Try before you buy"
        ],
        "sellingPlansToCreate": [
          {
            "name": "TBYB",
            "options": "Try free for 14 days",
            "category": "TRY_BEFORE_YOU_BUY",
            "billingPolicy": {
              "fixed": {
                "checkoutCharge": {
                  "type": "PRICE",
                  "value": {
                    "fixedValue": 0
                  }
                },
                "remainingBalanceChargeTrigger": "TIME_AFTER_CHECKOUT",
                "remainingBalanceChargeTimeAfterCheckout": "P14D"
              }
            },
            "inventoryPolicy": {
              "reserve": "ON_SALE"
            },
            "deliveryPolicy": {
              "fixed": {
                "fulfillmentTrigger": "ASAP"
              }
            }
          }
        ]
      },
      "resources": {
        "productIds": [
          "gid://shopify/Product/121709582"
        ],
        "productVariantIds": []
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
    mutation createSellingPlanGroup($input: SellingPlanGroupInput!, $resources: SellingPlanGroupResourceInput) {
      sellingPlanGroupCreate(input: $input, resources: $resources) {
        sellingPlanGroup {
          id
          sellingPlans(first: 1) {
            edges {
              node {
                id
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
          "input": {
              "name": "TBYB",
              "merchantCode": "tbyb",
              "options": [
                  "Try before you buy"
              ],
              "sellingPlansToCreate": [
                  {
                      "name": "TBYB",
                      "options": "Try free for 14 days",
                      "category": "TRY_BEFORE_YOU_BUY",
                      "billingPolicy": {
                          "fixed": {
                              "checkoutCharge": {
                                  "type": "PRICE",
                                  "value": {
                                      "fixedValue": 0
                                  }
                              },
                              "remainingBalanceChargeTrigger": "TIME_AFTER_CHECKOUT",
                              "remainingBalanceChargeTimeAfterCheckout": "P14D"
                          }
                      },
                      "inventoryPolicy": {
                          "reserve": "ON_SALE"
                      },
                      "deliveryPolicy": {
                          "fixed": {
                              "fulfillmentTrigger": "ASAP"
                          }
                      }
                  }
              ]
          },
          "resources": {
              "productIds": [
                  "gid://shopify/Product/121709582"
              ],
              "productVariantIds": []
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
    mutation createSellingPlanGroup($input: SellingPlanGroupInput!, $resources: SellingPlanGroupResourceInput) {
      sellingPlanGroupCreate(input: $input, resources: $resources) {
        sellingPlanGroup {
          id
          sellingPlans(first: 1) {
            edges {
              node {
                id
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
    "input": {
      "name": "TBYB",
      "merchantCode": "tbyb",
      "options": [
        "Try before you buy"
      ],
      "sellingPlansToCreate": [
        {
          "name": "TBYB",
          "options": "Try free for 14 days",
          "category": "TRY_BEFORE_YOU_BUY",
          "billingPolicy": {
            "fixed": {
              "checkoutCharge": {
                "type": "PRICE",
                "value": {
                  "fixedValue": 0
                }
              },
              "remainingBalanceChargeTrigger": "TIME_AFTER_CHECKOUT",
              "remainingBalanceChargeTimeAfterCheckout": "P14D"
            }
          },
          "inventoryPolicy": {
            "reserve": "ON_SALE"
          },
          "deliveryPolicy": {
            "fixed": {
              "fulfillmentTrigger": "ASAP"
            }
          }
        }
      ]
    },
    "resources": {
      "productIds": [
        "gid://shopify/Product/121709582"
      ],
      "productVariantIds": []
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation createSellingPlanGroup($input: SellingPlanGroupInput!, $resources: SellingPlanGroupResourceInput) {
        sellingPlanGroupCreate(input: $input, resources: $resources) {
          sellingPlanGroup {
            id
            sellingPlans(first: 1) {
              edges {
                node {
                  id
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
          "input": {
              "name": "TBYB",
              "merchantCode": "tbyb",
              "options": [
                  "Try before you buy"
              ],
              "sellingPlansToCreate": [
                  {
                      "name": "TBYB",
                      "options": "Try free for 14 days",
                      "category": "TRY_BEFORE_YOU_BUY",
                      "billingPolicy": {
                          "fixed": {
                              "checkoutCharge": {
                                  "type": "PRICE",
                                  "value": {
                                      "fixedValue": 0
                                  }
                              },
                              "remainingBalanceChargeTrigger": "TIME_AFTER_CHECKOUT",
                              "remainingBalanceChargeTimeAfterCheckout": "P14D"
                          }
                      },
                      "inventoryPolicy": {
                          "reserve": "ON_SALE"
                      },
                      "deliveryPolicy": {
                          "fixed": {
                              "fulfillmentTrigger": "ASAP"
                          }
                      }
                  }
              ]
          },
          "resources": {
              "productIds": [
                  "gid://shopify/Product/121709582"
              ],
              "productVariantIds": []
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation createSellingPlanGroup($input: SellingPlanGroupInput!, $resources: SellingPlanGroupResourceInput) {
    sellingPlanGroupCreate(input: $input, resources: $resources) {
      sellingPlanGroup {
        id
        sellingPlans(first: 1) {
          edges {
            node {
              id
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
    "input": {
      "name": "TBYB",
      "merchantCode": "tbyb",
      "options": [
        "Try before you buy"
      ],
      "sellingPlansToCreate": [
        {
          "name": "TBYB",
          "options": "Try free for 14 days",
          "category": "TRY_BEFORE_YOU_BUY",
          "billingPolicy": {
            "fixed": {
              "checkoutCharge": {
                "type": "PRICE",
                "value": {
                  "fixedValue": 0
                }
              },
              "remainingBalanceChargeTrigger": "TIME_AFTER_CHECKOUT",
              "remainingBalanceChargeTimeAfterCheckout": "P14D"
            }
          },
          "inventoryPolicy": {
            "reserve": "ON_SALE"
          },
          "deliveryPolicy": {
            "fixed": {
              "fulfillmentTrigger": "ASAP"
            }
          }
        }
      ]
    },
    "resources": {
      "productIds": [
        "gid://shopify/Product/121709582"
      ],
      "productVariantIds": []
    }
  }'
  ```

  #### Response

  ```json
  {
    "sellingPlanGroupCreate": {
      "sellingPlanGroup": {
        "id": "gid://shopify/SellingPlanGroup/1039518935",
        "sellingPlans": {
          "edges": [
            {
              "node": {
                "id": "gid://shopify/SellingPlan/1070277430"
              }
            }
          ]
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Create a prepaid selling plan group with anchor dates

  #### Query

  ```graphql
  mutation createSellingPlanGroup($input: SellingPlanGroupInput!, $resources: SellingPlanGroupResourceInput) {
    sellingPlanGroupCreate(input: $input, resources: $resources) {
      sellingPlanGroup {
        id
        sellingPlans(first: 1) {
          edges {
            node {
              id
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
    "input": {
      "name": "Delivered every week and billed every three weeks",
      "merchantCode": "prepaid-weekly",
      "options": [
        "1 week"
      ],
      "sellingPlansToCreate": [
        {
          "name": "Delivered every week",
          "options": "1 Week(s)",
          "category": "SUBSCRIPTION",
          "billingPolicy": {
            "recurring": {
              "interval": "WEEK",
              "intervalCount": 3,
              "anchors": [
                {
                  "cutoffDay": 2,
                  "day": 4,
                  "type": "WEEKDAY"
                }
              ]
            }
          },
          "pricingPolicies": [
            {
              "fixed": {
                "adjustmentType": "PERCENTAGE",
                "adjustmentValue": {
                  "percentage": 25
                }
              }
            }
          ],
          "deliveryPolicy": {
            "recurring": {
              "interval": "WEEK",
              "intervalCount": 1,
              "anchors": [
                {
                  "cutoffDay": 2,
                  "day": 4,
                  "type": "WEEKDAY"
                }
              ]
            }
          }
        }
      ]
    },
    "resources": {
      "productIds": [
        "gid://shopify/Product/121709582"
      ],
      "productVariantIds": []
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
  "query": "mutation createSellingPlanGroup($input: SellingPlanGroupInput!, $resources: SellingPlanGroupResourceInput) { sellingPlanGroupCreate(input: $input, resources: $resources) { sellingPlanGroup { id sellingPlans(first: 1) { edges { node { id } } } } userErrors { field message } } }",
   "variables": {
      "input": {
        "name": "Delivered every week and billed every three weeks",
        "merchantCode": "prepaid-weekly",
        "options": [
          "1 week"
        ],
        "sellingPlansToCreate": [
          {
            "name": "Delivered every week",
            "options": "1 Week(s)",
            "category": "SUBSCRIPTION",
            "billingPolicy": {
              "recurring": {
                "interval": "WEEK",
                "intervalCount": 3,
                "anchors": [
                  {
                    "cutoffDay": 2,
                    "day": 4,
                    "type": "WEEKDAY"
                  }
                ]
              }
            },
            "pricingPolicies": [
              {
                "fixed": {
                  "adjustmentType": "PERCENTAGE",
                  "adjustmentValue": {
                    "percentage": 25
                  }
                }
              }
            ],
            "deliveryPolicy": {
              "recurring": {
                "interval": "WEEK",
                "intervalCount": 1,
                "anchors": [
                  {
                    "cutoffDay": 2,
                    "day": 4,
                    "type": "WEEKDAY"
                  }
                ]
              }
            }
          }
        ]
      },
      "resources": {
        "productIds": [
          "gid://shopify/Product/121709582"
        ],
        "productVariantIds": []
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
    mutation createSellingPlanGroup($input: SellingPlanGroupInput!, $resources: SellingPlanGroupResourceInput) {
      sellingPlanGroupCreate(input: $input, resources: $resources) {
        sellingPlanGroup {
          id
          sellingPlans(first: 1) {
            edges {
              node {
                id
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
          "input": {
              "name": "Delivered every week and billed every three weeks",
              "merchantCode": "prepaid-weekly",
              "options": [
                  "1 week"
              ],
              "sellingPlansToCreate": [
                  {
                      "name": "Delivered every week",
                      "options": "1 Week(s)",
                      "category": "SUBSCRIPTION",
                      "billingPolicy": {
                          "recurring": {
                              "interval": "WEEK",
                              "intervalCount": 3,
                              "anchors": [
                                  {
                                      "cutoffDay": 2,
                                      "day": 4,
                                      "type": "WEEKDAY"
                                  }
                              ]
                          }
                      },
                      "pricingPolicies": [
                          {
                              "fixed": {
                                  "adjustmentType": "PERCENTAGE",
                                  "adjustmentValue": {
                                      "percentage": 25
                                  }
                              }
                          }
                      ],
                      "deliveryPolicy": {
                          "recurring": {
                              "interval": "WEEK",
                              "intervalCount": 1,
                              "anchors": [
                                  {
                                      "cutoffDay": 2,
                                      "day": 4,
                                      "type": "WEEKDAY"
                                  }
                              ]
                          }
                      }
                  }
              ]
          },
          "resources": {
              "productIds": [
                  "gid://shopify/Product/121709582"
              ],
              "productVariantIds": []
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
    mutation createSellingPlanGroup($input: SellingPlanGroupInput!, $resources: SellingPlanGroupResourceInput) {
      sellingPlanGroupCreate(input: $input, resources: $resources) {
        sellingPlanGroup {
          id
          sellingPlans(first: 1) {
            edges {
              node {
                id
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
    "input": {
      "name": "Delivered every week and billed every three weeks",
      "merchantCode": "prepaid-weekly",
      "options": [
        "1 week"
      ],
      "sellingPlansToCreate": [
        {
          "name": "Delivered every week",
          "options": "1 Week(s)",
          "category": "SUBSCRIPTION",
          "billingPolicy": {
            "recurring": {
              "interval": "WEEK",
              "intervalCount": 3,
              "anchors": [
                {
                  "cutoffDay": 2,
                  "day": 4,
                  "type": "WEEKDAY"
                }
              ]
            }
          },
          "pricingPolicies": [
            {
              "fixed": {
                "adjustmentType": "PERCENTAGE",
                "adjustmentValue": {
                  "percentage": 25
                }
              }
            }
          ],
          "deliveryPolicy": {
            "recurring": {
              "interval": "WEEK",
              "intervalCount": 1,
              "anchors": [
                {
                  "cutoffDay": 2,
                  "day": 4,
                  "type": "WEEKDAY"
                }
              ]
            }
          }
        }
      ]
    },
    "resources": {
      "productIds": [
        "gid://shopify/Product/121709582"
      ],
      "productVariantIds": []
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation createSellingPlanGroup($input: SellingPlanGroupInput!, $resources: SellingPlanGroupResourceInput) {
        sellingPlanGroupCreate(input: $input, resources: $resources) {
          sellingPlanGroup {
            id
            sellingPlans(first: 1) {
              edges {
                node {
                  id
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
          "input": {
              "name": "Delivered every week and billed every three weeks",
              "merchantCode": "prepaid-weekly",
              "options": [
                  "1 week"
              ],
              "sellingPlansToCreate": [
                  {
                      "name": "Delivered every week",
                      "options": "1 Week(s)",
                      "category": "SUBSCRIPTION",
                      "billingPolicy": {
                          "recurring": {
                              "interval": "WEEK",
                              "intervalCount": 3,
                              "anchors": [
                                  {
                                      "cutoffDay": 2,
                                      "day": 4,
                                      "type": "WEEKDAY"
                                  }
                              ]
                          }
                      },
                      "pricingPolicies": [
                          {
                              "fixed": {
                                  "adjustmentType": "PERCENTAGE",
                                  "adjustmentValue": {
                                      "percentage": 25
                                  }
                              }
                          }
                      ],
                      "deliveryPolicy": {
                          "recurring": {
                              "interval": "WEEK",
                              "intervalCount": 1,
                              "anchors": [
                                  {
                                      "cutoffDay": 2,
                                      "day": 4,
                                      "type": "WEEKDAY"
                                  }
                              ]
                          }
                      }
                  }
              ]
          },
          "resources": {
              "productIds": [
                  "gid://shopify/Product/121709582"
              ],
              "productVariantIds": []
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation createSellingPlanGroup($input: SellingPlanGroupInput!, $resources: SellingPlanGroupResourceInput) {
    sellingPlanGroupCreate(input: $input, resources: $resources) {
      sellingPlanGroup {
        id
        sellingPlans(first: 1) {
          edges {
            node {
              id
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
    "input": {
      "name": "Delivered every week and billed every three weeks",
      "merchantCode": "prepaid-weekly",
      "options": [
        "1 week"
      ],
      "sellingPlansToCreate": [
        {
          "name": "Delivered every week",
          "options": "1 Week(s)",
          "category": "SUBSCRIPTION",
          "billingPolicy": {
            "recurring": {
              "interval": "WEEK",
              "intervalCount": 3,
              "anchors": [
                {
                  "cutoffDay": 2,
                  "day": 4,
                  "type": "WEEKDAY"
                }
              ]
            }
          },
          "pricingPolicies": [
            {
              "fixed": {
                "adjustmentType": "PERCENTAGE",
                "adjustmentValue": {
                  "percentage": 25
                }
              }
            }
          ],
          "deliveryPolicy": {
            "recurring": {
              "interval": "WEEK",
              "intervalCount": 1,
              "anchors": [
                {
                  "cutoffDay": 2,
                  "day": 4,
                  "type": "WEEKDAY"
                }
              ]
            }
          }
        }
      ]
    },
    "resources": {
      "productIds": [
        "gid://shopify/Product/121709582"
      ],
      "productVariantIds": []
    }
  }'
  ```

  #### Response

  ```json
  {
    "sellingPlanGroupCreate": {
      "sellingPlanGroup": {
        "id": "gid://shopify/SellingPlanGroup/1039518936",
        "sellingPlans": {
          "edges": [
            {
              "node": {
                "id": "gid://shopify/SellingPlan/1070277431"
              }
            }
          ]
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Create a selling plan group with metafields

  #### Query

  ```graphql
  mutation createSellingPlanGroup($input: SellingPlanGroupInput!, $resources: SellingPlanGroupResourceInput) {
    sellingPlanGroupCreate(input: $input, resources: $resources) {
      sellingPlanGroup {
        id
        sellingPlans(first: 1) {
          edges {
            node {
              id
              metafields(first: 1) {
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
      "name": "Subscribe and save",
      "merchantCode": "subscribe-and-save",
      "appId": "groovy",
      "options": [
        "Delivery every",
        "Delivery interval",
        "Fun every"
      ],
      "position": 1,
      "description": "Subscribe and save group",
      "sellingPlansToCreate": [
        {
          "name": "Pay every month deliver every month",
          "options": [
            "1",
            "month",
            "day"
          ],
          "metafields": [
            {
              "namespace": "for_testing",
              "key": "my_key",
              "value": "selling plan metafield",
              "type": "single_line_text_field"
            }
          ],
          "position": 1,
          "category": "SUBSCRIPTION",
          "billingPolicy": {
            "recurring": {
              "interval": "MONTH",
              "intervalCount": 1,
              "anchors": [
                {
                  "type": "MONTHDAY",
                  "day": 26
                }
              ]
            }
          },
          "deliveryPolicy": {
            "recurring": {
              "interval": "MONTH",
              "intervalCount": 1,
              "anchors": [
                {
                  "type": "MONTHDAY",
                  "day": 26
                }
              ],
              "cutoff": 5,
              "intent": "FULFILLMENT_BEGIN",
              "preAnchorBehavior": "ASAP"
            }
          },
          "inventoryPolicy": {
            "reserve": "ON_SALE"
          },
          "pricingPolicies": [
            {
              "fixed": {
                "adjustmentType": "PERCENTAGE",
                "adjustmentValue": {
                  "percentage": 25
                }
              }
            },
            {
              "recurring": {
                "afterCycle": 3,
                "adjustmentType": "PERCENTAGE",
                "adjustmentValue": {
                  "percentage": 26
                }
              }
            }
          ]
        }
      ]
    },
    "resources": {}
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation createSellingPlanGroup($input: SellingPlanGroupInput!, $resources: SellingPlanGroupResourceInput) { sellingPlanGroupCreate(input: $input, resources: $resources) { sellingPlanGroup { id sellingPlans(first: 1) { edges { node { id metafields(first: 1) { edges { node { id namespace key value } } } } } } } userErrors { field message } } }",
   "variables": {
      "input": {
        "name": "Subscribe and save",
        "merchantCode": "subscribe-and-save",
        "appId": "groovy",
        "options": [
          "Delivery every",
          "Delivery interval",
          "Fun every"
        ],
        "position": 1,
        "description": "Subscribe and save group",
        "sellingPlansToCreate": [
          {
            "name": "Pay every month deliver every month",
            "options": [
              "1",
              "month",
              "day"
            ],
            "metafields": [
              {
                "namespace": "for_testing",
                "key": "my_key",
                "value": "selling plan metafield",
                "type": "single_line_text_field"
              }
            ],
            "position": 1,
            "category": "SUBSCRIPTION",
            "billingPolicy": {
              "recurring": {
                "interval": "MONTH",
                "intervalCount": 1,
                "anchors": [
                  {
                    "type": "MONTHDAY",
                    "day": 26
                  }
                ]
              }
            },
            "deliveryPolicy": {
              "recurring": {
                "interval": "MONTH",
                "intervalCount": 1,
                "anchors": [
                  {
                    "type": "MONTHDAY",
                    "day": 26
                  }
                ],
                "cutoff": 5,
                "intent": "FULFILLMENT_BEGIN",
                "preAnchorBehavior": "ASAP"
              }
            },
            "inventoryPolicy": {
              "reserve": "ON_SALE"
            },
            "pricingPolicies": [
              {
                "fixed": {
                  "adjustmentType": "PERCENTAGE",
                  "adjustmentValue": {
                    "percentage": 25
                  }
                }
              },
              {
                "recurring": {
                  "afterCycle": 3,
                  "adjustmentType": "PERCENTAGE",
                  "adjustmentValue": {
                    "percentage": 26
                  }
                }
              }
            ]
          }
        ]
      },
      "resources": {}
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
    mutation createSellingPlanGroup($input: SellingPlanGroupInput!, $resources: SellingPlanGroupResourceInput) {
      sellingPlanGroupCreate(input: $input, resources: $resources) {
        sellingPlanGroup {
          id
          sellingPlans(first: 1) {
            edges {
              node {
                id
                metafields(first: 1) {
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
              "name": "Subscribe and save",
              "merchantCode": "subscribe-and-save",
              "appId": "groovy",
              "options": [
                  "Delivery every",
                  "Delivery interval",
                  "Fun every"
              ],
              "position": 1,
              "description": "Subscribe and save group",
              "sellingPlansToCreate": [
                  {
                      "name": "Pay every month deliver every month",
                      "options": [
                          "1",
                          "month",
                          "day"
                      ],
                      "metafields": [
                          {
                              "namespace": "for_testing",
                              "key": "my_key",
                              "value": "selling plan metafield",
                              "type": "single_line_text_field"
                          }
                      ],
                      "position": 1,
                      "category": "SUBSCRIPTION",
                      "billingPolicy": {
                          "recurring": {
                              "interval": "MONTH",
                              "intervalCount": 1,
                              "anchors": [
                                  {
                                      "type": "MONTHDAY",
                                      "day": 26
                                  }
                              ]
                          }
                      },
                      "deliveryPolicy": {
                          "recurring": {
                              "interval": "MONTH",
                              "intervalCount": 1,
                              "anchors": [
                                  {
                                      "type": "MONTHDAY",
                                      "day": 26
                                  }
                              ],
                              "cutoff": 5,
                              "intent": "FULFILLMENT_BEGIN",
                              "preAnchorBehavior": "ASAP"
                          }
                      },
                      "inventoryPolicy": {
                          "reserve": "ON_SALE"
                      },
                      "pricingPolicies": [
                          {
                              "fixed": {
                                  "adjustmentType": "PERCENTAGE",
                                  "adjustmentValue": {
                                      "percentage": 25
                                  }
                              }
                          },
                          {
                              "recurring": {
                                  "afterCycle": 3,
                                  "adjustmentType": "PERCENTAGE",
                                  "adjustmentValue": {
                                      "percentage": 26
                                  }
                              }
                          }
                      ]
                  }
              ]
          },
          "resources": {}
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
    mutation createSellingPlanGroup($input: SellingPlanGroupInput!, $resources: SellingPlanGroupResourceInput) {
      sellingPlanGroupCreate(input: $input, resources: $resources) {
        sellingPlanGroup {
          id
          sellingPlans(first: 1) {
            edges {
              node {
                id
                metafields(first: 1) {
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
      "name": "Subscribe and save",
      "merchantCode": "subscribe-and-save",
      "appId": "groovy",
      "options": [
        "Delivery every",
        "Delivery interval",
        "Fun every"
      ],
      "position": 1,
      "description": "Subscribe and save group",
      "sellingPlansToCreate": [
        {
          "name": "Pay every month deliver every month",
          "options": [
            "1",
            "month",
            "day"
          ],
          "metafields": [
            {
              "namespace": "for_testing",
              "key": "my_key",
              "value": "selling plan metafield",
              "type": "single_line_text_field"
            }
          ],
          "position": 1,
          "category": "SUBSCRIPTION",
          "billingPolicy": {
            "recurring": {
              "interval": "MONTH",
              "intervalCount": 1,
              "anchors": [
                {
                  "type": "MONTHDAY",
                  "day": 26
                }
              ]
            }
          },
          "deliveryPolicy": {
            "recurring": {
              "interval": "MONTH",
              "intervalCount": 1,
              "anchors": [
                {
                  "type": "MONTHDAY",
                  "day": 26
                }
              ],
              "cutoff": 5,
              "intent": "FULFILLMENT_BEGIN",
              "preAnchorBehavior": "ASAP"
            }
          },
          "inventoryPolicy": {
            "reserve": "ON_SALE"
          },
          "pricingPolicies": [
            {
              "fixed": {
                "adjustmentType": "PERCENTAGE",
                "adjustmentValue": {
                  "percentage": 25
                }
              }
            },
            {
              "recurring": {
                "afterCycle": 3,
                "adjustmentType": "PERCENTAGE",
                "adjustmentValue": {
                  "percentage": 26
                }
              }
            }
          ]
        }
      ]
    },
    "resources": {}
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation createSellingPlanGroup($input: SellingPlanGroupInput!, $resources: SellingPlanGroupResourceInput) {
        sellingPlanGroupCreate(input: $input, resources: $resources) {
          sellingPlanGroup {
            id
            sellingPlans(first: 1) {
              edges {
                node {
                  id
                  metafields(first: 1) {
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
              "name": "Subscribe and save",
              "merchantCode": "subscribe-and-save",
              "appId": "groovy",
              "options": [
                  "Delivery every",
                  "Delivery interval",
                  "Fun every"
              ],
              "position": 1,
              "description": "Subscribe and save group",
              "sellingPlansToCreate": [
                  {
                      "name": "Pay every month deliver every month",
                      "options": [
                          "1",
                          "month",
                          "day"
                      ],
                      "metafields": [
                          {
                              "namespace": "for_testing",
                              "key": "my_key",
                              "value": "selling plan metafield",
                              "type": "single_line_text_field"
                          }
                      ],
                      "position": 1,
                      "category": "SUBSCRIPTION",
                      "billingPolicy": {
                          "recurring": {
                              "interval": "MONTH",
                              "intervalCount": 1,
                              "anchors": [
                                  {
                                      "type": "MONTHDAY",
                                      "day": 26
                                  }
                              ]
                          }
                      },
                      "deliveryPolicy": {
                          "recurring": {
                              "interval": "MONTH",
                              "intervalCount": 1,
                              "anchors": [
                                  {
                                      "type": "MONTHDAY",
                                      "day": 26
                                  }
                              ],
                              "cutoff": 5,
                              "intent": "FULFILLMENT_BEGIN",
                              "preAnchorBehavior": "ASAP"
                          }
                      },
                      "inventoryPolicy": {
                          "reserve": "ON_SALE"
                      },
                      "pricingPolicies": [
                          {
                              "fixed": {
                                  "adjustmentType": "PERCENTAGE",
                                  "adjustmentValue": {
                                      "percentage": 25
                                  }
                              }
                          },
                          {
                              "recurring": {
                                  "afterCycle": 3,
                                  "adjustmentType": "PERCENTAGE",
                                  "adjustmentValue": {
                                      "percentage": 26
                                  }
                              }
                          }
                      ]
                  }
              ]
          },
          "resources": {}
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation createSellingPlanGroup($input: SellingPlanGroupInput!, $resources: SellingPlanGroupResourceInput) {
    sellingPlanGroupCreate(input: $input, resources: $resources) {
      sellingPlanGroup {
        id
        sellingPlans(first: 1) {
          edges {
            node {
              id
              metafields(first: 1) {
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
      "name": "Subscribe and save",
      "merchantCode": "subscribe-and-save",
      "appId": "groovy",
      "options": [
        "Delivery every",
        "Delivery interval",
        "Fun every"
      ],
      "position": 1,
      "description": "Subscribe and save group",
      "sellingPlansToCreate": [
        {
          "name": "Pay every month deliver every month",
          "options": [
            "1",
            "month",
            "day"
          ],
          "metafields": [
            {
              "namespace": "for_testing",
              "key": "my_key",
              "value": "selling plan metafield",
              "type": "single_line_text_field"
            }
          ],
          "position": 1,
          "category": "SUBSCRIPTION",
          "billingPolicy": {
            "recurring": {
              "interval": "MONTH",
              "intervalCount": 1,
              "anchors": [
                {
                  "type": "MONTHDAY",
                  "day": 26
                }
              ]
            }
          },
          "deliveryPolicy": {
            "recurring": {
              "interval": "MONTH",
              "intervalCount": 1,
              "anchors": [
                {
                  "type": "MONTHDAY",
                  "day": 26
                }
              ],
              "cutoff": 5,
              "intent": "FULFILLMENT_BEGIN",
              "preAnchorBehavior": "ASAP"
            }
          },
          "inventoryPolicy": {
            "reserve": "ON_SALE"
          },
          "pricingPolicies": [
            {
              "fixed": {
                "adjustmentType": "PERCENTAGE",
                "adjustmentValue": {
                  "percentage": 25
                }
              }
            },
            {
              "recurring": {
                "afterCycle": 3,
                "adjustmentType": "PERCENTAGE",
                "adjustmentValue": {
                  "percentage": 26
                }
              }
            }
          ]
        }
      ]
    },
    "resources": {}
  }'
  ```

  #### Response

  ```json
  {
    "sellingPlanGroupCreate": {
      "sellingPlanGroup": {
        "id": "gid://shopify/SellingPlanGroup/1039518934",
        "sellingPlans": {
          "edges": [
            {
              "node": {
                "id": "gid://shopify/SellingPlan/1070277429",
                "metafields": {
                  "edges": [
                    {
                      "node": {
                        "id": "gid://shopify/Metafield/1069228936",
                        "namespace": "for_testing",
                        "key": "my_key",
                        "value": "selling plan metafield"
                      }
                    }
                  ]
                }
              }
            }
          ]
        }
      },
      "userErrors": []
    }
  }
  ```

* ### sellingPlanGroupCreate reference
