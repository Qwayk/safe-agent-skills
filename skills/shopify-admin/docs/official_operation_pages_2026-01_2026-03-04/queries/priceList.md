---
title: priceList - GraphQL Admin
description: >-
  Returns a
  [`PriceList`](https://shopify.dev/docs/api/admin-graphql/latest/objects/PriceList)
  by ID. You can use price lists to specify either fixed prices or adjusted
  relative prices that override initial
  [`Product`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product)
  prices.


  Price lists enable contextual pricing for the
  [`Catalog`](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/Catalog)
  they are associated to. Each price list can define fixed prices for specific
  [`ProductVariant`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant)
  objects or percentage-based adjustments relative to other prices.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/priceList'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/priceList.md'
---

# price​List

query

Returns a [`PriceList`](https://shopify.dev/docs/api/admin-graphql/latest/objects/PriceList) by ID. You can use price lists to specify either fixed prices or adjusted relative prices that override initial [`Product`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product) prices.

Price lists enable contextual pricing for the [`Catalog`](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/Catalog) they are associated to. Each price list can define fixed prices for specific [`ProductVariant`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant) objects or percentage-based adjustments relative to other prices.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the `PriceList` to return.

***

## Possible returns

* Price​List

  [Price​List](https://shopify.dev/docs/api/admin-graphql/latest/objects/PriceList)

  A list that defines pricing for [product variants](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant). Price lists override default product prices with either fixed prices or percentage-based adjustments.

  Each price list associates with a [`Catalog`](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/Catalog) to determine which customers see the pricing. The catalog's context rules control when the price list applies, such as for specific markets, company locations, or apps.

  Learn how to [support different pricing models](https://shopify.dev/docs/apps/build/markets/build-catalog).

  * catalog

    [Catalog](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/Catalog)

    The catalog that the price list is associated with.

  * currency

    [Currency​Code!](https://shopify.dev/docs/api/admin-graphql/latest/enums/CurrencyCode)

    non-null

    The currency for fixed prices associated with this price list.

  * fixed​Prices​Count

    [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    non-null

    The number of fixed prices on the price list.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * name

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The unique name of the price list, used as a human-readable identifier.

  * parent

    [Price​List​Parent](https://shopify.dev/docs/api/admin-graphql/latest/objects/PriceListParent)

    Relative adjustments to other prices.

  * prices

    [Price​List​Price​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/PriceListPriceConnection)

    non-null

    A list of prices associated with the price list.

    * origin​Type

      [Price​List​Price​Origin​Type](https://shopify.dev/docs/api/admin-graphql/latest/enums/PriceListPriceOriginType)

      ### Arguments

      The origin of this price, either fixed (defined on the price list) or relative (calculated using an adjustment via a price list parent configuration).

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

    * query

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      A filter made up of terms, connectives, modifiers, and comparators. You can apply one or more filters to a query. Learn more about [Shopify API search syntax](https://shopify.dev/api/usage/search-syntax).

      * * id

          id

        * product\_id

          id

        - Filter by `id` range.

        - Example:
          * `id:1234`
          * `id:>=1234`
          * `id:<=1234`

      * variant\_id

        id

    ***

  * quantity​Rules

    [Quantity​Rule​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/QuantityRuleConnection)

    non-null

    A list of quantity rules associated with the price list, ordered by product variants.

    * origin​Type

      [Quantity​Rule​Origin​Type](https://shopify.dev/docs/api/admin-graphql/latest/enums/QuantityRuleOriginType)

      ### Arguments

      Whether the quantity rule is fixed (defined on the price list) or relative (the default quantity rule for the shop).

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

***

## Examples

* ### Retrieve Price List Details and Associated Catalog Information

  #### Description

  Retrieves the price list's catalog title. Fetches the currency used in the price list and details about the parent's adjustment type and value.

  #### Query

  ```graphql
  query {
    priceList(id: "gid://shopify/PriceList/524058083") {
      catalog {
        id
        title
      }
      prices(first: 5, query: "product_id:20995642") {
        nodes {
          price {
            amount
            currencyCode
          }
          variant {
            id
          }
        }
      }
      currency
      parent {
        adjustment {
          type
          value
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
  "query": "query { priceList(id: \"gid://shopify/PriceList/524058083\") { catalog { id title } prices(first: 5, query: \"product_id:20995642\") { nodes { price { amount currencyCode } variant { id } } } currency parent { adjustment { type value } } } }"
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
      priceList(id: "gid://shopify/PriceList/524058083") {
        catalog {
          id
          title
        }
        prices(first: 5, query: "product_id:20995642") {
          nodes {
            price {
              amount
              currencyCode
            }
            variant {
              id
            }
          }
        }
        currency
        parent {
          adjustment {
            type
            value
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
      priceList(id: "gid://shopify/PriceList/524058083") {
        catalog {
          id
          title
        }
        prices(first: 5, query: "product_id:20995642") {
          nodes {
            price {
              amount
              currencyCode
            }
            variant {
              id
            }
          }
        }
        currency
        parent {
          adjustment {
            type
            value
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
      priceList(id: "gid://shopify/PriceList/524058083") {
        catalog {
          id
          title
        }
        prices(first: 5, query: "product_id:20995642") {
          nodes {
            price {
              amount
              currencyCode
            }
            variant {
              id
            }
          }
        }
        currency
        parent {
          adjustment {
            type
            value
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
    priceList(id: "gid://shopify/PriceList/524058083") {
      catalog {
        id
        title
      }
      prices(first: 5, query: "product_id:20995642") {
        nodes {
          price {
            amount
            currencyCode
          }
          variant {
            id
          }
        }
      }
      currency
      parent {
        adjustment {
          type
          value
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "priceList": {
      "catalog": {
        "id": "gid://shopify/MarketCatalog/307400570",
        "title": "Just a simple catalog for a US Price List"
      },
      "prices": {
        "nodes": [
          {
            "price": {
              "amount": "9.0",
              "currencyCode": "USD"
            },
            "variant": {
              "id": "gid://shopify/ProductVariant/30322695"
            }
          },
          {
            "price": {
              "amount": "13.5",
              "currencyCode": "USD"
            },
            "variant": {
              "id": "gid://shopify/ProductVariant/113711323"
            }
          },
          {
            "price": {
              "amount": "13.5",
              "currencyCode": "USD"
            },
            "variant": {
              "id": "gid://shopify/ProductVariant/236948360"
            }
          }
        ]
      },
      "currency": "USD",
      "parent": {
        "adjustment": {
          "type": "PERCENTAGE_DECREASE",
          "value": 10
        }
      }
    }
  }
  ```

* ### Retrieve Quantity Rules on Price List

  #### Description

  Retrieves the fixed associated quantity rules on a price list.

  #### Query

  ```graphql
  query {
    priceList(id: "gid://shopify/PriceList/225060712") {
      quantityRules(first: 3, originType: FIXED) {
        nodes {
          increment
          maximum
          minimum
          productVariant {
            id
            title
          }
        }
      }
      currency
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
  "query": "query { priceList(id: \"gid://shopify/PriceList/225060712\") { quantityRules(first: 3, originType: FIXED) { nodes { increment maximum minimum productVariant { id title } } } currency } }"
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
      priceList(id: "gid://shopify/PriceList/225060712") {
        quantityRules(first: 3, originType: FIXED) {
          nodes {
            increment
            maximum
            minimum
            productVariant {
              id
              title
            }
          }
        }
        currency
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
      priceList(id: "gid://shopify/PriceList/225060712") {
        quantityRules(first: 3, originType: FIXED) {
          nodes {
            increment
            maximum
            minimum
            productVariant {
              id
              title
            }
          }
        }
        currency
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
      priceList(id: "gid://shopify/PriceList/225060712") {
        quantityRules(first: 3, originType: FIXED) {
          nodes {
            increment
            maximum
            minimum
            productVariant {
              id
              title
            }
          }
        }
        currency
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    priceList(id: "gid://shopify/PriceList/225060712") {
      quantityRules(first: 3, originType: FIXED) {
        nodes {
          increment
          maximum
          minimum
          productVariant {
            id
            title
          }
        }
      }
      currency
    }
  }'
  ```

  #### Response

  ```json
  {
    "priceList": {
      "quantityRules": {
        "nodes": [
          {
            "increment": 100,
            "maximum": 5000,
            "minimum": 500,
            "productVariant": {
              "id": "gid://shopify/ProductVariant/43729076",
              "title": "151cm"
            }
          },
          {
            "increment": 10,
            "maximum": 1000,
            "minimum": 100,
            "productVariant": {
              "id": "gid://shopify/ProductVariant/138327650",
              "title": "Default"
            }
          },
          {
            "increment": 5,
            "maximum": null,
            "minimum": 10,
            "productVariant": {
              "id": "gid://shopify/ProductVariant/389013007",
              "title": "Small"
            }
          }
        ]
      },
      "currency": "USD"
    }
  }
  ```

* ### Retrieve the FIXED prices on a price list

  #### Description

  Retrieve the first ten fixed prices on a price list, returning the associated price, compareAtPrice, and variant values.

  #### Query

  ```graphql
  query {
    priceList(id: "gid://shopify/PriceList/294167858") {
      id
      name
      prices(first: 10, originType: FIXED) {
        nodes {
          price {
            amount
            currencyCode
          }
          compareAtPrice {
            amount
            currencyCode
          }
          originType
          variant {
            id
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
  "query": "query { priceList(id: \"gid://shopify/PriceList/294167858\") { id name prices(first: 10, originType: FIXED) { nodes { price { amount currencyCode } compareAtPrice { amount currencyCode } originType variant { id } } } } }"
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
      priceList(id: "gid://shopify/PriceList/294167858") {
        id
        name
        prices(first: 10, originType: FIXED) {
          nodes {
            price {
              amount
              currencyCode
            }
            compareAtPrice {
              amount
              currencyCode
            }
            originType
            variant {
              id
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
      priceList(id: "gid://shopify/PriceList/294167858") {
        id
        name
        prices(first: 10, originType: FIXED) {
          nodes {
            price {
              amount
              currencyCode
            }
            compareAtPrice {
              amount
              currencyCode
            }
            originType
            variant {
              id
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
      priceList(id: "gid://shopify/PriceList/294167858") {
        id
        name
        prices(first: 10, originType: FIXED) {
          nodes {
            price {
              amount
              currencyCode
            }
            compareAtPrice {
              amount
              currencyCode
            }
            originType
            variant {
              id
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
    priceList(id: "gid://shopify/PriceList/294167858") {
      id
      name
      prices(first: 10, originType: FIXED) {
        nodes {
          price {
            amount
            currencyCode
          }
          compareAtPrice {
            amount
            currencyCode
          }
          originType
          variant {
            id
          }
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "priceList": {
      "id": "gid://shopify/PriceList/294167858",
      "name": "simple_pricelist",
      "prices": {
        "nodes": [
          {
            "price": {
              "amount": "19.96",
              "currencyCode": "USD"
            },
            "compareAtPrice": {
              "amount": "24.99",
              "currencyCode": "USD"
            },
            "originType": "FIXED",
            "variant": {
              "id": "gid://shopify/ProductVariant/113711323"
            }
          },
          {
            "price": {
              "amount": "9.99",
              "currencyCode": "USD"
            },
            "compareAtPrice": {
              "amount": "14.99",
              "currencyCode": "USD"
            },
            "originType": "FIXED",
            "variant": {
              "id": "gid://shopify/ProductVariant/498744621"
            }
          }
        ]
      }
    }
  }
  ```

* ### Retrieve the prices on a price list filtered by product\_id

  #### Description

  Retrieve the first ten prices on a price list, filtered by product\_id, returning the associated price, compareAtPrice, and variant values.

  #### Query

  ```graphql
  query {
    priceList(id: "gid://shopify/PriceList/294167858") {
      id
      name
      prices(first: 10, query: "product_id:20995642") {
        nodes {
          price {
            amount
            currencyCode
          }
          compareAtPrice {
            amount
            currencyCode
          }
          variant {
            id
            product {
              id
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
  "query": "query { priceList(id: \"gid://shopify/PriceList/294167858\") { id name prices(first: 10, query: \"product_id:20995642\") { nodes { price { amount currencyCode } compareAtPrice { amount currencyCode } variant { id product { id } } } } } }"
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
      priceList(id: "gid://shopify/PriceList/294167858") {
        id
        name
        prices(first: 10, query: "product_id:20995642") {
          nodes {
            price {
              amount
              currencyCode
            }
            compareAtPrice {
              amount
              currencyCode
            }
            variant {
              id
              product {
                id
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
    query {
      priceList(id: "gid://shopify/PriceList/294167858") {
        id
        name
        prices(first: 10, query: "product_id:20995642") {
          nodes {
            price {
              amount
              currencyCode
            }
            compareAtPrice {
              amount
              currencyCode
            }
            variant {
              id
              product {
                id
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
    data: `query {
      priceList(id: "gid://shopify/PriceList/294167858") {
        id
        name
        prices(first: 10, query: "product_id:20995642") {
          nodes {
            price {
              amount
              currencyCode
            }
            compareAtPrice {
              amount
              currencyCode
            }
            variant {
              id
              product {
                id
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
  'query {
    priceList(id: "gid://shopify/PriceList/294167858") {
      id
      name
      prices(first: 10, query: "product_id:20995642") {
        nodes {
          price {
            amount
            currencyCode
          }
          compareAtPrice {
            amount
            currencyCode
          }
          variant {
            id
            product {
              id
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
    "priceList": {
      "id": "gid://shopify/PriceList/294167858",
      "name": "simple_pricelist",
      "prices": {
        "nodes": [
          {
            "price": {
              "amount": "10.0",
              "currencyCode": "USD"
            },
            "compareAtPrice": {
              "amount": "14.0",
              "currencyCode": "USD"
            },
            "variant": {
              "id": "gid://shopify/ProductVariant/30322695",
              "product": {
                "id": "gid://shopify/Product/20995642"
              }
            }
          },
          {
            "price": {
              "amount": "19.96",
              "currencyCode": "USD"
            },
            "compareAtPrice": {
              "amount": "24.99",
              "currencyCode": "USD"
            },
            "variant": {
              "id": "gid://shopify/ProductVariant/113711323",
              "product": {
                "id": "gid://shopify/Product/20995642"
              }
            }
          },
          {
            "price": {
              "amount": "15.0",
              "currencyCode": "USD"
            },
            "compareAtPrice": {
              "amount": "17.0",
              "currencyCode": "USD"
            },
            "variant": {
              "id": "gid://shopify/ProductVariant/236948360",
              "product": {
                "id": "gid://shopify/Product/20995642"
              }
            }
          }
        ]
      }
    }
  }
  ```

* ### Retrieve the prices on a price list filtered by variant\_id

  #### Description

  Retrieve the first ten prices on a price list, filtered by variant\_id, returning the associated price, compareAtPrice, and variant values.

  #### Query

  ```graphql
  query {
    priceList(id: "gid://shopify/PriceList/294167858") {
      id
      name
      prices(first: 10, query: "variant_id:498744621") {
        nodes {
          price {
            amount
            currencyCode
          }
          compareAtPrice {
            amount
            currencyCode
          }
          variant {
            id
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
  "query": "query { priceList(id: \"gid://shopify/PriceList/294167858\") { id name prices(first: 10, query: \"variant_id:498744621\") { nodes { price { amount currencyCode } compareAtPrice { amount currencyCode } variant { id } } } } }"
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
      priceList(id: "gid://shopify/PriceList/294167858") {
        id
        name
        prices(first: 10, query: "variant_id:498744621") {
          nodes {
            price {
              amount
              currencyCode
            }
            compareAtPrice {
              amount
              currencyCode
            }
            variant {
              id
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
      priceList(id: "gid://shopify/PriceList/294167858") {
        id
        name
        prices(first: 10, query: "variant_id:498744621") {
          nodes {
            price {
              amount
              currencyCode
            }
            compareAtPrice {
              amount
              currencyCode
            }
            variant {
              id
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
      priceList(id: "gid://shopify/PriceList/294167858") {
        id
        name
        prices(first: 10, query: "variant_id:498744621") {
          nodes {
            price {
              amount
              currencyCode
            }
            compareAtPrice {
              amount
              currencyCode
            }
            variant {
              id
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
    priceList(id: "gid://shopify/PriceList/294167858") {
      id
      name
      prices(first: 10, query: "variant_id:498744621") {
        nodes {
          price {
            amount
            currencyCode
          }
          compareAtPrice {
            amount
            currencyCode
          }
          variant {
            id
          }
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "priceList": {
      "id": "gid://shopify/PriceList/294167858",
      "name": "simple_pricelist",
      "prices": {
        "nodes": [
          {
            "price": {
              "amount": "9.99",
              "currencyCode": "USD"
            },
            "compareAtPrice": {
              "amount": "14.99",
              "currencyCode": "USD"
            },
            "variant": {
              "id": "gid://shopify/ProductVariant/498744621"
            }
          }
        ]
      }
    }
  }
  ```
