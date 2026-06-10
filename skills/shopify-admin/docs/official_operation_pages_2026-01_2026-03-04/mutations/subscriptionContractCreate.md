---
title: subscriptionContractCreate - GraphQL Admin
description: >-
  Creates a subscription contract draft, which is an intention to create a new
  subscription. The draft lets you incrementally build and modify subscription
  details before committing them to create the actual
  [`SubscriptionContract`](https://shopify.dev/docs/api/admin-graphql/latest/objects/SubscriptionContract).


  The mutation requires
  [`Customer`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer)
  information, billing details, and contract configuration including the
  [`SubscriptionBillingPolicy`](https://shopify.dev/docs/api/admin-graphql/latest/objects/SubscriptionBillingPolicy)
  and
  [`SubscriptionDeliveryPolicy`](https://shopify.dev/docs/api/admin-graphql/latest/objects/SubscriptionDeliveryPolicy).
  You can specify the
  [`CustomerPaymentMethod`](https://shopify.dev/docs/api/admin-graphql/latest/objects/CustomerPaymentMethod),
  the
  [`MailingAddress`](https://shopify.dev/docs/api/admin-graphql/latest/objects/MailingAddress)
  for shipping, and subscription intervals.


  After you create the draft, you can either modify it with the
  [`subscriptionDraftUpdate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/subscriptionDraftUpdate)
  mutation or finalize and create the active subscription contract with
  [`subscriptionDraftCommit`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/subscriptionDraftCommit).


  Learn more about [building subscription
  contracts](https://shopify.dev/docs/apps/build/purchase-options/subscriptions/contracts/build-a-subscription-contract).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/subscriptionContractCreate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/subscriptionContractCreate.md
---

# subscription​Contract​Create

mutation

Requires `write_own_subscription_contracts` access scope. Also: The user must have manage\_orders\_information permission.

Creates a subscription contract draft, which is an intention to create a new subscription. The draft lets you incrementally build and modify subscription details before committing them to create the actual [`SubscriptionContract`](https://shopify.dev/docs/api/admin-graphql/latest/objects/SubscriptionContract).

The mutation requires [`Customer`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer) information, billing details, and contract configuration including the [`SubscriptionBillingPolicy`](https://shopify.dev/docs/api/admin-graphql/latest/objects/SubscriptionBillingPolicy) and [`SubscriptionDeliveryPolicy`](https://shopify.dev/docs/api/admin-graphql/latest/objects/SubscriptionDeliveryPolicy). You can specify the [`CustomerPaymentMethod`](https://shopify.dev/docs/api/admin-graphql/latest/objects/CustomerPaymentMethod), the [`MailingAddress`](https://shopify.dev/docs/api/admin-graphql/latest/objects/MailingAddress) for shipping, and subscription intervals.

After you create the draft, you can either modify it with the [`subscriptionDraftUpdate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/subscriptionDraftUpdate) mutation or finalize and create the active subscription contract with [`subscriptionDraftCommit`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/subscriptionDraftCommit).

Learn more about [building subscription contracts](https://shopify.dev/docs/apps/build/purchase-options/subscriptions/contracts/build-a-subscription-contract).

## Arguments

* input

  [Subscription​Contract​Create​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/SubscriptionContractCreateInput)

  required

  The properties of the new Subscription Contract.

***

## Subscription​Contract​Create​Payload returns

* draft

  [Subscription​Draft](https://shopify.dev/docs/api/admin-graphql/latest/objects/SubscriptionDraft)

  The Subscription Contract object.

* user​Errors

  [\[Subscription​Draft​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/SubscriptionDraftUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create a subscription contract with draft input

  #### Query

  ```graphql
  mutation createSubscriptionContract($input: SubscriptionContractCreateInput!) {
    subscriptionContractCreate(input: $input) {
      draft {
        id
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
      "customerId": "gid://shopify/Customer/544365967",
      "currencyCode": "USD",
      "nextBillingDate": "2024-10-11T21:11:01-04:00",
      "contract": {
        "status": "ACTIVE",
        "note": "Note of a thing.",
        "customAttributes": [
          {
            "key": "Test",
            "value": "Test value"
          }
        ],
        "paymentMethodId": "gid://shopify/CustomerPaymentMethod/b7cc6e3267aace169e516ed48be72dff",
        "billingPolicy": {
          "minCycles": 3,
          "maxCycles": 12,
          "intervalCount": 1,
          "interval": "MONTH",
          "anchors": [
            {
              "type": "MONTHDAY",
              "day": 12
            }
          ]
        },
        "deliveryPolicy": {
          "intervalCount": 1,
          "interval": "MONTH",
          "anchors": [
            {
              "type": "MONTHDAY",
              "day": 13
            }
          ]
        },
        "deliveryPrice": 2.99,
        "deliveryMethod": {
          "shipping": {
            "address": {
              "firstName": "Mont",
              "lastName": "Réal",
              "address1": "490 Rue De La Gauchetière O",
              "country": "Canada",
              "province": "Québec",
              "phone": "+16135551212",
              "zip": "H2Z 0B3",
              "city": "Montréal"
            },
            "shippingOption": {
              "title": "Subscription shipping",
              "presentmentTitle": "Translated shipping for subscription",
              "description": "5-7 Days",
              "code": "GROUND",
              "carrierServiceId": null
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
  "query": "mutation createSubscriptionContract($input: SubscriptionContractCreateInput!) { subscriptionContractCreate(input: $input) { draft { id } userErrors { field message } } }",
   "variables": {
      "input": {
        "customerId": "gid://shopify/Customer/544365967",
        "currencyCode": "USD",
        "nextBillingDate": "2024-10-11T21:11:01-04:00",
        "contract": {
          "status": "ACTIVE",
          "note": "Note of a thing.",
          "customAttributes": [
            {
              "key": "Test",
              "value": "Test value"
            }
          ],
          "paymentMethodId": "gid://shopify/CustomerPaymentMethod/b7cc6e3267aace169e516ed48be72dff",
          "billingPolicy": {
            "minCycles": 3,
            "maxCycles": 12,
            "intervalCount": 1,
            "interval": "MONTH",
            "anchors": [
              {
                "type": "MONTHDAY",
                "day": 12
              }
            ]
          },
          "deliveryPolicy": {
            "intervalCount": 1,
            "interval": "MONTH",
            "anchors": [
              {
                "type": "MONTHDAY",
                "day": 13
              }
            ]
          },
          "deliveryPrice": 2.99,
          "deliveryMethod": {
            "shipping": {
              "address": {
                "firstName": "Mont",
                "lastName": "Réal",
                "address1": "490 Rue De La Gauchetière O",
                "country": "Canada",
                "province": "Québec",
                "phone": "+16135551212",
                "zip": "H2Z 0B3",
                "city": "Montréal"
              },
              "shippingOption": {
                "title": "Subscription shipping",
                "presentmentTitle": "Translated shipping for subscription",
                "description": "5-7 Days",
                "code": "GROUND",
                "carrierServiceId": null
              }
            }
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
    mutation createSubscriptionContract($input: SubscriptionContractCreateInput!) {
      subscriptionContractCreate(input: $input) {
        draft {
          id
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
              "customerId": "gid://shopify/Customer/544365967",
              "currencyCode": "USD",
              "nextBillingDate": "2024-10-11T21:11:01-04:00",
              "contract": {
                  "status": "ACTIVE",
                  "note": "Note of a thing.",
                  "customAttributes": [
                      {
                          "key": "Test",
                          "value": "Test value"
                      }
                  ],
                  "paymentMethodId": "gid://shopify/CustomerPaymentMethod/b7cc6e3267aace169e516ed48be72dff",
                  "billingPolicy": {
                      "minCycles": 3,
                      "maxCycles": 12,
                      "intervalCount": 1,
                      "interval": "MONTH",
                      "anchors": [
                          {
                              "type": "MONTHDAY",
                              "day": 12
                          }
                      ]
                  },
                  "deliveryPolicy": {
                      "intervalCount": 1,
                      "interval": "MONTH",
                      "anchors": [
                          {
                              "type": "MONTHDAY",
                              "day": 13
                          }
                      ]
                  },
                  "deliveryPrice": 2.99,
                  "deliveryMethod": {
                      "shipping": {
                          "address": {
                              "firstName": "Mont",
                              "lastName": "Réal",
                              "address1": "490 Rue De La Gauchetière O",
                              "country": "Canada",
                              "province": "Québec",
                              "phone": "+16135551212",
                              "zip": "H2Z 0B3",
                              "city": "Montréal"
                          },
                          "shippingOption": {
                              "title": "Subscription shipping",
                              "presentmentTitle": "Translated shipping for subscription",
                              "description": "5-7 Days",
                              "code": "GROUND",
                              "carrierServiceId": null
                          }
                      }
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
    mutation createSubscriptionContract($input: SubscriptionContractCreateInput!) {
      subscriptionContractCreate(input: $input) {
        draft {
          id
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
      "customerId": "gid://shopify/Customer/544365967",
      "currencyCode": "USD",
      "nextBillingDate": "2024-10-11T21:11:01-04:00",
      "contract": {
        "status": "ACTIVE",
        "note": "Note of a thing.",
        "customAttributes": [
          {
            "key": "Test",
            "value": "Test value"
          }
        ],
        "paymentMethodId": "gid://shopify/CustomerPaymentMethod/b7cc6e3267aace169e516ed48be72dff",
        "billingPolicy": {
          "minCycles": 3,
          "maxCycles": 12,
          "intervalCount": 1,
          "interval": "MONTH",
          "anchors": [
            {
              "type": "MONTHDAY",
              "day": 12
            }
          ]
        },
        "deliveryPolicy": {
          "intervalCount": 1,
          "interval": "MONTH",
          "anchors": [
            {
              "type": "MONTHDAY",
              "day": 13
            }
          ]
        },
        "deliveryPrice": 2.99,
        "deliveryMethod": {
          "shipping": {
            "address": {
              "firstName": "Mont",
              "lastName": "Réal",
              "address1": "490 Rue De La Gauchetière O",
              "country": "Canada",
              "province": "Québec",
              "phone": "+16135551212",
              "zip": "H2Z 0B3",
              "city": "Montréal"
            },
            "shippingOption": {
              "title": "Subscription shipping",
              "presentmentTitle": "Translated shipping for subscription",
              "description": "5-7 Days",
              "code": "GROUND",
              "carrierServiceId": null
            }
          }
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
      "query": `mutation createSubscriptionContract($input: SubscriptionContractCreateInput!) {
        subscriptionContractCreate(input: $input) {
          draft {
            id
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "input": {
              "customerId": "gid://shopify/Customer/544365967",
              "currencyCode": "USD",
              "nextBillingDate": "2024-10-11T21:11:01-04:00",
              "contract": {
                  "status": "ACTIVE",
                  "note": "Note of a thing.",
                  "customAttributes": [
                      {
                          "key": "Test",
                          "value": "Test value"
                      }
                  ],
                  "paymentMethodId": "gid://shopify/CustomerPaymentMethod/b7cc6e3267aace169e516ed48be72dff",
                  "billingPolicy": {
                      "minCycles": 3,
                      "maxCycles": 12,
                      "intervalCount": 1,
                      "interval": "MONTH",
                      "anchors": [
                          {
                              "type": "MONTHDAY",
                              "day": 12
                          }
                      ]
                  },
                  "deliveryPolicy": {
                      "intervalCount": 1,
                      "interval": "MONTH",
                      "anchors": [
                          {
                              "type": "MONTHDAY",
                              "day": 13
                          }
                      ]
                  },
                  "deliveryPrice": 2.99,
                  "deliveryMethod": {
                      "shipping": {
                          "address": {
                              "firstName": "Mont",
                              "lastName": "Réal",
                              "address1": "490 Rue De La Gauchetière O",
                              "country": "Canada",
                              "province": "Québec",
                              "phone": "+16135551212",
                              "zip": "H2Z 0B3",
                              "city": "Montréal"
                          },
                          "shippingOption": {
                              "title": "Subscription shipping",
                              "presentmentTitle": "Translated shipping for subscription",
                              "description": "5-7 Days",
                              "code": "GROUND",
                              "carrierServiceId": null
                          }
                      }
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
  'mutation createSubscriptionContract($input: SubscriptionContractCreateInput!) {
    subscriptionContractCreate(input: $input) {
      draft {
        id
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
      "customerId": "gid://shopify/Customer/544365967",
      "currencyCode": "USD",
      "nextBillingDate": "2024-10-11T21:11:01-04:00",
      "contract": {
        "status": "ACTIVE",
        "note": "Note of a thing.",
        "customAttributes": [
          {
            "key": "Test",
            "value": "Test value"
          }
        ],
        "paymentMethodId": "gid://shopify/CustomerPaymentMethod/b7cc6e3267aace169e516ed48be72dff",
        "billingPolicy": {
          "minCycles": 3,
          "maxCycles": 12,
          "intervalCount": 1,
          "interval": "MONTH",
          "anchors": [
            {
              "type": "MONTHDAY",
              "day": 12
            }
          ]
        },
        "deliveryPolicy": {
          "intervalCount": 1,
          "interval": "MONTH",
          "anchors": [
            {
              "type": "MONTHDAY",
              "day": 13
            }
          ]
        },
        "deliveryPrice": 2.99,
        "deliveryMethod": {
          "shipping": {
            "address": {
              "firstName": "Mont",
              "lastName": "Réal",
              "address1": "490 Rue De La Gauchetière O",
              "country": "Canada",
              "province": "Québec",
              "phone": "+16135551212",
              "zip": "H2Z 0B3",
              "city": "Montréal"
            },
            "shippingOption": {
              "title": "Subscription shipping",
              "presentmentTitle": "Translated shipping for subscription",
              "description": "5-7 Days",
              "code": "GROUND",
              "carrierServiceId": null
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
    "subscriptionContractCreate": {
      "draft": {
        "id": "gid://shopify/SubscriptionDraft/1055577422"
      },
      "userErrors": []
    }
  }
  ```

* ### subscriptionContractCreate reference
