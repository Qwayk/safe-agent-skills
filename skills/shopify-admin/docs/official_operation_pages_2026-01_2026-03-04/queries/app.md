---
title: app - GraphQL Admin
description: >-
  Retrieves an
  [`App`](https://shopify.dev/docs/api/admin-graphql/latest/objects/App) by its
  ID. If no ID is provided, returns details about the currently authenticated
  app. The query provides access to app details including title, icon, and
  pricing information.


  If the app isn't installed on the current shop, then the
  [`installation`](https://shopify.dev/docs/api/admin-graphql/latest/queries/app#returns-App.fields.installation)
  field will be `null`.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/app'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/app.md'
---

# app

query

Retrieves an [`App`](https://shopify.dev/docs/api/admin-graphql/latest/objects/App) by its ID. If no ID is provided, returns details about the currently authenticated app. The query provides access to app details including title, icon, and pricing information.

If the app isn't installed on the current shop, then the [`installation`](https://shopify.dev/docs/api/admin-graphql/latest/queries/app#returns-App.fields.installation) field will be `null`.

## Arguments

* id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID to lookup the App by.

***

## Possible returns

* App

  [App](https://shopify.dev/docs/api/admin-graphql/latest/objects/App)

  A Shopify application that extends store functionality. Apps integrate with Shopify through APIs to add features, automate workflows, or connect external services.

  Provides metadata about the app including its developer information and listing details in the Shopify App Store. Use the [`installation`](https://shopify.dev/docs/api/admin-graphql/latest/objects/App#field-App.fields.installation) field to determine if the app is currently installed on the shop and access installation-specific details like granted [`AccessScope`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AccessScope) objects. Check [`failedRequirements`](https://shopify.dev/docs/api/admin-graphql/latest/objects/App#field-App.fields.failedRequirements) before installation to identify any prerequisites that must be met.

  * api​Key

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    A unique application API identifier.

  * app​Store​App​Url

    [URL](https://shopify.dev/docs/api/admin-graphql/latest/scalars/URL)

    App store page URL of the app.

  * app​Store​Developer​Url

    [URL](https://shopify.dev/docs/api/admin-graphql/latest/scalars/URL)

    App store page URL of the developer who created the app.

  * available​Access​Scopes

    [\[Access​Scope!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/AccessScope)

    non-null

    All requestable access scopes available to the app.

  * banner

    [Image!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Image)

    non-null

    Banner image for the app.

  * description

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    Description of the app.

  * developer​Name

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The name of the app developer.

  * developer​Type

    [App​Developer​Type!](https://shopify.dev/docs/api/admin-graphql/latest/enums/AppDeveloperType)

    non-null

    The type of app developer.

  * embedded

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the app uses the Embedded App SDK.

  * failed​Requirements

    [\[Failed​Requirement!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/FailedRequirement)

    non-null

    Requirements that must be met before the app can be installed.

  * features

    [\[String!\]!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    A list of app features that are shown in the Shopify App Store listing.

  * feedback

    [App​Feedback](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppFeedback)

    Feedback from this app about the store.

  * handle

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    Handle of the app.

  * icon

    [Image!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Image)

    non-null

    Icon that represents the app.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * installation

    [App​Installation](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppInstallation)

    Corresponding AppInstallation for this shop and App. Returns null if the App is not installed.

  * install​Url

    [URL](https://shopify.dev/docs/api/admin-graphql/latest/scalars/URL)

    Webpage where you can install the app, if app requires explicit user permission.

  * is​Post​Purchase​App​In​Use

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the app is the [post purchase](https://shopify.dev/apps/checkout/post-purchase) app in use.

  * optional​Access​Scopes

    [\[Access​Scope!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/AccessScope)

    non-null

    The optional scopes requested by the app. Lists the optional access scopes the app has declared in its configuration. These scopes are optionally requested by the app after installation.

  * previously​Installed

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the app was previously installed on the current shop.

  * pricing​Details

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    Detailed information about the app pricing.

  * pricing​Details​Summary

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    Summary of the app pricing details.

  * privacy​Policy​Url

    [URL](https://shopify.dev/docs/api/admin-graphql/latest/scalars/URL)

    Link to app privacy policy.

  * public​Category

    [App​Public​Category!](https://shopify.dev/docs/api/admin-graphql/latest/enums/AppPublicCategory)

    non-null

    The public category for the app.

  * published

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the app is published to the Shopify App Store.

  * requested​Access​Scopes

    [\[Access​Scope!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/AccessScope)

    non-null

    The access scopes requested by the app. Lists the access scopes the app has declared in its configuration. Merchant must grant approval to these scopes for the app to be installed.

  * screenshots

    [\[Image!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Image)

    non-null

    Screenshots of the app.

  * shopify​Developed

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the app was developed by Shopify.

  * title

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    Name of the app.

  * uninstall​Message

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    Message that appears when the app is uninstalled. For example: By removing this app, you will no longer be able to publish products to MySocialSite or view this app in your Shopify admin. You can re-enable this channel at any time.

  * webhook​Api​Version

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The webhook API version for the app.

  * developer​Url

    [URL!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/URL)

    non-nullDeprecated

  * launch​Url

    [URL!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/URL)

    non-nullDeprecated

  * navigation​Items

    [\[Navigation​Item!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/NavigationItem)

    non-nullDeprecated

  * uninstall​Url

    [URL](https://shopify.dev/docs/api/admin-graphql/latest/scalars/URL)

    Deprecated

***

## Examples

* ### Get an app by its ID

  #### Description

  Retrieve an app with its ID, returning the app title

  #### Query

  ```graphql
  query {
    app(id: "gid://shopify/App/193172482") {
      title
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
  "query": "query { app(id: \"gid://shopify/App/193172482\") { title } }"
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
      app(id: "gid://shopify/App/193172482") {
        title
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
      app(id: "gid://shopify/App/193172482") {
        title
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
      app(id: "gid://shopify/App/193172482") {
        title
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    app(id: "gid://shopify/App/193172482") {
      title
    }
  }'
  ```

  #### Response

  ```json
  {
    "app": {
      "title": "Invoicing Application"
    }
  }
  ```

* ### Get the currently authenticated app

  #### Description

  Retrieve the currently authenticated app, returning the app title

  #### Query

  ```graphql
  query {
    app {
      title
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
  "query": "query { app { title } }"
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
      app {
        title
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
      app {
        title
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
      app {
        title
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    app {
      title
    }
  }'
  ```

  #### Response

  ```json
  {
    "app": {
      "title": "Invoicing Application"
    }
  }
  ```

* ### Get the feedback field

  #### Query

  ```graphql
  query ShopFeedbackList {
    app(id: "gid://shopify/App/88312") {
      feedback {
        messages {
          message
        }
        feedbackGeneratedAt
        state
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
  "query": "query ShopFeedbackList { app(id: \"gid://shopify/App/88312\") { feedback { messages { message } feedbackGeneratedAt state } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query ShopFeedbackList {
      app(id: "gid://shopify/App/88312") {
        feedback {
          messages {
            message
          }
          feedbackGeneratedAt
          state
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
    query ShopFeedbackList {
      app(id: "gid://shopify/App/88312") {
        feedback {
          messages {
            message
          }
          feedbackGeneratedAt
          state
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
    data: `query ShopFeedbackList {
      app(id: "gid://shopify/App/88312") {
        feedback {
          messages {
            message
          }
          feedbackGeneratedAt
          state
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query ShopFeedbackList {
    app(id: "gid://shopify/App/88312") {
      feedback {
        messages {
          message
        }
        feedbackGeneratedAt
        state
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "app": {
      "feedback": {
        "messages": [
          {
            "message": "Buy Button is not connected. Connect your account to use this sales channel."
          }
        ],
        "feedbackGeneratedAt": "2024-12-17T19:29:36Z",
        "state": "REQUIRES_ACTION"
      }
    }
  }
  ```
