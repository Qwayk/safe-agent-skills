---
title: mobilePlatformApplications - GraphQL Admin
description: List the mobile platform applications.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/mobilePlatformApplications
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/mobilePlatformApplications.md
---

# mobile​Platform​Applications

query

Requires `read_mobile_platform_applications` access scope. Please contact Shopify Support to enable this scope for your app.

List the mobile platform applications.

## MobilePlatformApplicationConnection arguments

[MobilePlatformApplicationConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/MobilePlatformApplicationConnection)

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

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

***

## Possible returns

* edges

  [\[Mobile​Platform​Application​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MobilePlatformApplicationEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Mobile​Platform​Application!\]!](https://shopify.dev/docs/api/admin-graphql/latest/unions/MobilePlatformApplication)

  non-null

  A list of nodes that are contained in MobilePlatformApplicationEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### Get a list of Mobile Platform Applications

  #### Description

  This example demonstrates how to fetch a list of mobile platform applications.

  #### Query

  ```graphql
  query MobilePlatformApplicationQuery {
    mobilePlatformApplications(first: 10) {
      edges {
        node {
          ... on AndroidApplication {
            id
            applicationId
            sha256CertFingerprints
            appLinksEnabled
            __typename
          }
          ... on AppleApplication {
            id
            appId
            universalLinksEnabled
            appClipApplicationId
            appClipsEnabled
            sharedWebCredentialsEnabled
            __typename
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
  "query": "query MobilePlatformApplicationQuery { mobilePlatformApplications(first: 10) { edges { node { ... on AndroidApplication { id applicationId sha256CertFingerprints appLinksEnabled __typename } ... on AppleApplication { id appId universalLinksEnabled appClipApplicationId appClipsEnabled sharedWebCredentialsEnabled __typename } } } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query MobilePlatformApplicationQuery {
      mobilePlatformApplications(first: 10) {
        edges {
          node {
            ... on AndroidApplication {
              id
              applicationId
              sha256CertFingerprints
              appLinksEnabled
              __typename
            }
            ... on AppleApplication {
              id
              appId
              universalLinksEnabled
              appClipApplicationId
              appClipsEnabled
              sharedWebCredentialsEnabled
              __typename
            }
          }
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
    query MobilePlatformApplicationQuery {
      mobilePlatformApplications(first: 10) {
        edges {
          node {
            ... on AndroidApplication {
              id
              applicationId
              sha256CertFingerprints
              appLinksEnabled
              __typename
            }
            ... on AppleApplication {
              id
              appId
              universalLinksEnabled
              appClipApplicationId
              appClipsEnabled
              sharedWebCredentialsEnabled
              __typename
            }
          }
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
    data: `query MobilePlatformApplicationQuery {
      mobilePlatformApplications(first: 10) {
        edges {
          node {
            ... on AndroidApplication {
              id
              applicationId
              sha256CertFingerprints
              appLinksEnabled
              __typename
            }
            ... on AppleApplication {
              id
              appId
              universalLinksEnabled
              appClipApplicationId
              appClipsEnabled
              sharedWebCredentialsEnabled
              __typename
            }
          }
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query MobilePlatformApplicationQuery {
    mobilePlatformApplications(first: 10) {
      edges {
        node {
          ... on AndroidApplication {
            id
            applicationId
            sha256CertFingerprints
            appLinksEnabled
            __typename
          }
          ... on AppleApplication {
            id
            appId
            universalLinksEnabled
            appClipApplicationId
            appClipsEnabled
            sharedWebCredentialsEnabled
            __typename
          }
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "mobilePlatformApplications": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/MobilePlatformApplication/1066176067",
            "applicationId": "androidfake.org.domain.com",
            "sha256CertFingerprints": [
              "A1:B2:C3:D4"
            ],
            "appLinksEnabled": true,
            "__typename": "AndroidApplication"
          }
        },
        {
          "node": {
            "id": "gid://shopify/MobilePlatformApplication/1066176068",
            "appId": "applefake.org.domain.com",
            "universalLinksEnabled": true,
            "appClipApplicationId": "ios.shopify.io.Clip",
            "appClipsEnabled": true,
            "sharedWebCredentialsEnabled": true,
            "__typename": "AppleApplication"
          }
        }
      ]
    }
  }
  ```
