---
title: marketingEngagementCreate - GraphQL Admin
description: >-
  Creates a new marketing engagement for a marketing activity or a marketing
  channel.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/marketingEngagementCreate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/marketingEngagementCreate.md
---

# marketing​Engagement​Create

mutation

Requires `write_marketing_events` access scope.

Creates a new marketing engagement for a marketing activity or a marketing channel.

## Arguments

* channel​Handle

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The unique string identifier of the channel to which the engagement metrics are being provided. This should be set when and only when providing channel-level engagements. This should be nil when providing activity-level engagements. For the correct handle for your channel, contact your partner manager.

* marketing​Activity​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The identifier of the marketing activity for which the engagement metrics are being provided. This or the remoteId should be set when and only when providing activity-level engagements. This should be nil when providing channel-level engagements.

* marketing​Engagement

  [Marketing​Engagement​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/MarketingEngagementInput)

  required

  The marketing engagement's attributes.

* remote​Id

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  A custom unique identifier for the marketing activity, which can be used to manage the activity and send engagement metrics without having to store our marketing activity ID in your systems. This or the marketingActivityId should be set when and only when providing activity-level engagements. This should be nil when providing channel-level engagements.

***

## Marketing​Engagement​Create​Payload returns

* marketing​Engagement

  [Marketing​Engagement](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketingEngagement)

  The marketing engagement that was created. This represents customer activity taken on a marketing activity or a marketing channel.

* user​Errors

  [\[Marketing​Activity​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketingActivityUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create activity-level engagement for a marketing activity ID

  #### Query

  ```graphql
  mutation M($marketingEngagement: MarketingEngagementInput!, $marketingActivityId: ID, $channelHandle: String, $remoteId: String) {
    marketingEngagementCreate(marketingEngagement: $marketingEngagement, marketingActivityId: $marketingActivityId, channelHandle: $channelHandle, remoteId: $remoteId) {
      marketingEngagement {
        occurredOn
        utcOffset
        isCumulative
        adSpend {
          amount
          currencyCode
        }
        clicksCount
        impressionsCount
        commentsCount
        favoritesCount
        unsubscribesCount
        complaintsCount
        failsCount
        sendsCount
        uniqueViewsCount
        uniqueClicksCount
        sharesCount
        viewsCount
        sessionsCount
        sales {
          amount
          currencyCode
        }
        orders
        firstTimeCustomers
        returningCustomers
        marketingActivity {
          id
        }
        channelHandle
      }
      userErrors {
        field
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "marketingEngagement": {
      "occurredOn": "2018-06-29",
      "utcOffset": "-07:00",
      "isCumulative": false,
      "adSpend": {
        "currencyCode": "CAD",
        "amount": "19.90"
      },
      "impressionsCount": 100,
      "clicksCount": 40,
      "commentsCount": 1,
      "unsubscribesCount": 1,
      "complaintsCount": 1,
      "failsCount": 1,
      "sendsCount": 1,
      "uniqueViewsCount": 1,
      "uniqueClicksCount": 1,
      "sharesCount": 5,
      "viewsCount": 10,
      "favoritesCount": 0,
      "sessionsCount": 40,
      "sales": {
        "amount": "304.50",
        "currencyCode": "CAD"
      },
      "orders": 8,
      "firstTimeCustomers": 5,
      "returningCustomers": 3
    },
    "marketingActivityId": "gid://shopify/MarketingActivity/794355127",
    "channelHandle": null,
    "remoteId": null
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation M($marketingEngagement: MarketingEngagementInput!, $marketingActivityId: ID, $channelHandle: String, $remoteId: String) { marketingEngagementCreate(marketingEngagement: $marketingEngagement, marketingActivityId: $marketingActivityId, channelHandle: $channelHandle, remoteId: $remoteId) { marketingEngagement { occurredOn utcOffset isCumulative adSpend { amount currencyCode } clicksCount impressionsCount commentsCount favoritesCount unsubscribesCount complaintsCount failsCount sendsCount uniqueViewsCount uniqueClicksCount sharesCount viewsCount sessionsCount sales { amount currencyCode } orders firstTimeCustomers returningCustomers marketingActivity { id } channelHandle } userErrors { field message } } }",
   "variables": {
      "marketingEngagement": {
        "occurredOn": "2018-06-29",
        "utcOffset": "-07:00",
        "isCumulative": false,
        "adSpend": {
          "currencyCode": "CAD",
          "amount": "19.90"
        },
        "impressionsCount": 100,
        "clicksCount": 40,
        "commentsCount": 1,
        "unsubscribesCount": 1,
        "complaintsCount": 1,
        "failsCount": 1,
        "sendsCount": 1,
        "uniqueViewsCount": 1,
        "uniqueClicksCount": 1,
        "sharesCount": 5,
        "viewsCount": 10,
        "favoritesCount": 0,
        "sessionsCount": 40,
        "sales": {
          "amount": "304.50",
          "currencyCode": "CAD"
        },
        "orders": 8,
        "firstTimeCustomers": 5,
        "returningCustomers": 3
      },
      "marketingActivityId": "gid://shopify/MarketingActivity/794355127",
      "channelHandle": null,
      "remoteId": null
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
    mutation M($marketingEngagement: MarketingEngagementInput!, $marketingActivityId: ID, $channelHandle: String, $remoteId: String) {
      marketingEngagementCreate(marketingEngagement: $marketingEngagement, marketingActivityId: $marketingActivityId, channelHandle: $channelHandle, remoteId: $remoteId) {
        marketingEngagement {
          occurredOn
          utcOffset
          isCumulative
          adSpend {
            amount
            currencyCode
          }
          clicksCount
          impressionsCount
          commentsCount
          favoritesCount
          unsubscribesCount
          complaintsCount
          failsCount
          sendsCount
          uniqueViewsCount
          uniqueClicksCount
          sharesCount
          viewsCount
          sessionsCount
          sales {
            amount
            currencyCode
          }
          orders
          firstTimeCustomers
          returningCustomers
          marketingActivity {
            id
          }
          channelHandle
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "marketingEngagement": {
              "occurredOn": "2018-06-29",
              "utcOffset": "-07:00",
              "isCumulative": false,
              "adSpend": {
                  "currencyCode": "CAD",
                  "amount": "19.90"
              },
              "impressionsCount": 100,
              "clicksCount": 40,
              "commentsCount": 1,
              "unsubscribesCount": 1,
              "complaintsCount": 1,
              "failsCount": 1,
              "sendsCount": 1,
              "uniqueViewsCount": 1,
              "uniqueClicksCount": 1,
              "sharesCount": 5,
              "viewsCount": 10,
              "favoritesCount": 0,
              "sessionsCount": 40,
              "sales": {
                  "amount": "304.50",
                  "currencyCode": "CAD"
              },
              "orders": 8,
              "firstTimeCustomers": 5,
              "returningCustomers": 3
          },
          "marketingActivityId": "gid://shopify/MarketingActivity/794355127",
          "channelHandle": null,
          "remoteId": null
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
    mutation M($marketingEngagement: MarketingEngagementInput!, $marketingActivityId: ID, $channelHandle: String, $remoteId: String) {
      marketingEngagementCreate(marketingEngagement: $marketingEngagement, marketingActivityId: $marketingActivityId, channelHandle: $channelHandle, remoteId: $remoteId) {
        marketingEngagement {
          occurredOn
          utcOffset
          isCumulative
          adSpend {
            amount
            currencyCode
          }
          clicksCount
          impressionsCount
          commentsCount
          favoritesCount
          unsubscribesCount
          complaintsCount
          failsCount
          sendsCount
          uniqueViewsCount
          uniqueClicksCount
          sharesCount
          viewsCount
          sessionsCount
          sales {
            amount
            currencyCode
          }
          orders
          firstTimeCustomers
          returningCustomers
          marketingActivity {
            id
          }
          channelHandle
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "marketingEngagement": {
      "occurredOn": "2018-06-29",
      "utcOffset": "-07:00",
      "isCumulative": false,
      "adSpend": {
        "currencyCode": "CAD",
        "amount": "19.90"
      },
      "impressionsCount": 100,
      "clicksCount": 40,
      "commentsCount": 1,
      "unsubscribesCount": 1,
      "complaintsCount": 1,
      "failsCount": 1,
      "sendsCount": 1,
      "uniqueViewsCount": 1,
      "uniqueClicksCount": 1,
      "sharesCount": 5,
      "viewsCount": 10,
      "favoritesCount": 0,
      "sessionsCount": 40,
      "sales": {
        "amount": "304.50",
        "currencyCode": "CAD"
      },
      "orders": 8,
      "firstTimeCustomers": 5,
      "returningCustomers": 3
    },
    "marketingActivityId": "gid://shopify/MarketingActivity/794355127",
    "channelHandle": null,
    "remoteId": null
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation M($marketingEngagement: MarketingEngagementInput!, $marketingActivityId: ID, $channelHandle: String, $remoteId: String) {
        marketingEngagementCreate(marketingEngagement: $marketingEngagement, marketingActivityId: $marketingActivityId, channelHandle: $channelHandle, remoteId: $remoteId) {
          marketingEngagement {
            occurredOn
            utcOffset
            isCumulative
            adSpend {
              amount
              currencyCode
            }
            clicksCount
            impressionsCount
            commentsCount
            favoritesCount
            unsubscribesCount
            complaintsCount
            failsCount
            sendsCount
            uniqueViewsCount
            uniqueClicksCount
            sharesCount
            viewsCount
            sessionsCount
            sales {
              amount
              currencyCode
            }
            orders
            firstTimeCustomers
            returningCustomers
            marketingActivity {
              id
            }
            channelHandle
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "marketingEngagement": {
              "occurredOn": "2018-06-29",
              "utcOffset": "-07:00",
              "isCumulative": false,
              "adSpend": {
                  "currencyCode": "CAD",
                  "amount": "19.90"
              },
              "impressionsCount": 100,
              "clicksCount": 40,
              "commentsCount": 1,
              "unsubscribesCount": 1,
              "complaintsCount": 1,
              "failsCount": 1,
              "sendsCount": 1,
              "uniqueViewsCount": 1,
              "uniqueClicksCount": 1,
              "sharesCount": 5,
              "viewsCount": 10,
              "favoritesCount": 0,
              "sessionsCount": 40,
              "sales": {
                  "amount": "304.50",
                  "currencyCode": "CAD"
              },
              "orders": 8,
              "firstTimeCustomers": 5,
              "returningCustomers": 3
          },
          "marketingActivityId": "gid://shopify/MarketingActivity/794355127",
          "channelHandle": null,
          "remoteId": null
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation M($marketingEngagement: MarketingEngagementInput!, $marketingActivityId: ID, $channelHandle: String, $remoteId: String) {
    marketingEngagementCreate(marketingEngagement: $marketingEngagement, marketingActivityId: $marketingActivityId, channelHandle: $channelHandle, remoteId: $remoteId) {
      marketingEngagement {
        occurredOn
        utcOffset
        isCumulative
        adSpend {
          amount
          currencyCode
        }
        clicksCount
        impressionsCount
        commentsCount
        favoritesCount
        unsubscribesCount
        complaintsCount
        failsCount
        sendsCount
        uniqueViewsCount
        uniqueClicksCount
        sharesCount
        viewsCount
        sessionsCount
        sales {
          amount
          currencyCode
        }
        orders
        firstTimeCustomers
        returningCustomers
        marketingActivity {
          id
        }
        channelHandle
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "marketingEngagement": {
      "occurredOn": "2018-06-29",
      "utcOffset": "-07:00",
      "isCumulative": false,
      "adSpend": {
        "currencyCode": "CAD",
        "amount": "19.90"
      },
      "impressionsCount": 100,
      "clicksCount": 40,
      "commentsCount": 1,
      "unsubscribesCount": 1,
      "complaintsCount": 1,
      "failsCount": 1,
      "sendsCount": 1,
      "uniqueViewsCount": 1,
      "uniqueClicksCount": 1,
      "sharesCount": 5,
      "viewsCount": 10,
      "favoritesCount": 0,
      "sessionsCount": 40,
      "sales": {
        "amount": "304.50",
        "currencyCode": "CAD"
      },
      "orders": 8,
      "firstTimeCustomers": 5,
      "returningCustomers": 3
    },
    "marketingActivityId": "gid://shopify/MarketingActivity/794355127",
    "channelHandle": null,
    "remoteId": null
  }'
  ```

  #### Response

  ```json
  {
    "marketingEngagementCreate": {
      "marketingEngagement": {
        "occurredOn": "2018-06-29",
        "utcOffset": "-07:00",
        "isCumulative": false,
        "adSpend": {
          "amount": "19.9",
          "currencyCode": "CAD"
        },
        "clicksCount": 40,
        "impressionsCount": 100,
        "commentsCount": 1,
        "favoritesCount": 0,
        "unsubscribesCount": 1,
        "complaintsCount": 1,
        "failsCount": 1,
        "sendsCount": 1,
        "uniqueViewsCount": 1,
        "uniqueClicksCount": 1,
        "sharesCount": 5,
        "viewsCount": 10,
        "sessionsCount": 40,
        "sales": {
          "amount": "304.5",
          "currencyCode": "CAD"
        },
        "orders": "8.0",
        "firstTimeCustomers": "5.0",
        "returningCustomers": "3.0",
        "marketingActivity": {
          "id": "gid://shopify/MarketingActivity/794355127"
        },
        "channelHandle": null
      },
      "userErrors": []
    }
  }
  ```

* ### Create activity-level engagement with a remote ID

  #### Query

  ```graphql
  mutation M($marketingEngagement: MarketingEngagementInput!, $marketingActivityId: ID, $channelHandle: String, $remoteId: String) {
    marketingEngagementCreate(marketingEngagement: $marketingEngagement, marketingActivityId: $marketingActivityId, channelHandle: $channelHandle, remoteId: $remoteId) {
      marketingEngagement {
        occurredOn
        utcOffset
        isCumulative
        adSpend {
          amount
          currencyCode
        }
        clicksCount
        impressionsCount
        commentsCount
        favoritesCount
        unsubscribesCount
        complaintsCount
        failsCount
        sendsCount
        uniqueViewsCount
        uniqueClicksCount
        sharesCount
        viewsCount
        sessionsCount
        sales {
          amount
          currencyCode
        }
        orders
        firstTimeCustomers
        returningCustomers
        marketingActivity {
          id
        }
        channelHandle
      }
      userErrors {
        field
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "marketingEngagement": {
      "occurredOn": "2018-06-29",
      "utcOffset": "-07:00",
      "isCumulative": false,
      "adSpend": {
        "currencyCode": "CAD",
        "amount": "19.90"
      },
      "impressionsCount": 100,
      "clicksCount": 40,
      "commentsCount": 1,
      "unsubscribesCount": 1,
      "complaintsCount": 1,
      "failsCount": 1,
      "sendsCount": 1,
      "uniqueViewsCount": 1,
      "uniqueClicksCount": 1,
      "sharesCount": 5,
      "viewsCount": 10,
      "favoritesCount": 0,
      "sessionsCount": 40,
      "sales": {
        "amount": "304.50",
        "currencyCode": "CAD"
      },
      "orders": 8,
      "firstTimeCustomers": 5,
      "returningCustomers": 3
    },
    "marketingActivityId": null,
    "channelHandle": null,
    "remoteId": "1234:5678"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation M($marketingEngagement: MarketingEngagementInput!, $marketingActivityId: ID, $channelHandle: String, $remoteId: String) { marketingEngagementCreate(marketingEngagement: $marketingEngagement, marketingActivityId: $marketingActivityId, channelHandle: $channelHandle, remoteId: $remoteId) { marketingEngagement { occurredOn utcOffset isCumulative adSpend { amount currencyCode } clicksCount impressionsCount commentsCount favoritesCount unsubscribesCount complaintsCount failsCount sendsCount uniqueViewsCount uniqueClicksCount sharesCount viewsCount sessionsCount sales { amount currencyCode } orders firstTimeCustomers returningCustomers marketingActivity { id } channelHandle } userErrors { field message } } }",
   "variables": {
      "marketingEngagement": {
        "occurredOn": "2018-06-29",
        "utcOffset": "-07:00",
        "isCumulative": false,
        "adSpend": {
          "currencyCode": "CAD",
          "amount": "19.90"
        },
        "impressionsCount": 100,
        "clicksCount": 40,
        "commentsCount": 1,
        "unsubscribesCount": 1,
        "complaintsCount": 1,
        "failsCount": 1,
        "sendsCount": 1,
        "uniqueViewsCount": 1,
        "uniqueClicksCount": 1,
        "sharesCount": 5,
        "viewsCount": 10,
        "favoritesCount": 0,
        "sessionsCount": 40,
        "sales": {
          "amount": "304.50",
          "currencyCode": "CAD"
        },
        "orders": 8,
        "firstTimeCustomers": 5,
        "returningCustomers": 3
      },
      "marketingActivityId": null,
      "channelHandle": null,
      "remoteId": "1234:5678"
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
    mutation M($marketingEngagement: MarketingEngagementInput!, $marketingActivityId: ID, $channelHandle: String, $remoteId: String) {
      marketingEngagementCreate(marketingEngagement: $marketingEngagement, marketingActivityId: $marketingActivityId, channelHandle: $channelHandle, remoteId: $remoteId) {
        marketingEngagement {
          occurredOn
          utcOffset
          isCumulative
          adSpend {
            amount
            currencyCode
          }
          clicksCount
          impressionsCount
          commentsCount
          favoritesCount
          unsubscribesCount
          complaintsCount
          failsCount
          sendsCount
          uniqueViewsCount
          uniqueClicksCount
          sharesCount
          viewsCount
          sessionsCount
          sales {
            amount
            currencyCode
          }
          orders
          firstTimeCustomers
          returningCustomers
          marketingActivity {
            id
          }
          channelHandle
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "marketingEngagement": {
              "occurredOn": "2018-06-29",
              "utcOffset": "-07:00",
              "isCumulative": false,
              "adSpend": {
                  "currencyCode": "CAD",
                  "amount": "19.90"
              },
              "impressionsCount": 100,
              "clicksCount": 40,
              "commentsCount": 1,
              "unsubscribesCount": 1,
              "complaintsCount": 1,
              "failsCount": 1,
              "sendsCount": 1,
              "uniqueViewsCount": 1,
              "uniqueClicksCount": 1,
              "sharesCount": 5,
              "viewsCount": 10,
              "favoritesCount": 0,
              "sessionsCount": 40,
              "sales": {
                  "amount": "304.50",
                  "currencyCode": "CAD"
              },
              "orders": 8,
              "firstTimeCustomers": 5,
              "returningCustomers": 3
          },
          "marketingActivityId": null,
          "channelHandle": null,
          "remoteId": "1234:5678"
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
    mutation M($marketingEngagement: MarketingEngagementInput!, $marketingActivityId: ID, $channelHandle: String, $remoteId: String) {
      marketingEngagementCreate(marketingEngagement: $marketingEngagement, marketingActivityId: $marketingActivityId, channelHandle: $channelHandle, remoteId: $remoteId) {
        marketingEngagement {
          occurredOn
          utcOffset
          isCumulative
          adSpend {
            amount
            currencyCode
          }
          clicksCount
          impressionsCount
          commentsCount
          favoritesCount
          unsubscribesCount
          complaintsCount
          failsCount
          sendsCount
          uniqueViewsCount
          uniqueClicksCount
          sharesCount
          viewsCount
          sessionsCount
          sales {
            amount
            currencyCode
          }
          orders
          firstTimeCustomers
          returningCustomers
          marketingActivity {
            id
          }
          channelHandle
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "marketingEngagement": {
      "occurredOn": "2018-06-29",
      "utcOffset": "-07:00",
      "isCumulative": false,
      "adSpend": {
        "currencyCode": "CAD",
        "amount": "19.90"
      },
      "impressionsCount": 100,
      "clicksCount": 40,
      "commentsCount": 1,
      "unsubscribesCount": 1,
      "complaintsCount": 1,
      "failsCount": 1,
      "sendsCount": 1,
      "uniqueViewsCount": 1,
      "uniqueClicksCount": 1,
      "sharesCount": 5,
      "viewsCount": 10,
      "favoritesCount": 0,
      "sessionsCount": 40,
      "sales": {
        "amount": "304.50",
        "currencyCode": "CAD"
      },
      "orders": 8,
      "firstTimeCustomers": 5,
      "returningCustomers": 3
    },
    "marketingActivityId": null,
    "channelHandle": null,
    "remoteId": "1234:5678"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation M($marketingEngagement: MarketingEngagementInput!, $marketingActivityId: ID, $channelHandle: String, $remoteId: String) {
        marketingEngagementCreate(marketingEngagement: $marketingEngagement, marketingActivityId: $marketingActivityId, channelHandle: $channelHandle, remoteId: $remoteId) {
          marketingEngagement {
            occurredOn
            utcOffset
            isCumulative
            adSpend {
              amount
              currencyCode
            }
            clicksCount
            impressionsCount
            commentsCount
            favoritesCount
            unsubscribesCount
            complaintsCount
            failsCount
            sendsCount
            uniqueViewsCount
            uniqueClicksCount
            sharesCount
            viewsCount
            sessionsCount
            sales {
              amount
              currencyCode
            }
            orders
            firstTimeCustomers
            returningCustomers
            marketingActivity {
              id
            }
            channelHandle
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "marketingEngagement": {
              "occurredOn": "2018-06-29",
              "utcOffset": "-07:00",
              "isCumulative": false,
              "adSpend": {
                  "currencyCode": "CAD",
                  "amount": "19.90"
              },
              "impressionsCount": 100,
              "clicksCount": 40,
              "commentsCount": 1,
              "unsubscribesCount": 1,
              "complaintsCount": 1,
              "failsCount": 1,
              "sendsCount": 1,
              "uniqueViewsCount": 1,
              "uniqueClicksCount": 1,
              "sharesCount": 5,
              "viewsCount": 10,
              "favoritesCount": 0,
              "sessionsCount": 40,
              "sales": {
                  "amount": "304.50",
                  "currencyCode": "CAD"
              },
              "orders": 8,
              "firstTimeCustomers": 5,
              "returningCustomers": 3
          },
          "marketingActivityId": null,
          "channelHandle": null,
          "remoteId": "1234:5678"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation M($marketingEngagement: MarketingEngagementInput!, $marketingActivityId: ID, $channelHandle: String, $remoteId: String) {
    marketingEngagementCreate(marketingEngagement: $marketingEngagement, marketingActivityId: $marketingActivityId, channelHandle: $channelHandle, remoteId: $remoteId) {
      marketingEngagement {
        occurredOn
        utcOffset
        isCumulative
        adSpend {
          amount
          currencyCode
        }
        clicksCount
        impressionsCount
        commentsCount
        favoritesCount
        unsubscribesCount
        complaintsCount
        failsCount
        sendsCount
        uniqueViewsCount
        uniqueClicksCount
        sharesCount
        viewsCount
        sessionsCount
        sales {
          amount
          currencyCode
        }
        orders
        firstTimeCustomers
        returningCustomers
        marketingActivity {
          id
        }
        channelHandle
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "marketingEngagement": {
      "occurredOn": "2018-06-29",
      "utcOffset": "-07:00",
      "isCumulative": false,
      "adSpend": {
        "currencyCode": "CAD",
        "amount": "19.90"
      },
      "impressionsCount": 100,
      "clicksCount": 40,
      "commentsCount": 1,
      "unsubscribesCount": 1,
      "complaintsCount": 1,
      "failsCount": 1,
      "sendsCount": 1,
      "uniqueViewsCount": 1,
      "uniqueClicksCount": 1,
      "sharesCount": 5,
      "viewsCount": 10,
      "favoritesCount": 0,
      "sessionsCount": 40,
      "sales": {
        "amount": "304.50",
        "currencyCode": "CAD"
      },
      "orders": 8,
      "firstTimeCustomers": 5,
      "returningCustomers": 3
    },
    "marketingActivityId": null,
    "channelHandle": null,
    "remoteId": "1234:5678"
  }'
  ```

  #### Response

  ```json
  {
    "marketingEngagementCreate": {
      "marketingEngagement": {
        "occurredOn": "2018-06-29",
        "utcOffset": "-07:00",
        "isCumulative": false,
        "adSpend": {
          "amount": "19.9",
          "currencyCode": "CAD"
        },
        "clicksCount": 40,
        "impressionsCount": 100,
        "commentsCount": 1,
        "favoritesCount": 0,
        "unsubscribesCount": 1,
        "complaintsCount": 1,
        "failsCount": 1,
        "sendsCount": 1,
        "uniqueViewsCount": 1,
        "uniqueClicksCount": 1,
        "sharesCount": 5,
        "viewsCount": 10,
        "sessionsCount": 40,
        "sales": {
          "amount": "304.5",
          "currencyCode": "CAD"
        },
        "orders": "8.0",
        "firstTimeCustomers": "5.0",
        "returningCustomers": "3.0",
        "marketingActivity": {
          "id": "gid://shopify/MarketingActivity/794355127"
        },
        "channelHandle": null
      },
      "userErrors": []
    }
  }
  ```

* ### Create activity-level engagement with conversion metrics for a marketing activity ID

  #### Query

  ```graphql
  mutation M($marketingEngagement: MarketingEngagementInput!, $marketingActivityId: ID, $channelHandle: String, $remoteId: String) {
    marketingEngagementCreate(marketingEngagement: $marketingEngagement, marketingActivityId: $marketingActivityId, channelHandle: $channelHandle, remoteId: $remoteId) {
      marketingEngagement {
        occurredOn
        utcOffset
        isCumulative
        adSpend {
          amount
          currencyCode
        }
        clicksCount
        impressionsCount
        commentsCount
        favoritesCount
        unsubscribesCount
        complaintsCount
        failsCount
        sendsCount
        uniqueViewsCount
        uniqueClicksCount
        sharesCount
        viewsCount
        sessionsCount
        sales {
          amount
          currencyCode
        }
        orders
        firstTimeCustomers
        returningCustomers
        primaryConversions
        allConversions
        marketingActivity {
          id
        }
        channelHandle
      }
      userErrors {
        field
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "marketingEngagement": {
      "occurredOn": "2018-06-29",
      "utcOffset": "-07:00",
      "isCumulative": false,
      "adSpend": {
        "currencyCode": "CAD",
        "amount": "19.90"
      },
      "impressionsCount": 100,
      "clicksCount": 40,
      "commentsCount": 1,
      "unsubscribesCount": 1,
      "complaintsCount": 1,
      "failsCount": 1,
      "sendsCount": 1,
      "uniqueViewsCount": 1,
      "uniqueClicksCount": 1,
      "sharesCount": 5,
      "viewsCount": 10,
      "favoritesCount": 0,
      "sessionsCount": 40,
      "sales": {
        "amount": "304.50",
        "currencyCode": "CAD"
      },
      "orders": 8,
      "firstTimeCustomers": 5,
      "returningCustomers": 3,
      "primaryConversions": 8,
      "allConversions": 40
    },
    "marketingActivityId": "gid://shopify/MarketingActivity/794355127",
    "channelHandle": null,
    "remoteId": null
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation M($marketingEngagement: MarketingEngagementInput!, $marketingActivityId: ID, $channelHandle: String, $remoteId: String) { marketingEngagementCreate(marketingEngagement: $marketingEngagement, marketingActivityId: $marketingActivityId, channelHandle: $channelHandle, remoteId: $remoteId) { marketingEngagement { occurredOn utcOffset isCumulative adSpend { amount currencyCode } clicksCount impressionsCount commentsCount favoritesCount unsubscribesCount complaintsCount failsCount sendsCount uniqueViewsCount uniqueClicksCount sharesCount viewsCount sessionsCount sales { amount currencyCode } orders firstTimeCustomers returningCustomers primaryConversions allConversions marketingActivity { id } channelHandle } userErrors { field message } } }",
   "variables": {
      "marketingEngagement": {
        "occurredOn": "2018-06-29",
        "utcOffset": "-07:00",
        "isCumulative": false,
        "adSpend": {
          "currencyCode": "CAD",
          "amount": "19.90"
        },
        "impressionsCount": 100,
        "clicksCount": 40,
        "commentsCount": 1,
        "unsubscribesCount": 1,
        "complaintsCount": 1,
        "failsCount": 1,
        "sendsCount": 1,
        "uniqueViewsCount": 1,
        "uniqueClicksCount": 1,
        "sharesCount": 5,
        "viewsCount": 10,
        "favoritesCount": 0,
        "sessionsCount": 40,
        "sales": {
          "amount": "304.50",
          "currencyCode": "CAD"
        },
        "orders": 8,
        "firstTimeCustomers": 5,
        "returningCustomers": 3,
        "primaryConversions": 8,
        "allConversions": 40
      },
      "marketingActivityId": "gid://shopify/MarketingActivity/794355127",
      "channelHandle": null,
      "remoteId": null
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
    mutation M($marketingEngagement: MarketingEngagementInput!, $marketingActivityId: ID, $channelHandle: String, $remoteId: String) {
      marketingEngagementCreate(marketingEngagement: $marketingEngagement, marketingActivityId: $marketingActivityId, channelHandle: $channelHandle, remoteId: $remoteId) {
        marketingEngagement {
          occurredOn
          utcOffset
          isCumulative
          adSpend {
            amount
            currencyCode
          }
          clicksCount
          impressionsCount
          commentsCount
          favoritesCount
          unsubscribesCount
          complaintsCount
          failsCount
          sendsCount
          uniqueViewsCount
          uniqueClicksCount
          sharesCount
          viewsCount
          sessionsCount
          sales {
            amount
            currencyCode
          }
          orders
          firstTimeCustomers
          returningCustomers
          primaryConversions
          allConversions
          marketingActivity {
            id
          }
          channelHandle
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "marketingEngagement": {
              "occurredOn": "2018-06-29",
              "utcOffset": "-07:00",
              "isCumulative": false,
              "adSpend": {
                  "currencyCode": "CAD",
                  "amount": "19.90"
              },
              "impressionsCount": 100,
              "clicksCount": 40,
              "commentsCount": 1,
              "unsubscribesCount": 1,
              "complaintsCount": 1,
              "failsCount": 1,
              "sendsCount": 1,
              "uniqueViewsCount": 1,
              "uniqueClicksCount": 1,
              "sharesCount": 5,
              "viewsCount": 10,
              "favoritesCount": 0,
              "sessionsCount": 40,
              "sales": {
                  "amount": "304.50",
                  "currencyCode": "CAD"
              },
              "orders": 8,
              "firstTimeCustomers": 5,
              "returningCustomers": 3,
              "primaryConversions": 8,
              "allConversions": 40
          },
          "marketingActivityId": "gid://shopify/MarketingActivity/794355127",
          "channelHandle": null,
          "remoteId": null
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
    mutation M($marketingEngagement: MarketingEngagementInput!, $marketingActivityId: ID, $channelHandle: String, $remoteId: String) {
      marketingEngagementCreate(marketingEngagement: $marketingEngagement, marketingActivityId: $marketingActivityId, channelHandle: $channelHandle, remoteId: $remoteId) {
        marketingEngagement {
          occurredOn
          utcOffset
          isCumulative
          adSpend {
            amount
            currencyCode
          }
          clicksCount
          impressionsCount
          commentsCount
          favoritesCount
          unsubscribesCount
          complaintsCount
          failsCount
          sendsCount
          uniqueViewsCount
          uniqueClicksCount
          sharesCount
          viewsCount
          sessionsCount
          sales {
            amount
            currencyCode
          }
          orders
          firstTimeCustomers
          returningCustomers
          primaryConversions
          allConversions
          marketingActivity {
            id
          }
          channelHandle
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "marketingEngagement": {
      "occurredOn": "2018-06-29",
      "utcOffset": "-07:00",
      "isCumulative": false,
      "adSpend": {
        "currencyCode": "CAD",
        "amount": "19.90"
      },
      "impressionsCount": 100,
      "clicksCount": 40,
      "commentsCount": 1,
      "unsubscribesCount": 1,
      "complaintsCount": 1,
      "failsCount": 1,
      "sendsCount": 1,
      "uniqueViewsCount": 1,
      "uniqueClicksCount": 1,
      "sharesCount": 5,
      "viewsCount": 10,
      "favoritesCount": 0,
      "sessionsCount": 40,
      "sales": {
        "amount": "304.50",
        "currencyCode": "CAD"
      },
      "orders": 8,
      "firstTimeCustomers": 5,
      "returningCustomers": 3,
      "primaryConversions": 8,
      "allConversions": 40
    },
    "marketingActivityId": "gid://shopify/MarketingActivity/794355127",
    "channelHandle": null,
    "remoteId": null
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation M($marketingEngagement: MarketingEngagementInput!, $marketingActivityId: ID, $channelHandle: String, $remoteId: String) {
        marketingEngagementCreate(marketingEngagement: $marketingEngagement, marketingActivityId: $marketingActivityId, channelHandle: $channelHandle, remoteId: $remoteId) {
          marketingEngagement {
            occurredOn
            utcOffset
            isCumulative
            adSpend {
              amount
              currencyCode
            }
            clicksCount
            impressionsCount
            commentsCount
            favoritesCount
            unsubscribesCount
            complaintsCount
            failsCount
            sendsCount
            uniqueViewsCount
            uniqueClicksCount
            sharesCount
            viewsCount
            sessionsCount
            sales {
              amount
              currencyCode
            }
            orders
            firstTimeCustomers
            returningCustomers
            primaryConversions
            allConversions
            marketingActivity {
              id
            }
            channelHandle
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "marketingEngagement": {
              "occurredOn": "2018-06-29",
              "utcOffset": "-07:00",
              "isCumulative": false,
              "adSpend": {
                  "currencyCode": "CAD",
                  "amount": "19.90"
              },
              "impressionsCount": 100,
              "clicksCount": 40,
              "commentsCount": 1,
              "unsubscribesCount": 1,
              "complaintsCount": 1,
              "failsCount": 1,
              "sendsCount": 1,
              "uniqueViewsCount": 1,
              "uniqueClicksCount": 1,
              "sharesCount": 5,
              "viewsCount": 10,
              "favoritesCount": 0,
              "sessionsCount": 40,
              "sales": {
                  "amount": "304.50",
                  "currencyCode": "CAD"
              },
              "orders": 8,
              "firstTimeCustomers": 5,
              "returningCustomers": 3,
              "primaryConversions": 8,
              "allConversions": 40
          },
          "marketingActivityId": "gid://shopify/MarketingActivity/794355127",
          "channelHandle": null,
          "remoteId": null
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation M($marketingEngagement: MarketingEngagementInput!, $marketingActivityId: ID, $channelHandle: String, $remoteId: String) {
    marketingEngagementCreate(marketingEngagement: $marketingEngagement, marketingActivityId: $marketingActivityId, channelHandle: $channelHandle, remoteId: $remoteId) {
      marketingEngagement {
        occurredOn
        utcOffset
        isCumulative
        adSpend {
          amount
          currencyCode
        }
        clicksCount
        impressionsCount
        commentsCount
        favoritesCount
        unsubscribesCount
        complaintsCount
        failsCount
        sendsCount
        uniqueViewsCount
        uniqueClicksCount
        sharesCount
        viewsCount
        sessionsCount
        sales {
          amount
          currencyCode
        }
        orders
        firstTimeCustomers
        returningCustomers
        primaryConversions
        allConversions
        marketingActivity {
          id
        }
        channelHandle
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "marketingEngagement": {
      "occurredOn": "2018-06-29",
      "utcOffset": "-07:00",
      "isCumulative": false,
      "adSpend": {
        "currencyCode": "CAD",
        "amount": "19.90"
      },
      "impressionsCount": 100,
      "clicksCount": 40,
      "commentsCount": 1,
      "unsubscribesCount": 1,
      "complaintsCount": 1,
      "failsCount": 1,
      "sendsCount": 1,
      "uniqueViewsCount": 1,
      "uniqueClicksCount": 1,
      "sharesCount": 5,
      "viewsCount": 10,
      "favoritesCount": 0,
      "sessionsCount": 40,
      "sales": {
        "amount": "304.50",
        "currencyCode": "CAD"
      },
      "orders": 8,
      "firstTimeCustomers": 5,
      "returningCustomers": 3,
      "primaryConversions": 8,
      "allConversions": 40
    },
    "marketingActivityId": "gid://shopify/MarketingActivity/794355127",
    "channelHandle": null,
    "remoteId": null
  }'
  ```

  #### Response

  ```json
  {
    "marketingEngagementCreate": {
      "marketingEngagement": {
        "occurredOn": "2018-06-29",
        "utcOffset": "-07:00",
        "isCumulative": false,
        "adSpend": {
          "amount": "19.9",
          "currencyCode": "CAD"
        },
        "clicksCount": 40,
        "impressionsCount": 100,
        "commentsCount": 1,
        "favoritesCount": 0,
        "unsubscribesCount": 1,
        "complaintsCount": 1,
        "failsCount": 1,
        "sendsCount": 1,
        "uniqueViewsCount": 1,
        "uniqueClicksCount": 1,
        "sharesCount": 5,
        "viewsCount": 10,
        "sessionsCount": 40,
        "sales": {
          "amount": "304.5",
          "currencyCode": "CAD"
        },
        "orders": "8.0",
        "firstTimeCustomers": "5.0",
        "returningCustomers": "3.0",
        "primaryConversions": "8.0",
        "allConversions": "40.0",
        "marketingActivity": {
          "id": "gid://shopify/MarketingActivity/794355127"
        },
        "channelHandle": null
      },
      "userErrors": []
    }
  }
  ```

* ### Create activity-level engagement with conversion metrics with a remote ID

  #### Query

  ```graphql
  mutation M($marketingEngagement: MarketingEngagementInput!, $marketingActivityId: ID, $channelHandle: String, $remoteId: String) {
    marketingEngagementCreate(marketingEngagement: $marketingEngagement, marketingActivityId: $marketingActivityId, channelHandle: $channelHandle, remoteId: $remoteId) {
      marketingEngagement {
        occurredOn
        utcOffset
        isCumulative
        adSpend {
          amount
          currencyCode
        }
        clicksCount
        impressionsCount
        commentsCount
        favoritesCount
        unsubscribesCount
        complaintsCount
        failsCount
        sendsCount
        uniqueViewsCount
        uniqueClicksCount
        sharesCount
        viewsCount
        sessionsCount
        sales {
          amount
          currencyCode
        }
        orders
        firstTimeCustomers
        returningCustomers
        primaryConversions
        allConversions
        marketingActivity {
          id
        }
        channelHandle
      }
      userErrors {
        field
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "marketingEngagement": {
      "occurredOn": "2018-06-29",
      "utcOffset": "-07:00",
      "isCumulative": false,
      "adSpend": {
        "currencyCode": "CAD",
        "amount": "19.90"
      },
      "impressionsCount": 100,
      "clicksCount": 40,
      "commentsCount": 1,
      "unsubscribesCount": 1,
      "complaintsCount": 1,
      "failsCount": 1,
      "sendsCount": 1,
      "uniqueViewsCount": 1,
      "uniqueClicksCount": 1,
      "sharesCount": 5,
      "viewsCount": 10,
      "favoritesCount": 0,
      "sessionsCount": 40,
      "sales": {
        "amount": "304.50",
        "currencyCode": "CAD"
      },
      "orders": 8,
      "firstTimeCustomers": 5,
      "returningCustomers": 3,
      "primaryConversions": 8,
      "allConversions": 40
    },
    "marketingActivityId": null,
    "channelHandle": null,
    "remoteId": "1234:5678"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation M($marketingEngagement: MarketingEngagementInput!, $marketingActivityId: ID, $channelHandle: String, $remoteId: String) { marketingEngagementCreate(marketingEngagement: $marketingEngagement, marketingActivityId: $marketingActivityId, channelHandle: $channelHandle, remoteId: $remoteId) { marketingEngagement { occurredOn utcOffset isCumulative adSpend { amount currencyCode } clicksCount impressionsCount commentsCount favoritesCount unsubscribesCount complaintsCount failsCount sendsCount uniqueViewsCount uniqueClicksCount sharesCount viewsCount sessionsCount sales { amount currencyCode } orders firstTimeCustomers returningCustomers primaryConversions allConversions marketingActivity { id } channelHandle } userErrors { field message } } }",
   "variables": {
      "marketingEngagement": {
        "occurredOn": "2018-06-29",
        "utcOffset": "-07:00",
        "isCumulative": false,
        "adSpend": {
          "currencyCode": "CAD",
          "amount": "19.90"
        },
        "impressionsCount": 100,
        "clicksCount": 40,
        "commentsCount": 1,
        "unsubscribesCount": 1,
        "complaintsCount": 1,
        "failsCount": 1,
        "sendsCount": 1,
        "uniqueViewsCount": 1,
        "uniqueClicksCount": 1,
        "sharesCount": 5,
        "viewsCount": 10,
        "favoritesCount": 0,
        "sessionsCount": 40,
        "sales": {
          "amount": "304.50",
          "currencyCode": "CAD"
        },
        "orders": 8,
        "firstTimeCustomers": 5,
        "returningCustomers": 3,
        "primaryConversions": 8,
        "allConversions": 40
      },
      "marketingActivityId": null,
      "channelHandle": null,
      "remoteId": "1234:5678"
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
    mutation M($marketingEngagement: MarketingEngagementInput!, $marketingActivityId: ID, $channelHandle: String, $remoteId: String) {
      marketingEngagementCreate(marketingEngagement: $marketingEngagement, marketingActivityId: $marketingActivityId, channelHandle: $channelHandle, remoteId: $remoteId) {
        marketingEngagement {
          occurredOn
          utcOffset
          isCumulative
          adSpend {
            amount
            currencyCode
          }
          clicksCount
          impressionsCount
          commentsCount
          favoritesCount
          unsubscribesCount
          complaintsCount
          failsCount
          sendsCount
          uniqueViewsCount
          uniqueClicksCount
          sharesCount
          viewsCount
          sessionsCount
          sales {
            amount
            currencyCode
          }
          orders
          firstTimeCustomers
          returningCustomers
          primaryConversions
          allConversions
          marketingActivity {
            id
          }
          channelHandle
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "marketingEngagement": {
              "occurredOn": "2018-06-29",
              "utcOffset": "-07:00",
              "isCumulative": false,
              "adSpend": {
                  "currencyCode": "CAD",
                  "amount": "19.90"
              },
              "impressionsCount": 100,
              "clicksCount": 40,
              "commentsCount": 1,
              "unsubscribesCount": 1,
              "complaintsCount": 1,
              "failsCount": 1,
              "sendsCount": 1,
              "uniqueViewsCount": 1,
              "uniqueClicksCount": 1,
              "sharesCount": 5,
              "viewsCount": 10,
              "favoritesCount": 0,
              "sessionsCount": 40,
              "sales": {
                  "amount": "304.50",
                  "currencyCode": "CAD"
              },
              "orders": 8,
              "firstTimeCustomers": 5,
              "returningCustomers": 3,
              "primaryConversions": 8,
              "allConversions": 40
          },
          "marketingActivityId": null,
          "channelHandle": null,
          "remoteId": "1234:5678"
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
    mutation M($marketingEngagement: MarketingEngagementInput!, $marketingActivityId: ID, $channelHandle: String, $remoteId: String) {
      marketingEngagementCreate(marketingEngagement: $marketingEngagement, marketingActivityId: $marketingActivityId, channelHandle: $channelHandle, remoteId: $remoteId) {
        marketingEngagement {
          occurredOn
          utcOffset
          isCumulative
          adSpend {
            amount
            currencyCode
          }
          clicksCount
          impressionsCount
          commentsCount
          favoritesCount
          unsubscribesCount
          complaintsCount
          failsCount
          sendsCount
          uniqueViewsCount
          uniqueClicksCount
          sharesCount
          viewsCount
          sessionsCount
          sales {
            amount
            currencyCode
          }
          orders
          firstTimeCustomers
          returningCustomers
          primaryConversions
          allConversions
          marketingActivity {
            id
          }
          channelHandle
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "marketingEngagement": {
      "occurredOn": "2018-06-29",
      "utcOffset": "-07:00",
      "isCumulative": false,
      "adSpend": {
        "currencyCode": "CAD",
        "amount": "19.90"
      },
      "impressionsCount": 100,
      "clicksCount": 40,
      "commentsCount": 1,
      "unsubscribesCount": 1,
      "complaintsCount": 1,
      "failsCount": 1,
      "sendsCount": 1,
      "uniqueViewsCount": 1,
      "uniqueClicksCount": 1,
      "sharesCount": 5,
      "viewsCount": 10,
      "favoritesCount": 0,
      "sessionsCount": 40,
      "sales": {
        "amount": "304.50",
        "currencyCode": "CAD"
      },
      "orders": 8,
      "firstTimeCustomers": 5,
      "returningCustomers": 3,
      "primaryConversions": 8,
      "allConversions": 40
    },
    "marketingActivityId": null,
    "channelHandle": null,
    "remoteId": "1234:5678"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation M($marketingEngagement: MarketingEngagementInput!, $marketingActivityId: ID, $channelHandle: String, $remoteId: String) {
        marketingEngagementCreate(marketingEngagement: $marketingEngagement, marketingActivityId: $marketingActivityId, channelHandle: $channelHandle, remoteId: $remoteId) {
          marketingEngagement {
            occurredOn
            utcOffset
            isCumulative
            adSpend {
              amount
              currencyCode
            }
            clicksCount
            impressionsCount
            commentsCount
            favoritesCount
            unsubscribesCount
            complaintsCount
            failsCount
            sendsCount
            uniqueViewsCount
            uniqueClicksCount
            sharesCount
            viewsCount
            sessionsCount
            sales {
              amount
              currencyCode
            }
            orders
            firstTimeCustomers
            returningCustomers
            primaryConversions
            allConversions
            marketingActivity {
              id
            }
            channelHandle
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "marketingEngagement": {
              "occurredOn": "2018-06-29",
              "utcOffset": "-07:00",
              "isCumulative": false,
              "adSpend": {
                  "currencyCode": "CAD",
                  "amount": "19.90"
              },
              "impressionsCount": 100,
              "clicksCount": 40,
              "commentsCount": 1,
              "unsubscribesCount": 1,
              "complaintsCount": 1,
              "failsCount": 1,
              "sendsCount": 1,
              "uniqueViewsCount": 1,
              "uniqueClicksCount": 1,
              "sharesCount": 5,
              "viewsCount": 10,
              "favoritesCount": 0,
              "sessionsCount": 40,
              "sales": {
                  "amount": "304.50",
                  "currencyCode": "CAD"
              },
              "orders": 8,
              "firstTimeCustomers": 5,
              "returningCustomers": 3,
              "primaryConversions": 8,
              "allConversions": 40
          },
          "marketingActivityId": null,
          "channelHandle": null,
          "remoteId": "1234:5678"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation M($marketingEngagement: MarketingEngagementInput!, $marketingActivityId: ID, $channelHandle: String, $remoteId: String) {
    marketingEngagementCreate(marketingEngagement: $marketingEngagement, marketingActivityId: $marketingActivityId, channelHandle: $channelHandle, remoteId: $remoteId) {
      marketingEngagement {
        occurredOn
        utcOffset
        isCumulative
        adSpend {
          amount
          currencyCode
        }
        clicksCount
        impressionsCount
        commentsCount
        favoritesCount
        unsubscribesCount
        complaintsCount
        failsCount
        sendsCount
        uniqueViewsCount
        uniqueClicksCount
        sharesCount
        viewsCount
        sessionsCount
        sales {
          amount
          currencyCode
        }
        orders
        firstTimeCustomers
        returningCustomers
        primaryConversions
        allConversions
        marketingActivity {
          id
        }
        channelHandle
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "marketingEngagement": {
      "occurredOn": "2018-06-29",
      "utcOffset": "-07:00",
      "isCumulative": false,
      "adSpend": {
        "currencyCode": "CAD",
        "amount": "19.90"
      },
      "impressionsCount": 100,
      "clicksCount": 40,
      "commentsCount": 1,
      "unsubscribesCount": 1,
      "complaintsCount": 1,
      "failsCount": 1,
      "sendsCount": 1,
      "uniqueViewsCount": 1,
      "uniqueClicksCount": 1,
      "sharesCount": 5,
      "viewsCount": 10,
      "favoritesCount": 0,
      "sessionsCount": 40,
      "sales": {
        "amount": "304.50",
        "currencyCode": "CAD"
      },
      "orders": 8,
      "firstTimeCustomers": 5,
      "returningCustomers": 3,
      "primaryConversions": 8,
      "allConversions": 40
    },
    "marketingActivityId": null,
    "channelHandle": null,
    "remoteId": "1234:5678"
  }'
  ```

  #### Response

  ```json
  {
    "marketingEngagementCreate": {
      "marketingEngagement": {
        "occurredOn": "2018-06-29",
        "utcOffset": "-07:00",
        "isCumulative": false,
        "adSpend": {
          "amount": "19.9",
          "currencyCode": "CAD"
        },
        "clicksCount": 40,
        "impressionsCount": 100,
        "commentsCount": 1,
        "favoritesCount": 0,
        "unsubscribesCount": 1,
        "complaintsCount": 1,
        "failsCount": 1,
        "sendsCount": 1,
        "uniqueViewsCount": 1,
        "uniqueClicksCount": 1,
        "sharesCount": 5,
        "viewsCount": 10,
        "sessionsCount": 40,
        "sales": {
          "amount": "304.5",
          "currencyCode": "CAD"
        },
        "orders": "8.0",
        "firstTimeCustomers": "5.0",
        "returningCustomers": "3.0",
        "primaryConversions": "8.0",
        "allConversions": "40.0",
        "marketingActivity": {
          "id": "gid://shopify/MarketingActivity/794355127"
        },
        "channelHandle": null
      },
      "userErrors": []
    }
  }
  ```

* ### Create channel-level engagement for a channel handle

  #### Query

  ```graphql
  mutation M($marketingEngagement: MarketingEngagementInput!, $marketingActivityId: ID, $channelHandle: String, $remoteId: String) {
    marketingEngagementCreate(marketingEngagement: $marketingEngagement, marketingActivityId: $marketingActivityId, channelHandle: $channelHandle, remoteId: $remoteId) {
      marketingEngagement {
        occurredOn
        utcOffset
        isCumulative
        adSpend {
          amount
          currencyCode
        }
        clicksCount
        impressionsCount
        commentsCount
        favoritesCount
        unsubscribesCount
        complaintsCount
        failsCount
        sendsCount
        uniqueViewsCount
        uniqueClicksCount
        sharesCount
        viewsCount
        sessionsCount
        sales {
          amount
          currencyCode
        }
        orders
        firstTimeCustomers
        returningCustomers
        marketingActivity {
          id
        }
        channelHandle
      }
      userErrors {
        field
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "marketingEngagement": {
      "occurredOn": "2018-06-29",
      "utcOffset": "-07:00",
      "isCumulative": false,
      "adSpend": {
        "currencyCode": "CAD",
        "amount": "19.90"
      },
      "impressionsCount": 100,
      "clicksCount": 40,
      "commentsCount": 1,
      "unsubscribesCount": 1,
      "complaintsCount": 1,
      "failsCount": 1,
      "sendsCount": 1,
      "uniqueViewsCount": 1,
      "uniqueClicksCount": 1,
      "sharesCount": 5,
      "viewsCount": 10,
      "favoritesCount": 0,
      "sessionsCount": 40,
      "sales": {
        "amount": "304.50",
        "currencyCode": "CAD"
      },
      "orders": 8,
      "firstTimeCustomers": 5,
      "returningCustomers": 3
    },
    "marketingActivityId": null,
    "channelHandle": "my-channel-handle",
    "remoteId": null
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation M($marketingEngagement: MarketingEngagementInput!, $marketingActivityId: ID, $channelHandle: String, $remoteId: String) { marketingEngagementCreate(marketingEngagement: $marketingEngagement, marketingActivityId: $marketingActivityId, channelHandle: $channelHandle, remoteId: $remoteId) { marketingEngagement { occurredOn utcOffset isCumulative adSpend { amount currencyCode } clicksCount impressionsCount commentsCount favoritesCount unsubscribesCount complaintsCount failsCount sendsCount uniqueViewsCount uniqueClicksCount sharesCount viewsCount sessionsCount sales { amount currencyCode } orders firstTimeCustomers returningCustomers marketingActivity { id } channelHandle } userErrors { field message } } }",
   "variables": {
      "marketingEngagement": {
        "occurredOn": "2018-06-29",
        "utcOffset": "-07:00",
        "isCumulative": false,
        "adSpend": {
          "currencyCode": "CAD",
          "amount": "19.90"
        },
        "impressionsCount": 100,
        "clicksCount": 40,
        "commentsCount": 1,
        "unsubscribesCount": 1,
        "complaintsCount": 1,
        "failsCount": 1,
        "sendsCount": 1,
        "uniqueViewsCount": 1,
        "uniqueClicksCount": 1,
        "sharesCount": 5,
        "viewsCount": 10,
        "favoritesCount": 0,
        "sessionsCount": 40,
        "sales": {
          "amount": "304.50",
          "currencyCode": "CAD"
        },
        "orders": 8,
        "firstTimeCustomers": 5,
        "returningCustomers": 3
      },
      "marketingActivityId": null,
      "channelHandle": "my-channel-handle",
      "remoteId": null
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
    mutation M($marketingEngagement: MarketingEngagementInput!, $marketingActivityId: ID, $channelHandle: String, $remoteId: String) {
      marketingEngagementCreate(marketingEngagement: $marketingEngagement, marketingActivityId: $marketingActivityId, channelHandle: $channelHandle, remoteId: $remoteId) {
        marketingEngagement {
          occurredOn
          utcOffset
          isCumulative
          adSpend {
            amount
            currencyCode
          }
          clicksCount
          impressionsCount
          commentsCount
          favoritesCount
          unsubscribesCount
          complaintsCount
          failsCount
          sendsCount
          uniqueViewsCount
          uniqueClicksCount
          sharesCount
          viewsCount
          sessionsCount
          sales {
            amount
            currencyCode
          }
          orders
          firstTimeCustomers
          returningCustomers
          marketingActivity {
            id
          }
          channelHandle
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "marketingEngagement": {
              "occurredOn": "2018-06-29",
              "utcOffset": "-07:00",
              "isCumulative": false,
              "adSpend": {
                  "currencyCode": "CAD",
                  "amount": "19.90"
              },
              "impressionsCount": 100,
              "clicksCount": 40,
              "commentsCount": 1,
              "unsubscribesCount": 1,
              "complaintsCount": 1,
              "failsCount": 1,
              "sendsCount": 1,
              "uniqueViewsCount": 1,
              "uniqueClicksCount": 1,
              "sharesCount": 5,
              "viewsCount": 10,
              "favoritesCount": 0,
              "sessionsCount": 40,
              "sales": {
                  "amount": "304.50",
                  "currencyCode": "CAD"
              },
              "orders": 8,
              "firstTimeCustomers": 5,
              "returningCustomers": 3
          },
          "marketingActivityId": null,
          "channelHandle": "my-channel-handle",
          "remoteId": null
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
    mutation M($marketingEngagement: MarketingEngagementInput!, $marketingActivityId: ID, $channelHandle: String, $remoteId: String) {
      marketingEngagementCreate(marketingEngagement: $marketingEngagement, marketingActivityId: $marketingActivityId, channelHandle: $channelHandle, remoteId: $remoteId) {
        marketingEngagement {
          occurredOn
          utcOffset
          isCumulative
          adSpend {
            amount
            currencyCode
          }
          clicksCount
          impressionsCount
          commentsCount
          favoritesCount
          unsubscribesCount
          complaintsCount
          failsCount
          sendsCount
          uniqueViewsCount
          uniqueClicksCount
          sharesCount
          viewsCount
          sessionsCount
          sales {
            amount
            currencyCode
          }
          orders
          firstTimeCustomers
          returningCustomers
          marketingActivity {
            id
          }
          channelHandle
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "marketingEngagement": {
      "occurredOn": "2018-06-29",
      "utcOffset": "-07:00",
      "isCumulative": false,
      "adSpend": {
        "currencyCode": "CAD",
        "amount": "19.90"
      },
      "impressionsCount": 100,
      "clicksCount": 40,
      "commentsCount": 1,
      "unsubscribesCount": 1,
      "complaintsCount": 1,
      "failsCount": 1,
      "sendsCount": 1,
      "uniqueViewsCount": 1,
      "uniqueClicksCount": 1,
      "sharesCount": 5,
      "viewsCount": 10,
      "favoritesCount": 0,
      "sessionsCount": 40,
      "sales": {
        "amount": "304.50",
        "currencyCode": "CAD"
      },
      "orders": 8,
      "firstTimeCustomers": 5,
      "returningCustomers": 3
    },
    "marketingActivityId": null,
    "channelHandle": "my-channel-handle",
    "remoteId": null
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation M($marketingEngagement: MarketingEngagementInput!, $marketingActivityId: ID, $channelHandle: String, $remoteId: String) {
        marketingEngagementCreate(marketingEngagement: $marketingEngagement, marketingActivityId: $marketingActivityId, channelHandle: $channelHandle, remoteId: $remoteId) {
          marketingEngagement {
            occurredOn
            utcOffset
            isCumulative
            adSpend {
              amount
              currencyCode
            }
            clicksCount
            impressionsCount
            commentsCount
            favoritesCount
            unsubscribesCount
            complaintsCount
            failsCount
            sendsCount
            uniqueViewsCount
            uniqueClicksCount
            sharesCount
            viewsCount
            sessionsCount
            sales {
              amount
              currencyCode
            }
            orders
            firstTimeCustomers
            returningCustomers
            marketingActivity {
              id
            }
            channelHandle
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "marketingEngagement": {
              "occurredOn": "2018-06-29",
              "utcOffset": "-07:00",
              "isCumulative": false,
              "adSpend": {
                  "currencyCode": "CAD",
                  "amount": "19.90"
              },
              "impressionsCount": 100,
              "clicksCount": 40,
              "commentsCount": 1,
              "unsubscribesCount": 1,
              "complaintsCount": 1,
              "failsCount": 1,
              "sendsCount": 1,
              "uniqueViewsCount": 1,
              "uniqueClicksCount": 1,
              "sharesCount": 5,
              "viewsCount": 10,
              "favoritesCount": 0,
              "sessionsCount": 40,
              "sales": {
                  "amount": "304.50",
                  "currencyCode": "CAD"
              },
              "orders": 8,
              "firstTimeCustomers": 5,
              "returningCustomers": 3
          },
          "marketingActivityId": null,
          "channelHandle": "my-channel-handle",
          "remoteId": null
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation M($marketingEngagement: MarketingEngagementInput!, $marketingActivityId: ID, $channelHandle: String, $remoteId: String) {
    marketingEngagementCreate(marketingEngagement: $marketingEngagement, marketingActivityId: $marketingActivityId, channelHandle: $channelHandle, remoteId: $remoteId) {
      marketingEngagement {
        occurredOn
        utcOffset
        isCumulative
        adSpend {
          amount
          currencyCode
        }
        clicksCount
        impressionsCount
        commentsCount
        favoritesCount
        unsubscribesCount
        complaintsCount
        failsCount
        sendsCount
        uniqueViewsCount
        uniqueClicksCount
        sharesCount
        viewsCount
        sessionsCount
        sales {
          amount
          currencyCode
        }
        orders
        firstTimeCustomers
        returningCustomers
        marketingActivity {
          id
        }
        channelHandle
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "marketingEngagement": {
      "occurredOn": "2018-06-29",
      "utcOffset": "-07:00",
      "isCumulative": false,
      "adSpend": {
        "currencyCode": "CAD",
        "amount": "19.90"
      },
      "impressionsCount": 100,
      "clicksCount": 40,
      "commentsCount": 1,
      "unsubscribesCount": 1,
      "complaintsCount": 1,
      "failsCount": 1,
      "sendsCount": 1,
      "uniqueViewsCount": 1,
      "uniqueClicksCount": 1,
      "sharesCount": 5,
      "viewsCount": 10,
      "favoritesCount": 0,
      "sessionsCount": 40,
      "sales": {
        "amount": "304.50",
        "currencyCode": "CAD"
      },
      "orders": 8,
      "firstTimeCustomers": 5,
      "returningCustomers": 3
    },
    "marketingActivityId": null,
    "channelHandle": "my-channel-handle",
    "remoteId": null
  }'
  ```

  #### Response

  ```json
  {
    "marketingEngagementCreate": {
      "marketingEngagement": {
        "occurredOn": "2018-06-29",
        "utcOffset": "-07:00",
        "isCumulative": false,
        "adSpend": {
          "amount": "19.9",
          "currencyCode": "CAD"
        },
        "clicksCount": 40,
        "impressionsCount": 100,
        "commentsCount": 1,
        "favoritesCount": 0,
        "unsubscribesCount": 1,
        "complaintsCount": 1,
        "failsCount": 1,
        "sendsCount": 1,
        "uniqueViewsCount": 1,
        "uniqueClicksCount": 1,
        "sharesCount": 5,
        "viewsCount": 10,
        "sessionsCount": 40,
        "sales": {
          "amount": "304.5",
          "currencyCode": "CAD"
        },
        "orders": "8.0",
        "firstTimeCustomers": "5.0",
        "returningCustomers": "3.0",
        "marketingActivity": null,
        "channelHandle": "my-channel-handle"
      },
      "userErrors": []
    }
  }
  ```

* ### Create channel-level engagement with conversion metrics for a channel handle

  #### Query

  ```graphql
  mutation M($marketingEngagement: MarketingEngagementInput!, $marketingActivityId: ID, $channelHandle: String, $remoteId: String) {
    marketingEngagementCreate(marketingEngagement: $marketingEngagement, marketingActivityId: $marketingActivityId, channelHandle: $channelHandle, remoteId: $remoteId) {
      marketingEngagement {
        occurredOn
        utcOffset
        isCumulative
        adSpend {
          amount
          currencyCode
        }
        clicksCount
        impressionsCount
        commentsCount
        favoritesCount
        unsubscribesCount
        complaintsCount
        failsCount
        sendsCount
        uniqueViewsCount
        uniqueClicksCount
        sharesCount
        viewsCount
        sessionsCount
        sales {
          amount
          currencyCode
        }
        orders
        firstTimeCustomers
        returningCustomers
        primaryConversions
        allConversions
        marketingActivity {
          id
        }
        channelHandle
      }
      userErrors {
        field
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "marketingEngagement": {
      "occurredOn": "2018-06-29",
      "utcOffset": "-07:00",
      "isCumulative": false,
      "adSpend": {
        "currencyCode": "CAD",
        "amount": "19.90"
      },
      "impressionsCount": 100,
      "clicksCount": 40,
      "commentsCount": 1,
      "unsubscribesCount": 1,
      "complaintsCount": 1,
      "failsCount": 1,
      "sendsCount": 1,
      "uniqueViewsCount": 1,
      "uniqueClicksCount": 1,
      "sharesCount": 5,
      "viewsCount": 10,
      "favoritesCount": 0,
      "sessionsCount": 40,
      "sales": {
        "amount": "304.50",
        "currencyCode": "CAD"
      },
      "orders": 8,
      "firstTimeCustomers": 5,
      "returningCustomers": 3,
      "primaryConversions": 8,
      "allConversions": 40
    },
    "marketingActivityId": null,
    "channelHandle": "my-channel-handle",
    "remoteId": null
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation M($marketingEngagement: MarketingEngagementInput!, $marketingActivityId: ID, $channelHandle: String, $remoteId: String) { marketingEngagementCreate(marketingEngagement: $marketingEngagement, marketingActivityId: $marketingActivityId, channelHandle: $channelHandle, remoteId: $remoteId) { marketingEngagement { occurredOn utcOffset isCumulative adSpend { amount currencyCode } clicksCount impressionsCount commentsCount favoritesCount unsubscribesCount complaintsCount failsCount sendsCount uniqueViewsCount uniqueClicksCount sharesCount viewsCount sessionsCount sales { amount currencyCode } orders firstTimeCustomers returningCustomers primaryConversions allConversions marketingActivity { id } channelHandle } userErrors { field message } } }",
   "variables": {
      "marketingEngagement": {
        "occurredOn": "2018-06-29",
        "utcOffset": "-07:00",
        "isCumulative": false,
        "adSpend": {
          "currencyCode": "CAD",
          "amount": "19.90"
        },
        "impressionsCount": 100,
        "clicksCount": 40,
        "commentsCount": 1,
        "unsubscribesCount": 1,
        "complaintsCount": 1,
        "failsCount": 1,
        "sendsCount": 1,
        "uniqueViewsCount": 1,
        "uniqueClicksCount": 1,
        "sharesCount": 5,
        "viewsCount": 10,
        "favoritesCount": 0,
        "sessionsCount": 40,
        "sales": {
          "amount": "304.50",
          "currencyCode": "CAD"
        },
        "orders": 8,
        "firstTimeCustomers": 5,
        "returningCustomers": 3,
        "primaryConversions": 8,
        "allConversions": 40
      },
      "marketingActivityId": null,
      "channelHandle": "my-channel-handle",
      "remoteId": null
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
    mutation M($marketingEngagement: MarketingEngagementInput!, $marketingActivityId: ID, $channelHandle: String, $remoteId: String) {
      marketingEngagementCreate(marketingEngagement: $marketingEngagement, marketingActivityId: $marketingActivityId, channelHandle: $channelHandle, remoteId: $remoteId) {
        marketingEngagement {
          occurredOn
          utcOffset
          isCumulative
          adSpend {
            amount
            currencyCode
          }
          clicksCount
          impressionsCount
          commentsCount
          favoritesCount
          unsubscribesCount
          complaintsCount
          failsCount
          sendsCount
          uniqueViewsCount
          uniqueClicksCount
          sharesCount
          viewsCount
          sessionsCount
          sales {
            amount
            currencyCode
          }
          orders
          firstTimeCustomers
          returningCustomers
          primaryConversions
          allConversions
          marketingActivity {
            id
          }
          channelHandle
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "marketingEngagement": {
              "occurredOn": "2018-06-29",
              "utcOffset": "-07:00",
              "isCumulative": false,
              "adSpend": {
                  "currencyCode": "CAD",
                  "amount": "19.90"
              },
              "impressionsCount": 100,
              "clicksCount": 40,
              "commentsCount": 1,
              "unsubscribesCount": 1,
              "complaintsCount": 1,
              "failsCount": 1,
              "sendsCount": 1,
              "uniqueViewsCount": 1,
              "uniqueClicksCount": 1,
              "sharesCount": 5,
              "viewsCount": 10,
              "favoritesCount": 0,
              "sessionsCount": 40,
              "sales": {
                  "amount": "304.50",
                  "currencyCode": "CAD"
              },
              "orders": 8,
              "firstTimeCustomers": 5,
              "returningCustomers": 3,
              "primaryConversions": 8,
              "allConversions": 40
          },
          "marketingActivityId": null,
          "channelHandle": "my-channel-handle",
          "remoteId": null
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
    mutation M($marketingEngagement: MarketingEngagementInput!, $marketingActivityId: ID, $channelHandle: String, $remoteId: String) {
      marketingEngagementCreate(marketingEngagement: $marketingEngagement, marketingActivityId: $marketingActivityId, channelHandle: $channelHandle, remoteId: $remoteId) {
        marketingEngagement {
          occurredOn
          utcOffset
          isCumulative
          adSpend {
            amount
            currencyCode
          }
          clicksCount
          impressionsCount
          commentsCount
          favoritesCount
          unsubscribesCount
          complaintsCount
          failsCount
          sendsCount
          uniqueViewsCount
          uniqueClicksCount
          sharesCount
          viewsCount
          sessionsCount
          sales {
            amount
            currencyCode
          }
          orders
          firstTimeCustomers
          returningCustomers
          primaryConversions
          allConversions
          marketingActivity {
            id
          }
          channelHandle
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "marketingEngagement": {
      "occurredOn": "2018-06-29",
      "utcOffset": "-07:00",
      "isCumulative": false,
      "adSpend": {
        "currencyCode": "CAD",
        "amount": "19.90"
      },
      "impressionsCount": 100,
      "clicksCount": 40,
      "commentsCount": 1,
      "unsubscribesCount": 1,
      "complaintsCount": 1,
      "failsCount": 1,
      "sendsCount": 1,
      "uniqueViewsCount": 1,
      "uniqueClicksCount": 1,
      "sharesCount": 5,
      "viewsCount": 10,
      "favoritesCount": 0,
      "sessionsCount": 40,
      "sales": {
        "amount": "304.50",
        "currencyCode": "CAD"
      },
      "orders": 8,
      "firstTimeCustomers": 5,
      "returningCustomers": 3,
      "primaryConversions": 8,
      "allConversions": 40
    },
    "marketingActivityId": null,
    "channelHandle": "my-channel-handle",
    "remoteId": null
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation M($marketingEngagement: MarketingEngagementInput!, $marketingActivityId: ID, $channelHandle: String, $remoteId: String) {
        marketingEngagementCreate(marketingEngagement: $marketingEngagement, marketingActivityId: $marketingActivityId, channelHandle: $channelHandle, remoteId: $remoteId) {
          marketingEngagement {
            occurredOn
            utcOffset
            isCumulative
            adSpend {
              amount
              currencyCode
            }
            clicksCount
            impressionsCount
            commentsCount
            favoritesCount
            unsubscribesCount
            complaintsCount
            failsCount
            sendsCount
            uniqueViewsCount
            uniqueClicksCount
            sharesCount
            viewsCount
            sessionsCount
            sales {
              amount
              currencyCode
            }
            orders
            firstTimeCustomers
            returningCustomers
            primaryConversions
            allConversions
            marketingActivity {
              id
            }
            channelHandle
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "marketingEngagement": {
              "occurredOn": "2018-06-29",
              "utcOffset": "-07:00",
              "isCumulative": false,
              "adSpend": {
                  "currencyCode": "CAD",
                  "amount": "19.90"
              },
              "impressionsCount": 100,
              "clicksCount": 40,
              "commentsCount": 1,
              "unsubscribesCount": 1,
              "complaintsCount": 1,
              "failsCount": 1,
              "sendsCount": 1,
              "uniqueViewsCount": 1,
              "uniqueClicksCount": 1,
              "sharesCount": 5,
              "viewsCount": 10,
              "favoritesCount": 0,
              "sessionsCount": 40,
              "sales": {
                  "amount": "304.50",
                  "currencyCode": "CAD"
              },
              "orders": 8,
              "firstTimeCustomers": 5,
              "returningCustomers": 3,
              "primaryConversions": 8,
              "allConversions": 40
          },
          "marketingActivityId": null,
          "channelHandle": "my-channel-handle",
          "remoteId": null
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation M($marketingEngagement: MarketingEngagementInput!, $marketingActivityId: ID, $channelHandle: String, $remoteId: String) {
    marketingEngagementCreate(marketingEngagement: $marketingEngagement, marketingActivityId: $marketingActivityId, channelHandle: $channelHandle, remoteId: $remoteId) {
      marketingEngagement {
        occurredOn
        utcOffset
        isCumulative
        adSpend {
          amount
          currencyCode
        }
        clicksCount
        impressionsCount
        commentsCount
        favoritesCount
        unsubscribesCount
        complaintsCount
        failsCount
        sendsCount
        uniqueViewsCount
        uniqueClicksCount
        sharesCount
        viewsCount
        sessionsCount
        sales {
          amount
          currencyCode
        }
        orders
        firstTimeCustomers
        returningCustomers
        primaryConversions
        allConversions
        marketingActivity {
          id
        }
        channelHandle
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "marketingEngagement": {
      "occurredOn": "2018-06-29",
      "utcOffset": "-07:00",
      "isCumulative": false,
      "adSpend": {
        "currencyCode": "CAD",
        "amount": "19.90"
      },
      "impressionsCount": 100,
      "clicksCount": 40,
      "commentsCount": 1,
      "unsubscribesCount": 1,
      "complaintsCount": 1,
      "failsCount": 1,
      "sendsCount": 1,
      "uniqueViewsCount": 1,
      "uniqueClicksCount": 1,
      "sharesCount": 5,
      "viewsCount": 10,
      "favoritesCount": 0,
      "sessionsCount": 40,
      "sales": {
        "amount": "304.50",
        "currencyCode": "CAD"
      },
      "orders": 8,
      "firstTimeCustomers": 5,
      "returningCustomers": 3,
      "primaryConversions": 8,
      "allConversions": 40
    },
    "marketingActivityId": null,
    "channelHandle": "my-channel-handle",
    "remoteId": null
  }'
  ```

  #### Response

  ```json
  {
    "marketingEngagementCreate": {
      "marketingEngagement": {
        "occurredOn": "2018-06-29",
        "utcOffset": "-07:00",
        "isCumulative": false,
        "adSpend": {
          "amount": "19.9",
          "currencyCode": "CAD"
        },
        "clicksCount": 40,
        "impressionsCount": 100,
        "commentsCount": 1,
        "favoritesCount": 0,
        "unsubscribesCount": 1,
        "complaintsCount": 1,
        "failsCount": 1,
        "sendsCount": 1,
        "uniqueViewsCount": 1,
        "uniqueClicksCount": 1,
        "sharesCount": 5,
        "viewsCount": 10,
        "sessionsCount": 40,
        "sales": {
          "amount": "304.5",
          "currencyCode": "CAD"
        },
        "orders": "8.0",
        "firstTimeCustomers": "5.0",
        "returningCustomers": "3.0",
        "primaryConversions": "8.0",
        "allConversions": "40.0",
        "marketingActivity": null,
        "channelHandle": "my-channel-handle"
      },
      "userErrors": []
    }
  }
  ```

* ### Creates marketing engagements on a marketing event

  #### Query

  ```graphql
  mutation M($marketingEngagement: MarketingEngagementInput!, $marketingActivityId: ID!) {
    marketingEngagementCreate(marketingEngagement: $marketingEngagement, marketingActivityId: $marketingActivityId) {
      marketingEngagement {
        occurredOn
        clicksCount
        commentsCount
        favoritesCount
        impressionsCount
        unsubscribesCount
        complaintsCount
        failsCount
        sendsCount
        uniqueViewsCount
        uniqueClicksCount
        isCumulative
        utcOffset
        adSpend {
          amount
          currencyCode
        }
        marketingActivity {
          id
        }
      }
      userErrors {
        field
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "marketingEngagement": {
      "occurredOn": "2018-06-29",
      "adSpend": {
        "currencyCode": "CAD",
        "amount": "19.90"
      },
      "utcOffset": "-07:00",
      "impressionsCount": 100,
      "clicksCount": 40,
      "commentsCount": 1,
      "unsubscribesCount": 1,
      "complaintsCount": 1,
      "failsCount": 1,
      "sendsCount": 1,
      "uniqueViewsCount": 1,
      "uniqueClicksCount": 1,
      "isCumulative": true,
      "favoritesCount": 0
    },
    "marketingActivityId": "gid://shopify/MarketingActivity/794355127"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation M($marketingEngagement: MarketingEngagementInput!, $marketingActivityId: ID!) { marketingEngagementCreate(marketingEngagement: $marketingEngagement, marketingActivityId: $marketingActivityId) { marketingEngagement { occurredOn clicksCount commentsCount favoritesCount impressionsCount unsubscribesCount complaintsCount failsCount sendsCount uniqueViewsCount uniqueClicksCount isCumulative utcOffset adSpend { amount currencyCode } marketingActivity { id } } userErrors { field message } } }",
   "variables": {
      "marketingEngagement": {
        "occurredOn": "2018-06-29",
        "adSpend": {
          "currencyCode": "CAD",
          "amount": "19.90"
        },
        "utcOffset": "-07:00",
        "impressionsCount": 100,
        "clicksCount": 40,
        "commentsCount": 1,
        "unsubscribesCount": 1,
        "complaintsCount": 1,
        "failsCount": 1,
        "sendsCount": 1,
        "uniqueViewsCount": 1,
        "uniqueClicksCount": 1,
        "isCumulative": true,
        "favoritesCount": 0
      },
      "marketingActivityId": "gid://shopify/MarketingActivity/794355127"
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
    mutation M($marketingEngagement: MarketingEngagementInput!, $marketingActivityId: ID!) {
      marketingEngagementCreate(marketingEngagement: $marketingEngagement, marketingActivityId: $marketingActivityId) {
        marketingEngagement {
          occurredOn
          clicksCount
          commentsCount
          favoritesCount
          impressionsCount
          unsubscribesCount
          complaintsCount
          failsCount
          sendsCount
          uniqueViewsCount
          uniqueClicksCount
          isCumulative
          utcOffset
          adSpend {
            amount
            currencyCode
          }
          marketingActivity {
            id
          }
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "marketingEngagement": {
              "occurredOn": "2018-06-29",
              "adSpend": {
                  "currencyCode": "CAD",
                  "amount": "19.90"
              },
              "utcOffset": "-07:00",
              "impressionsCount": 100,
              "clicksCount": 40,
              "commentsCount": 1,
              "unsubscribesCount": 1,
              "complaintsCount": 1,
              "failsCount": 1,
              "sendsCount": 1,
              "uniqueViewsCount": 1,
              "uniqueClicksCount": 1,
              "isCumulative": true,
              "favoritesCount": 0
          },
          "marketingActivityId": "gid://shopify/MarketingActivity/794355127"
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
    mutation M($marketingEngagement: MarketingEngagementInput!, $marketingActivityId: ID!) {
      marketingEngagementCreate(marketingEngagement: $marketingEngagement, marketingActivityId: $marketingActivityId) {
        marketingEngagement {
          occurredOn
          clicksCount
          commentsCount
          favoritesCount
          impressionsCount
          unsubscribesCount
          complaintsCount
          failsCount
          sendsCount
          uniqueViewsCount
          uniqueClicksCount
          isCumulative
          utcOffset
          adSpend {
            amount
            currencyCode
          }
          marketingActivity {
            id
          }
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "marketingEngagement": {
      "occurredOn": "2018-06-29",
      "adSpend": {
        "currencyCode": "CAD",
        "amount": "19.90"
      },
      "utcOffset": "-07:00",
      "impressionsCount": 100,
      "clicksCount": 40,
      "commentsCount": 1,
      "unsubscribesCount": 1,
      "complaintsCount": 1,
      "failsCount": 1,
      "sendsCount": 1,
      "uniqueViewsCount": 1,
      "uniqueClicksCount": 1,
      "isCumulative": true,
      "favoritesCount": 0
    },
    "marketingActivityId": "gid://shopify/MarketingActivity/794355127"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation M($marketingEngagement: MarketingEngagementInput!, $marketingActivityId: ID!) {
        marketingEngagementCreate(marketingEngagement: $marketingEngagement, marketingActivityId: $marketingActivityId) {
          marketingEngagement {
            occurredOn
            clicksCount
            commentsCount
            favoritesCount
            impressionsCount
            unsubscribesCount
            complaintsCount
            failsCount
            sendsCount
            uniqueViewsCount
            uniqueClicksCount
            isCumulative
            utcOffset
            adSpend {
              amount
              currencyCode
            }
            marketingActivity {
              id
            }
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "marketingEngagement": {
              "occurredOn": "2018-06-29",
              "adSpend": {
                  "currencyCode": "CAD",
                  "amount": "19.90"
              },
              "utcOffset": "-07:00",
              "impressionsCount": 100,
              "clicksCount": 40,
              "commentsCount": 1,
              "unsubscribesCount": 1,
              "complaintsCount": 1,
              "failsCount": 1,
              "sendsCount": 1,
              "uniqueViewsCount": 1,
              "uniqueClicksCount": 1,
              "isCumulative": true,
              "favoritesCount": 0
          },
          "marketingActivityId": "gid://shopify/MarketingActivity/794355127"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation M($marketingEngagement: MarketingEngagementInput!, $marketingActivityId: ID!) {
    marketingEngagementCreate(marketingEngagement: $marketingEngagement, marketingActivityId: $marketingActivityId) {
      marketingEngagement {
        occurredOn
        clicksCount
        commentsCount
        favoritesCount
        impressionsCount
        unsubscribesCount
        complaintsCount
        failsCount
        sendsCount
        uniqueViewsCount
        uniqueClicksCount
        isCumulative
        utcOffset
        adSpend {
          amount
          currencyCode
        }
        marketingActivity {
          id
        }
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "marketingEngagement": {
      "occurredOn": "2018-06-29",
      "adSpend": {
        "currencyCode": "CAD",
        "amount": "19.90"
      },
      "utcOffset": "-07:00",
      "impressionsCount": 100,
      "clicksCount": 40,
      "commentsCount": 1,
      "unsubscribesCount": 1,
      "complaintsCount": 1,
      "failsCount": 1,
      "sendsCount": 1,
      "uniqueViewsCount": 1,
      "uniqueClicksCount": 1,
      "isCumulative": true,
      "favoritesCount": 0
    },
    "marketingActivityId": "gid://shopify/MarketingActivity/794355127"
  }'
  ```

  #### Response

  ```json
  {
    "marketingEngagementCreate": {
      "marketingEngagement": {
        "occurredOn": "2018-06-29",
        "clicksCount": 40,
        "commentsCount": 1,
        "favoritesCount": 0,
        "impressionsCount": 100,
        "unsubscribesCount": 1,
        "complaintsCount": 1,
        "failsCount": 1,
        "sendsCount": 1,
        "uniqueViewsCount": 1,
        "uniqueClicksCount": 1,
        "isCumulative": true,
        "utcOffset": "-07:00",
        "adSpend": {
          "amount": "19.9",
          "currencyCode": "CAD"
        },
        "marketingActivity": {
          "id": "gid://shopify/MarketingActivity/794355127"
        }
      },
      "userErrors": []
    }
  }
  ```

* ### marketingEngagementCreate reference
