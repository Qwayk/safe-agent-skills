---
title: appInstallation - GraphQL Admin
description: >-
  Retrieves an
  [`AppInstallation`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppInstallation)
  by ID. If no ID is provided, returns the installation for the currently
  authenticated
  [`App`](https://shopify.dev/docs/api/admin-graphql/latest/objects/App). The
  query provides essential data for validating installation state and managing
  app functionality within a store.


  Use this query to access installation details including granted
  [`AccessScope`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AccessScope)
  objects, active
  [`AppSubscription`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppSubscription)
  objects,
  [`AppCredit`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppCredit)
  objects,
  [`AppPurchaseOneTime`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppPurchaseOneTime)
  objects, and app-specific metadata.


  Learn more about [app
  installation](https://shopify.dev/docs/apps/build/authentication-authorization/app-installation).
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/appInstallation'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/appInstallation.md'
---

# app​Installation

query

Retrieves an [`AppInstallation`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppInstallation) by ID. If no ID is provided, returns the installation for the currently authenticated [`App`](https://shopify.dev/docs/api/admin-graphql/latest/objects/App). The query provides essential data for validating installation state and managing app functionality within a store.

Use this query to access installation details including granted [`AccessScope`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AccessScope) objects, active [`AppSubscription`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppSubscription) objects, [`AppCredit`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppCredit) objects, [`AppPurchaseOneTime`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppPurchaseOneTime) objects, and app-specific metadata.

Learn more about [app installation](https://shopify.dev/docs/apps/build/authentication-authorization/app-installation).

## Arguments

* id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  ID used to lookup AppInstallation.

***

## Possible returns

* App​Installation

  [App​Installation](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppInstallation)

  An app installed on a shop. Each installation tracks the permissions granted to the app through [`AccessScope`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AccessScope) objects, along with billing subscriptions and [`Metafield`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Metafield) objects.

  The installation provides metafields that only the owning [`App`](https://shopify.dev/docs/api/admin-graphql/latest/objects/App) can access. These metafields store app-specific configuration that merchants and other apps can't modify. The installation also provides URLs for launching and uninstalling the app, along with any active [`AppSubscription`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppSubscription) objects or [`AppPurchaseOneTime`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppPurchaseOneTime) purchases.

  * access​Scopes

    [\[Access​Scope!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/AccessScope)

    non-null

    The access scopes granted to the application by a merchant during installation.

  * active​Subscriptions

    [\[App​Subscription!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppSubscription)

    non-null

    The active application subscriptions billed to the shop on a recurring basis.

  * all​Subscriptions

    [App​Subscription​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/AppSubscriptionConnection)

    non-null

    All subscriptions created for a shop.

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

    * sort​Key

      [App​Subscription​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/AppSubscriptionSortKeys)

      Default:CREATED\_AT

      Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

    ***

  * app

    [App!](https://shopify.dev/docs/api/admin-graphql/latest/objects/App)

    non-null

    Application which is installed.

  * credits

    [App​Credit​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/AppCreditConnection)

    non-null

    Credits that can be used towards future app purchases.

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

    * sort​Key

      [App​Transaction​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/AppTransactionSortKeys)

      Default:CREATED\_AT

      Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

    ***

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * launch​Url

    [URL!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/URL)

    non-null

    The URL to launch the application.

  * metafield

    [Metafield](https://shopify.dev/docs/api/admin-graphql/latest/objects/Metafield)

    A [custom field](https://shopify.dev/docs/apps/build/custom-data), including its `namespace` and `key`, that's associated with a Shopify resource for the purposes of adding and storing additional information.

    * namespace

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      ### Arguments

      The container the metafield belongs to. If omitted, the app-reserved namespace will be used.

    * key

      [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      required

      The key for the metafield.

    ***

  * metafields

    [Metafield​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/MetafieldConnection)

    non-null

    A list of [custom fields](https://shopify.dev/docs/apps/build/custom-data) that a merchant associates with a Shopify resource.

    * namespace

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      ### Arguments

      The metafield namespace to filter by. If omitted, all metafields are returned.

    * keys

      [\[String!\]](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      List of keys of metafields in the format `namespace.key`, will be returned in the same format.

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

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

  * one​Time​Purchases

    [App​Purchase​One​Time​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/AppPurchaseOneTimeConnection)

    non-null

    One-time purchases to a shop.

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

    * sort​Key

      [App​Transaction​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/AppTransactionSortKeys)

      Default:CREATED\_AT

      Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

    ***

  * revenue​Attribution​Records

    [App​Revenue​Attribution​Record​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/AppRevenueAttributionRecordConnection)

    non-null

    The records that track the externally-captured revenue for the app. The records are used for revenue attribution purposes.

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

    * sort​Key

      [App​Revenue​Attribution​Record​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/AppRevenueAttributionRecordSortKeys)

      Default:CREATED\_AT

      Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

    ***

  * uninstall​Url

    [URL](https://shopify.dev/docs/api/admin-graphql/latest/scalars/URL)

    The URL to uninstall the application.

  * channel

    [Channel](https://shopify.dev/docs/api/admin-graphql/latest/objects/Channel)

    Deprecated

  * publication

    [Publication](https://shopify.dev/docs/api/admin-graphql/latest/objects/Publication)

    Deprecated

  * subscriptions

    [\[App​Subscription!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppSubscription)

    non-nullDeprecated

***

## Examples

* ### Get a metafield attached to an app installation

  #### Description

  Get the metafield value identified by \`secret\_keys.api\_key\` on a specific app installation.

  #### Query

  ```graphql
  query AppInstallationMetafield($namespace: String!, $key: String!, $ownerId: ID!) {
    appInstallation(id: $ownerId) {
      apiKey: metafield(namespace: $namespace, key: $key) {
        value
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "namespace": "secret_keys",
    "key": "api_key",
    "ownerId": "gid://shopify/AppInstallation/1002334195"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query AppInstallationMetafield($namespace: String!, $key: String!, $ownerId: ID!) { appInstallation(id: $ownerId) { apiKey: metafield(namespace: $namespace, key: $key) { value } } }",
   "variables": {
      "namespace": "secret_keys",
      "key": "api_key",
      "ownerId": "gid://shopify/AppInstallation/1002334195"
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
    query AppInstallationMetafield($namespace: String!, $key: String!, $ownerId: ID!) {
      appInstallation(id: $ownerId) {
        apiKey: metafield(namespace: $namespace, key: $key) {
          value
        }
      }
    }`,
    {
      variables: {
          "namespace": "secret_keys",
          "key": "api_key",
          "ownerId": "gid://shopify/AppInstallation/1002334195"
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
    query AppInstallationMetafield($namespace: String!, $key: String!, $ownerId: ID!) {
      appInstallation(id: $ownerId) {
        apiKey: metafield(namespace: $namespace, key: $key) {
          value
        }
      }
    }
  QUERY

  variables = {
    "namespace": "secret_keys",
    "key": "api_key",
    "ownerId": "gid://shopify/AppInstallation/1002334195"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query AppInstallationMetafield($namespace: String!, $key: String!, $ownerId: ID!) {
        appInstallation(id: $ownerId) {
          apiKey: metafield(namespace: $namespace, key: $key) {
            value
          }
        }
      }`,
      "variables": {
          "namespace": "secret_keys",
          "key": "api_key",
          "ownerId": "gid://shopify/AppInstallation/1002334195"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query AppInstallationMetafield($namespace: String!, $key: String!, $ownerId: ID!) {
    appInstallation(id: $ownerId) {
      apiKey: metafield(namespace: $namespace, key: $key) {
        value
      }
    }
  }' \
  --variables \
  '{
    "namespace": "secret_keys",
    "key": "api_key",
    "ownerId": "gid://shopify/AppInstallation/1002334195"
  }'
  ```

  #### Response

  ```json
  {
    "appInstallation": {
      "apiKey": {
        "value": "aSBhbSBhIHNlY3JldCBrZXk="
      }
    }
  }
  ```

* ### Get metafields attached to an app installation

  #### Description

  Get a page of metafields attached to a specific app installation.

  #### Query

  ```graphql
  query AppInstallationMetafields($ownerId: ID!) {
    appInstallation(id: $ownerId) {
      metafields(first: 3) {
        edges {
          node {
            namespace
            key
            value
          }
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "ownerId": "gid://shopify/AppInstallation/1002334195"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query AppInstallationMetafields($ownerId: ID!) { appInstallation(id: $ownerId) { metafields(first: 3) { edges { node { namespace key value } } } } }",
   "variables": {
      "ownerId": "gid://shopify/AppInstallation/1002334195"
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
    query AppInstallationMetafields($ownerId: ID!) {
      appInstallation(id: $ownerId) {
        metafields(first: 3) {
          edges {
            node {
              namespace
              key
              value
            }
          }
        }
      }
    }`,
    {
      variables: {
          "ownerId": "gid://shopify/AppInstallation/1002334195"
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
    query AppInstallationMetafields($ownerId: ID!) {
      appInstallation(id: $ownerId) {
        metafields(first: 3) {
          edges {
            node {
              namespace
              key
              value
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "ownerId": "gid://shopify/AppInstallation/1002334195"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query AppInstallationMetafields($ownerId: ID!) {
        appInstallation(id: $ownerId) {
          metafields(first: 3) {
            edges {
              node {
                namespace
                key
                value
              }
            }
          }
        }
      }`,
      "variables": {
          "ownerId": "gid://shopify/AppInstallation/1002334195"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query AppInstallationMetafields($ownerId: ID!) {
    appInstallation(id: $ownerId) {
      metafields(first: 3) {
        edges {
          node {
            namespace
            key
            value
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "ownerId": "gid://shopify/AppInstallation/1002334195"
  }'
  ```

  #### Response

  ```json
  {
    "appInstallation": {
      "metafields": {
        "edges": [
          {
            "node": {
              "namespace": "secret_keys",
              "key": "api_key",
              "value": "aSBhbSBhIHNlY3JldCBrZXk="
            }
          }
        ]
      }
    }
  }
  ```

* ### Get the URL used to launch the application

  #### Description

  The following query retrieves the launchUrl associated with the appInstallation.

  #### Query

  ```graphql
  query {
    appInstallation(id: "gid://shopify/AppInstallation/1002334195") {
      launchUrl
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
  "query": "query { appInstallation(id: \"gid://shopify/AppInstallation/1002334195\") { launchUrl } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query {
      appInstallation(id: "gid://shopify/AppInstallation/1002334195") {
        launchUrl
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
    query {
      appInstallation(id: "gid://shopify/AppInstallation/1002334195") {
        launchUrl
      }
    }
  QUERY

  response = client.query(query: query)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: `query {
      appInstallation(id: "gid://shopify/AppInstallation/1002334195") {
        launchUrl
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    appInstallation(id: "gid://shopify/AppInstallation/1002334195") {
      launchUrl
    }
  }'
  ```

  #### Response

  ```json
  {
    "appInstallation": {
      "launchUrl": "https://snowdevil.myshopify.com/admin/api_permissions/1002334195/redirect"
    }
  }
  ```

* ### Get the URL used to uninstall the application

  #### Description

  The following query retrieves the uninstallUrl associated with the appInstallation.

  #### Query

  ```graphql
  query {
    appInstallation(id: "gid://shopify/AppInstallation/688276949") {
      uninstallUrl
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
  "query": "query { appInstallation(id: \"gid://shopify/AppInstallation/688276949\") { uninstallUrl } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query {
      appInstallation(id: "gid://shopify/AppInstallation/688276949") {
        uninstallUrl
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
    query {
      appInstallation(id: "gid://shopify/AppInstallation/688276949") {
        uninstallUrl
      }
    }
  QUERY

  response = client.query(query: query)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: `query {
      appInstallation(id: "gid://shopify/AppInstallation/688276949") {
        uninstallUrl
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    appInstallation(id: "gid://shopify/AppInstallation/688276949") {
      uninstallUrl
    }
  }'
  ```

  #### Response

  ```json
  {
    "appInstallation": {
      "uninstallUrl": null
    }
  }
  ```

* ### Get the access scopes associated with the app installation

  #### Description

  The following query returns all the access scopes that were granted to the application during installation.

  #### Query

  ```graphql
  query {
    appInstallation(id: "gid://shopify/AppInstallation/1002334195") {
      accessScopes {
        handle
        description
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
  "query": "query { appInstallation(id: \"gid://shopify/AppInstallation/1002334195\") { accessScopes { handle description } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query {
      appInstallation(id: "gid://shopify/AppInstallation/1002334195") {
        accessScopes {
          handle
          description
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
    query {
      appInstallation(id: "gid://shopify/AppInstallation/1002334195") {
        accessScopes {
          handle
          description
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
    data: `query {
      appInstallation(id: "gid://shopify/AppInstallation/1002334195") {
        accessScopes {
          handle
          description
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    appInstallation(id: "gid://shopify/AppInstallation/1002334195") {
      accessScopes {
        handle
        description
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "appInstallation": {
      "accessScopes": [
        {
          "handle": "write_content",
          "description": "Modify store content like articles, blogs, comments, pages, and redirects"
        },
        {
          "handle": "write_themes",
          "description": "Modify theme templates and theme assets"
        },
        {
          "handle": "write_products",
          "description": "Modify products, variants, and collections"
        },
        {
          "handle": "write_customers",
          "description": "Modify customer details and customer groups"
        },
        {
          "handle": "write_orders",
          "description": "Modify orders, transactions, and fulfillments"
        },
        {
          "handle": "write_script_tags",
          "description": "Modify script tags in your store's theme template files"
        },
        {
          "handle": "write_shipping",
          "description": "Modify shipping rates, countries, and provinces"
        },
        {
          "handle": "read_content",
          "description": "Read store content like articles, blogs, comments, pages, and redirects"
        },
        {
          "handle": "read_themes",
          "description": "Read theme templates and theme assets"
        },
        {
          "handle": "read_products",
          "description": "Read products, variants, and collections"
        },
        {
          "handle": "read_customers",
          "description": "Read customer details and customer groups"
        },
        {
          "handle": "read_orders",
          "description": "Read orders, transactions, and fulfillments"
        },
        {
          "handle": "read_script_tags",
          "description": "Read script tags in your store's theme template files"
        },
        {
          "handle": "read_shipping",
          "description": "Read shipping rates, countries, and provinces"
        }
      ]
    }
  }
  ```

* ### Get the active subscriptions for the app installation

  #### Description

  The following query returns the IDs of the active subscriptions billed by the application. Returns an "access denied" error if the user is not allowed to approve application charges.

  #### Query

  ```graphql
  query {
    appInstallation(id: "gid://shopify/AppInstallation/881878037") {
      activeSubscriptions {
        id
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
  "query": "query { appInstallation(id: \"gid://shopify/AppInstallation/881878037\") { activeSubscriptions { id } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query {
      appInstallation(id: "gid://shopify/AppInstallation/881878037") {
        activeSubscriptions {
          id
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
    query {
      appInstallation(id: "gid://shopify/AppInstallation/881878037") {
        activeSubscriptions {
          id
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
    data: `query {
      appInstallation(id: "gid://shopify/AppInstallation/881878037") {
        activeSubscriptions {
          id
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    appInstallation(id: "gid://shopify/AppInstallation/881878037") {
      activeSubscriptions {
        id
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "appInstallation": {
      "activeSubscriptions": [
        {
          "id": "gid://shopify/AppSubscription/1029266946"
        }
      ]
    }
  }
  ```

* ### Get the app associated with the installation

  #### Description

  The following query retrieves the application associated with the installation, returning the associated ID.

  #### Query

  ```graphql
  query {
    appInstallation(id: "gid://shopify/AppInstallation/1002334195") {
      app {
        id
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
  "query": "query { appInstallation(id: \"gid://shopify/AppInstallation/1002334195\") { app { id } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query {
      appInstallation(id: "gid://shopify/AppInstallation/1002334195") {
        app {
          id
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
    query {
      appInstallation(id: "gid://shopify/AppInstallation/1002334195") {
        app {
          id
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
    data: `query {
      appInstallation(id: "gid://shopify/AppInstallation/1002334195") {
        app {
          id
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    appInstallation(id: "gid://shopify/AppInstallation/1002334195") {
      app {
        id
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "appInstallation": {
      "app": {
        "id": "gid://shopify/App/1002334195"
      }
    }
  }
  ```

* ### Retrieves all application credits

  #### Query

  ```graphql
  query GetAppInstallationCredits($appInstallationId: ID!) {
    appInstallation(id: $appInstallationId) {
      credits(first: 10) {
        edges {
          node {
            amount {
              amount
              currencyCode
            }
            createdAt
            description
            id
          }
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "appInstallationId": "gid://shopify/AppInstallation/236444539"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query GetAppInstallationCredits($appInstallationId: ID!) { appInstallation(id: $appInstallationId) { credits(first: 10) { edges { node { amount { amount currencyCode } createdAt description id } } } } }",
   "variables": {
      "appInstallationId": "gid://shopify/AppInstallation/236444539"
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
    query GetAppInstallationCredits($appInstallationId: ID!) {
      appInstallation(id: $appInstallationId) {
        credits(first: 10) {
          edges {
            node {
              amount {
                amount
                currencyCode
              }
              createdAt
              description
              id
            }
          }
        }
      }
    }`,
    {
      variables: {
          "appInstallationId": "gid://shopify/AppInstallation/236444539"
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
    query GetAppInstallationCredits($appInstallationId: ID!) {
      appInstallation(id: $appInstallationId) {
        credits(first: 10) {
          edges {
            node {
              amount {
                amount
                currencyCode
              }
              createdAt
              description
              id
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "appInstallationId": "gid://shopify/AppInstallation/236444539"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query GetAppInstallationCredits($appInstallationId: ID!) {
        appInstallation(id: $appInstallationId) {
          credits(first: 10) {
            edges {
              node {
                amount {
                  amount
                  currencyCode
                }
                createdAt
                description
                id
              }
            }
          }
        }
      }`,
      "variables": {
          "appInstallationId": "gid://shopify/AppInstallation/236444539"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query GetAppInstallationCredits($appInstallationId: ID!) {
    appInstallation(id: $appInstallationId) {
      credits(first: 10) {
        edges {
          node {
            amount {
              amount
              currencyCode
            }
            createdAt
            description
            id
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "appInstallationId": "gid://shopify/AppInstallation/236444539"
  }'
  ```

  #### Response

  ```json
  {
    "appInstallation": {
      "credits": {
        "edges": []
      }
    }
  }
  ```
