---
title: currentAppInstallation - GraphQL Admin
description: >-
  Returns the
  [`AppInstallation`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppInstallation)
  for the currently authenticated app. Provides access to granted access scopes,
  active
  [`AppSubscription`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppSubscription)
  objects, and billing information for your app.


  Use this query to check which permissions your app has, monitor subscription
  status, or retrieve
  [`AppCredit`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppCredit)
  objects. Learn more about [managing access
  scopes](https://shopify.dev/docs/api/usage/access-scopes#checking-granted-access-scopes),
  [subscription
  billing](https://shopify.dev/docs/apps/launch/billing/subscription-billing),
  and [app
  credits](https://shopify.dev/docs/apps/launch/billing/award-app-credits).
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/currentAppInstallation
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/currentAppInstallation.md
---

# current​App​Installation

query

Returns the [`AppInstallation`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppInstallation) for the currently authenticated app. Provides access to granted access scopes, active [`AppSubscription`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppSubscription) objects, and billing information for your app.

Use this query to check which permissions your app has, monitor subscription status, or retrieve [`AppCredit`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppCredit) objects. Learn more about [managing access scopes](https://shopify.dev/docs/api/usage/access-scopes#checking-granted-access-scopes), [subscription billing](https://shopify.dev/docs/apps/launch/billing/subscription-billing), and [app credits](https://shopify.dev/docs/apps/launch/billing/award-app-credits).

## Possible returns

* App​Installation

  [App​Installation!](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppInstallation)

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

* ### Get a list of access scopes

  #### Query

  ```graphql
  query AccessScopeList {
    currentAppInstallation {
      accessScopes {
        handle
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
  "query": "query AccessScopeList { currentAppInstallation { accessScopes { handle } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query AccessScopeList {
      currentAppInstallation {
        accessScopes {
          handle
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
    query AccessScopeList {
      currentAppInstallation {
        accessScopes {
          handle
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
    data: `query AccessScopeList {
      currentAppInstallation {
        accessScopes {
          handle
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query AccessScopeList {
    currentAppInstallation {
      accessScopes {
        handle
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "currentAppInstallation": {
      "accessScopes": [
        {
          "handle": "read_all_orders"
        },
        {
          "handle": "read_all_subscription_contracts"
        },
        {
          "handle": "read_analytics_overviews"
        },
        {
          "handle": "read_billing"
        },
        {
          "handle": "read_checkouts"
        },
        {
          "handle": "read_discovery"
        },
        {
          "handle": "read_discovery_synonym_groups"
        },
        {
          "handle": "read_payment_settings"
        },
        {
          "handle": "read_subscription_plans"
        },
        {
          "handle": "read_users"
        },
        {
          "handle": "read_customer_merge"
        },
        {
          "handle": "write_admin_shop_settings"
        },
        {
          "handle": "write_analytics_overviews"
        },
        {
          "handle": "write_apps"
        },
        {
          "handle": "write_brand"
        },
        {
          "handle": "write_brand_settings"
        },
        {
          "handle": "write_content"
        },
        {
          "handle": "write_customer_data_redaction_requests"
        },
        {
          "handle": "write_customer_payment_methods"
        },
        {
          "handle": "write_customers"
        },
        {
          "handle": "write_discounts"
        },
        {
          "handle": "write_discovery"
        },
        {
          "handle": "write_discovery_synonym_groups"
        },
        {
          "handle": "write_draft_orders"
        },
        {
          "handle": "write_files"
        },
        {
          "handle": "write_fulfillments"
        },
        {
          "handle": "write_gift_cards"
        },
        {
          "handle": "write_home"
        },
        {
          "handle": "write_inventory"
        },
        {
          "handle": "write_locations"
        },
        {
          "handle": "write_marketing_events"
        },
        {
          "handle": "write_media_processing"
        },
        {
          "handle": "write_merchant_managed_fulfillment_orders"
        },
        {
          "handle": "write_metaobjects"
        },
        {
          "handle": "write_metaobject_definitions"
        },
        {
          "handle": "write_notifications"
        },
        {
          "handle": "write_online_store"
        },
        {
          "handle": "write_online_store_pages"
        },
        {
          "handle": "write_online_store_navigation"
        },
        {
          "handle": "write_order_edits"
        },
        {
          "handle": "write_orders"
        },
        {
          "handle": "write_order_refunds"
        },
        {
          "handle": "write_payment_mandate"
        },
        {
          "handle": "write_price_rules"
        },
        {
          "handle": "write_products"
        },
        {
          "handle": "write_publications"
        },
        {
          "handle": "write_reports"
        },
        {
          "handle": "write_script_tags"
        },
        {
          "handle": "write_shipping"
        },
        {
          "handle": "write_themes"
        },
        {
          "handle": "write_third_party_fulfillment_orders"
        },
        {
          "handle": "write_customer_merge"
        },
        {
          "handle": "write_companies"
        },
        {
          "handle": "read_analytics"
        },
        {
          "handle": "read_admin_shop_settings"
        },
        {
          "handle": "read_apps"
        },
        {
          "handle": "read_brand"
        },
        {
          "handle": "read_brand_settings"
        },
        {
          "handle": "read_content"
        },
        {
          "handle": "read_customer_data_redaction_requests"
        },
        {
          "handle": "read_customer_payment_methods"
        },
        {
          "handle": "read_customers"
        },
        {
          "handle": "read_discounts"
        },
        {
          "handle": "read_draft_orders"
        },
        {
          "handle": "read_files"
        },
        {
          "handle": "read_fulfillments"
        },
        {
          "handle": "read_gift_cards"
        },
        {
          "handle": "read_home"
        },
        {
          "handle": "read_inventory"
        },
        {
          "handle": "read_locations"
        },
        {
          "handle": "read_marketing_events"
        },
        {
          "handle": "read_media_processing"
        },
        {
          "handle": "read_merchant_managed_fulfillment_orders"
        },
        {
          "handle": "read_metaobjects"
        },
        {
          "handle": "read_metaobject_definitions"
        },
        {
          "handle": "read_notifications"
        },
        {
          "handle": "read_online_store"
        },
        {
          "handle": "read_online_store_pages"
        },
        {
          "handle": "read_online_store_navigation"
        },
        {
          "handle": "read_order_edits"
        },
        {
          "handle": "read_orders"
        },
        {
          "handle": "read_payment_mandate"
        },
        {
          "handle": "read_price_rules"
        },
        {
          "handle": "read_products"
        },
        {
          "handle": "read_publications"
        },
        {
          "handle": "read_reports"
        },
        {
          "handle": "read_script_tags"
        },
        {
          "handle": "read_shipping"
        },
        {
          "handle": "read_themes"
        },
        {
          "handle": "read_third_party_fulfillment_orders"
        },
        {
          "handle": "read_companies"
        }
      ]
    }
  }
  ```

* ### Retrieves a list of application charges

  #### Query

  ```graphql
  query {
    currentAppInstallation {
      oneTimePurchases(first: 10) {
        edges {
          node {
            createdAt
            id
            name
            price {
              amount
              currencyCode
            }
            status
            test
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
  "query": "query { currentAppInstallation { oneTimePurchases(first: 10) { edges { node { createdAt id name price { amount currencyCode } status test } } } } }"
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
      currentAppInstallation {
        oneTimePurchases(first: 10) {
          edges {
            node {
              createdAt
              id
              name
              price {
                amount
                currencyCode
              }
              status
              test
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
    query {
      currentAppInstallation {
        oneTimePurchases(first: 10) {
          edges {
            node {
              createdAt
              id
              name
              price {
                amount
                currencyCode
              }
              status
              test
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
    data: `query {
      currentAppInstallation {
        oneTimePurchases(first: 10) {
          edges {
            node {
              createdAt
              id
              name
              price {
                amount
                currencyCode
              }
              status
              test
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
  'query {
    currentAppInstallation {
      oneTimePurchases(first: 10) {
        edges {
          node {
            createdAt
            id
            name
            price {
              amount
              currencyCode
            }
            status
            test
          }
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "currentAppInstallation": {
      "oneTimePurchases": {
        "edges": []
      }
    }
  }
  ```

* ### Retrieves a list of recurring application charges

  #### Query

  ```graphql
  query GetRecurringApplicationCharges {
    currentAppInstallation {
      activeSubscriptions {
        id
        name
        status
        lineItems {
          id
          plan {
            pricingDetails {
              __typename
            }
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
  "query": "query GetRecurringApplicationCharges { currentAppInstallation { activeSubscriptions { id name status lineItems { id plan { pricingDetails { __typename } } } } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query GetRecurringApplicationCharges {
      currentAppInstallation {
        activeSubscriptions {
          id
          name
          status
          lineItems {
            id
            plan {
              pricingDetails {
                __typename
              }
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
    query GetRecurringApplicationCharges {
      currentAppInstallation {
        activeSubscriptions {
          id
          name
          status
          lineItems {
            id
            plan {
              pricingDetails {
                __typename
              }
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
    data: `query GetRecurringApplicationCharges {
      currentAppInstallation {
        activeSubscriptions {
          id
          name
          status
          lineItems {
            id
            plan {
              pricingDetails {
                __typename
              }
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
  'query GetRecurringApplicationCharges {
    currentAppInstallation {
      activeSubscriptions {
        id
        name
        status
        lineItems {
          id
          plan {
            pricingDetails {
              __typename
            }
          }
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "currentAppInstallation": {
      "activeSubscriptions": []
    }
  }
  ```
