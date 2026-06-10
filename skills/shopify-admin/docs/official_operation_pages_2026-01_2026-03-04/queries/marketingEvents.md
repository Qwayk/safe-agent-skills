---
title: marketingEvents - GraphQL Admin
description: A list of marketing events associated with the marketing app.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/marketingEvents'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/marketingEvents.md'
---

# marketing​Events

query

A list of marketing events associated with the marketing app.

## MarketingEventConnection arguments

[MarketingEventConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/MarketingEventConnection)

* after

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* before

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* first

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* last

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* query

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  A filter made up of terms, connectives, modifiers, and comparators. You can apply one or more filters to a query. Learn more about [Shopify API search syntax](https://shopify.dev/api/usage/search-syntax).

  * app\_id

    id

  * description

    string

  * * id

      id

    * started\_at

      time

    - Filter by `id` range.

    - Example:
      * `id:1234`
      * `id:>=1234`
      * `id:<=1234`

  * type

    string

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

* sort​Key

  [Marketing​Event​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/MarketingEventSortKeys)

  Default:ID

  Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

***

## Possible returns

* edges

  [\[Marketing​Event​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketingEventEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Marketing​Event!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketingEvent)

  non-null

  A list of nodes that are contained in MarketingEventEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### Retrieves a list of all marketing events

  #### Query

  ```graphql
  query MarketingEventList {
    marketingEvents(first: 10) {
      edges {
        node {
          id
          type
          remoteId
          startedAt
          endedAt
          scheduledToEndAt
          manageUrl
          previewUrl
          utmCampaign
          utmMedium
          utmSource
          description
          marketingChannelType
          sourceAndMedium
        }
      }
      pageInfo {
        hasNextPage
        endCursor
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
  "query": "query MarketingEventList { marketingEvents(first: 10) { edges { node { id type remoteId startedAt endedAt scheduledToEndAt manageUrl previewUrl utmCampaign utmMedium utmSource description marketingChannelType sourceAndMedium } } pageInfo { hasNextPage endCursor } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query MarketingEventList {
      marketingEvents(first: 10) {
        edges {
          node {
            id
            type
            remoteId
            startedAt
            endedAt
            scheduledToEndAt
            manageUrl
            previewUrl
            utmCampaign
            utmMedium
            utmSource
            description
            marketingChannelType
            sourceAndMedium
          }
        }
        pageInfo {
          hasNextPage
          endCursor
        }
      }
    }`,
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
    query MarketingEventList {
      marketingEvents(first: 10) {
        edges {
          node {
            id
            type
            remoteId
            startedAt
            endedAt
            scheduledToEndAt
            manageUrl
            previewUrl
            utmCampaign
            utmMedium
            utmSource
            description
            marketingChannelType
            sourceAndMedium
          }
        }
        pageInfo {
          hasNextPage
          endCursor
        }
      }
    }
  QUERY

  response = client.query(query: query)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: `query MarketingEventList {
      marketingEvents(first: 10) {
        edges {
          node {
            id
            type
            remoteId
            startedAt
            endedAt
            scheduledToEndAt
            manageUrl
            previewUrl
            utmCampaign
            utmMedium
            utmSource
            description
            marketingChannelType
            sourceAndMedium
          }
        }
        pageInfo {
          hasNextPage
          endCursor
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query MarketingEventList {
    marketingEvents(first: 10) {
      edges {
        node {
          id
          type
          remoteId
          startedAt
          endedAt
          scheduledToEndAt
          manageUrl
          previewUrl
          utmCampaign
          utmMedium
          utmSource
          description
          marketingChannelType
          sourceAndMedium
        }
      }
      pageInfo {
        hasNextPage
        endCursor
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "marketingEvents": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/MarketingEvent/40997430",
            "type": "AD",
            "remoteId": "2345:6789",
            "startedAt": "2012-01-01T00:00:00Z",
            "endedAt": null,
            "scheduledToEndAt": null,
            "manageUrl": null,
            "previewUrl": null,
            "utmCampaign": "1234567899",
            "utmMedium": "facebook-ad",
            "utmSource": "facebook",
            "description": null,
            "marketingChannelType": "SOCIAL",
            "sourceAndMedium": "Facebook ad"
          }
        },
        {
          "node": {
            "id": "gid://shopify/MarketingEvent/56540067",
            "type": "NEWSLETTER",
            "remoteId": "222",
            "startedAt": "2024-11-17T20:47:51Z",
            "endedAt": null,
            "scheduledToEndAt": null,
            "manageUrl": "https://example.com",
            "previewUrl": "https://example.com/image.png",
            "utmCampaign": null,
            "utmMedium": null,
            "utmSource": null,
            "description": "External Marketing Activity Campaign",
            "marketingChannelType": "DISPLAY",
            "sourceAndMedium": "Display newsletter"
          }
        },
        {
          "node": {
            "id": "gid://shopify/MarketingEvent/151661601",
            "type": "NEWSLETTER",
            "remoteId": null,
            "startedAt": "2024-11-08T20:47:51Z",
            "endedAt": null,
            "scheduledToEndAt": null,
            "manageUrl": null,
            "previewUrl": null,
            "utmCampaign": "email-for-deleted-automation",
            "utmMedium": "newsletter",
            "utmSource": "email",
            "description": null,
            "marketingChannelType": "EMAIL",
            "sourceAndMedium": "Email newsletter"
          }
        },
        {
          "node": {
            "id": "gid://shopify/MarketingEvent/178808684",
            "type": "AD",
            "remoteId": null,
            "startedAt": "2012-01-01T00:00:00Z",
            "endedAt": null,
            "scheduledToEndAt": null,
            "manageUrl": null,
            "previewUrl": null,
            "utmCampaign": "google-shopping",
            "utmMedium": "ad",
            "utmSource": "google",
            "description": null,
            "marketingChannelType": "SEARCH",
            "sourceAndMedium": "Google ad"
          }
        },
        {
          "node": {
            "id": "gid://shopify/MarketingEvent/179113300",
            "type": "ABANDONED_CART",
            "remoteId": null,
            "startedAt": "2024-11-03T20:47:51Z",
            "endedAt": null,
            "scheduledToEndAt": null,
            "manageUrl": null,
            "previewUrl": null,
            "utmCampaign": "shopify_abandoned_checkout_email-1519754247",
            "utmMedium": "email",
            "utmSource": "abandoned_cart",
            "description": null,
            "marketingChannelType": "EMAIL",
            "sourceAndMedium": "Abandoned cart email"
          }
        },
        {
          "node": {
            "id": "gid://shopify/MarketingEvent/216774463",
            "type": "NEWSLETTER",
            "remoteId": "333",
            "startedAt": "2024-11-17T20:47:51Z",
            "endedAt": null,
            "scheduledToEndAt": null,
            "manageUrl": "https://example.com",
            "previewUrl": "https://example.com/image.png",
            "utmCampaign": null,
            "utmMedium": null,
            "utmSource": null,
            "description": "External Marketing Activity Ad Group",
            "marketingChannelType": "DISPLAY",
            "sourceAndMedium": "Display newsletter"
          }
        },
        {
          "node": {
            "id": "gid://shopify/MarketingEvent/264437935",
            "type": "NEWSLETTER",
            "remoteId": "444",
            "startedAt": "2024-11-17T20:47:51Z",
            "endedAt": null,
            "scheduledToEndAt": null,
            "manageUrl": "https://example.com",
            "previewUrl": "https://example.com/image.png",
            "utmCampaign": null,
            "utmMedium": null,
            "utmSource": null,
            "description": "External Marketing Activity Ad",
            "marketingChannelType": "DISPLAY",
            "sourceAndMedium": "Display newsletter"
          }
        },
        {
          "node": {
            "id": "gid://shopify/MarketingEvent/283266064",
            "type": "AD",
            "remoteId": null,
            "startedAt": "2012-01-01T00:00:00Z",
            "endedAt": null,
            "scheduledToEndAt": null,
            "manageUrl": null,
            "previewUrl": null,
            "utmCampaign": "google-shopping-4",
            "utmMedium": "ad",
            "utmSource": "google",
            "description": "Marketing Activity 4 for Snowdevil",
            "marketingChannelType": "SEARCH",
            "sourceAndMedium": "Google ad"
          }
        },
        {
          "node": {
            "id": "gid://shopify/MarketingEvent/325573600",
            "type": "POST",
            "remoteId": "1234:56779989",
            "startedAt": "2024-11-17T20:47:51Z",
            "endedAt": null,
            "scheduledToEndAt": null,
            "manageUrl": null,
            "previewUrl": null,
            "utmCampaign": "123456789000",
            "utmMedium": "facebook-post",
            "utmSource": "facebook",
            "description": null,
            "marketingChannelType": "SOCIAL",
            "sourceAndMedium": "Facebook post"
          }
        },
        {
          "node": {
            "id": "gid://shopify/MarketingEvent/425025702",
            "type": "NEWSLETTER",
            "remoteId": null,
            "startedAt": "2024-11-08T20:47:51Z",
            "endedAt": null,
            "scheduledToEndAt": null,
            "manageUrl": null,
            "previewUrl": null,
            "utmCampaign": "asdf",
            "utmMedium": "newsletter",
            "utmSource": "email",
            "description": null,
            "marketingChannelType": "EMAIL",
            "sourceAndMedium": "Email newsletter"
          }
        }
      ],
      "pageInfo": {
        "hasNextPage": true,
        "endCursor": "eyJsYXN0X2lkIjo0MjUwMjU3MDIsImxhc3RfdmFsdWUiOiI0MjUwMjU3MDIifQ=="
      }
    }
  }
  ```
