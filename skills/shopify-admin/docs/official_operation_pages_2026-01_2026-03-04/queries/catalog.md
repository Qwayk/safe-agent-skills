---
title: catalog - GraphQL Admin
description: >-
  Retrieves a
  [catalog](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/Catalog)
  by its ID.

  A catalog represents a list of products with publishing and pricing
  information,

  and can be associated with a context, such as a market, company location, or
  app.


  Use the `catalog` query to retrieve information associated with the following
  workflows:


  - Managing product publications across different contexts

  - Setting up contextual pricing with price lists

  - Managing market-specific product availability

  - Configuring B2B customer catalogs


  There are several types of catalogs:


  -
  [`MarketCatalog`](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketCatalog)

  -
  [`AppCatalog`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppCatalog)

  -
  [`CompanyLocationCatalog`](https://shopify.dev/docs/api/admin-graphql/latest/objects/CompanyLocationCatalog)


  Learn more about [catalogs for different
  markets](https://shopify.dev/docs/apps/build/markets/catalogs-different-markets).
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/catalog'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/catalog.md'
---

# catalog

query

Retrieves a [catalog](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/Catalog) by its ID. A catalog represents a list of products with publishing and pricing information, and can be associated with a context, such as a market, company location, or app.

Use the `catalog` query to retrieve information associated with the following workflows:

* Managing product publications across different contexts
* Setting up contextual pricing with price lists
* Managing market-specific product availability
* Configuring B2B customer catalogs

There are several types of catalogs:

* [`MarketCatalog`](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketCatalog)
* [`AppCatalog`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppCatalog)
* [`CompanyLocationCatalog`](https://shopify.dev/docs/api/admin-graphql/latest/objects/CompanyLocationCatalog)

Learn more about [catalogs for different markets](https://shopify.dev/docs/apps/build/markets/catalogs-different-markets).

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the `Catalog` to return.

***

## Possible returns

* Catalog

  [Catalog](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/Catalog)

  A list of products with publishing and pricing information. A catalog can be associated with a specific context, such as a [`Market`](https://shopify.dev/docs/api/admin-graphql/2026-01/objects/market), [`CompanyLocation`](https://shopify.dev/docs/api/admin-graphql/2026-01/objects/companylocation), or [`App`](https://shopify.dev/docs/api/admin-graphql/2026-01/objects/app).

  Catalogs can optionally include a publication to control product visibility and a price list to customize pricing. When a publication isn't associated with a catalog, product availability is determined by the sales channel.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * operations

    [\[Resource​Operation!\]!](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/ResourceOperation)

    non-null

    Most recent catalog operations.

  * price​List

    [Price​List](https://shopify.dev/docs/api/admin-graphql/latest/objects/PriceList)

    The price list associated with the catalog.

  * publication

    [Publication](https://shopify.dev/docs/api/admin-graphql/latest/objects/Publication)

    A group of products and collections that's published to a catalog.

  * status

    [Catalog​Status!](https://shopify.dev/docs/api/admin-graphql/latest/enums/CatalogStatus)

    non-null

    The status of the catalog.

  * title

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The name of the catalog.

***

## Examples

* ### Monitor catalog operations and status

  #### Description

  Monitor the operational status and recent activities of a \[catalog]\(https://shopify.dev/docs/api/admin-graphql/latest/interfaces/Catalog) by retrieving its operations history. This query is useful for tracking catalog updates, imports, and other administrative operations. The \`operations\` field provides insight into recent changes and can help you identify any issues or ongoing processes affecting the catalog's functionality.

  #### Query

  ```graphql
  query {
    catalog(id: "gid://shopify/Catalog/1068177672") {
      id
      title
      status
      operations {
        __typename
        ... on CatalogCsvOperation {
          id
          status
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
  "query": "query { catalog(id: \"gid://shopify/Catalog/1068177672\") { id title status operations { __typename ... on CatalogCsvOperation { id status } } } }"
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
      catalog(id: "gid://shopify/Catalog/1068177672") {
        id
        title
        status
        operations {
          __typename
          ... on CatalogCsvOperation {
            id
            status
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
      catalog(id: "gid://shopify/Catalog/1068177672") {
        id
        title
        status
        operations {
          __typename
          ... on CatalogCsvOperation {
            id
            status
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
      catalog(id: "gid://shopify/Catalog/1068177672") {
        id
        title
        status
        operations {
          __typename
          ... on CatalogCsvOperation {
            id
            status
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
    catalog(id: "gid://shopify/Catalog/1068177672") {
      id
      title
      status
      operations {
        __typename
        ... on CatalogCsvOperation {
          id
          status
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "catalog": {
      "id": "gid://shopify/AppCatalog/1068177672",
      "title": "Operations Monitoring Catalog",
      "status": "ACTIVE",
      "operations": [
        {
          "__typename": "CatalogCsvOperation",
          "id": "gid://shopify/CatalogCsvOperation/1065229254",
          "status": "COMPLETE"
        }
      ]
    }
  }
  ```

* ### Retrieve a catalog with pricing details

  #### Description

  Retrieve comprehensive catalog information including the associated \[price list]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/PriceList) details. This query demonstrates how to access the catalog's pricing information through the price list, which contains the currency and pricing rules that apply to products in this catalog. This information is essential for understanding how products are priced within the catalog context. Learn more about \[catalog pricing]\(https://shopify.dev/docs/apps/build/markets/catalogs-different-markets).

  #### Query

  ```graphql
  query {
    catalog(id: "gid://shopify/Catalog/1068177671") {
      id
      title
      status
      priceList {
        id
        currency
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
  "query": "query { catalog(id: \"gid://shopify/Catalog/1068177671\") { id title status priceList { id currency } } }"
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
      catalog(id: "gid://shopify/Catalog/1068177671") {
        id
        title
        status
        priceList {
          id
          currency
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
      catalog(id: "gid://shopify/Catalog/1068177671") {
        id
        title
        status
        priceList {
          id
          currency
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
      catalog(id: "gid://shopify/Catalog/1068177671") {
        id
        title
        status
        priceList {
          id
          currency
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
    catalog(id: "gid://shopify/Catalog/1068177671") {
      id
      title
      status
      priceList {
        id
        currency
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "catalog": {
      "id": "gid://shopify/CompanyLocationCatalog/1068177671",
      "title": "B2B Catalog with Pricing",
      "status": "ACTIVE",
      "priceList": null
    }
  }
  ```

* ### Retrieve a catalog's title and status

  #### Description

  Retrieve the title and status of a \[catalog]\(https://shopify.dev/docs/api/admin-graphql/latest/interfaces/Catalog) using its ID. This query is useful when building admin interfaces or dashboards where you need to show catalog details to merchants. The response includes the catalog's human-readable title for display purposes and its status to indicate whether it's active and ready for use.

  #### Query

  ```graphql
  query {
    catalog(id: "gid://shopify/Catalog/1068177678") {
      id
      title
      status
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
  "query": "query { catalog(id: \"gid://shopify/Catalog/1068177678\") { id title status } }"
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
      catalog(id: "gid://shopify/Catalog/1068177678") {
        id
        title
        status
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
      catalog(id: "gid://shopify/Catalog/1068177678") {
        id
        title
        status
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
      catalog(id: "gid://shopify/Catalog/1068177678") {
        id
        title
        status
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    catalog(id: "gid://shopify/Catalog/1068177678") {
      id
      title
      status
    }
  }'
  ```

  #### Response

  ```json
  {
    "catalog": {
      "id": "gid://shopify/MarketCatalog/1068177678",
      "title": "Market Catalog Example",
      "status": "ACTIVE"
    }
  }
  ```
