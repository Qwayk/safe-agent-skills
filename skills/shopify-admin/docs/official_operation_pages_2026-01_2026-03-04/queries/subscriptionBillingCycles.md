---
title: subscriptionBillingCycles - GraphQL Admin
description: Returns subscription billing cycles for a contract ID.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/subscriptionBillingCycles
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/subscriptionBillingCycles.md
---

# subscription​Billing​Cycles

query

Returns subscription billing cycles for a contract ID.

## SubscriptionBillingCycleConnection arguments

[SubscriptionBillingCycleConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/SubscriptionBillingCycleConnection)

* after

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* before

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* billing​Cycles​Date​Range​Selector

  [Subscription​Billing​Cycles​Date​Range​Selector](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/SubscriptionBillingCyclesDateRangeSelector)

  Select subscription billing cycles within a date range.

* billing​Cycles​Index​Range​Selector

  [Subscription​Billing​Cycles​Index​Range​Selector](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/SubscriptionBillingCyclesIndexRangeSelector)

  Select subscription billing cycles within an index range.

* contract​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the subscription contract to retrieve billing cycles for.

* first

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* last

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

* sort​Key

  [Subscription​Billing​Cycles​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/SubscriptionBillingCyclesSortKeys)

  Default:CYCLE\_INDEX

  Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

***

## Possible returns

* edges

  [\[Subscription​Billing​Cycle​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/SubscriptionBillingCycleEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Subscription​Billing​Cycle!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/SubscriptionBillingCycle)

  non-null

  A list of nodes that are contained in SubscriptionBillingCycleEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### Get the billing cycles between specific dates

  #### Description

  Retrieves the billing cycles from \`2022-12-15\` to \`2023-02-15\` and returns their \`billingAttemptExpectedDate\`.

  #### Query

  ```graphql
  query subscriptionBillingCycles($contractId: ID!) {
    subscriptionBillingCycles(first: 10, contractId: $contractId, billingCyclesDateRangeSelector: {startDate: "2022-12-15T00:00:00Z", endDate: "2023-02-15T00:00:00Z"}) {
      edges {
        node {
          billingAttemptExpectedDate
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "contractId": "gid://shopify/SubscriptionContract/593791907"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query subscriptionBillingCycles($contractId: ID!) { subscriptionBillingCycles(first: 10, contractId: $contractId, billingCyclesDateRangeSelector: {startDate: \"2022-12-15T00:00:00Z\", endDate: \"2023-02-15T00:00:00Z\"}) { edges { node { billingAttemptExpectedDate } } } }",
   "variables": {
      "contractId": "gid://shopify/SubscriptionContract/593791907"
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
    query subscriptionBillingCycles($contractId: ID!) {
      subscriptionBillingCycles(first: 10, contractId: $contractId, billingCyclesDateRangeSelector: {startDate: "2022-12-15T00:00:00Z", endDate: "2023-02-15T00:00:00Z"}) {
        edges {
          node {
            billingAttemptExpectedDate
          }
        }
      }
    }`,
    {
      variables: {
          "contractId": "gid://shopify/SubscriptionContract/593791907"
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
    query subscriptionBillingCycles($contractId: ID!) {
      subscriptionBillingCycles(first: 10, contractId: $contractId, billingCyclesDateRangeSelector: {startDate: "2022-12-15T00:00:00Z", endDate: "2023-02-15T00:00:00Z"}) {
        edges {
          node {
            billingAttemptExpectedDate
          }
        }
      }
    }
  QUERY

  variables = {
    "contractId": "gid://shopify/SubscriptionContract/593791907"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query subscriptionBillingCycles($contractId: ID!) {
        subscriptionBillingCycles(first: 10, contractId: $contractId, billingCyclesDateRangeSelector: {startDate: "2022-12-15T00:00:00Z", endDate: "2023-02-15T00:00:00Z"}) {
          edges {
            node {
              billingAttemptExpectedDate
            }
          }
        }
      }`,
      "variables": {
          "contractId": "gid://shopify/SubscriptionContract/593791907"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query subscriptionBillingCycles($contractId: ID!) {
    subscriptionBillingCycles(first: 10, contractId: $contractId, billingCyclesDateRangeSelector: {startDate: "2022-12-15T00:00:00Z", endDate: "2023-02-15T00:00:00Z"}) {
      edges {
        node {
          billingAttemptExpectedDate
        }
      }
    }
  }' \
  --variables \
  '{
    "contractId": "gid://shopify/SubscriptionContract/593791907"
  }'
  ```

  #### Response

  ```json
  {
    "subscriptionBillingCycles": {
      "edges": [
        {
          "node": {
            "billingAttemptExpectedDate": "2023-01-02T01:00:00Z"
          }
        },
        {
          "node": {
            "billingAttemptExpectedDate": "2023-02-02T01:00:00Z"
          }
        },
        {
          "node": {
            "billingAttemptExpectedDate": "2023-03-02T01:00:00Z"
          }
        }
      ]
    }
  }
  ```

* ### Get the billing cycles between specific indexes

  #### Description

  Retrieves the billing cycles from cycle indexes \`1\` to \`3\` and returns their \`billingAttemptExpectedDate\`.

  #### Query

  ```graphql
  query subscriptionBillingCycles($contractId: ID!) {
    subscriptionBillingCycles(first: 10, contractId: $contractId, billingCyclesIndexRangeSelector: {startIndex: 1, endIndex: 3}) {
      edges {
        node {
          billingAttemptExpectedDate
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "contractId": "gid://shopify/SubscriptionContract/593791907"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query subscriptionBillingCycles($contractId: ID!) { subscriptionBillingCycles(first: 10, contractId: $contractId, billingCyclesIndexRangeSelector: {startIndex: 1, endIndex: 3}) { edges { node { billingAttemptExpectedDate } } } }",
   "variables": {
      "contractId": "gid://shopify/SubscriptionContract/593791907"
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
    query subscriptionBillingCycles($contractId: ID!) {
      subscriptionBillingCycles(first: 10, contractId: $contractId, billingCyclesIndexRangeSelector: {startIndex: 1, endIndex: 3}) {
        edges {
          node {
            billingAttemptExpectedDate
          }
        }
      }
    }`,
    {
      variables: {
          "contractId": "gid://shopify/SubscriptionContract/593791907"
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
    query subscriptionBillingCycles($contractId: ID!) {
      subscriptionBillingCycles(first: 10, contractId: $contractId, billingCyclesIndexRangeSelector: {startIndex: 1, endIndex: 3}) {
        edges {
          node {
            billingAttemptExpectedDate
          }
        }
      }
    }
  QUERY

  variables = {
    "contractId": "gid://shopify/SubscriptionContract/593791907"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query subscriptionBillingCycles($contractId: ID!) {
        subscriptionBillingCycles(first: 10, contractId: $contractId, billingCyclesIndexRangeSelector: {startIndex: 1, endIndex: 3}) {
          edges {
            node {
              billingAttemptExpectedDate
            }
          }
        }
      }`,
      "variables": {
          "contractId": "gid://shopify/SubscriptionContract/593791907"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query subscriptionBillingCycles($contractId: ID!) {
    subscriptionBillingCycles(first: 10, contractId: $contractId, billingCyclesIndexRangeSelector: {startIndex: 1, endIndex: 3}) {
      edges {
        node {
          billingAttemptExpectedDate
        }
      }
    }
  }' \
  --variables \
  '{
    "contractId": "gid://shopify/SubscriptionContract/593791907"
  }'
  ```

  #### Response

  ```json
  {
    "subscriptionBillingCycles": {
      "edges": [
        {
          "node": {
            "billingAttemptExpectedDate": "2022-01-02T11:59:59Z"
          }
        },
        {
          "node": {
            "billingAttemptExpectedDate": "2020-11-25T15:00:00Z"
          }
        },
        {
          "node": {
            "billingAttemptExpectedDate": "2022-03-01T00:00:00Z"
          }
        }
      ]
    }
  }
  ```
