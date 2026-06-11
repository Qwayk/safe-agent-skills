---
title: subscriptionBillingCycle - GraphQL Admin
description: Returns a subscription billing cycle found either by cycle index or date.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/subscriptionBillingCycle
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/subscriptionBillingCycle.md
---

# subscription​Billing​Cycle

query

Returns a subscription billing cycle found either by cycle index or date.

## Arguments

* billing​Cycle​Input

  [Subscription​Billing​Cycle​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/SubscriptionBillingCycleInput)

  required

  Input object used to select and use billing cycles.

***

## Possible returns

* Subscription​Billing​Cycle

  [Subscription​Billing​Cycle](https://shopify.dev/docs/api/admin-graphql/latest/objects/SubscriptionBillingCycle)

  A subscription billing cycle.

  * billing​Attempt​Expected​Date

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date on which the billing attempt is expected to be made.

  * billing​Attempts

    [Subscription​Billing​Attempt​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/SubscriptionBillingAttemptConnection)

    non-null

    The list of billing attempts associated with the billing cycle.

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      ### Arguments

      The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * after

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * last

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * before

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * reverse

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Default:false

      Reverse the order of the underlying list.

    ***

  * cycle​End​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The end date of the billing cycle.

  * cycle​Index

    [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    non-null

    The index of the billing cycle.

  * cycle​Start​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The start date of the billing cycle.

  * edited

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether this billing cycle was edited.

  * edited​Contract

    [Subscription​Billing​Cycle​Edited​Contract](https://shopify.dev/docs/api/admin-graphql/latest/objects/SubscriptionBillingCycleEditedContract)

    The active edited contract for the billing cycle.

  * skipped

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether this billing cycle was skipped.

  * source​Contract

    [Subscription​Contract!](https://shopify.dev/docs/api/admin-graphql/latest/objects/SubscriptionContract)

    non-null

    The subscription contract that the billing cycle belongs to.

  * status

    [Subscription​Billing​Cycle​Billing​Cycle​Status!](https://shopify.dev/docs/api/admin-graphql/latest/enums/SubscriptionBillingCycleBillingCycleStatus)

    non-null

    The status of the billing cycle.

***

## Examples

* ### Get a billing cycle by cycle index

  #### Description

  Retrieves a billing cycle with cycle index \`1\` and returns the \`billingAttemptExpectedDate\`.

  #### Query

  ```graphql
  query subscriptionBillingCycle($contractId: ID!, $index: Int!) {
    subscriptionBillingCycle(billingCycleInput: {contractId: $contractId, selector: {index: $index}}) {
      billingAttemptExpectedDate
    }
  }
  ```

  #### Variables

  ```json
  {
    "contractId": "gid://shopify/SubscriptionContract/593791907",
    "index": 1
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query subscriptionBillingCycle($contractId: ID!, $index: Int!) { subscriptionBillingCycle(billingCycleInput: {contractId: $contractId, selector: {index: $index}}) { billingAttemptExpectedDate } }",
   "variables": {
      "contractId": "gid://shopify/SubscriptionContract/593791907",
      "index": 1
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
    query subscriptionBillingCycle($contractId: ID!, $index: Int!) {
      subscriptionBillingCycle(billingCycleInput: {contractId: $contractId, selector: {index: $index}}) {
        billingAttemptExpectedDate
      }
    }`,
    {
      variables: {
          "contractId": "gid://shopify/SubscriptionContract/593791907",
          "index": 1
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
    query subscriptionBillingCycle($contractId: ID!, $index: Int!) {
      subscriptionBillingCycle(billingCycleInput: {contractId: $contractId, selector: {index: $index}}) {
        billingAttemptExpectedDate
      }
    }
  QUERY

  variables = {
    "contractId": "gid://shopify/SubscriptionContract/593791907",
    "index": 1
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query subscriptionBillingCycle($contractId: ID!, $index: Int!) {
        subscriptionBillingCycle(billingCycleInput: {contractId: $contractId, selector: {index: $index}}) {
          billingAttemptExpectedDate
        }
      }`,
      "variables": {
          "contractId": "gid://shopify/SubscriptionContract/593791907",
          "index": 1
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query subscriptionBillingCycle($contractId: ID!, $index: Int!) {
    subscriptionBillingCycle(billingCycleInput: {contractId: $contractId, selector: {index: $index}}) {
      billingAttemptExpectedDate
    }
  }' \
  --variables \
  '{
    "contractId": "gid://shopify/SubscriptionContract/593791907",
    "index": 1
  }'
  ```

  #### Response

  ```json
  {
    "subscriptionBillingCycle": {
      "billingAttemptExpectedDate": "2022-01-02T11:59:59Z"
    }
  }
  ```

* ### Get a billing cycle by date

  #### Description

  Retrieves the billing cycle that includes the date \`2022-12-01\` and returns the \`billingAttemptExpectedDate\`.

  #### Query

  ```graphql
  query subscriptionBillingCycle($contractId: ID!, $date: DateTime!) {
    subscriptionBillingCycle(billingCycleInput: {contractId: $contractId, selector: {date: $date}}) {
      billingAttemptExpectedDate
    }
  }
  ```

  #### Variables

  ```json
  {
    "contractId": "gid://shopify/SubscriptionContract/593791907",
    "date": "2022-12-01T00:00:00Z"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query subscriptionBillingCycle($contractId: ID!, $date: DateTime!) { subscriptionBillingCycle(billingCycleInput: {contractId: $contractId, selector: {date: $date}}) { billingAttemptExpectedDate } }",
   "variables": {
      "contractId": "gid://shopify/SubscriptionContract/593791907",
      "date": "2022-12-01T00:00:00Z"
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
    query subscriptionBillingCycle($contractId: ID!, $date: DateTime!) {
      subscriptionBillingCycle(billingCycleInput: {contractId: $contractId, selector: {date: $date}}) {
        billingAttemptExpectedDate
      }
    }`,
    {
      variables: {
          "contractId": "gid://shopify/SubscriptionContract/593791907",
          "date": "2022-12-01T00:00:00Z"
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
    query subscriptionBillingCycle($contractId: ID!, $date: DateTime!) {
      subscriptionBillingCycle(billingCycleInput: {contractId: $contractId, selector: {date: $date}}) {
        billingAttemptExpectedDate
      }
    }
  QUERY

  variables = {
    "contractId": "gid://shopify/SubscriptionContract/593791907",
    "date": "2022-12-01T00:00:00Z"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query subscriptionBillingCycle($contractId: ID!, $date: DateTime!) {
        subscriptionBillingCycle(billingCycleInput: {contractId: $contractId, selector: {date: $date}}) {
          billingAttemptExpectedDate
        }
      }`,
      "variables": {
          "contractId": "gid://shopify/SubscriptionContract/593791907",
          "date": "2022-12-01T00:00:00Z"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query subscriptionBillingCycle($contractId: ID!, $date: DateTime!) {
    subscriptionBillingCycle(billingCycleInput: {contractId: $contractId, selector: {date: $date}}) {
      billingAttemptExpectedDate
    }
  }' \
  --variables \
  '{
    "contractId": "gid://shopify/SubscriptionContract/593791907",
    "date": "2022-12-01T00:00:00Z"
  }'
  ```

  #### Response

  ```json
  {
    "subscriptionBillingCycle": {
      "billingAttemptExpectedDate": "2022-12-02T01:00:00Z"
    }
  }
  ```
