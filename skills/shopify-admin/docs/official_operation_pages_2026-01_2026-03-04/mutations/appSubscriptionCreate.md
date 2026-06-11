---
title: appSubscriptionCreate - GraphQL Admin
description: >-
  Creates a recurring or usage-based
  [`AppSubscription`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppSubscription)
  that charges merchants for app features and services. The subscription
  includes one or more
  [`AppSubscriptionLineItem`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppSubscriptionLineItem)
  objects that define the pricing structure, billing intervals, and optional
  [`AppSubscriptionDiscount`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppSubscriptionDiscount)
  values.


  Returns a [confirmation
  URL](https://shopify.dev/docs/api/admin-graphql/latest/mutations/appSubscriptionCreate#returns-confirmationUrl)
  where the merchant approves or declines the charges. After approval, the
  subscription becomes active and billing begins after any trial period expires.
  You can specify
  [`AppSubscriptionReplacementBehavior`](https://shopify.dev/docs/api/admin-graphql/latest/enums/AppSubscriptionReplacementBehavior)
  to control how this subscription interacts with existing active subscriptions.


  Learn more about [creating app
  subscriptions](https://shopify.dev/docs/apps/launch/billing/subscription-billing/create-time-based-subscriptions).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/appSubscriptionCreate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/appSubscriptionCreate.md
---

# app​Subscription​Create

mutation

Creates a recurring or usage-based [`AppSubscription`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppSubscription) that charges merchants for app features and services. The subscription includes one or more [`AppSubscriptionLineItem`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppSubscriptionLineItem) objects that define the pricing structure, billing intervals, and optional [`AppSubscriptionDiscount`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppSubscriptionDiscount) values.

Returns a [confirmation URL](https://shopify.dev/docs/api/admin-graphql/latest/mutations/appSubscriptionCreate#returns-confirmationUrl) where the merchant approves or declines the charges. After approval, the subscription becomes active and billing begins after any trial period expires. You can specify [`AppSubscriptionReplacementBehavior`](https://shopify.dev/docs/api/admin-graphql/latest/enums/AppSubscriptionReplacementBehavior) to control how this subscription interacts with existing active subscriptions.

Learn more about [creating app subscriptions](https://shopify.dev/docs/apps/launch/billing/subscription-billing/create-time-based-subscriptions).

## Arguments

* line​Items

  [\[App​Subscription​Line​Item​Input!\]!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/AppSubscriptionLineItemInput)

  required

  Attaches one or more pricing plans to an app subscription. Only one pricing plan can be defined for each available type.

* name

  [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  required

  A descriptive name for the app subscription.

* replacement​Behavior

  [App​Subscription​Replacement​Behavior](https://shopify.dev/docs/api/admin-graphql/latest/enums/AppSubscriptionReplacementBehavior)

  Default:STANDARD

  The replacement behavior when creating an app subscription for a merchant with an already existing app subscription.

* return​Url

  [URL!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/URL)

  required

  The URL pointing to the page where the merchant is redirected after approving the app subscription.

* test

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Whether the app subscription is a test transaction.

* trial​Days

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The number of days of the free trial period, beginning on the day that the merchant approves the app charges.

***

## App​Subscription​Create​Payload returns

* app​Subscription

  [App​Subscription](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppSubscription)

  The newly-created app subscription.

* confirmation​Url

  [URL](https://shopify.dev/docs/api/admin-graphql/latest/scalars/URL)

  The URL pointing to the page where the merchant approves or declines the charges for an app subscription.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create a subscription for an app on a recurring pricing plan only.

  #### Query

  ```graphql
  mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) {
    appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) {
      userErrors {
        field
        message
      }
      appSubscription {
        id
      }
      confirmationUrl
    }
  }
  ```

  #### Variables

  ```json
  {
    "name": "Super Duper Recurring Plan",
    "returnUrl": "http://super-duper.shopifyapps.com/",
    "lineItems": [
      {
        "plan": {
          "appRecurringPricingDetails": {
            "price": {
              "amount": 10,
              "currencyCode": "USD"
            },
            "interval": "EVERY_30_DAYS"
          }
        }
      }
    ]
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) { appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) { userErrors { field message } appSubscription { id } confirmationUrl } }",
   "variables": {
      "name": "Super Duper Recurring Plan",
      "returnUrl": "http://super-duper.shopifyapps.com/",
      "lineItems": [
        {
          "plan": {
            "appRecurringPricingDetails": {
              "price": {
                "amount": 10,
                "currencyCode": "USD"
              },
              "interval": "EVERY_30_DAYS"
            }
          }
        }
      ]
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
    mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) {
      appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) {
        userErrors {
          field
          message
        }
        appSubscription {
          id
        }
        confirmationUrl
      }
    }`,
    {
      variables: {
          "name": "Super Duper Recurring Plan",
          "returnUrl": "http://super-duper.shopifyapps.com/",
          "lineItems": [
              {
                  "plan": {
                      "appRecurringPricingDetails": {
                          "price": {
                              "amount": 10,
                              "currencyCode": "USD"
                          },
                          "interval": "EVERY_30_DAYS"
                      }
                  }
              }
          ]
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
    mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) {
      appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) {
        userErrors {
          field
          message
        }
        appSubscription {
          id
        }
        confirmationUrl
      }
    }
  QUERY

  variables = {
    "name": "Super Duper Recurring Plan",
    "returnUrl": "http://super-duper.shopifyapps.com/",
    "lineItems": [
      {
        "plan": {
          "appRecurringPricingDetails": {
            "price": {
              "amount": 10,
              "currencyCode": "USD"
            },
            "interval": "EVERY_30_DAYS"
          }
        }
      }
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) {
        appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) {
          userErrors {
            field
            message
          }
          appSubscription {
            id
          }
          confirmationUrl
        }
      }`,
      "variables": {
          "name": "Super Duper Recurring Plan",
          "returnUrl": "http://super-duper.shopifyapps.com/",
          "lineItems": [
              {
                  "plan": {
                      "appRecurringPricingDetails": {
                          "price": {
                              "amount": 10,
                              "currencyCode": "USD"
                          },
                          "interval": "EVERY_30_DAYS"
                      }
                  }
              }
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) {
    appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) {
      userErrors {
        field
        message
      }
      appSubscription {
        id
      }
      confirmationUrl
    }
  }' \
  --variables \
  '{
    "name": "Super Duper Recurring Plan",
    "returnUrl": "http://super-duper.shopifyapps.com/",
    "lineItems": [
      {
        "plan": {
          "appRecurringPricingDetails": {
            "price": {
              "amount": 10,
              "currencyCode": "USD"
            },
            "interval": "EVERY_30_DAYS"
          }
        }
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "appSubscriptionCreate": {
      "userErrors": [],
      "appSubscription": {
        "id": "gid://shopify/AppSubscription/1029266964"
      },
      "confirmationUrl": "https://billingshop.myshopify.com/admin/charges/166357/1029266964/RecurringApplicationCharge/confirm_recurring_application_charge?signature=BAh7BzoHaWRpBBReWT06EmF1dG9fYWN0aXZhdGVU--40f1bb287931224ca72323613fc6255d8a38a2c8"
    }
  }
  ```

* ### Create a subscription for an app on a usage pricing plan only.

  #### Query

  ```graphql
  mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) {
    appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) {
      userErrors {
        field
        message
      }
      appSubscription {
        id
        lineItems {
          id
          plan {
            pricingDetails
            __typename
          }
        }
      }
      confirmationUrl
    }
  }
  ```

  #### Variables

  ```json
  {
    "name": "Super Duper Usage Plan",
    "returnUrl": "http://super-duper.shopifyapps.com/",
    "lineItems": [
      {
        "plan": {
          "appUsagePricingDetails": {
            "terms": "$1 for 100 emails",
            "cappedAmount": {
              "amount": 20,
              "currencyCode": "USD"
            }
          }
        }
      }
    ]
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) { appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) { userErrors { field message } appSubscription { id lineItems { id plan { pricingDetails __typename } } } confirmationUrl } }",
   "variables": {
      "name": "Super Duper Usage Plan",
      "returnUrl": "http://super-duper.shopifyapps.com/",
      "lineItems": [
        {
          "plan": {
            "appUsagePricingDetails": {
              "terms": "$1 for 100 emails",
              "cappedAmount": {
                "amount": 20,
                "currencyCode": "USD"
              }
            }
          }
        }
      ]
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
    mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) {
      appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) {
        userErrors {
          field
          message
        }
        appSubscription {
          id
          lineItems {
            id
            plan {
              pricingDetails
              __typename
            }
          }
        }
        confirmationUrl
      }
    }`,
    {
      variables: {
          "name": "Super Duper Usage Plan",
          "returnUrl": "http://super-duper.shopifyapps.com/",
          "lineItems": [
              {
                  "plan": {
                      "appUsagePricingDetails": {
                          "terms": "$1 for 100 emails",
                          "cappedAmount": {
                              "amount": 20,
                              "currencyCode": "USD"
                          }
                      }
                  }
              }
          ]
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
    mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) {
      appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) {
        userErrors {
          field
          message
        }
        appSubscription {
          id
          lineItems {
            id
            plan {
              pricingDetails
              __typename
            }
          }
        }
        confirmationUrl
      }
    }
  QUERY

  variables = {
    "name": "Super Duper Usage Plan",
    "returnUrl": "http://super-duper.shopifyapps.com/",
    "lineItems": [
      {
        "plan": {
          "appUsagePricingDetails": {
            "terms": "$1 for 100 emails",
            "cappedAmount": {
              "amount": 20,
              "currencyCode": "USD"
            }
          }
        }
      }
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) {
        appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) {
          userErrors {
            field
            message
          }
          appSubscription {
            id
            lineItems {
              id
              plan {
                pricingDetails
                __typename
              }
            }
          }
          confirmationUrl
        }
      }`,
      "variables": {
          "name": "Super Duper Usage Plan",
          "returnUrl": "http://super-duper.shopifyapps.com/",
          "lineItems": [
              {
                  "plan": {
                      "appUsagePricingDetails": {
                          "terms": "$1 for 100 emails",
                          "cappedAmount": {
                              "amount": 20,
                              "currencyCode": "USD"
                          }
                      }
                  }
              }
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) {
    appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) {
      userErrors {
        field
        message
      }
      appSubscription {
        id
        lineItems {
          id
          plan {
            pricingDetails
            __typename
          }
        }
      }
      confirmationUrl
    }
  }' \
  --variables \
  '{
    "name": "Super Duper Usage Plan",
    "returnUrl": "http://super-duper.shopifyapps.com/",
    "lineItems": [
      {
        "plan": {
          "appUsagePricingDetails": {
            "terms": "$1 for 100 emails",
            "cappedAmount": {
              "amount": 20,
              "currencyCode": "USD"
            }
          }
        }
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "appSubscriptionCreate": {
      "userErrors": [],
      "appSubscription": {
        "id": "gid://shopify/AppSubscription/1029266960",
        "lineItems": [
          {
            "id": "gid://shopify/AppSubscriptionLineItem/1029266960?v=1&index=0",
            "plan": {
              "pricingDetails": {},
              "__typename": "AppPlanV2"
            }
          }
        ]
      },
      "confirmationUrl": "https://billingshop.myshopify.com/admin/charges/166357/1029266960/RecurringApplicationCharge/confirm_recurring_application_charge?signature=BAh7BzoHaWRpBBBeWT06EmF1dG9fYWN0aXZhdGVU--6a3125051f687d95ba16132e5fb9a0419e0e4d18"
    }
  }
  ```

* ### Create a subscription for an app on an annual recurring pricing plan.

  #### Query

  ```graphql
  mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) {
    appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) {
      userErrors {
        field
        message
      }
      appSubscription {
        id
      }
      confirmationUrl
    }
  }
  ```

  #### Variables

  ```json
  {
    "name": "Super Duper Recurring Plan",
    "returnUrl": "http://super-duper.shopifyapps.com/",
    "lineItems": [
      {
        "plan": {
          "appRecurringPricingDetails": {
            "price": {
              "amount": 10,
              "currencyCode": "USD"
            },
            "interval": "ANNUAL"
          }
        }
      }
    ]
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) { appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) { userErrors { field message } appSubscription { id } confirmationUrl } }",
   "variables": {
      "name": "Super Duper Recurring Plan",
      "returnUrl": "http://super-duper.shopifyapps.com/",
      "lineItems": [
        {
          "plan": {
            "appRecurringPricingDetails": {
              "price": {
                "amount": 10,
                "currencyCode": "USD"
              },
              "interval": "ANNUAL"
            }
          }
        }
      ]
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
    mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) {
      appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) {
        userErrors {
          field
          message
        }
        appSubscription {
          id
        }
        confirmationUrl
      }
    }`,
    {
      variables: {
          "name": "Super Duper Recurring Plan",
          "returnUrl": "http://super-duper.shopifyapps.com/",
          "lineItems": [
              {
                  "plan": {
                      "appRecurringPricingDetails": {
                          "price": {
                              "amount": 10,
                              "currencyCode": "USD"
                          },
                          "interval": "ANNUAL"
                      }
                  }
              }
          ]
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
    mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) {
      appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) {
        userErrors {
          field
          message
        }
        appSubscription {
          id
        }
        confirmationUrl
      }
    }
  QUERY

  variables = {
    "name": "Super Duper Recurring Plan",
    "returnUrl": "http://super-duper.shopifyapps.com/",
    "lineItems": [
      {
        "plan": {
          "appRecurringPricingDetails": {
            "price": {
              "amount": 10,
              "currencyCode": "USD"
            },
            "interval": "ANNUAL"
          }
        }
      }
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) {
        appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) {
          userErrors {
            field
            message
          }
          appSubscription {
            id
          }
          confirmationUrl
        }
      }`,
      "variables": {
          "name": "Super Duper Recurring Plan",
          "returnUrl": "http://super-duper.shopifyapps.com/",
          "lineItems": [
              {
                  "plan": {
                      "appRecurringPricingDetails": {
                          "price": {
                              "amount": 10,
                              "currencyCode": "USD"
                          },
                          "interval": "ANNUAL"
                      }
                  }
              }
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) {
    appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) {
      userErrors {
        field
        message
      }
      appSubscription {
        id
      }
      confirmationUrl
    }
  }' \
  --variables \
  '{
    "name": "Super Duper Recurring Plan",
    "returnUrl": "http://super-duper.shopifyapps.com/",
    "lineItems": [
      {
        "plan": {
          "appRecurringPricingDetails": {
            "price": {
              "amount": 10,
              "currencyCode": "USD"
            },
            "interval": "ANNUAL"
          }
        }
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "appSubscriptionCreate": {
      "userErrors": [],
      "appSubscription": {
        "id": "gid://shopify/AppSubscription/1029266967"
      },
      "confirmationUrl": "https://billingshop.myshopify.com/admin/charges/166357/1029266967/RecurringApplicationCharge/confirm_recurring_application_charge?signature=BAh7BzoHaWRpBBdeWT06EmF1dG9fYWN0aXZhdGVU--fe672a2422bba8ab370938f6f5f1df9aaf5ddd8d"
    }
  }
  ```

* ### Create a subscription for an app on both a recurring pricing plan and usage pricing plan.

  #### Query

  ```graphql
  mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) {
    appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) {
      userErrors {
        field
        message
      }
      appSubscription {
        id
        lineItems {
          id
          plan {
            pricingDetails {
              __typename
            }
          }
        }
      }
      confirmationUrl
    }
  }
  ```

  #### Variables

  ```json
  {
    "name": "Super Duper Recurring and Usage Plan",
    "returnUrl": "http://super-duper.shopifyapps.com/",
    "lineItems": [
      {
        "plan": {
          "appUsagePricingDetails": {
            "terms": "$1 for 100 emails",
            "cappedAmount": {
              "amount": 20,
              "currencyCode": "USD"
            }
          }
        }
      },
      {
        "plan": {
          "appRecurringPricingDetails": {
            "price": {
              "amount": 10,
              "currencyCode": "USD"
            }
          }
        }
      }
    ]
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) { appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) { userErrors { field message } appSubscription { id lineItems { id plan { pricingDetails { __typename } } } } confirmationUrl } }",
   "variables": {
      "name": "Super Duper Recurring and Usage Plan",
      "returnUrl": "http://super-duper.shopifyapps.com/",
      "lineItems": [
        {
          "plan": {
            "appUsagePricingDetails": {
              "terms": "$1 for 100 emails",
              "cappedAmount": {
                "amount": 20,
                "currencyCode": "USD"
              }
            }
          }
        },
        {
          "plan": {
            "appRecurringPricingDetails": {
              "price": {
                "amount": 10,
                "currencyCode": "USD"
              }
            }
          }
        }
      ]
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
    mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) {
      appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) {
        userErrors {
          field
          message
        }
        appSubscription {
          id
          lineItems {
            id
            plan {
              pricingDetails {
                __typename
              }
            }
          }
        }
        confirmationUrl
      }
    }`,
    {
      variables: {
          "name": "Super Duper Recurring and Usage Plan",
          "returnUrl": "http://super-duper.shopifyapps.com/",
          "lineItems": [
              {
                  "plan": {
                      "appUsagePricingDetails": {
                          "terms": "$1 for 100 emails",
                          "cappedAmount": {
                              "amount": 20,
                              "currencyCode": "USD"
                          }
                      }
                  }
              },
              {
                  "plan": {
                      "appRecurringPricingDetails": {
                          "price": {
                              "amount": 10,
                              "currencyCode": "USD"
                          }
                      }
                  }
              }
          ]
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
    mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) {
      appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) {
        userErrors {
          field
          message
        }
        appSubscription {
          id
          lineItems {
            id
            plan {
              pricingDetails {
                __typename
              }
            }
          }
        }
        confirmationUrl
      }
    }
  QUERY

  variables = {
    "name": "Super Duper Recurring and Usage Plan",
    "returnUrl": "http://super-duper.shopifyapps.com/",
    "lineItems": [
      {
        "plan": {
          "appUsagePricingDetails": {
            "terms": "$1 for 100 emails",
            "cappedAmount": {
              "amount": 20,
              "currencyCode": "USD"
            }
          }
        }
      },
      {
        "plan": {
          "appRecurringPricingDetails": {
            "price": {
              "amount": 10,
              "currencyCode": "USD"
            }
          }
        }
      }
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) {
        appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) {
          userErrors {
            field
            message
          }
          appSubscription {
            id
            lineItems {
              id
              plan {
                pricingDetails {
                  __typename
                }
              }
            }
          }
          confirmationUrl
        }
      }`,
      "variables": {
          "name": "Super Duper Recurring and Usage Plan",
          "returnUrl": "http://super-duper.shopifyapps.com/",
          "lineItems": [
              {
                  "plan": {
                      "appUsagePricingDetails": {
                          "terms": "$1 for 100 emails",
                          "cappedAmount": {
                              "amount": 20,
                              "currencyCode": "USD"
                          }
                      }
                  }
              },
              {
                  "plan": {
                      "appRecurringPricingDetails": {
                          "price": {
                              "amount": 10,
                              "currencyCode": "USD"
                          }
                      }
                  }
              }
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) {
    appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) {
      userErrors {
        field
        message
      }
      appSubscription {
        id
        lineItems {
          id
          plan {
            pricingDetails {
              __typename
            }
          }
        }
      }
      confirmationUrl
    }
  }' \
  --variables \
  '{
    "name": "Super Duper Recurring and Usage Plan",
    "returnUrl": "http://super-duper.shopifyapps.com/",
    "lineItems": [
      {
        "plan": {
          "appUsagePricingDetails": {
            "terms": "$1 for 100 emails",
            "cappedAmount": {
              "amount": 20,
              "currencyCode": "USD"
            }
          }
        }
      },
      {
        "plan": {
          "appRecurringPricingDetails": {
            "price": {
              "amount": 10,
              "currencyCode": "USD"
            }
          }
        }
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "appSubscriptionCreate": {
      "userErrors": [],
      "appSubscription": {
        "id": "gid://shopify/AppSubscription/1029266961",
        "lineItems": [
          {
            "id": "gid://shopify/AppSubscriptionLineItem/1029266961?v=1&index=0",
            "plan": {
              "pricingDetails": {
                "__typename": "AppRecurringPricing"
              }
            }
          },
          {
            "id": "gid://shopify/AppSubscriptionLineItem/1029266961?v=1&index=1",
            "plan": {
              "pricingDetails": {
                "__typename": "AppUsagePricing"
              }
            }
          }
        ]
      },
      "confirmationUrl": "https://billingshop.myshopify.com/admin/charges/166357/1029266961/RecurringApplicationCharge/confirm_recurring_application_charge?signature=BAh7BzoHaWRpBBFeWT06EmF1dG9fYWN0aXZhdGVU--6385f33920ae03746bbd6dd9dd1c41bb13879f5f"
    }
  }
  ```

* ### Create a subscription with a fixed amount discount

  #### Description

  Apply a fixed amount discount on the recurring cost of a subscription.

  #### Query

  ```graphql
  mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) {
    appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) {
      userErrors {
        field
        message
      }
      confirmationUrl
      appSubscription {
        id
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "name": "30 Day Recurring Plan",
    "returnUrl": "https://review-app.shopifyapps.com",
    "lineItems": [
      {
        "plan": {
          "appRecurringPricingDetails": {
            "price": {
              "amount": 40,
              "currencyCode": "USD"
            },
            "discount": {
              "value": {
                "amount": 5
              },
              "durationLimitInIntervals": 2
            },
            "interval": "EVERY_30_DAYS"
          }
        }
      }
    ]
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) { appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) { userErrors { field message } confirmationUrl appSubscription { id } } }",
   "variables": {
      "name": "30 Day Recurring Plan",
      "returnUrl": "https://review-app.shopifyapps.com",
      "lineItems": [
        {
          "plan": {
            "appRecurringPricingDetails": {
              "price": {
                "amount": 40,
                "currencyCode": "USD"
              },
              "discount": {
                "value": {
                  "amount": 5
                },
                "durationLimitInIntervals": 2
              },
              "interval": "EVERY_30_DAYS"
            }
          }
        }
      ]
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
    mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) {
      appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) {
        userErrors {
          field
          message
        }
        confirmationUrl
        appSubscription {
          id
        }
      }
    }`,
    {
      variables: {
          "name": "30 Day Recurring Plan",
          "returnUrl": "https://review-app.shopifyapps.com",
          "lineItems": [
              {
                  "plan": {
                      "appRecurringPricingDetails": {
                          "price": {
                              "amount": 40,
                              "currencyCode": "USD"
                          },
                          "discount": {
                              "value": {
                                  "amount": 5
                              },
                              "durationLimitInIntervals": 2
                          },
                          "interval": "EVERY_30_DAYS"
                      }
                  }
              }
          ]
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
    mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) {
      appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) {
        userErrors {
          field
          message
        }
        confirmationUrl
        appSubscription {
          id
        }
      }
    }
  QUERY

  variables = {
    "name": "30 Day Recurring Plan",
    "returnUrl": "https://review-app.shopifyapps.com",
    "lineItems": [
      {
        "plan": {
          "appRecurringPricingDetails": {
            "price": {
              "amount": 40,
              "currencyCode": "USD"
            },
            "discount": {
              "value": {
                "amount": 5
              },
              "durationLimitInIntervals": 2
            },
            "interval": "EVERY_30_DAYS"
          }
        }
      }
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) {
        appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) {
          userErrors {
            field
            message
          }
          confirmationUrl
          appSubscription {
            id
          }
        }
      }`,
      "variables": {
          "name": "30 Day Recurring Plan",
          "returnUrl": "https://review-app.shopifyapps.com",
          "lineItems": [
              {
                  "plan": {
                      "appRecurringPricingDetails": {
                          "price": {
                              "amount": 40,
                              "currencyCode": "USD"
                          },
                          "discount": {
                              "value": {
                                  "amount": 5
                              },
                              "durationLimitInIntervals": 2
                          },
                          "interval": "EVERY_30_DAYS"
                      }
                  }
              }
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) {
    appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) {
      userErrors {
        field
        message
      }
      confirmationUrl
      appSubscription {
        id
      }
    }
  }' \
  --variables \
  '{
    "name": "30 Day Recurring Plan",
    "returnUrl": "https://review-app.shopifyapps.com",
    "lineItems": [
      {
        "plan": {
          "appRecurringPricingDetails": {
            "price": {
              "amount": 40,
              "currencyCode": "USD"
            },
            "discount": {
              "value": {
                "amount": 5
              },
              "durationLimitInIntervals": 2
            },
            "interval": "EVERY_30_DAYS"
          }
        }
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "appSubscriptionCreate": {
      "userErrors": [],
      "confirmationUrl": "https://billingshop.myshopify.com/admin/charges/166357/1029266959/RecurringApplicationCharge/confirm_recurring_application_charge?signature=BAh7BzoHaWRpBA9eWT06EmF1dG9fYWN0aXZhdGVU--f374cbfa230bebd8e270af37a779d920de2dfe69",
      "appSubscription": {
        "id": "gid://shopify/AppSubscription/1029266959"
      }
    }
  }
  ```

* ### Create a subscription with a free trial.

  #### Query

  ```graphql
  mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!, $trialDays: Int) {
    appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems, trialDays: $trialDays) {
      userErrors {
        field
        message
      }
      appSubscription {
        id
      }
      confirmationUrl
    }
  }
  ```

  #### Variables

  ```json
  {
    "name": "Super Duper Recurring Plan with a Trial",
    "returnUrl": "http://super-duper.shopifyapps.com/",
    "trialDays": 7,
    "lineItems": [
      {
        "plan": {
          "appRecurringPricingDetails": {
            "price": {
              "amount": 10,
              "currencyCode": "USD"
            }
          }
        }
      }
    ]
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!, $trialDays: Int) { appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems, trialDays: $trialDays) { userErrors { field message } appSubscription { id } confirmationUrl } }",
   "variables": {
      "name": "Super Duper Recurring Plan with a Trial",
      "returnUrl": "http://super-duper.shopifyapps.com/",
      "trialDays": 7,
      "lineItems": [
        {
          "plan": {
            "appRecurringPricingDetails": {
              "price": {
                "amount": 10,
                "currencyCode": "USD"
              }
            }
          }
        }
      ]
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
    mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!, $trialDays: Int) {
      appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems, trialDays: $trialDays) {
        userErrors {
          field
          message
        }
        appSubscription {
          id
        }
        confirmationUrl
      }
    }`,
    {
      variables: {
          "name": "Super Duper Recurring Plan with a Trial",
          "returnUrl": "http://super-duper.shopifyapps.com/",
          "trialDays": 7,
          "lineItems": [
              {
                  "plan": {
                      "appRecurringPricingDetails": {
                          "price": {
                              "amount": 10,
                              "currencyCode": "USD"
                          }
                      }
                  }
              }
          ]
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
    mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!, $trialDays: Int) {
      appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems, trialDays: $trialDays) {
        userErrors {
          field
          message
        }
        appSubscription {
          id
        }
        confirmationUrl
      }
    }
  QUERY

  variables = {
    "name": "Super Duper Recurring Plan with a Trial",
    "returnUrl": "http://super-duper.shopifyapps.com/",
    "trialDays": 7,
    "lineItems": [
      {
        "plan": {
          "appRecurringPricingDetails": {
            "price": {
              "amount": 10,
              "currencyCode": "USD"
            }
          }
        }
      }
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!, $trialDays: Int) {
        appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems, trialDays: $trialDays) {
          userErrors {
            field
            message
          }
          appSubscription {
            id
          }
          confirmationUrl
        }
      }`,
      "variables": {
          "name": "Super Duper Recurring Plan with a Trial",
          "returnUrl": "http://super-duper.shopifyapps.com/",
          "trialDays": 7,
          "lineItems": [
              {
                  "plan": {
                      "appRecurringPricingDetails": {
                          "price": {
                              "amount": 10,
                              "currencyCode": "USD"
                          }
                      }
                  }
              }
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!, $trialDays: Int) {
    appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems, trialDays: $trialDays) {
      userErrors {
        field
        message
      }
      appSubscription {
        id
      }
      confirmationUrl
    }
  }' \
  --variables \
  '{
    "name": "Super Duper Recurring Plan with a Trial",
    "returnUrl": "http://super-duper.shopifyapps.com/",
    "trialDays": 7,
    "lineItems": [
      {
        "plan": {
          "appRecurringPricingDetails": {
            "price": {
              "amount": 10,
              "currencyCode": "USD"
            }
          }
        }
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "appSubscriptionCreate": {
      "userErrors": [],
      "appSubscription": {
        "id": "gid://shopify/AppSubscription/1029266965"
      },
      "confirmationUrl": "https://billingshop.myshopify.com/admin/charges/166357/1029266965/RecurringApplicationCharge/confirm_recurring_application_charge?signature=BAh7BzoHaWRpBBVeWT06EmF1dG9fYWN0aXZhdGVU--f3e64505cf5f399b7e631756ff1d6c95f80af98c"
    }
  }
  ```

* ### Create a subscription with a percentage value discount

  #### Description

  Apply a percentage value discount on the recurring cost of a subscription.

  #### Query

  ```graphql
  mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) {
    appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) {
      userErrors {
        field
        message
      }
      confirmationUrl
      appSubscription {
        id
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "name": "30 Day Recurring Plan",
    "returnUrl": "https://review-app.shopifyapps.com",
    "lineItems": [
      {
        "plan": {
          "appRecurringPricingDetails": {
            "price": {
              "amount": 40,
              "currencyCode": "USD"
            },
            "discount": {
              "value": {
                "percentage": 0.2
              },
              "durationLimitInIntervals": 10
            },
            "interval": "EVERY_30_DAYS"
          }
        }
      }
    ]
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) { appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) { userErrors { field message } confirmationUrl appSubscription { id } } }",
   "variables": {
      "name": "30 Day Recurring Plan",
      "returnUrl": "https://review-app.shopifyapps.com",
      "lineItems": [
        {
          "plan": {
            "appRecurringPricingDetails": {
              "price": {
                "amount": 40,
                "currencyCode": "USD"
              },
              "discount": {
                "value": {
                  "percentage": 0.2
                },
                "durationLimitInIntervals": 10
              },
              "interval": "EVERY_30_DAYS"
            }
          }
        }
      ]
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
    mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) {
      appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) {
        userErrors {
          field
          message
        }
        confirmationUrl
        appSubscription {
          id
        }
      }
    }`,
    {
      variables: {
          "name": "30 Day Recurring Plan",
          "returnUrl": "https://review-app.shopifyapps.com",
          "lineItems": [
              {
                  "plan": {
                      "appRecurringPricingDetails": {
                          "price": {
                              "amount": 40,
                              "currencyCode": "USD"
                          },
                          "discount": {
                              "value": {
                                  "percentage": 0.2
                              },
                              "durationLimitInIntervals": 10
                          },
                          "interval": "EVERY_30_DAYS"
                      }
                  }
              }
          ]
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
    mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) {
      appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) {
        userErrors {
          field
          message
        }
        confirmationUrl
        appSubscription {
          id
        }
      }
    }
  QUERY

  variables = {
    "name": "30 Day Recurring Plan",
    "returnUrl": "https://review-app.shopifyapps.com",
    "lineItems": [
      {
        "plan": {
          "appRecurringPricingDetails": {
            "price": {
              "amount": 40,
              "currencyCode": "USD"
            },
            "discount": {
              "value": {
                "percentage": 0.2
              },
              "durationLimitInIntervals": 10
            },
            "interval": "EVERY_30_DAYS"
          }
        }
      }
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) {
        appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) {
          userErrors {
            field
            message
          }
          confirmationUrl
          appSubscription {
            id
          }
        }
      }`,
      "variables": {
          "name": "30 Day Recurring Plan",
          "returnUrl": "https://review-app.shopifyapps.com",
          "lineItems": [
              {
                  "plan": {
                      "appRecurringPricingDetails": {
                          "price": {
                              "amount": 40,
                              "currencyCode": "USD"
                          },
                          "discount": {
                              "value": {
                                  "percentage": 0.2
                              },
                              "durationLimitInIntervals": 10
                          },
                          "interval": "EVERY_30_DAYS"
                      }
                  }
              }
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) {
    appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) {
      userErrors {
        field
        message
      }
      confirmationUrl
      appSubscription {
        id
      }
    }
  }' \
  --variables \
  '{
    "name": "30 Day Recurring Plan",
    "returnUrl": "https://review-app.shopifyapps.com",
    "lineItems": [
      {
        "plan": {
          "appRecurringPricingDetails": {
            "price": {
              "amount": 40,
              "currencyCode": "USD"
            },
            "discount": {
              "value": {
                "percentage": 0.2
              },
              "durationLimitInIntervals": 10
            },
            "interval": "EVERY_30_DAYS"
          }
        }
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "appSubscriptionCreate": {
      "userErrors": [],
      "confirmationUrl": "https://billingshop.myshopify.com/admin/charges/166357/1029266963/RecurringApplicationCharge/confirm_recurring_application_charge?signature=BAh7BzoHaWRpBBNeWT06EmF1dG9fYWN0aXZhdGVU--175a4c86f29fd8f88234ec365eec27ab2dc7d8e3",
      "appSubscription": {
        "id": "gid://shopify/AppSubscription/1029266963"
      }
    }
  }
  ```

* ### Create a subscription with add-on modules

  #### Description

  Demonstrates how to increase usage caps to bill for 'add on modules' where Module A has a fixed price of $20 every 30 days, and Module B as a fixed price of $15 every 30 days plus $1 for every 100 emails.

  #### Query

  ```graphql
  mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) {
    appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) {
      userErrors {
        field
        message
      }
      confirmationUrl
      appSubscription {
        id
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "name": "Subscription for Module A and Module B",
    "returnUrl": "http://super-duper.shopifyapps.com",
    "lineItems": [
      {
        "plan": {
          "appUsagePricingDetails": {
            "terms": "$1 for 100 emails for Module B",
            "cappedAmount": {
              "amount": 20,
              "currencyCode": "USD"
            }
          }
        }
      },
      {
        "plan": {
          "appRecurringPricingDetails": {
            "price": {
              "amount": 35,
              "currencyCode": "USD"
            }
          }
        }
      }
    ]
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) { appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) { userErrors { field message } confirmationUrl appSubscription { id } } }",
   "variables": {
      "name": "Subscription for Module A and Module B",
      "returnUrl": "http://super-duper.shopifyapps.com",
      "lineItems": [
        {
          "plan": {
            "appUsagePricingDetails": {
              "terms": "$1 for 100 emails for Module B",
              "cappedAmount": {
                "amount": 20,
                "currencyCode": "USD"
              }
            }
          }
        },
        {
          "plan": {
            "appRecurringPricingDetails": {
              "price": {
                "amount": 35,
                "currencyCode": "USD"
              }
            }
          }
        }
      ]
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
    mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) {
      appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) {
        userErrors {
          field
          message
        }
        confirmationUrl
        appSubscription {
          id
        }
      }
    }`,
    {
      variables: {
          "name": "Subscription for Module A and Module B",
          "returnUrl": "http://super-duper.shopifyapps.com",
          "lineItems": [
              {
                  "plan": {
                      "appUsagePricingDetails": {
                          "terms": "$1 for 100 emails for Module B",
                          "cappedAmount": {
                              "amount": 20,
                              "currencyCode": "USD"
                          }
                      }
                  }
              },
              {
                  "plan": {
                      "appRecurringPricingDetails": {
                          "price": {
                              "amount": 35,
                              "currencyCode": "USD"
                          }
                      }
                  }
              }
          ]
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
    mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) {
      appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) {
        userErrors {
          field
          message
        }
        confirmationUrl
        appSubscription {
          id
        }
      }
    }
  QUERY

  variables = {
    "name": "Subscription for Module A and Module B",
    "returnUrl": "http://super-duper.shopifyapps.com",
    "lineItems": [
      {
        "plan": {
          "appUsagePricingDetails": {
            "terms": "$1 for 100 emails for Module B",
            "cappedAmount": {
              "amount": 20,
              "currencyCode": "USD"
            }
          }
        }
      },
      {
        "plan": {
          "appRecurringPricingDetails": {
            "price": {
              "amount": 35,
              "currencyCode": "USD"
            }
          }
        }
      }
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) {
        appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) {
          userErrors {
            field
            message
          }
          confirmationUrl
          appSubscription {
            id
          }
        }
      }`,
      "variables": {
          "name": "Subscription for Module A and Module B",
          "returnUrl": "http://super-duper.shopifyapps.com",
          "lineItems": [
              {
                  "plan": {
                      "appUsagePricingDetails": {
                          "terms": "$1 for 100 emails for Module B",
                          "cappedAmount": {
                              "amount": 20,
                              "currencyCode": "USD"
                          }
                      }
                  }
              },
              {
                  "plan": {
                      "appRecurringPricingDetails": {
                          "price": {
                              "amount": 35,
                              "currencyCode": "USD"
                          }
                      }
                  }
              }
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) {
    appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) {
      userErrors {
        field
        message
      }
      confirmationUrl
      appSubscription {
        id
      }
    }
  }' \
  --variables \
  '{
    "name": "Subscription for Module A and Module B",
    "returnUrl": "http://super-duper.shopifyapps.com",
    "lineItems": [
      {
        "plan": {
          "appUsagePricingDetails": {
            "terms": "$1 for 100 emails for Module B",
            "cappedAmount": {
              "amount": 20,
              "currencyCode": "USD"
            }
          }
        }
      },
      {
        "plan": {
          "appRecurringPricingDetails": {
            "price": {
              "amount": 35,
              "currencyCode": "USD"
            }
          }
        }
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "appSubscriptionCreate": {
      "userErrors": [],
      "confirmationUrl": "https://billingshop.myshopify.com/admin/charges/166357/1029266966/RecurringApplicationCharge/confirm_recurring_application_charge?signature=BAh7BzoHaWRpBBZeWT06EmF1dG9fYWN0aXZhdGVU--f80e7f189ca7afad7364c4182577a8b8c801254f",
      "appSubscription": {
        "id": "gid://shopify/AppSubscription/1029266966"
      }
    }
  }
  ```

* ### Creates a recurring application charge

  #### Query

  ```graphql
  mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) {
    appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) {
      userErrors {
        field
        message
      }
      confirmationUrl
      appSubscription {
        id
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "name": "Super Duper Recurring Plan",
    "returnUrl": "http://super-duper.shopifyapps.com",
    "lineItems": [
      {
        "plan": {
          "appRecurringPricingDetails": {
            "price": {
              "amount": 10,
              "currencyCode": "USD"
            },
            "interval": "EVERY_30_DAYS"
          }
        }
      }
    ]
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) { appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) { userErrors { field message } confirmationUrl appSubscription { id } } }",
   "variables": {
      "name": "Super Duper Recurring Plan",
      "returnUrl": "http://super-duper.shopifyapps.com",
      "lineItems": [
        {
          "plan": {
            "appRecurringPricingDetails": {
              "price": {
                "amount": 10,
                "currencyCode": "USD"
              },
              "interval": "EVERY_30_DAYS"
            }
          }
        }
      ]
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
    mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) {
      appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) {
        userErrors {
          field
          message
        }
        confirmationUrl
        appSubscription {
          id
        }
      }
    }`,
    {
      variables: {
          "name": "Super Duper Recurring Plan",
          "returnUrl": "http://super-duper.shopifyapps.com",
          "lineItems": [
              {
                  "plan": {
                      "appRecurringPricingDetails": {
                          "price": {
                              "amount": 10,
                              "currencyCode": "USD"
                          },
                          "interval": "EVERY_30_DAYS"
                      }
                  }
              }
          ]
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
    mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) {
      appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) {
        userErrors {
          field
          message
        }
        confirmationUrl
        appSubscription {
          id
        }
      }
    }
  QUERY

  variables = {
    "name": "Super Duper Recurring Plan",
    "returnUrl": "http://super-duper.shopifyapps.com",
    "lineItems": [
      {
        "plan": {
          "appRecurringPricingDetails": {
            "price": {
              "amount": 10,
              "currencyCode": "USD"
            },
            "interval": "EVERY_30_DAYS"
          }
        }
      }
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) {
        appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) {
          userErrors {
            field
            message
          }
          confirmationUrl
          appSubscription {
            id
          }
        }
      }`,
      "variables": {
          "name": "Super Duper Recurring Plan",
          "returnUrl": "http://super-duper.shopifyapps.com",
          "lineItems": [
              {
                  "plan": {
                      "appRecurringPricingDetails": {
                          "price": {
                              "amount": 10,
                              "currencyCode": "USD"
                          },
                          "interval": "EVERY_30_DAYS"
                      }
                  }
              }
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation AppSubscriptionCreate($name: String!, $lineItems: [AppSubscriptionLineItemInput!]!, $returnUrl: URL!) {
    appSubscriptionCreate(name: $name, returnUrl: $returnUrl, lineItems: $lineItems) {
      userErrors {
        field
        message
      }
      confirmationUrl
      appSubscription {
        id
      }
    }
  }' \
  --variables \
  '{
    "name": "Super Duper Recurring Plan",
    "returnUrl": "http://super-duper.shopifyapps.com",
    "lineItems": [
      {
        "plan": {
          "appRecurringPricingDetails": {
            "price": {
              "amount": 10,
              "currencyCode": "USD"
            },
            "interval": "EVERY_30_DAYS"
          }
        }
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "appSubscriptionCreate": {
      "userErrors": [],
      "confirmationUrl": "https://billingshop.myshopify.com/admin/charges/166357/1029266962/RecurringApplicationCharge/confirm_recurring_application_charge?signature=BAh7BzoHaWRpBBJeWT06EmF1dG9fYWN0aXZhdGVU--c94d382d1fe3012e03e22dcb2253e14d14933433",
      "appSubscription": {
        "id": "gid://shopify/AppSubscription/1029266962"
      }
    }
  }
  ```

* ### appSubscriptionCreate reference
