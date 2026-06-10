---
title: domain - GraphQL Admin
description: Returns a `Domain` resource by ID.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/domain'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/domain.md'
---

# domain

query

Returns a `Domain` resource by ID.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the `Domain` to return.

***

## Possible returns

* Domain

  [Domain](https://shopify.dev/docs/api/admin-graphql/latest/objects/Domain)

  A unique string that represents the address of a Shopify store on the Internet.

  * host

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The host name of the domain. For example, `example.com`.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * localization

    [Domain​Localization](https://shopify.dev/docs/api/admin-graphql/latest/objects/DomainLocalization)

    The localization of the domain, if the domain doesn't redirect.

  * market​Web​Presence

    [Market​Web​Presence](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketWebPresence)

    The web presence of the domain.

  * ssl​Enabled

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether SSL is enabled.

  * url

    [URL!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/URL)

    non-null

    The URL of the domain (for example, `https://example.com`).

***

## Examples

* ### Retrieve a domain by ID

  #### Description

  Retrieve information about a domain by its ID.

  #### Query

  ```graphql
  query {
    domain(id: "gid://shopify/Domain/948873163") {
      host
      url
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
  "query": "query { domain(id: \"gid://shopify/Domain/948873163\") { host url } }"
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
      domain(id: "gid://shopify/Domain/948873163") {
        host
        url
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
      domain(id: "gid://shopify/Domain/948873163") {
        host
        url
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
      domain(id: "gid://shopify/Domain/948873163") {
        host
        url
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    domain(id: "gid://shopify/Domain/948873163") {
      host
      url
    }
  }'
  ```

  #### Response

  ```json
  {
    "domain": {
      "host": "www.snowdevil.ca",
      "url": "https://www.snowdevil.ca"
    }
  }
  ```

* ### Retrieve information about a shop's domains

  #### Description

  The following query retrieves information for the domain names associated with the shop.

  #### Query

  ```graphql
  query {
    shop {
      domains {
        id
        host
        url
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
  "query": "query { shop { domains { id host url } } }"
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
      shop {
        domains {
          id
          host
          url
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
      shop {
        domains {
          id
          host
          url
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
      shop {
        domains {
          id
          host
          url
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
    shop {
      domains {
        id
        host
        url
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "shop": {
      "domains": [
        {
          "id": "gid://shopify/Domain/26371970",
          "host": "snowdevil.myshopify.com",
          "url": "https://snowdevil.myshopify.com"
        },
        {
          "id": "gid://shopify/Domain/948873163",
          "host": "www.snowdevil.ca",
          "url": "https://www.snowdevil.ca"
        }
      ]
    }
  }
  ```
