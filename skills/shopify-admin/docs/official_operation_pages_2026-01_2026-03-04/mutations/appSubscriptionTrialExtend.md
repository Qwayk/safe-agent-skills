---
title: appSubscriptionTrialExtend - GraphQL Admin
description: >-
  Extends the trial period for an existing app subscription. Trial extensions
  give merchants additional time to use the app before committing to paid
  billing.


  Requires the subscription ID and the number of days to extend (between one and
  1000). The extension modifies the existing trial end date, allowing continued
  access to subscription features without immediate billing. Returns the updated
  [`AppSubscription`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppSubscription).


  Learn more about [offering free
  trials](https://shopify.dev/docs/apps/launch/billing/offer-free-trials).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/appSubscriptionTrialExtend
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/appSubscriptionTrialExtend.md
---

# app​Subscription​Trial​Extend

mutation

Requires This must be a third party developed application that you can access.

Extends the trial period for an existing app subscription. Trial extensions give merchants additional time to use the app before committing to paid billing.

Requires the subscription ID and the number of days to extend (between one and 1000). The extension modifies the existing trial end date, allowing continued access to subscription features without immediate billing. Returns the updated [`AppSubscription`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppSubscription).

Learn more about [offering free trials](https://shopify.dev/docs/apps/launch/billing/offer-free-trials).

## Arguments

* days

  [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  required

  The number of days to extend the trial. The value must be greater than 0 and less than or equal to 1000.

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the app subscription to extend the trial for.

***

## App​Subscription​Trial​Extend​Payload returns

* app​Subscription

  [App​Subscription](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppSubscription)

  The app subscription that had its trial extended.

* user​Errors

  [\[App​Subscription​Trial​Extend​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppSubscriptionTrialExtendUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Extend an app subscription for a shop

  #### Query

  ```graphql
  mutation AppSubscriptionTrialExtend($id: ID!, $days: Int!) {
    appSubscriptionTrialExtend(id: $id, days: $days) {
      userErrors {
        field
        message
        code
      }
      appSubscription {
        id
        status
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/AppSubscription/443388186",
    "days": 10
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation AppSubscriptionTrialExtend($id: ID!, $days: Int!) { appSubscriptionTrialExtend(id: $id, days: $days) { userErrors { field message code } appSubscription { id status } } }",
   "variables": {
      "id": "gid://shopify/AppSubscription/443388186",
      "days": 10
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
    mutation AppSubscriptionTrialExtend($id: ID!, $days: Int!) {
      appSubscriptionTrialExtend(id: $id, days: $days) {
        userErrors {
          field
          message
          code
        }
        appSubscription {
          id
          status
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/AppSubscription/443388186",
          "days": 10
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
    mutation AppSubscriptionTrialExtend($id: ID!, $days: Int!) {
      appSubscriptionTrialExtend(id: $id, days: $days) {
        userErrors {
          field
          message
          code
        }
        appSubscription {
          id
          status
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/AppSubscription/443388186",
    "days": 10
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation AppSubscriptionTrialExtend($id: ID!, $days: Int!) {
        appSubscriptionTrialExtend(id: $id, days: $days) {
          userErrors {
            field
            message
            code
          }
          appSubscription {
            id
            status
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/AppSubscription/443388186",
          "days": 10
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation AppSubscriptionTrialExtend($id: ID!, $days: Int!) {
    appSubscriptionTrialExtend(id: $id, days: $days) {
      userErrors {
        field
        message
        code
      }
      appSubscription {
        id
        status
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/AppSubscription/443388186",
    "days": 10
  }'
  ```

  #### Response

  ```json
  {
    "appSubscriptionTrialExtend": {
      "userErrors": [],
      "appSubscription": {
        "id": "gid://shopify/AppSubscription/443388186",
        "status": "ACTIVE"
      }
    }
  }
  ```

* ### appSubscriptionTrialExtend reference
