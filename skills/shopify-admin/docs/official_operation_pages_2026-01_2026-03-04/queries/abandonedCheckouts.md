---
title: abandonedCheckouts - GraphQL Admin
description: >-
  Returns a list of abandoned checkouts. A checkout is considered abandoned when
  a customer adds contact information but doesn't complete their purchase.
  Includes both abandoned and recovered checkouts.


  Each checkout provides
  [`Customer`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer)
  details,
  [`AbandonedCheckoutLineItem`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AbandonedCheckoutLineItem)
  objects, pricing information, and a recovery URL for re-engaging customers who
  didn't complete their purchase.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/abandonedCheckouts'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/abandonedCheckouts.md
---

# abandoned​Checkouts

query

Returns a list of abandoned checkouts. A checkout is considered abandoned when a customer adds contact information but doesn't complete their purchase. Includes both abandoned and recovered checkouts.

Each checkout provides [`Customer`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer) details, [`AbandonedCheckoutLineItem`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AbandonedCheckoutLineItem) objects, pricing information, and a recovery URL for re-engaging customers who didn't complete their purchase.

## AbandonedCheckoutConnection arguments

[AbandonedCheckoutConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/AbandonedCheckoutConnection)

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

    * created\_at

      time

    - Filter by a case-insensitive search of multiple fields in a document.

    - Example:

      * `query=Bob Norman`
      * `query=title:green hoodie`

      The date and time (in [ISO 8601 format](http://en.wikipedia.org/wiki/ISO_8601)) when the abandoned cart was created.

  * email\_state

    string

    Filter by `abandoned_email_state` value. Possible values: `sent`, `not_sent`, `scheduled` and `suppressed`.

  * * id

      id

    * recovery\_state

      string

    - Filter by `id` range.

    - Example:

      * `id:1234`
      * `id:>=1234`
      * `id:<=1234`

      Possible values: `recovered` and `not_recovered`.

  * status

    string

    Possible values: `open` and `closed`.

  * updated\_at

    time

    The date and time (in [ISO 8601 format](http://en.wikipedia.org/wiki/ISO_8601)) when the abandoned cart was last updated.

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

* saved​Search​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of a [saved search](https://shopify.dev/api/admin-graphql/latest/objects/savedsearch#field-id). The search’s query string is used as the query argument.

* sort​Key

  [Abandoned​Checkout​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/AbandonedCheckoutSortKeys)

  Default:ID

  Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

***

## Possible returns

* edges

  [\[Abandoned​Checkout​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/AbandonedCheckoutEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Abandoned​Checkout!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/AbandonedCheckout)

  non-null

  A list of nodes that are contained in AbandonedCheckoutEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### Retrieves a list of abandoned checkouts

  #### Query

  ```graphql
  query AbandonedCheckouts {
    abandonedCheckouts(first: 1) {
      nodes {
        abandonedCheckoutUrl
        billingAddress {
          country
        }
        completedAt
        createdAt
        customer {
          firstName
          lastName
          email
        }
        id
        shippingAddress {
          country
        }
        updatedAt
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
  "query": "query AbandonedCheckouts { abandonedCheckouts(first: 1) { nodes { abandonedCheckoutUrl billingAddress { country } completedAt createdAt customer { firstName lastName email } id shippingAddress { country } updatedAt } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query AbandonedCheckouts {
      abandonedCheckouts(first: 1) {
        nodes {
          abandonedCheckoutUrl
          billingAddress {
            country
          }
          completedAt
          createdAt
          customer {
            firstName
            lastName
            email
          }
          id
          shippingAddress {
            country
          }
          updatedAt
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
    query AbandonedCheckouts {
      abandonedCheckouts(first: 1) {
        nodes {
          abandonedCheckoutUrl
          billingAddress {
            country
          }
          completedAt
          createdAt
          customer {
            firstName
            lastName
            email
          }
          id
          shippingAddress {
            country
          }
          updatedAt
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
    data: `query AbandonedCheckouts {
      abandonedCheckouts(first: 1) {
        nodes {
          abandonedCheckoutUrl
          billingAddress {
            country
          }
          completedAt
          createdAt
          customer {
            firstName
            lastName
            email
          }
          id
          shippingAddress {
            country
          }
          updatedAt
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query AbandonedCheckouts {
    abandonedCheckouts(first: 1) {
      nodes {
        abandonedCheckoutUrl
        billingAddress {
          country
        }
        completedAt
        createdAt
        customer {
          firstName
          lastName
          email
        }
        id
        shippingAddress {
          country
        }
        updatedAt
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "abandonedCheckouts": {
      "nodes": [
        {
          "abandonedCheckoutUrl": "https://www.snowdevil.ca/26371970/checkouts/ac/cart_token_k23sabns3/recover?key=secret_token_i23kd8f88&locale=en",
          "billingAddress": {
            "country": "Canada"
          },
          "completedAt": null,
          "createdAt": "2125-07-31T15:57:11Z",
          "customer": {
            "firstName": "Bob",
            "lastName": "Bobsen",
            "email": "bob@example.com"
          },
          "id": "gid://shopify/AbandonedCheckout/123",
          "shippingAddress": {
            "country": "Canada"
          },
          "updatedAt": "2125-07-31T15:57:11Z"
        }
      ]
    }
  }
  ```
