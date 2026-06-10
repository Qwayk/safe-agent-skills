---
title: catalogCreate - GraphQL Admin
description: >-
  Creates a
  [`Catalog`](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/Catalog)
  that controls product availability and pricing for specific contexts like
  [markets](https://shopify.dev/docs/api/admin-graphql/latest/objects/Market) or
  B2B [company
  locations](https://shopify.dev/docs/api/admin-graphql/latest/objects/CompanyLocation).


  ### Publications and Price Lists


  -
  **[`Publication`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Publication)**
  objects control which products are visible in a catalog. Publications are
  **optional**. When a publication isn't associated with a catalog, product
  availability is determined by the sales channel.

  -
  **[`PriceList`](https://shopify.dev/docs/api/admin-graphql/latest/objects/PriceList)**
  objects define custom pricing for products in a catalog.


  You can optionally associate a publication and price list when creating the
  catalog, or add them later using separate mutations.


  ### When to use Publications


  **Create a publication only if you need to:**

  - Limit which products are visible in a specific context (e.g., show different
  products to different company locations or markets)

  - Publish a curated subset of your product catalog


  **Do NOT create a publication if:**

  - You want product availability determined by the sales channel

  - You only need to customize pricing (use a price list without a publication)


  > **Important:** For company location catalogs that only require custom
  pricing, create the catalog with a price list but without a publication.


  Learn more about [managing catalog
  contexts](https://shopify.dev/docs/apps/build/markets/new-markets/catalogs)
  and [using catalogs for different
  markets](https://shopify.dev/docs/apps/build/markets/catalogs-different-markets).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/catalogCreate'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/catalogCreate.md'
---

# catalog​Create

mutation

Requires `write_products` access scope. Also: The user must have permission to create and edit catalogs.

Creates a [`Catalog`](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/Catalog) that controls product availability and pricing for specific contexts like [markets](https://shopify.dev/docs/api/admin-graphql/latest/objects/Market) or B2B [company locations](https://shopify.dev/docs/api/admin-graphql/latest/objects/CompanyLocation).

### Publications and Price Lists

* **[`Publication`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Publication)** objects control which products are visible in a catalog. Publications are **optional**. When a publication isn't associated with a catalog, product availability is determined by the sales channel.
* **[`PriceList`](https://shopify.dev/docs/api/admin-graphql/latest/objects/PriceList)** objects define custom pricing for products in a catalog.

You can optionally associate a publication and price list when creating the catalog, or add them later using separate mutations.

### When to use Publications

**Create a publication only if you need to:**

* Limit which products are visible in a specific context (e.g., show different products to different company locations or markets)
* Publish a curated subset of your product catalog

**Do NOT create a publication if:**

* You want product availability determined by the sales channel
* You only need to customize pricing (use a price list without a publication)

> **Important:** For company location catalogs that only require custom pricing, create the catalog with a price list but without a publication.

Learn more about [managing catalog contexts](https://shopify.dev/docs/apps/build/markets/new-markets/catalogs) and [using catalogs for different markets](https://shopify.dev/docs/apps/build/markets/catalogs-different-markets).

## Arguments

* input

  [Catalog​Create​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/CatalogCreateInput)

  required

  The properties of the new catalog.

***

## Catalog​Create​Payload returns

* catalog

  [Catalog](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/Catalog)

  The newly created catalog.

* user​Errors

  [\[Catalog​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CatalogUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create a catalog with a publication

  #### Query

  ```graphql
  mutation catalogCreate($input: CatalogCreateInput!) {
    catalogCreate(input: $input) {
      catalog {
        id
        status
        title
        publication {
          id
          autoPublish
        }
        priceList {
          id
          currency
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
    "input": {
      "title": "Market Catalog",
      "status": "ACTIVE",
      "context": {
        "marketIds": [
          "gid://shopify/Market/128989799"
        ]
      },
      "priceListId": "gid://shopify/PriceList/294167858",
      "publicationId": "gid://shopify/Publication/1056839876"
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
  "query": "mutation catalogCreate($input: CatalogCreateInput!) { catalogCreate(input: $input) { catalog { id status title publication { id autoPublish } priceList { id currency } } userErrors { field message } } }",
   "variables": {
      "input": {
        "title": "Market Catalog",
        "status": "ACTIVE",
        "context": {
          "marketIds": [
            "gid://shopify/Market/128989799"
          ]
        },
        "priceListId": "gid://shopify/PriceList/294167858",
        "publicationId": "gid://shopify/Publication/1056839876"
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
    mutation catalogCreate($input: CatalogCreateInput!) {
      catalogCreate(input: $input) {
        catalog {
          id
          status
          title
          publication {
            id
            autoPublish
          }
          priceList {
            id
            currency
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
          "input": {
              "title": "Market Catalog",
              "status": "ACTIVE",
              "context": {
                  "marketIds": [
                      "gid://shopify/Market/128989799"
                  ]
              },
              "priceListId": "gid://shopify/PriceList/294167858",
              "publicationId": "gid://shopify/Publication/1056839876"
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
    mutation catalogCreate($input: CatalogCreateInput!) {
      catalogCreate(input: $input) {
        catalog {
          id
          status
          title
          publication {
            id
            autoPublish
          }
          priceList {
            id
            currency
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
    "input": {
      "title": "Market Catalog",
      "status": "ACTIVE",
      "context": {
        "marketIds": [
          "gid://shopify/Market/128989799"
        ]
      },
      "priceListId": "gid://shopify/PriceList/294167858",
      "publicationId": "gid://shopify/Publication/1056839876"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation catalogCreate($input: CatalogCreateInput!) {
        catalogCreate(input: $input) {
          catalog {
            id
            status
            title
            publication {
              id
              autoPublish
            }
            priceList {
              id
              currency
            }
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "input": {
              "title": "Market Catalog",
              "status": "ACTIVE",
              "context": {
                  "marketIds": [
                      "gid://shopify/Market/128989799"
                  ]
              },
              "priceListId": "gid://shopify/PriceList/294167858",
              "publicationId": "gid://shopify/Publication/1056839876"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation catalogCreate($input: CatalogCreateInput!) {
    catalogCreate(input: $input) {
      catalog {
        id
        status
        title
        publication {
          id
          autoPublish
        }
        priceList {
          id
          currency
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
    "input": {
      "title": "Market Catalog",
      "status": "ACTIVE",
      "context": {
        "marketIds": [
          "gid://shopify/Market/128989799"
        ]
      },
      "priceListId": "gid://shopify/PriceList/294167858",
      "publicationId": "gid://shopify/Publication/1056839876"
    }
  }'
  ```

  #### Response

  ```json
  {
    "catalogCreate": {
      "catalog": {
        "id": "gid://shopify/MarketCatalog/1068177653",
        "status": "ACTIVE",
        "title": "Market Catalog",
        "publication": {
          "id": "gid://shopify/Publication/1056839876",
          "autoPublish": false
        },
        "priceList": {
          "id": "gid://shopify/PriceList/294167858",
          "currency": "USD"
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Create a pricing-only catalog

  #### Description

  Create a \[pricing-only catalog]\(https://shopify.dev/docs/apps/build/markets/catalogs-different-markets#pricing-only-catalogs).

  #### Query

  ```graphql
  mutation catalogCreate($input: CatalogCreateInput!) {
    catalogCreate(input: $input) {
      catalog {
        id
        status
        title
        priceList {
          id
          currency
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
    "input": {
      "title": "Pricing Only Catalog",
      "status": "DRAFT",
      "context": {
        "marketIds": [
          "gid://shopify/Market/1054177655"
        ]
      },
      "priceListId": "gid://shopify/PriceList/294167858"
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
  "query": "mutation catalogCreate($input: CatalogCreateInput!) { catalogCreate(input: $input) { catalog { id status title priceList { id currency } } userErrors { field message } } }",
   "variables": {
      "input": {
        "title": "Pricing Only Catalog",
        "status": "DRAFT",
        "context": {
          "marketIds": [
            "gid://shopify/Market/1054177655"
          ]
        },
        "priceListId": "gid://shopify/PriceList/294167858"
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
    mutation catalogCreate($input: CatalogCreateInput!) {
      catalogCreate(input: $input) {
        catalog {
          id
          status
          title
          priceList {
            id
            currency
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
          "input": {
              "title": "Pricing Only Catalog",
              "status": "DRAFT",
              "context": {
                  "marketIds": [
                      "gid://shopify/Market/1054177655"
                  ]
              },
              "priceListId": "gid://shopify/PriceList/294167858"
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
    mutation catalogCreate($input: CatalogCreateInput!) {
      catalogCreate(input: $input) {
        catalog {
          id
          status
          title
          priceList {
            id
            currency
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
    "input": {
      "title": "Pricing Only Catalog",
      "status": "DRAFT",
      "context": {
        "marketIds": [
          "gid://shopify/Market/1054177655"
        ]
      },
      "priceListId": "gid://shopify/PriceList/294167858"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation catalogCreate($input: CatalogCreateInput!) {
        catalogCreate(input: $input) {
          catalog {
            id
            status
            title
            priceList {
              id
              currency
            }
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "input": {
              "title": "Pricing Only Catalog",
              "status": "DRAFT",
              "context": {
                  "marketIds": [
                      "gid://shopify/Market/1054177655"
                  ]
              },
              "priceListId": "gid://shopify/PriceList/294167858"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation catalogCreate($input: CatalogCreateInput!) {
    catalogCreate(input: $input) {
      catalog {
        id
        status
        title
        priceList {
          id
          currency
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
    "input": {
      "title": "Pricing Only Catalog",
      "status": "DRAFT",
      "context": {
        "marketIds": [
          "gid://shopify/Market/1054177655"
        ]
      },
      "priceListId": "gid://shopify/PriceList/294167858"
    }
  }'
  ```

  #### Response

  ```json
  {
    "catalogCreate": {
      "catalog": {
        "id": "gid://shopify/MarketCatalog/1068177654",
        "status": "DRAFT",
        "title": "Pricing Only Catalog",
        "priceList": {
          "id": "gid://shopify/PriceList/294167858",
          "currency": "USD"
        }
      },
      "userErrors": []
    }
  }
  ```

* ### catalogCreate reference
