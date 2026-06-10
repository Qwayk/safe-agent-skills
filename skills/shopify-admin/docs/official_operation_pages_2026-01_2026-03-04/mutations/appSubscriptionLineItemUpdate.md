---
title: appSubscriptionLineItemUpdate - GraphQL Admin
description: >-
  Updates the capped amount on usage-based billing for an
  [`AppSubscriptionLineItem`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppSubscriptionLineItem).
  Enables you to modify the maximum charge limit that prevents merchants from
  exceeding a specified threshold during their billing period.


  The mutation returns a [confirmation
  URL](https://shopify.dev/docs/api/admin-graphql/latest/mutations/appSubscriptionCreate#returns-confirmationUrl)
  where the merchant must approve the new pricing limit before it takes effect.
  Use this when adjusting usage limits based on merchant needs or changing
  pricing models.


  Learn more about [updating the maximum charge for a
  subscription](https://shopify.dev/docs/apps/launch/billing/subscription-billing/update-max-charge).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/appSubscriptionLineItemUpdate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/appSubscriptionLineItemUpdate.md
---

# app​Subscription​Line​Item​Update

mutation

Updates the capped amount on usage-based billing for an [`AppSubscriptionLineItem`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppSubscriptionLineItem). Enables you to modify the maximum charge limit that prevents merchants from exceeding a specified threshold during their billing period.

The mutation returns a [confirmation URL](https://shopify.dev/docs/api/admin-graphql/latest/mutations/appSubscriptionCreate#returns-confirmationUrl) where the merchant must approve the new pricing limit before it takes effect. Use this when adjusting usage limits based on merchant needs or changing pricing models.

Learn more about [updating the maximum charge for a subscription](https://shopify.dev/docs/apps/launch/billing/subscription-billing/update-max-charge).

## Arguments

* capped​Amount

  [Money​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/MoneyInput)

  required

  The new maximum amount of usage charges that can be incurred within a subscription billing interval.

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the app subscription line item to be updated.

***

## App​Subscription​Line​Item​Update​Payload returns

* app​Subscription

  [App​Subscription](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppSubscription)

  The updated app subscription.

* confirmation​Url

  [URL](https://shopify.dev/docs/api/admin-graphql/latest/scalars/URL)

  The URL where the merchant approves or declines the updated app subscription line item.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Updates the capped amount of a recurring application charge

  #### Description

  You can modify the capped amount on a usage pricing plan.

  #### Query

  ```graphql
  mutation appSubscriptionLineItemUpdate($cappedAmount: MoneyInput!, $id: ID!) {
    appSubscriptionLineItemUpdate(cappedAmount: $cappedAmount, id: $id) {
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
    "id": "gid://shopify/AppSubscriptionLineItem/1029266946?v=1&index=1",
    "cappedAmount": {
      "amount": 100,
      "currencyCode": "USD"
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
  "query": "mutation appSubscriptionLineItemUpdate($cappedAmount: MoneyInput!, $id: ID!) { appSubscriptionLineItemUpdate(cappedAmount: $cappedAmount, id: $id) { userErrors { field message } confirmationUrl appSubscription { id } } }",
   "variables": {
      "id": "gid://shopify/AppSubscriptionLineItem/1029266946?v=1&index=1",
      "cappedAmount": {
        "amount": 100,
        "currencyCode": "USD"
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
    mutation appSubscriptionLineItemUpdate($cappedAmount: MoneyInput!, $id: ID!) {
      appSubscriptionLineItemUpdate(cappedAmount: $cappedAmount, id: $id) {
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
          "id": "gid://shopify/AppSubscriptionLineItem/1029266946?v=1&index=1",
          "cappedAmount": {
              "amount": 100,
              "currencyCode": "USD"
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
    mutation appSubscriptionLineItemUpdate($cappedAmount: MoneyInput!, $id: ID!) {
      appSubscriptionLineItemUpdate(cappedAmount: $cappedAmount, id: $id) {
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
    "id": "gid://shopify/AppSubscriptionLineItem/1029266946?v=1&index=1",
    "cappedAmount": {
      "amount": 100,
      "currencyCode": "USD"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation appSubscriptionLineItemUpdate($cappedAmount: MoneyInput!, $id: ID!) {
        appSubscriptionLineItemUpdate(cappedAmount: $cappedAmount, id: $id) {
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
          "id": "gid://shopify/AppSubscriptionLineItem/1029266946?v=1&index=1",
          "cappedAmount": {
              "amount": 100,
              "currencyCode": "USD"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation appSubscriptionLineItemUpdate($cappedAmount: MoneyInput!, $id: ID!) {
    appSubscriptionLineItemUpdate(cappedAmount: $cappedAmount, id: $id) {
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
    "id": "gid://shopify/AppSubscriptionLineItem/1029266946?v=1&index=1",
    "cappedAmount": {
      "amount": 100,
      "currencyCode": "USD"
    }
  }'
  ```

  #### Response

  ```json
  {
    "appSubscriptionLineItemUpdate": {
      "userErrors": [],
      "confirmationUrl": "https://billingshop.myshopify.com/admin/charges/193172482/1029266946/RecurringApplicationCharge/confirm_update_capped_amount?signature=BAh7BzoHaWRpBAJeWT06EmF1dG9fYWN0aXZhdGVG--5d28879b4ac4355216b7e6d2f861f9c245272daa",
      "appSubscription": {
        "id": "gid://shopify/AppSubscription/1029266946"
      }
    }
  }
  ```

* ### appSubscriptionLineItemUpdate reference
