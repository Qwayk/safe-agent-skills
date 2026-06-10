---
title: abandonedCheckoutsCount - GraphQL Admin
description: >-
  Returns the count of abandoned checkouts for the given shop. Limited to a
  maximum of 10000 by default.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/abandonedCheckoutsCount
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/abandonedCheckoutsCount.md
---

# abandoned​Checkouts​Count

query

Requires `read_orders` access scope. Also: The user must have manage\_abandoned\_checkouts permission.

Returns the count of abandoned checkouts for the given shop. Limited to a maximum of 10000 by default.

## Arguments

* limit

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  Default:10000

  The upper bound on count value before returning a result. Use `null` to have no limit.

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

* saved​Search​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of an existing saved search. The search’s query string is used as the query argument. Refer to the [`SavedSearch`](https://shopify.dev/api/admin-graphql/latest/objects/savedsearch) object.

***

## Possible returns

* Count

  [Count](https://shopify.dev/docs/api/admin-graphql/latest/objects/Count)

  A numeric count with precision information indicating whether the count is exact or an estimate.

  * count

    [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    non-null

    The count of elements.

  * precision

    [Count​Precision!](https://shopify.dev/docs/api/admin-graphql/latest/enums/CountPrecision)

    non-null

    The count's precision, or the exactness of the value.

***

## Examples

* ### Retrieves a count of checkouts

  #### Query

  ```graphql
  query AbandonedCheckoutsCount {
    abandonedCheckoutsCount(limit: 1000) {
      count
      precision
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
  "query": "query AbandonedCheckoutsCount { abandonedCheckoutsCount(limit: 1000) { count precision } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query AbandonedCheckoutsCount {
      abandonedCheckoutsCount(limit: 1000) {
        count
        precision
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
    query AbandonedCheckoutsCount {
      abandonedCheckoutsCount(limit: 1000) {
        count
        precision
      }
    }
  QUERY

  response = client.query(query: query)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: `query AbandonedCheckoutsCount {
      abandonedCheckoutsCount(limit: 1000) {
        count
        precision
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query AbandonedCheckoutsCount {
    abandonedCheckoutsCount(limit: 1000) {
      count
      precision
    }
  }'
  ```

  #### Response

  ```json
  {
    "abandonedCheckoutsCount": {
      "count": 38,
      "precision": "EXACT"
    }
  }
  ```
