---
title: publishableUnpublishToCurrentChannel - GraphQL Admin
description: >-
  Unpublishes a resource from the current channel. If the resource is a product,
  then it's visible in the channel only if the product status is `active`.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/publishableUnpublishToCurrentChannel
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/publishableUnpublishToCurrentChannel.md
---

# publishable​Unpublish​To​Current​Channel

mutation

Requires `write_publications` access scope. Also: The user must have a permission to create and edit products.

Deprecated. Use [publishableUnpublish](https://shopify.dev/docs/api/admin-graphql/latest/mutations/publishableUnpublish) instead.

Unpublishes a resource from the current channel. If the resource is a product, then it's visible in the channel only if the product status is `active`.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The resource to delete or update publications for.

***

## Publishable​Unpublish​To​Current​Channel​Payload returns

* publishable

  [Publishable](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/Publishable)

  Resource that has been unpublished.

* shop

  [Shop!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Shop)

  non-null

  The user's shop.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Unpublish a product from the current channel

  #### Query

  ```graphql
  mutation publishableUnpublishToCurrentChannel($id: ID!) {
    publishableUnpublishToCurrentChannel(id: $id) {
      publishable {
        availablePublicationsCount {
          count
        }
        resourcePublicationsCount {
          count
        }
      }
      shop {
        publicationCount
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
    "id": "gid://shopify/Product/921728736"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation publishableUnpublishToCurrentChannel($id: ID!) { publishableUnpublishToCurrentChannel(id: $id) { publishable { availablePublicationsCount { count } resourcePublicationsCount { count } } shop { publicationCount } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/Product/921728736"
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
    mutation publishableUnpublishToCurrentChannel($id: ID!) {
      publishableUnpublishToCurrentChannel(id: $id) {
        publishable {
          availablePublicationsCount {
            count
          }
          resourcePublicationsCount {
            count
          }
        }
        shop {
          publicationCount
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/Product/921728736"
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
    mutation publishableUnpublishToCurrentChannel($id: ID!) {
      publishableUnpublishToCurrentChannel(id: $id) {
        publishable {
          availablePublicationsCount {
            count
          }
          resourcePublicationsCount {
            count
          }
        }
        shop {
          publicationCount
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/Product/921728736"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation publishableUnpublishToCurrentChannel($id: ID!) {
        publishableUnpublishToCurrentChannel(id: $id) {
          publishable {
            availablePublicationsCount {
              count
            }
            resourcePublicationsCount {
              count
            }
          }
          shop {
            publicationCount
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/Product/921728736"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation publishableUnpublishToCurrentChannel($id: ID!) {
    publishableUnpublishToCurrentChannel(id: $id) {
      publishable {
        availablePublicationsCount {
          count
        }
        resourcePublicationsCount {
          count
        }
      }
      shop {
        publicationCount
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/Product/921728736"
  }'
  ```

  #### Response

  ```json
  {
    "publishableUnpublishToCurrentChannel": {
      "publishable": {
        "availablePublicationsCount": {
          "count": 1
        },
        "resourcePublicationsCount": {
          "count": 1
        }
      },
      "shop": {
        "publicationCount": 3
      },
      "userErrors": []
    }
  }
  ```

* ### publishableUnpublishToCurrentChannel reference
