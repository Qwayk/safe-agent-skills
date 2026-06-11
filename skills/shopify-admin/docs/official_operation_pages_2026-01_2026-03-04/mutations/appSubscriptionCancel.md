---
title: appSubscriptionCancel - GraphQL Admin
description: >-
  Cancels an active app subscription, stopping future billing cycles. The
  cancellation behavior depends on the `replacementBehavior` setting - it can
  either disable auto-renewal (allowing the subscription to continue until the
  end of the current billing period) or immediately cancel with prorated
  refunds.


  When a merchant decides to discontinue using subscription features, this
  mutation provides a clean cancellation workflow that respects billing periods
  and merchant expectations.


  Use the `AppSubscriptionCancel` mutation to:

  - Process merchant-initiated subscription cancellations

  - Terminate subscriptions due to policy violations or account issues

  - Handle subscription cancellations during app uninstallation workflows


  The cancellation timing and merchant access depends on the
  `replacementBehavior` setting and the app's specific implementation of
  subscription management.


  For subscription lifecycle management and cancellation best practices, consult
  the [subscription management
  guide](https://shopify.dev/docs/apps/launch/billing/subscription-billing).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/appSubscriptionCancel
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/appSubscriptionCancel.md
---

# app​Subscription​Cancel

mutation

Cancels an active app subscription, stopping future billing cycles. The cancellation behavior depends on the `replacementBehavior` setting - it can either disable auto-renewal (allowing the subscription to continue until the end of the current billing period) or immediately cancel with prorated refunds.

When a merchant decides to discontinue using subscription features, this mutation provides a clean cancellation workflow that respects billing periods and merchant expectations.

Use the `AppSubscriptionCancel` mutation to:

* Process merchant-initiated subscription cancellations
* Terminate subscriptions due to policy violations or account issues
* Handle subscription cancellations during app uninstallation workflows

The cancellation timing and merchant access depends on the `replacementBehavior` setting and the app's specific implementation of subscription management.

For subscription lifecycle management and cancellation best practices, consult the [subscription management guide](https://shopify.dev/docs/apps/launch/billing/subscription-billing).

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the app subscription to be cancelled.

* prorate

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Whether to issue prorated credits for the unused portion of the app subscription. There will be a corresponding deduction (based on revenue share) to your Partner account. For example, if a $10.00 app subscription (with 0% revenue share) is cancelled and prorated half way through the billing cycle, then the merchant will be credited $5.00 and that amount will be deducted from your Partner account.

***

## App​Subscription​Cancel​Payload returns

* app​Subscription

  [App​Subscription](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppSubscription)

  The cancelled app subscription.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Cancel an app subscription on a shop and issue prorated credits

  #### Query

  ```graphql
  mutation AppSubscriptionCancel($id: ID!, $prorate: Boolean) {
    appSubscriptionCancel(id: $id, prorate: $prorate) {
      userErrors {
        field
        message
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
    "id": "gid://shopify/AppSubscription/1029266957",
    "prorate": true
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation AppSubscriptionCancel($id: ID!, $prorate: Boolean) { appSubscriptionCancel(id: $id, prorate: $prorate) { userErrors { field message } appSubscription { id status } } }",
   "variables": {
      "id": "gid://shopify/AppSubscription/1029266957",
      "prorate": true
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
    mutation AppSubscriptionCancel($id: ID!, $prorate: Boolean) {
      appSubscriptionCancel(id: $id, prorate: $prorate) {
        userErrors {
          field
          message
        }
        appSubscription {
          id
          status
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/AppSubscription/1029266957",
          "prorate": true
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
    mutation AppSubscriptionCancel($id: ID!, $prorate: Boolean) {
      appSubscriptionCancel(id: $id, prorate: $prorate) {
        userErrors {
          field
          message
        }
        appSubscription {
          id
          status
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/AppSubscription/1029266957",
    "prorate": true
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation AppSubscriptionCancel($id: ID!, $prorate: Boolean) {
        appSubscriptionCancel(id: $id, prorate: $prorate) {
          userErrors {
            field
            message
          }
          appSubscription {
            id
            status
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/AppSubscription/1029266957",
          "prorate": true
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation AppSubscriptionCancel($id: ID!, $prorate: Boolean) {
    appSubscriptionCancel(id: $id, prorate: $prorate) {
      userErrors {
        field
        message
      }
      appSubscription {
        id
        status
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/AppSubscription/1029266957",
    "prorate": true
  }'
  ```

  #### Response

  ```json
  {
    "appSubscriptionCancel": {
      "userErrors": [],
      "appSubscription": {
        "id": "gid://shopify/AppSubscription/1029266957",
        "status": "CANCELLED"
      }
    }
  }
  ```

* ### Cancels a recurring application charge

  #### Query

  ```graphql
  mutation AppSubscriptionCancel($id: ID!) {
    appSubscriptionCancel(id: $id) {
      userErrors {
        field
        message
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
    "id": "gid://shopify/AppSubscription/1029266958"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation AppSubscriptionCancel($id: ID!) { appSubscriptionCancel(id: $id) { userErrors { field message } appSubscription { id status } } }",
   "variables": {
      "id": "gid://shopify/AppSubscription/1029266958"
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
    mutation AppSubscriptionCancel($id: ID!) {
      appSubscriptionCancel(id: $id) {
        userErrors {
          field
          message
        }
        appSubscription {
          id
          status
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/AppSubscription/1029266958"
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
    mutation AppSubscriptionCancel($id: ID!) {
      appSubscriptionCancel(id: $id) {
        userErrors {
          field
          message
        }
        appSubscription {
          id
          status
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/AppSubscription/1029266958"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation AppSubscriptionCancel($id: ID!) {
        appSubscriptionCancel(id: $id) {
          userErrors {
            field
            message
          }
          appSubscription {
            id
            status
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/AppSubscription/1029266958"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation AppSubscriptionCancel($id: ID!) {
    appSubscriptionCancel(id: $id) {
      userErrors {
        field
        message
      }
      appSubscription {
        id
        status
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/AppSubscription/1029266958"
  }'
  ```

  #### Response

  ```json
  {
    "appSubscriptionCancel": {
      "userErrors": [],
      "appSubscription": {
        "id": "gid://shopify/AppSubscription/1029266958",
        "status": "CANCELLED"
      }
    }
  }
  ```

* ### appSubscriptionCancel reference
