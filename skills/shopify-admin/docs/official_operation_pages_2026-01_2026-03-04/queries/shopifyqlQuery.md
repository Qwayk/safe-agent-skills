---
title: shopifyqlQuery - GraphQL Admin
description: >-
  Executes a [ShopifyQL query](https://shopify.dev/docs/apps/build/shopifyql) to
  analyze store data and returns results in a tabular format.


  The response includes column metadata with names, data types, and display
  names, along with the actual data rows. If the query contains syntax errors,
  then the response provides parse error messages instead of table data.


  Read the [ShopifyQL reference
  documentation](https://shopify.dev/docs/api/shopifyql) for more information on
  how to write ShopifyQL queries.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/shopifyqlQuery'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/shopifyqlQuery.md'
---

# shopifyql​Query

query

Requires `read_reports` access scope. Also: Level 2 access to Customer data including name, address, phone, and email fields. Please refer to protected customer data [requirements](https://shopify.dev/docs/apps/launch/protected-customer-data).

Executes a [ShopifyQL query](https://shopify.dev/docs/apps/build/shopifyql) to analyze store data and returns results in a tabular format.

The response includes column metadata with names, data types, and display names, along with the actual data rows. If the query contains syntax errors, then the response provides parse error messages instead of table data.

Read the [ShopifyQL reference documentation](https://shopify.dev/docs/api/shopifyql) for more information on how to write ShopifyQL queries.

## Arguments

* query

  [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  required

  A ShopifyQL query string following the [ShopifyQL syntax](https://shopify.dev/docs/api/shopifyql). Queries must include `FROM` to specify the data source (such as `sales`, `orders`, or `customers`) and `SHOW` to select metrics and dimensions. Example: `FROM sales SHOW total_sales TIMESERIES month SINCE -12m`.

***

## Possible returns

* Shopifyql​Query​Response

  [Shopifyql​Query​Response](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopifyqlQueryResponse)

  A response to a ShopifyQL query.

  * parse​Errors

    [\[String!\]!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    A list of parse errors, if parsing fails.

  * table​Data

    [Shopifyql​Table​Data](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopifyqlTableData)

    The result in a tabular format with column and row data.

***

## Examples

* ### Get a table data response using ShopifyQL query.

  #### Description

  Uses a ShopifyQL query to retrieve data that's structured in a table format.

  #### Query

  ```graphql
  query {
    shopifyqlQuery(query: "FROM sales SHOW total_sales GROUP BY month SINCE -3m ORDER BY month") {
      tableData {
        columns {
          name
          dataType
          displayName
        }
        rows
      }
      parseErrors
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
  "query": "query { shopifyqlQuery(query: \"FROM sales SHOW total_sales GROUP BY month SINCE -3m ORDER BY month\") { tableData { columns { name dataType displayName } rows } parseErrors } }"
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
      shopifyqlQuery(query: "FROM sales SHOW total_sales GROUP BY month SINCE -3m ORDER BY month") {
        tableData {
          columns {
            name
            dataType
            displayName
          }
          rows
        }
        parseErrors
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
      shopifyqlQuery(query: "FROM sales SHOW total_sales GROUP BY month SINCE -3m ORDER BY month") {
        tableData {
          columns {
            name
            dataType
            displayName
          }
          rows
        }
        parseErrors
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
      shopifyqlQuery(query: "FROM sales SHOW total_sales GROUP BY month SINCE -3m ORDER BY month") {
        tableData {
          columns {
            name
            dataType
            displayName
          }
          rows
        }
        parseErrors
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    shopifyqlQuery(query: "FROM sales SHOW total_sales GROUP BY month SINCE -3m ORDER BY month") {
      tableData {
        columns {
          name
          dataType
          displayName
        }
        rows
      }
      parseErrors
    }
  }'
  ```

  #### Response

  ```json
  {
    "shopifyqlQuery": {
      "tableData": {
        "columns": [
          {
            "name": "month",
            "dataType": "MONTH_TIMESTAMP",
            "displayName": "Month"
          },
          {
            "name": "total_sales",
            "dataType": "MONEY",
            "displayName": "Total sales"
          }
        ],
        "rows": [
          {
            "month": "2025-01-01",
            "total_sales": "123.456"
          }
        ]
      },
      "parseErrors": []
    }
  }
  ```

* ### Get a table data response with generated columns using ShopifyQL query.

  #### Description

  Uses a ShopifyQL query to retrieve data that's structured in a table format with generated columns.

  #### Query

  ```graphql
  query {
    shopifyqlQuery(query: "FROM sales SHOW total_sales GROUP BY month SINCE -3m ORDER BY month WITH TOTALS") {
      tableData {
        columns {
          name
          dataType
          displayName
        }
        rows
      }
      parseErrors
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
  "query": "query { shopifyqlQuery(query: \"FROM sales SHOW total_sales GROUP BY month SINCE -3m ORDER BY month WITH TOTALS\") { tableData { columns { name dataType displayName } rows } parseErrors } }"
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
      shopifyqlQuery(query: "FROM sales SHOW total_sales GROUP BY month SINCE -3m ORDER BY month WITH TOTALS") {
        tableData {
          columns {
            name
            dataType
            displayName
          }
          rows
        }
        parseErrors
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
      shopifyqlQuery(query: "FROM sales SHOW total_sales GROUP BY month SINCE -3m ORDER BY month WITH TOTALS") {
        tableData {
          columns {
            name
            dataType
            displayName
          }
          rows
        }
        parseErrors
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
      shopifyqlQuery(query: "FROM sales SHOW total_sales GROUP BY month SINCE -3m ORDER BY month WITH TOTALS") {
        tableData {
          columns {
            name
            dataType
            displayName
          }
          rows
        }
        parseErrors
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    shopifyqlQuery(query: "FROM sales SHOW total_sales GROUP BY month SINCE -3m ORDER BY month WITH TOTALS") {
      tableData {
        columns {
          name
          dataType
          displayName
        }
        rows
      }
      parseErrors
    }
  }'
  ```

  #### Response

  ```json
  {
    "shopifyqlQuery": {
      "tableData": {
        "columns": [
          {
            "name": "month",
            "dataType": "MONTH_TIMESTAMP",
            "displayName": "Month"
          },
          {
            "name": "total_sales",
            "dataType": "MONEY",
            "displayName": "Total sales"
          },
          {
            "name": "total_sales__totals",
            "dataType": "MONEY",
            "displayName": "Total sales (totals)"
          }
        ],
        "rows": [
          {
            "month": "2025-01-01",
            "total_sales": "123.456",
            "total_sales__totals": "1234.56"
          }
        ]
      },
      "parseErrors": []
    }
  }
  ```

* ### Handle Parse error in ShopifyQL query

  #### Description

  An example of handling a parsing error from a ShopifyQL query.

  #### Query

  ```graphql
  query {
    shopifyqlQuery(query: "FROM sales SHOW total_sale") {
      tableData {
        columns {
          name
          dataType
          displayName
        }
        rows
      }
      parseErrors
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
  "query": "query { shopifyqlQuery(query: \"FROM sales SHOW total_sale\") { tableData { columns { name dataType displayName } rows } parseErrors } }"
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
      shopifyqlQuery(query: "FROM sales SHOW total_sale") {
        tableData {
          columns {
            name
            dataType
            displayName
          }
          rows
        }
        parseErrors
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
      shopifyqlQuery(query: "FROM sales SHOW total_sale") {
        tableData {
          columns {
            name
            dataType
            displayName
          }
          rows
        }
        parseErrors
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
      shopifyqlQuery(query: "FROM sales SHOW total_sale") {
        tableData {
          columns {
            name
            dataType
            displayName
          }
          rows
        }
        parseErrors
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    shopifyqlQuery(query: "FROM sales SHOW total_sale") {
      tableData {
        columns {
          name
          dataType
          displayName
        }
        rows
      }
      parseErrors
    }
  }'
  ```

  #### Response

  ```json
  {
    "shopifyqlQuery": {
      "tableData": null,
      "parseErrors": [
        "Column Not Found: Column 'total_sale' not found"
      ]
    }
  }
  ```
