---
title: marketUpdate - GraphQL Admin
description: Updates the properties of a market.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/marketUpdate'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/marketUpdate.md'
---

# market​Update

mutation

Requires `read_markets` for queries and both `read_markets` as well as `write_markets` for mutations.

Updates the properties of a market.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the market to update.

* input

  [Market​Update​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/MarketUpdateInput)

  required

  The properties to update.

***

## Market​Update​Payload returns

* market

  [Market](https://shopify.dev/docs/api/admin-graphql/latest/objects/Market)

  The market object.

* user​Errors

  [\[Market​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Update a market status to make it draft

  #### Description

  A draft market never matches any buyers. You can toggle its status to make it active or inactive.

  #### Query

  ```graphql
  mutation marketUpdate($input: MarketUpdateInput!) {
    marketUpdate(id: "gid://shopify/Market/73827535", input: $input) {
      market {
        id
        handle
        status
        conditions {
          regionsCondition {
            regions(first: 10) {
              edges {
                node {
                  id
                  name
                }
              }
            }
          }
        }
        currencySettings {
          baseCurrency {
            currencyCode
          }
          localCurrencies
        }
      }
      userErrors {
        field
        message
        code
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "status": "DRAFT"
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
  "query": "mutation marketUpdate($input: MarketUpdateInput!) { marketUpdate(id: \"gid://shopify/Market/73827535\", input: $input) { market { id handle status conditions { regionsCondition { regions(first: 10) { edges { node { id name } } } } } currencySettings { baseCurrency { currencyCode } localCurrencies } } userErrors { field message code } } }",
   "variables": {
      "input": {
        "status": "DRAFT"
      }
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
    mutation marketUpdate($input: MarketUpdateInput!) {
      marketUpdate(id: "gid://shopify/Market/73827535", input: $input) {
        market {
          id
          handle
          status
          conditions {
            regionsCondition {
              regions(first: 10) {
                edges {
                  node {
                    id
                    name
                  }
                }
              }
            }
          }
          currencySettings {
            baseCurrency {
              currencyCode
            }
            localCurrencies
          }
        }
        userErrors {
          field
          message
          code
        }
      }
    }`,
    {
      variables: {
          "input": {
              "status": "DRAFT"
          }
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
    mutation marketUpdate($input: MarketUpdateInput!) {
      marketUpdate(id: "gid://shopify/Market/73827535", input: $input) {
        market {
          id
          handle
          status
          conditions {
            regionsCondition {
              regions(first: 10) {
                edges {
                  node {
                    id
                    name
                  }
                }
              }
            }
          }
          currencySettings {
            baseCurrency {
              currencyCode
            }
            localCurrencies
          }
        }
        userErrors {
          field
          message
          code
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "status": "DRAFT"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation marketUpdate($input: MarketUpdateInput!) {
        marketUpdate(id: "gid://shopify/Market/73827535", input: $input) {
          market {
            id
            handle
            status
            conditions {
              regionsCondition {
                regions(first: 10) {
                  edges {
                    node {
                      id
                      name
                    }
                  }
                }
              }
            }
            currencySettings {
              baseCurrency {
                currencyCode
              }
              localCurrencies
            }
          }
          userErrors {
            field
            message
            code
          }
        }
      }`,
      "variables": {
          "input": {
              "status": "DRAFT"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation marketUpdate($input: MarketUpdateInput!) {
    marketUpdate(id: "gid://shopify/Market/73827535", input: $input) {
      market {
        id
        handle
        status
        conditions {
          regionsCondition {
            regions(first: 10) {
              edges {
                node {
                  id
                  name
                }
              }
            }
          }
        }
        currencySettings {
          baseCurrency {
            currencyCode
          }
          localCurrencies
        }
      }
      userErrors {
        field
        message
        code
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "status": "DRAFT"
    }
  }'
  ```

  #### Response

  ```json
  {
    "marketUpdate": {
      "market": {
        "id": "gid://shopify/Market/73827535",
        "handle": "us",
        "status": "DRAFT",
        "conditions": {
          "regionsCondition": {
            "regions": {
              "edges": [
                {
                  "node": {
                    "id": "gid://shopify/MarketRegionCountry/397370199",
                    "name": "United States"
                  }
                }
              ]
            }
          }
        },
        "currencySettings": {
          "baseCurrency": {
            "currencyCode": "USD"
          },
          "localCurrencies": false
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Update a market to add a new catalog

  #### Description

  A market can have multiple catalogs. This example shows how to add a new catalog to a market.

  #### Query

  ```graphql
  mutation marketUpdate($input: MarketUpdateInput!) {
    marketUpdate(id: "gid://shopify/Market/73827535", input: $input) {
      market {
        id
        handle
        status
        conditions {
          regionsCondition {
            regions(first: 10) {
              edges {
                node {
                  id
                  name
                }
              }
            }
          }
        }
        catalogs(first: 10) {
          edges {
            node {
              id
            }
          }
        }
      }
      userErrors {
        field
        message
        code
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "catalogsToAdd": [
        "gid://shopify/Catalog/307400570"
      ]
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
  "query": "mutation marketUpdate($input: MarketUpdateInput!) { marketUpdate(id: \"gid://shopify/Market/73827535\", input: $input) { market { id handle status conditions { regionsCondition { regions(first: 10) { edges { node { id name } } } } } catalogs(first: 10) { edges { node { id } } } } userErrors { field message code } } }",
   "variables": {
      "input": {
        "catalogsToAdd": [
          "gid://shopify/Catalog/307400570"
        ]
      }
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
    mutation marketUpdate($input: MarketUpdateInput!) {
      marketUpdate(id: "gid://shopify/Market/73827535", input: $input) {
        market {
          id
          handle
          status
          conditions {
            regionsCondition {
              regions(first: 10) {
                edges {
                  node {
                    id
                    name
                  }
                }
              }
            }
          }
          catalogs(first: 10) {
            edges {
              node {
                id
              }
            }
          }
        }
        userErrors {
          field
          message
          code
        }
      }
    }`,
    {
      variables: {
          "input": {
              "catalogsToAdd": [
                  "gid://shopify/Catalog/307400570"
              ]
          }
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
    mutation marketUpdate($input: MarketUpdateInput!) {
      marketUpdate(id: "gid://shopify/Market/73827535", input: $input) {
        market {
          id
          handle
          status
          conditions {
            regionsCondition {
              regions(first: 10) {
                edges {
                  node {
                    id
                    name
                  }
                }
              }
            }
          }
          catalogs(first: 10) {
            edges {
              node {
                id
              }
            }
          }
        }
        userErrors {
          field
          message
          code
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "catalogsToAdd": [
        "gid://shopify/Catalog/307400570"
      ]
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation marketUpdate($input: MarketUpdateInput!) {
        marketUpdate(id: "gid://shopify/Market/73827535", input: $input) {
          market {
            id
            handle
            status
            conditions {
              regionsCondition {
                regions(first: 10) {
                  edges {
                    node {
                      id
                      name
                    }
                  }
                }
              }
            }
            catalogs(first: 10) {
              edges {
                node {
                  id
                }
              }
            }
          }
          userErrors {
            field
            message
            code
          }
        }
      }`,
      "variables": {
          "input": {
              "catalogsToAdd": [
                  "gid://shopify/Catalog/307400570"
              ]
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation marketUpdate($input: MarketUpdateInput!) {
    marketUpdate(id: "gid://shopify/Market/73827535", input: $input) {
      market {
        id
        handle
        status
        conditions {
          regionsCondition {
            regions(first: 10) {
              edges {
                node {
                  id
                  name
                }
              }
            }
          }
        }
        catalogs(first: 10) {
          edges {
            node {
              id
            }
          }
        }
      }
      userErrors {
        field
        message
        code
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "catalogsToAdd": [
        "gid://shopify/Catalog/307400570"
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "marketUpdate": {
      "market": {
        "id": "gid://shopify/Market/73827535",
        "handle": "us",
        "status": "ACTIVE",
        "conditions": {
          "regionsCondition": {
            "regions": {
              "edges": [
                {
                  "node": {
                    "id": "gid://shopify/MarketRegionCountry/397370199",
                    "name": "United States"
                  }
                }
              ]
            }
          }
        },
        "catalogs": {
          "edges": [
            {
              "node": {
                "id": "gid://shopify/MarketCatalog/73827535"
              }
            },
            {
              "node": {
                "id": "gid://shopify/MarketCatalog/307400570"
              }
            }
          ]
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Update a market to change its conditions

  #### Description

  A market's conditions can be updated to match different buyers. This example shows how to update a market to match buyers in Great Britain.

  #### Query

  ```graphql
  mutation marketUpdate($input: MarketUpdateInput!) {
    marketUpdate(id: "gid://shopify/Market/73827535", input: $input) {
      market {
        id
        handle
        status
        conditions {
          regionsCondition {
            regions(first: 10) {
              edges {
                node {
                  id
                  name
                }
              }
            }
          }
        }
        catalogs(first: 10) {
          edges {
            node {
              id
            }
          }
        }
      }
      userErrors {
        field
        message
        code
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "conditions": {
        "conditionsToAdd": {
          "regionsCondition": {
            "regions": [
              {
                "countryCode": "GB"
              }
            ]
          }
        },
        "conditionsToDelete": {
          "regionsCondition": {
            "regions": [
              {
                "countryCode": "US"
              }
            ]
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
  "query": "mutation marketUpdate($input: MarketUpdateInput!) { marketUpdate(id: \"gid://shopify/Market/73827535\", input: $input) { market { id handle status conditions { regionsCondition { regions(first: 10) { edges { node { id name } } } } } catalogs(first: 10) { edges { node { id } } } } userErrors { field message code } } }",
   "variables": {
      "input": {
        "conditions": {
          "conditionsToAdd": {
            "regionsCondition": {
              "regions": [
                {
                  "countryCode": "GB"
                }
              ]
            }
          },
          "conditionsToDelete": {
            "regionsCondition": {
              "regions": [
                {
                  "countryCode": "US"
                }
              ]
            }
          }
        }
      }
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
    mutation marketUpdate($input: MarketUpdateInput!) {
      marketUpdate(id: "gid://shopify/Market/73827535", input: $input) {
        market {
          id
          handle
          status
          conditions {
            regionsCondition {
              regions(first: 10) {
                edges {
                  node {
                    id
                    name
                  }
                }
              }
            }
          }
          catalogs(first: 10) {
            edges {
              node {
                id
              }
            }
          }
        }
        userErrors {
          field
          message
          code
        }
      }
    }`,
    {
      variables: {
          "input": {
              "conditions": {
                  "conditionsToAdd": {
                      "regionsCondition": {
                          "regions": [
                              {
                                  "countryCode": "GB"
                              }
                          ]
                      }
                  },
                  "conditionsToDelete": {
                      "regionsCondition": {
                          "regions": [
                              {
                                  "countryCode": "US"
                              }
                          ]
                      }
                  }
              }
          }
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
    mutation marketUpdate($input: MarketUpdateInput!) {
      marketUpdate(id: "gid://shopify/Market/73827535", input: $input) {
        market {
          id
          handle
          status
          conditions {
            regionsCondition {
              regions(first: 10) {
                edges {
                  node {
                    id
                    name
                  }
                }
              }
            }
          }
          catalogs(first: 10) {
            edges {
              node {
                id
              }
            }
          }
        }
        userErrors {
          field
          message
          code
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "conditions": {
        "conditionsToAdd": {
          "regionsCondition": {
            "regions": [
              {
                "countryCode": "GB"
              }
            ]
          }
        },
        "conditionsToDelete": {
          "regionsCondition": {
            "regions": [
              {
                "countryCode": "US"
              }
            ]
          }
        }
      }
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation marketUpdate($input: MarketUpdateInput!) {
        marketUpdate(id: "gid://shopify/Market/73827535", input: $input) {
          market {
            id
            handle
            status
            conditions {
              regionsCondition {
                regions(first: 10) {
                  edges {
                    node {
                      id
                      name
                    }
                  }
                }
              }
            }
            catalogs(first: 10) {
              edges {
                node {
                  id
                }
              }
            }
          }
          userErrors {
            field
            message
            code
          }
        }
      }`,
      "variables": {
          "input": {
              "conditions": {
                  "conditionsToAdd": {
                      "regionsCondition": {
                          "regions": [
                              {
                                  "countryCode": "GB"
                              }
                          ]
                      }
                  },
                  "conditionsToDelete": {
                      "regionsCondition": {
                          "regions": [
                              {
                                  "countryCode": "US"
                              }
                          ]
                      }
                  }
              }
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation marketUpdate($input: MarketUpdateInput!) {
    marketUpdate(id: "gid://shopify/Market/73827535", input: $input) {
      market {
        id
        handle
        status
        conditions {
          regionsCondition {
            regions(first: 10) {
              edges {
                node {
                  id
                  name
                }
              }
            }
          }
        }
        catalogs(first: 10) {
          edges {
            node {
              id
            }
          }
        }
      }
      userErrors {
        field
        message
        code
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "conditions": {
        "conditionsToAdd": {
          "regionsCondition": {
            "regions": [
              {
                "countryCode": "GB"
              }
            ]
          }
        },
        "conditionsToDelete": {
          "regionsCondition": {
            "regions": [
              {
                "countryCode": "US"
              }
            ]
          }
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "marketUpdate": {
      "market": {
        "id": "gid://shopify/Market/73827535",
        "handle": "us",
        "status": "ACTIVE",
        "conditions": {
          "regionsCondition": {
            "regions": {
              "edges": [
                {
                  "node": {
                    "id": "gid://shopify/MarketRegionCountry/1072830590",
                    "name": "United Kingdom"
                  }
                }
              ]
            }
          }
        },
        "catalogs": {
          "edges": [
            {
              "node": {
                "id": "gid://shopify/MarketCatalog/73827535"
              }
            }
          ]
        }
      },
      "userErrors": []
    }
  }
  ```

* ### marketUpdate reference
