---
title: marketCreate - GraphQL Admin
description: >-
  Creates a
  [`Market`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Market)
  to deliver customized shopping experiences. Markets define various aspects of
  the buyer experience including pricing, product availability, custom content,
  inventory and fulfillment priorities, and payment methods.


  Define conditions to match buyers by region, company location, retail
  location, or other criteria. Configure
  [`MarketCurrencySettings`](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketCurrencySettings)
  to control currency behavior. Set
  [`MarketPriceInclusions`](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketPriceInclusions)
  to determine tax and duty display. Assign
  [`Catalog`](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/Catalog)
  objects and
  [`MarketWebPresence`](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketWebPresence)
  configurations to control product availability and SEO strategy.


  Learn more about [Shopify
  Markets](https://shopify.dev/docs/apps/build/markets).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/marketCreate'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/marketCreate.md'
---

# market​Create

mutation

Requires `read_markets` for queries and both `read_markets` as well as `write_markets` for mutations.

Creates a [`Market`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Market) to deliver customized shopping experiences. Markets define various aspects of the buyer experience including pricing, product availability, custom content, inventory and fulfillment priorities, and payment methods.

Define conditions to match buyers by region, company location, retail location, or other criteria. Configure [`MarketCurrencySettings`](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketCurrencySettings) to control currency behavior. Set [`MarketPriceInclusions`](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketPriceInclusions) to determine tax and duty display. Assign [`Catalog`](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/Catalog) objects and [`MarketWebPresence`](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketWebPresence) configurations to control product availability and SEO strategy.

Learn more about [Shopify Markets](https://shopify.dev/docs/apps/build/markets).

## Arguments

* input

  [Market​Create​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/MarketCreateInput)

  required

  The properties of the new market.

***

## Market​Create​Payload returns

* market

  [Market](https://shopify.dev/docs/api/admin-graphql/latest/objects/Market)

  The market object.

* user​Errors

  [\[Market​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create a B2B market for all company locations located in the United States

  #### Description

  Create a B2B market for all company locations located in the United States. The market includes all existing and future company locations located in the United States. This market type is currently only available in the dev preview.

  #### Query

  ```graphql
  mutation marketCreate($input: MarketCreateInput!) {
    marketCreate(input: $input) {
      market {
        id
        handle
        status
        conditions {
          companyLocationsCondition {
            companyLocations(first: 10) {
              edges {
                node {
                  id
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
      "name": "Company Location Market",
      "handle": "Company-Location",
      "enabled": true,
      "conditions": {
        "regionsCondition": {
          "regions": [
            {
              "countryCode": "US"
            }
          ]
        },
        "companyLocationsCondition": {
          "applicationLevel": "ALL"
        }
      },
      "currencySettings": {
        "baseCurrency": "USD",
        "localCurrencies": false
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
  "query": "mutation marketCreate($input: MarketCreateInput!) { marketCreate(input: $input) { market { id handle status conditions { companyLocationsCondition { companyLocations(first: 10) { edges { node { id } } } } } currencySettings { baseCurrency { currencyCode } localCurrencies } } userErrors { field message code } } }",
   "variables": {
      "input": {
        "name": "Company Location Market",
        "handle": "Company-Location",
        "enabled": true,
        "conditions": {
          "regionsCondition": {
            "regions": [
              {
                "countryCode": "US"
              }
            ]
          },
          "companyLocationsCondition": {
            "applicationLevel": "ALL"
          }
        },
        "currencySettings": {
          "baseCurrency": "USD",
          "localCurrencies": false
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
    mutation marketCreate($input: MarketCreateInput!) {
      marketCreate(input: $input) {
        market {
          id
          handle
          status
          conditions {
            companyLocationsCondition {
              companyLocations(first: 10) {
                edges {
                  node {
                    id
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
              "name": "Company Location Market",
              "handle": "Company-Location",
              "enabled": true,
              "conditions": {
                  "regionsCondition": {
                      "regions": [
                          {
                              "countryCode": "US"
                          }
                      ]
                  },
                  "companyLocationsCondition": {
                      "applicationLevel": "ALL"
                  }
              },
              "currencySettings": {
                  "baseCurrency": "USD",
                  "localCurrencies": false
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
    mutation marketCreate($input: MarketCreateInput!) {
      marketCreate(input: $input) {
        market {
          id
          handle
          status
          conditions {
            companyLocationsCondition {
              companyLocations(first: 10) {
                edges {
                  node {
                    id
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
      "name": "Company Location Market",
      "handle": "Company-Location",
      "enabled": true,
      "conditions": {
        "regionsCondition": {
          "regions": [
            {
              "countryCode": "US"
            }
          ]
        },
        "companyLocationsCondition": {
          "applicationLevel": "ALL"
        }
      },
      "currencySettings": {
        "baseCurrency": "USD",
        "localCurrencies": false
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
      "query": `mutation marketCreate($input: MarketCreateInput!) {
        marketCreate(input: $input) {
          market {
            id
            handle
            status
            conditions {
              companyLocationsCondition {
                companyLocations(first: 10) {
                  edges {
                    node {
                      id
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
              "name": "Company Location Market",
              "handle": "Company-Location",
              "enabled": true,
              "conditions": {
                  "regionsCondition": {
                      "regions": [
                          {
                              "countryCode": "US"
                          }
                      ]
                  },
                  "companyLocationsCondition": {
                      "applicationLevel": "ALL"
                  }
              },
              "currencySettings": {
                  "baseCurrency": "USD",
                  "localCurrencies": false
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
  'mutation marketCreate($input: MarketCreateInput!) {
    marketCreate(input: $input) {
      market {
        id
        handle
        status
        conditions {
          companyLocationsCondition {
            companyLocations(first: 10) {
              edges {
                node {
                  id
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
      "name": "Company Location Market",
      "handle": "Company-Location",
      "enabled": true,
      "conditions": {
        "regionsCondition": {
          "regions": [
            {
              "countryCode": "US"
            }
          ]
        },
        "companyLocationsCondition": {
          "applicationLevel": "ALL"
        }
      },
      "currencySettings": {
        "baseCurrency": "USD",
        "localCurrencies": false
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "marketCreate": {
      "market": {
        "id": "gid://shopify/Market/1068177656",
        "handle": "company-location",
        "status": "ACTIVE",
        "conditions": {
          "companyLocationsCondition": {
            "companyLocations": {
              "edges": []
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

* ### Create a B2B market with a specific currency and price inclusions

  #### Description

  Create a B2B market for a specific company location with a specific currency and price inclusions. This market type is currently only available in the dev preview.

  #### Query

  ```graphql
  mutation marketCreate($input: MarketCreateInput!) {
    marketCreate(input: $input) {
      market {
        id
        handle
        status
        conditions {
          companyLocationsCondition {
            companyLocations(first: 10) {
              edges {
                node {
                  id
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
      "name": "Company Location Market",
      "handle": "company-location-market",
      "enabled": true,
      "conditions": {
        "companyLocationsCondition": {
          "companyLocationIds": [
            "gid://shopify/CompanyLocation/423757199"
          ]
        }
      },
      "currencySettings": {
        "baseCurrency": "USD",
        "localCurrencies": false
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
  "query": "mutation marketCreate($input: MarketCreateInput!) { marketCreate(input: $input) { market { id handle status conditions { companyLocationsCondition { companyLocations(first: 10) { edges { node { id } } } } } currencySettings { baseCurrency { currencyCode } localCurrencies } } userErrors { field message code } } }",
   "variables": {
      "input": {
        "name": "Company Location Market",
        "handle": "company-location-market",
        "enabled": true,
        "conditions": {
          "companyLocationsCondition": {
            "companyLocationIds": [
              "gid://shopify/CompanyLocation/423757199"
            ]
          }
        },
        "currencySettings": {
          "baseCurrency": "USD",
          "localCurrencies": false
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
    mutation marketCreate($input: MarketCreateInput!) {
      marketCreate(input: $input) {
        market {
          id
          handle
          status
          conditions {
            companyLocationsCondition {
              companyLocations(first: 10) {
                edges {
                  node {
                    id
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
              "name": "Company Location Market",
              "handle": "company-location-market",
              "enabled": true,
              "conditions": {
                  "companyLocationsCondition": {
                      "companyLocationIds": [
                          "gid://shopify/CompanyLocation/423757199"
                      ]
                  }
              },
              "currencySettings": {
                  "baseCurrency": "USD",
                  "localCurrencies": false
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
    mutation marketCreate($input: MarketCreateInput!) {
      marketCreate(input: $input) {
        market {
          id
          handle
          status
          conditions {
            companyLocationsCondition {
              companyLocations(first: 10) {
                edges {
                  node {
                    id
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
      "name": "Company Location Market",
      "handle": "company-location-market",
      "enabled": true,
      "conditions": {
        "companyLocationsCondition": {
          "companyLocationIds": [
            "gid://shopify/CompanyLocation/423757199"
          ]
        }
      },
      "currencySettings": {
        "baseCurrency": "USD",
        "localCurrencies": false
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
      "query": `mutation marketCreate($input: MarketCreateInput!) {
        marketCreate(input: $input) {
          market {
            id
            handle
            status
            conditions {
              companyLocationsCondition {
                companyLocations(first: 10) {
                  edges {
                    node {
                      id
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
              "name": "Company Location Market",
              "handle": "company-location-market",
              "enabled": true,
              "conditions": {
                  "companyLocationsCondition": {
                      "companyLocationIds": [
                          "gid://shopify/CompanyLocation/423757199"
                      ]
                  }
              },
              "currencySettings": {
                  "baseCurrency": "USD",
                  "localCurrencies": false
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
  'mutation marketCreate($input: MarketCreateInput!) {
    marketCreate(input: $input) {
      market {
        id
        handle
        status
        conditions {
          companyLocationsCondition {
            companyLocations(first: 10) {
              edges {
                node {
                  id
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
      "name": "Company Location Market",
      "handle": "company-location-market",
      "enabled": true,
      "conditions": {
        "companyLocationsCondition": {
          "companyLocationIds": [
            "gid://shopify/CompanyLocation/423757199"
          ]
        }
      },
      "currencySettings": {
        "baseCurrency": "USD",
        "localCurrencies": false
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "marketCreate": {
      "market": {
        "id": "gid://shopify/Market/1068177655",
        "handle": "company-location-market",
        "status": "ACTIVE",
        "conditions": {
          "companyLocationsCondition": {
            "companyLocations": {
              "edges": [
                {
                  "node": {
                    "id": "gid://shopify/CompanyLocation/423757199"
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

* ### Create a North America market with a catalog and web presences

  #### Description

  Create a region market matching buyers located in the United States, Canada, and Mexico.

  #### Query

  ```graphql
  mutation marketCreate($input: MarketCreateInput!) {
    marketCreate(input: $input) {
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
        webPresences(first: 10) {
          edges {
            node {
              domain {
                id
              }
              subfolderSuffix
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
      "name": "North America Market",
      "handle": "NA",
      "enabled": true,
      "conditions": {
        "regionsCondition": {
          "regions": [
            {
              "countryCode": "US"
            },
            {
              "countryCode": "CA"
            },
            {
              "countryCode": "MX"
            }
          ]
        }
      },
      "catalogs": [
        "gid://shopify/Catalog/307400570"
      ],
      "webPresences": [
        "gid://shopify/MarketWebPresence/1068177655"
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
  "query": "mutation marketCreate($input: MarketCreateInput!) { marketCreate(input: $input) { market { id handle status conditions { regionsCondition { regions(first: 10) { edges { node { id name } } } } } catalogs(first: 10) { edges { node { id } } } webPresences(first: 10) { edges { node { domain { id } subfolderSuffix } } } } userErrors { field message code } } }",
   "variables": {
      "input": {
        "name": "North America Market",
        "handle": "NA",
        "enabled": true,
        "conditions": {
          "regionsCondition": {
            "regions": [
              {
                "countryCode": "US"
              },
              {
                "countryCode": "CA"
              },
              {
                "countryCode": "MX"
              }
            ]
          }
        },
        "catalogs": [
          "gid://shopify/Catalog/307400570"
        ],
        "webPresences": [
          "gid://shopify/MarketWebPresence/1068177655"
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
    mutation marketCreate($input: MarketCreateInput!) {
      marketCreate(input: $input) {
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
          webPresences(first: 10) {
            edges {
              node {
                domain {
                  id
                }
                subfolderSuffix
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
              "name": "North America Market",
              "handle": "NA",
              "enabled": true,
              "conditions": {
                  "regionsCondition": {
                      "regions": [
                          {
                              "countryCode": "US"
                          },
                          {
                              "countryCode": "CA"
                          },
                          {
                              "countryCode": "MX"
                          }
                      ]
                  }
              },
              "catalogs": [
                  "gid://shopify/Catalog/307400570"
              ],
              "webPresences": [
                  "gid://shopify/MarketWebPresence/1068177655"
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
    mutation marketCreate($input: MarketCreateInput!) {
      marketCreate(input: $input) {
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
          webPresences(first: 10) {
            edges {
              node {
                domain {
                  id
                }
                subfolderSuffix
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
      "name": "North America Market",
      "handle": "NA",
      "enabled": true,
      "conditions": {
        "regionsCondition": {
          "regions": [
            {
              "countryCode": "US"
            },
            {
              "countryCode": "CA"
            },
            {
              "countryCode": "MX"
            }
          ]
        }
      },
      "catalogs": [
        "gid://shopify/Catalog/307400570"
      ],
      "webPresences": [
        "gid://shopify/MarketWebPresence/1068177655"
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
      "query": `mutation marketCreate($input: MarketCreateInput!) {
        marketCreate(input: $input) {
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
            webPresences(first: 10) {
              edges {
                node {
                  domain {
                    id
                  }
                  subfolderSuffix
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
              "name": "North America Market",
              "handle": "NA",
              "enabled": true,
              "conditions": {
                  "regionsCondition": {
                      "regions": [
                          {
                              "countryCode": "US"
                          },
                          {
                              "countryCode": "CA"
                          },
                          {
                              "countryCode": "MX"
                          }
                      ]
                  }
              },
              "catalogs": [
                  "gid://shopify/Catalog/307400570"
              ],
              "webPresences": [
                  "gid://shopify/MarketWebPresence/1068177655"
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
  'mutation marketCreate($input: MarketCreateInput!) {
    marketCreate(input: $input) {
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
        webPresences(first: 10) {
          edges {
            node {
              domain {
                id
              }
              subfolderSuffix
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
      "name": "North America Market",
      "handle": "NA",
      "enabled": true,
      "conditions": {
        "regionsCondition": {
          "regions": [
            {
              "countryCode": "US"
            },
            {
              "countryCode": "CA"
            },
            {
              "countryCode": "MX"
            }
          ]
        }
      },
      "catalogs": [
        "gid://shopify/Catalog/307400570"
      ],
      "webPresences": [
        "gid://shopify/MarketWebPresence/1068177655"
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "marketCreate": {
      "market": {
        "id": "gid://shopify/Market/1068177654",
        "handle": "na",
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
                },
                {
                  "node": {
                    "id": "gid://shopify/MarketRegionCountry/948873163",
                    "name": "Canada"
                  }
                },
                {
                  "node": {
                    "id": "gid://shopify/MarketRegionCountry/1072830589",
                    "name": "Mexico"
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
                "id": "gid://shopify/MarketCatalog/307400570"
              }
            }
          ]
        },
        "webPresences": {
          "edges": [
            {
              "node": {
                "domain": {
                  "id": "gid://shopify/Domain/1071590560"
                },
                "subfolderSuffix": null
              }
            }
          ]
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Create a POS market for all locations

  #### Description

  Create a POS market for all locations. The market includes all existing and future locations. This market type is currently only available in the dev preview.

  #### Query

  ```graphql
  mutation marketCreate($input: MarketCreateInput!) {
    marketCreate(input: $input) {
      market {
        id
        handle
        status
        conditions {
          locationsCondition {
            locations(first: 10) {
              edges {
                node {
                  id
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
      "name": "All POS Market",
      "handle": "all-pos-market",
      "enabled": true,
      "conditions": {
        "regionsCondition": {
          "regions": [
            {
              "countryCode": "US"
            }
          ]
        },
        "locationsCondition": {
          "applicationLevel": "ALL"
        }
      },
      "currencySettings": {
        "baseCurrency": "USD",
        "localCurrencies": false
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
  "query": "mutation marketCreate($input: MarketCreateInput!) { marketCreate(input: $input) { market { id handle status conditions { locationsCondition { locations(first: 10) { edges { node { id } } } } } currencySettings { baseCurrency { currencyCode } localCurrencies } } userErrors { field message code } } }",
   "variables": {
      "input": {
        "name": "All POS Market",
        "handle": "all-pos-market",
        "enabled": true,
        "conditions": {
          "regionsCondition": {
            "regions": [
              {
                "countryCode": "US"
              }
            ]
          },
          "locationsCondition": {
            "applicationLevel": "ALL"
          }
        },
        "currencySettings": {
          "baseCurrency": "USD",
          "localCurrencies": false
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
    mutation marketCreate($input: MarketCreateInput!) {
      marketCreate(input: $input) {
        market {
          id
          handle
          status
          conditions {
            locationsCondition {
              locations(first: 10) {
                edges {
                  node {
                    id
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
              "name": "All POS Market",
              "handle": "all-pos-market",
              "enabled": true,
              "conditions": {
                  "regionsCondition": {
                      "regions": [
                          {
                              "countryCode": "US"
                          }
                      ]
                  },
                  "locationsCondition": {
                      "applicationLevel": "ALL"
                  }
              },
              "currencySettings": {
                  "baseCurrency": "USD",
                  "localCurrencies": false
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
    mutation marketCreate($input: MarketCreateInput!) {
      marketCreate(input: $input) {
        market {
          id
          handle
          status
          conditions {
            locationsCondition {
              locations(first: 10) {
                edges {
                  node {
                    id
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
      "name": "All POS Market",
      "handle": "all-pos-market",
      "enabled": true,
      "conditions": {
        "regionsCondition": {
          "regions": [
            {
              "countryCode": "US"
            }
          ]
        },
        "locationsCondition": {
          "applicationLevel": "ALL"
        }
      },
      "currencySettings": {
        "baseCurrency": "USD",
        "localCurrencies": false
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
      "query": `mutation marketCreate($input: MarketCreateInput!) {
        marketCreate(input: $input) {
          market {
            id
            handle
            status
            conditions {
              locationsCondition {
                locations(first: 10) {
                  edges {
                    node {
                      id
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
              "name": "All POS Market",
              "handle": "all-pos-market",
              "enabled": true,
              "conditions": {
                  "regionsCondition": {
                      "regions": [
                          {
                              "countryCode": "US"
                          }
                      ]
                  },
                  "locationsCondition": {
                      "applicationLevel": "ALL"
                  }
              },
              "currencySettings": {
                  "baseCurrency": "USD",
                  "localCurrencies": false
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
  'mutation marketCreate($input: MarketCreateInput!) {
    marketCreate(input: $input) {
      market {
        id
        handle
        status
        conditions {
          locationsCondition {
            locations(first: 10) {
              edges {
                node {
                  id
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
      "name": "All POS Market",
      "handle": "all-pos-market",
      "enabled": true,
      "conditions": {
        "regionsCondition": {
          "regions": [
            {
              "countryCode": "US"
            }
          ]
        },
        "locationsCondition": {
          "applicationLevel": "ALL"
        }
      },
      "currencySettings": {
        "baseCurrency": "USD",
        "localCurrencies": false
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "marketCreate": {
      "market": {
        "id": "gid://shopify/Market/1068177657",
        "handle": "all-pos-market",
        "status": "ACTIVE",
        "conditions": {
          "locationsCondition": {
            "locations": {
              "edges": []
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

* ### marketCreate reference
