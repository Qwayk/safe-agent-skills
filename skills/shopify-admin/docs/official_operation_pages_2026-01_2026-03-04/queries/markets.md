---
title: markets - GraphQL Admin
description: >-
  Returns a paginated list of
  [`Market`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Market)
  objects configured for the shop. Markets match buyers based on defined
  conditions to deliver customized shopping experiences.


  Filter markets by
  [`MarketType`](https://shopify.dev/docs/api/admin-graphql/latest/enums/MarketType)
  and
  [`MarketStatus`](https://shopify.dev/docs/api/admin-graphql/latest/enums/MarketStatus),
  search by name, and control sort order. Retrieve market configurations
  including
  [`MarketCurrencySettings`](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketCurrencySettings),
  [`MarketWebPresence`](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketWebPresence)
  objects, and
  [`MarketConditions`](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketConditions).


  Learn more about [Shopify
  Markets](https://shopify.dev/docs/apps/build/markets).
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/markets'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/markets.md'
---

# markets

query

Requires `read_markets` for queries and both `read_markets` as well as `write_markets` for mutations.

Returns a paginated list of [`Market`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Market) objects configured for the shop. Markets match buyers based on defined conditions to deliver customized shopping experiences.

Filter markets by [`MarketType`](https://shopify.dev/docs/api/admin-graphql/latest/enums/MarketType) and [`MarketStatus`](https://shopify.dev/docs/api/admin-graphql/latest/enums/MarketStatus), search by name, and control sort order. Retrieve market configurations including [`MarketCurrencySettings`](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketCurrencySettings), [`MarketWebPresence`](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketWebPresence) objects, and [`MarketConditions`](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketConditions).

Learn more about [Shopify Markets](https://shopify.dev/docs/apps/build/markets).

## MarketConnection arguments

[MarketConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/MarketConnection)

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

  * * default

      string

    * id

      id

    * market\_condition\_types

      string

    - Filter by a case-insensitive search of multiple fields in a document.

    - Example:

      * `query=Bob Norman`
      * `query=title:green hoodie`

      Filter by `id` range.

    - Example:

      * `id:1234`
      * `id:>=1234`
      * `id:<=1234`

      A comma-separated list of condition types.

  * market\_type

    string

  * name

    string

  * * status

      string

    * wildcard\_company\_location\_with\_country\_code

      string

    -
    - Valid values:
      * `ACTIVE`
      * `DRAFT`

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

* sort​Key

  [Markets​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/MarketsSortKeys)

  Default:NAME

  Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

* type

  [Market​Type](https://shopify.dev/docs/api/admin-graphql/latest/enums/MarketType)

  Default:null

  Filters markets by type.

***

## Possible returns

* edges

  [\[Market​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Market!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Market)

  non-null

  A list of nodes that are contained in MarketEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### Get market web presences and their root URLs

  #### Description

  The following query loads the web presences configured for a shop’s markets and the language-specific root URLs available on each.

  #### Query

  ```graphql
  query Markets {
    markets(first: 4) {
      nodes {
        name
        webPresence {
          rootUrls {
            locale
            url
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
  "query": "query Markets { markets(first: 4) { nodes { name webPresence { rootUrls { locale url } } } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query Markets {
      markets(first: 4) {
        nodes {
          name
          webPresence {
            rootUrls {
              locale
              url
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
    query Markets {
      markets(first: 4) {
        nodes {
          name
          webPresence {
            rootUrls {
              locale
              url
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
    data: `query Markets {
      markets(first: 4) {
        nodes {
          name
          webPresence {
            rootUrls {
              locale
              url
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
  'query Markets {
    markets(first: 4) {
      nodes {
        name
        webPresence {
          rootUrls {
            locale
            url
          }
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "markets": {
      "nodes": [
        {
          "name": "Canada",
          "webPresence": {
            "rootUrls": [
              {
                "locale": "en",
                "url": "https://defaultglobal.com/en-ca"
              },
              {
                "locale": "fr",
                "url": "https://defaultglobal.com/fr-ca"
              }
            ]
          }
        },
        {
          "name": "European Union",
          "webPresence": {
            "rootUrls": [
              {
                "locale": "en",
                "url": "https://defaultglobal.com/en-eu"
              },
              {
                "locale": "es",
                "url": "https://defaultglobal.com/es-eu"
              },
              {
                "locale": "fr",
                "url": "https://defaultglobal.com/fr-eu"
              }
            ]
          }
        },
        {
          "name": "United Kingdom",
          "webPresence": {
            "rootUrls": [
              {
                "locale": "en",
                "url": "https://uk.defaultglobal.com"
              }
            ]
          }
        },
        {
          "name": "United States",
          "webPresence": {
            "rootUrls": [
              {
                "locale": "en",
                "url": "https://defaultglobal.com"
              },
              {
                "locale": "es",
                "url": "https://defaultglobal.com/es"
              }
            ]
          }
        }
      ]
    }
  }
  ```

* ### Get the first four markets

  #### Description

  The following query retrieves the first four markets, their names, and what regions are included in them.

  #### Query

  ```graphql
  query Markets {
    markets(first: 4) {
      nodes {
        id
        name
        regions(first: 2) {
          pageInfo {
            hasNextPage
          }
          nodes {
            name
            ... on MarketRegionCountry {
              code
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
  "query": "query Markets { markets(first: 4) { nodes { id name regions(first: 2) { pageInfo { hasNextPage } nodes { name ... on MarketRegionCountry { code } } } } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query Markets {
      markets(first: 4) {
        nodes {
          id
          name
          regions(first: 2) {
            pageInfo {
              hasNextPage
            }
            nodes {
              name
              ... on MarketRegionCountry {
                code
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
    query Markets {
      markets(first: 4) {
        nodes {
          id
          name
          regions(first: 2) {
            pageInfo {
              hasNextPage
            }
            nodes {
              name
              ... on MarketRegionCountry {
                code
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
    data: `query Markets {
      markets(first: 4) {
        nodes {
          id
          name
          regions(first: 2) {
            pageInfo {
              hasNextPage
            }
            nodes {
              name
              ... on MarketRegionCountry {
                code
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
  'query Markets {
    markets(first: 4) {
      nodes {
        id
        name
        regions(first: 2) {
          pageInfo {
            hasNextPage
          }
          nodes {
            name
            ... on MarketRegionCountry {
              code
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
    "markets": {
      "nodes": [
        {
          "id": "gid://shopify/Market/249692835",
          "name": "Canada",
          "regions": {
            "pageInfo": {
              "hasNextPage": false
            },
            "nodes": [
              {
                "name": "Canada",
                "code": "CA"
              }
            ]
          }
        },
        {
          "id": "gid://shopify/Market/58345162",
          "name": "European Union",
          "regions": {
            "pageInfo": {
              "hasNextPage": true
            },
            "nodes": [
              {
                "name": "Germany",
                "code": "DE"
              },
              {
                "name": "Belgium",
                "code": "BE"
              }
            ]
          }
        },
        {
          "id": "gid://shopify/Market/867658238",
          "name": "United Kingdom",
          "regions": {
            "pageInfo": {
              "hasNextPage": false
            },
            "nodes": [
              {
                "name": "United Kingdom",
                "code": "GB"
              }
            ]
          }
        },
        {
          "id": "gid://shopify/Market/371343838",
          "name": "United States",
          "regions": {
            "pageInfo": {
              "hasNextPage": false
            },
            "nodes": [
              {
                "name": "United States",
                "code": "US"
              }
            ]
          }
        }
      ]
    }
  }
  ```
