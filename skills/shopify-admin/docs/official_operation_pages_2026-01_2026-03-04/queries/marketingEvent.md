---
title: marketingEvent - GraphQL Admin
description: Returns a `MarketingEvent` resource by ID.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/marketingEvent'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/marketingEvent.md'
---

# marketing​Event

query

Returns a `MarketingEvent` resource by ID.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the `MarketingEvent` to return.

***

## Possible returns

* Marketing​Event

  [Marketing​Event](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketingEvent)

  Represents actions that market a merchant's store or products.

  * app

    [App!](https://shopify.dev/docs/api/admin-graphql/latest/objects/App)

    non-null

    The app that the marketing event is attributed to.

  * channel​Handle

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The unique string identifier of the channel to which this activity belongs. For the correct handle for your channel, contact your partner manager.

  * description

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    A human-readable description of the marketing event.

  * ended​At

    [Date​Time](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    The date and time when the marketing event ended.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * legacy​Resource​Id

    [Unsigned​Int64!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/UnsignedInt64)

    non-null

    The ID of the corresponding resource in the REST Admin API.

  * manage​Url

    [URL](https://shopify.dev/docs/api/admin-graphql/latest/scalars/URL)

    The URL where the marketing event can be managed.

  * marketing​Channel​Type

    [Marketing​Channel](https://shopify.dev/docs/api/admin-graphql/latest/enums/MarketingChannel)

    The medium through which the marketing activity and event reached consumers. This is used for reporting aggregation.

  * preview​Url

    [URL](https://shopify.dev/docs/api/admin-graphql/latest/scalars/URL)

    The URL where the marketing event can be previewed.

  * remote​Id

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    An optional ID that helps Shopify validate engagement data.

  * scheduled​To​End​At

    [Date​Time](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    The date and time when the marketing event is scheduled to end.

  * source​And​Medium

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    Where the `MarketingEvent` occurred and what kind of content was used. Because `utmSource` and `utmMedium` are often used interchangeably, this is based on a combination of `marketingChannel`, `referringDomain`, and `type` to provide a consistent representation for any given piece of marketing regardless of the app that created it.

  * started​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time when the marketing event started.

  * type

    [Marketing​Tactic!](https://shopify.dev/docs/api/admin-graphql/latest/enums/MarketingTactic)

    non-null

    The marketing event type.

  * utm​Campaign

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The name of the marketing campaign.

  * utm​Medium

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The medium that the marketing campaign is using. Example values: `cpc`, `banner`.

  * utm​Source

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The referrer of the marketing event. Example values: `google`, `newsletter`.

  * channel

    [Marketing​Channel](https://shopify.dev/docs/api/admin-graphql/latest/enums/MarketingChannel)

    Deprecated

  * target​Type​Display​Text

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-nullDeprecated

***

## Examples

* ### Retrieves a single marketing event

  #### Query

  ```graphql
  query MarketingEventShow {
    marketingEvent(id: "gid://shopify/MarketingEvent/425025702") {
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
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query MarketingEventShow { marketingEvent(id: \"gid://shopify/MarketingEvent/425025702\") { id type remoteId startedAt endedAt scheduledToEndAt manageUrl previewUrl utmCampaign utmMedium utmSource description marketingChannelType sourceAndMedium } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query MarketingEventShow {
      marketingEvent(id: "gid://shopify/MarketingEvent/425025702") {
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
    query MarketingEventShow {
      marketingEvent(id: "gid://shopify/MarketingEvent/425025702") {
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
  QUERY

  response = client.query(query: query)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: `query MarketingEventShow {
      marketingEvent(id: "gid://shopify/MarketingEvent/425025702") {
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
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query MarketingEventShow {
    marketingEvent(id: "gid://shopify/MarketingEvent/425025702") {
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
  }'
  ```

  #### Response

  ```json
  {
    "marketingEvent": {
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
  ```
