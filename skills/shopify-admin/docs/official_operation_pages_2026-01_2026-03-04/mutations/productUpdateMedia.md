---
title: productUpdateMedia - GraphQL Admin
description: >-
  Updates properties of media attached to a
  [`Product`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product).
  You can modify alt text for accessibility or change preview images for
  existing media items.


  Provide the product ID and an array of
  [`UpdateMediaInput`](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/UpdateMediaInput)
  objects. Each update specifies the media's ID and the properties to change.
  Updates apply only to media already attached to the product and don't affect
  their position in the product gallery.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/productUpdateMedia
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/productUpdateMedia.md
---

# product​Update​Media

mutation

Requires `write_products` access scope. Also: The user must have a permission to update media for a product.

Deprecated. Use [fileUpdate](https://shopify.dev/docs/api/admin-graphql/latest/mutations/fileUpdate) instead.

Updates properties of media attached to a [`Product`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product). You can modify alt text for accessibility or change preview images for existing media items.

Provide the product ID and an array of [`UpdateMediaInput`](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/UpdateMediaInput) objects. Each update specifies the media's ID and the properties to change. Updates apply only to media already attached to the product and don't affect their position in the product gallery.

## Arguments

* media

  [\[Update​Media​Input!\]!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/UpdateMediaInput)

  required

  A list of media updates.

* product​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  Specifies the product on which media will be updated.

***

## Product​Update​Media​Payload returns

* media

  [\[Media!\]](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/Media)

  The updated media object.

* media​User​Errors

  [\[Media​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MediaUserError)

  non-null

  The list of errors that occurred from executing the mutation.

* product

  [Product](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product)

  The product on which media was updated.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-nullDeprecated

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Modify an existing Product Image

  #### Query

  ```graphql
  mutation ProductImageUpdate($id: ID!) {
    productUpdateMedia(productId: $id, media: [{id: "gid://shopify/MediaImage/853695510", alt: "Updated alt text."}]) {
      media {
        id
        alt
        status
        ... on MediaImage {
          image {
            url
          }
        }
      }
      mediaUserErrors {
        field
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/Product/108828309"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation ProductImageUpdate($id: ID!) { productUpdateMedia(productId: $id, media: [{id: \"gid://shopify/MediaImage/853695510\", alt: \"Updated alt text.\"}]) { media { id alt status ... on MediaImage { image { url } } } mediaUserErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/Product/108828309"
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
    mutation ProductImageUpdate($id: ID!) {
      productUpdateMedia(productId: $id, media: [{id: "gid://shopify/MediaImage/853695510", alt: "Updated alt text."}]) {
        media {
          id
          alt
          status
          ... on MediaImage {
            image {
              url
            }
          }
        }
        mediaUserErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/Product/108828309"
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
    mutation ProductImageUpdate($id: ID!) {
      productUpdateMedia(productId: $id, media: [{id: "gid://shopify/MediaImage/853695510", alt: "Updated alt text."}]) {
        media {
          id
          alt
          status
          ... on MediaImage {
            image {
              url
            }
          }
        }
        mediaUserErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/Product/108828309"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation ProductImageUpdate($id: ID!) {
        productUpdateMedia(productId: $id, media: [{id: "gid://shopify/MediaImage/853695510", alt: "Updated alt text."}]) {
          media {
            id
            alt
            status
            ... on MediaImage {
              image {
                url
              }
            }
          }
          mediaUserErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/Product/108828309"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation ProductImageUpdate($id: ID!) {
    productUpdateMedia(productId: $id, media: [{id: "gid://shopify/MediaImage/853695510", alt: "Updated alt text."}]) {
      media {
        id
        alt
        status
        ... on MediaImage {
          image {
            url
          }
        }
      }
      mediaUserErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/Product/108828309"
  }'
  ```

  #### Response

  ```json
  {
    "productUpdateMedia": {
      "media": [
        {
          "id": "gid://shopify/MediaImage/853695510",
          "alt": "Updated alt text.",
          "status": "READY",
          "image": {
            "url": "https://cdn.shopify.com/s/files/1/2637/1970/products/draft58.jpg?v=1730761095"
          }
        }
      ],
      "mediaUserErrors": []
    }
  }
  ```

* ### Update a product's media fields

  #### Description

  Update the media fields of a product

  #### Query

  ```graphql
  mutation productUpdateMedia($media: [UpdateMediaInput!]!, $productId: ID!) {
    productUpdateMedia(media: $media, productId: $productId) {
      media {
        alt
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "media": [
      {
        "alt": "Some alt text",
        "id": "gid://shopify/Video/723685877"
      },
      {
        "alt": "Some more alt text",
        "id": "gid://shopify/MediaImage/853695510"
      }
    ],
    "productId": "gid://shopify/Product/108828309"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation productUpdateMedia($media: [UpdateMediaInput!]!, $productId: ID!) { productUpdateMedia(media: $media, productId: $productId) { media { alt } } }",
   "variables": {
      "media": [
        {
          "alt": "Some alt text",
          "id": "gid://shopify/Video/723685877"
        },
        {
          "alt": "Some more alt text",
          "id": "gid://shopify/MediaImage/853695510"
        }
      ],
      "productId": "gid://shopify/Product/108828309"
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
    mutation productUpdateMedia($media: [UpdateMediaInput!]!, $productId: ID!) {
      productUpdateMedia(media: $media, productId: $productId) {
        media {
          alt
        }
      }
    }`,
    {
      variables: {
          "media": [
              {
                  "alt": "Some alt text",
                  "id": "gid://shopify/Video/723685877"
              },
              {
                  "alt": "Some more alt text",
                  "id": "gid://shopify/MediaImage/853695510"
              }
          ],
          "productId": "gid://shopify/Product/108828309"
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
    mutation productUpdateMedia($media: [UpdateMediaInput!]!, $productId: ID!) {
      productUpdateMedia(media: $media, productId: $productId) {
        media {
          alt
        }
      }
    }
  QUERY

  variables = {
    "media": [
      {
        "alt": "Some alt text",
        "id": "gid://shopify/Video/723685877"
      },
      {
        "alt": "Some more alt text",
        "id": "gid://shopify/MediaImage/853695510"
      }
    ],
    "productId": "gid://shopify/Product/108828309"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation productUpdateMedia($media: [UpdateMediaInput!]!, $productId: ID!) {
        productUpdateMedia(media: $media, productId: $productId) {
          media {
            alt
          }
        }
      }`,
      "variables": {
          "media": [
              {
                  "alt": "Some alt text",
                  "id": "gid://shopify/Video/723685877"
              },
              {
                  "alt": "Some more alt text",
                  "id": "gid://shopify/MediaImage/853695510"
              }
          ],
          "productId": "gid://shopify/Product/108828309"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation productUpdateMedia($media: [UpdateMediaInput!]!, $productId: ID!) {
    productUpdateMedia(media: $media, productId: $productId) {
      media {
        alt
      }
    }
  }' \
  --variables \
  '{
    "media": [
      {
        "alt": "Some alt text",
        "id": "gid://shopify/Video/723685877"
      },
      {
        "alt": "Some more alt text",
        "id": "gid://shopify/MediaImage/853695510"
      }
    ],
    "productId": "gid://shopify/Product/108828309"
  }'
  ```

  #### Response

  ```json
  {
    "productUpdateMedia": {
      "media": [
        {
          "alt": "Some alt text"
        },
        {
          "alt": "Some more alt text"
        }
      ]
    }
  }
  ```

* ### Update new media on a non-existent product

  #### Description

  Trying to update media on a non-existent product returns an error.

  #### Query

  ```graphql
  mutation productUpdateMedia($media: [UpdateMediaInput!]!, $productId: ID!) {
    productUpdateMedia(media: $media, productId: $productId) {
      product {
        id
        title
      }
      media {
        alt
      }
      mediaUserErrors {
        field
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "media": [
      {
        "alt": "Some alt text",
        "id": "gid://shopify/Video/723685877"
      },
      {
        "alt": "Some more alt text",
        "id": "gid://shopify/MediaImage/853695510"
      }
    ],
    "productId": "gid://shopify/Product/-1"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation productUpdateMedia($media: [UpdateMediaInput!]!, $productId: ID!) { productUpdateMedia(media: $media, productId: $productId) { product { id title } media { alt } mediaUserErrors { field message } } }",
   "variables": {
      "media": [
        {
          "alt": "Some alt text",
          "id": "gid://shopify/Video/723685877"
        },
        {
          "alt": "Some more alt text",
          "id": "gid://shopify/MediaImage/853695510"
        }
      ],
      "productId": "gid://shopify/Product/-1"
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
    mutation productUpdateMedia($media: [UpdateMediaInput!]!, $productId: ID!) {
      productUpdateMedia(media: $media, productId: $productId) {
        product {
          id
          title
        }
        media {
          alt
        }
        mediaUserErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "media": [
              {
                  "alt": "Some alt text",
                  "id": "gid://shopify/Video/723685877"
              },
              {
                  "alt": "Some more alt text",
                  "id": "gid://shopify/MediaImage/853695510"
              }
          ],
          "productId": "gid://shopify/Product/-1"
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
    mutation productUpdateMedia($media: [UpdateMediaInput!]!, $productId: ID!) {
      productUpdateMedia(media: $media, productId: $productId) {
        product {
          id
          title
        }
        media {
          alt
        }
        mediaUserErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "media": [
      {
        "alt": "Some alt text",
        "id": "gid://shopify/Video/723685877"
      },
      {
        "alt": "Some more alt text",
        "id": "gid://shopify/MediaImage/853695510"
      }
    ],
    "productId": "gid://shopify/Product/-1"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation productUpdateMedia($media: [UpdateMediaInput!]!, $productId: ID!) {
        productUpdateMedia(media: $media, productId: $productId) {
          product {
            id
            title
          }
          media {
            alt
          }
          mediaUserErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "media": [
              {
                  "alt": "Some alt text",
                  "id": "gid://shopify/Video/723685877"
              },
              {
                  "alt": "Some more alt text",
                  "id": "gid://shopify/MediaImage/853695510"
              }
          ],
          "productId": "gid://shopify/Product/-1"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation productUpdateMedia($media: [UpdateMediaInput!]!, $productId: ID!) {
    productUpdateMedia(media: $media, productId: $productId) {
      product {
        id
        title
      }
      media {
        alt
      }
      mediaUserErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "media": [
      {
        "alt": "Some alt text",
        "id": "gid://shopify/Video/723685877"
      },
      {
        "alt": "Some more alt text",
        "id": "gid://shopify/MediaImage/853695510"
      }
    ],
    "productId": "gid://shopify/Product/-1"
  }'
  ```

  #### Response

  ```json
  {
    "productUpdateMedia": {
      "product": null,
      "media": null,
      "mediaUserErrors": [
        {
          "field": [
            "productId"
          ],
          "message": "Product does not exist"
        }
      ]
    }
  }
  ```

* ### Update non-existent media on a non-existent product

  #### Description

  Trying to update non-existent media on a non-existent product returns an error.

  #### Query

  ```graphql
  mutation productUpdateMedia($media: [UpdateMediaInput!]!, $productId: ID!) {
    productUpdateMedia(media: $media, productId: $productId) {
      product {
        id
        title
      }
      media {
        alt
      }
      mediaUserErrors {
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
    "media": [
      {
        "alt": "Some more alt text",
        "id": "gid://shopify/MediaImage/-1"
      }
    ],
    "productId": "gid://shopify/Product/-1"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation productUpdateMedia($media: [UpdateMediaInput!]!, $productId: ID!) { productUpdateMedia(media: $media, productId: $productId) { product { id title } media { alt } mediaUserErrors { field message code } } }",
   "variables": {
      "media": [
        {
          "alt": "Some more alt text",
          "id": "gid://shopify/MediaImage/-1"
        }
      ],
      "productId": "gid://shopify/Product/-1"
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
    mutation productUpdateMedia($media: [UpdateMediaInput!]!, $productId: ID!) {
      productUpdateMedia(media: $media, productId: $productId) {
        product {
          id
          title
        }
        media {
          alt
        }
        mediaUserErrors {
          field
          message
          code
        }
      }
    }`,
    {
      variables: {
          "media": [
              {
                  "alt": "Some more alt text",
                  "id": "gid://shopify/MediaImage/-1"
              }
          ],
          "productId": "gid://shopify/Product/-1"
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
    mutation productUpdateMedia($media: [UpdateMediaInput!]!, $productId: ID!) {
      productUpdateMedia(media: $media, productId: $productId) {
        product {
          id
          title
        }
        media {
          alt
        }
        mediaUserErrors {
          field
          message
          code
        }
      }
    }
  QUERY

  variables = {
    "media": [
      {
        "alt": "Some more alt text",
        "id": "gid://shopify/MediaImage/-1"
      }
    ],
    "productId": "gid://shopify/Product/-1"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation productUpdateMedia($media: [UpdateMediaInput!]!, $productId: ID!) {
        productUpdateMedia(media: $media, productId: $productId) {
          product {
            id
            title
          }
          media {
            alt
          }
          mediaUserErrors {
            field
            message
            code
          }
        }
      }`,
      "variables": {
          "media": [
              {
                  "alt": "Some more alt text",
                  "id": "gid://shopify/MediaImage/-1"
              }
          ],
          "productId": "gid://shopify/Product/-1"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation productUpdateMedia($media: [UpdateMediaInput!]!, $productId: ID!) {
    productUpdateMedia(media: $media, productId: $productId) {
      product {
        id
        title
      }
      media {
        alt
      }
      mediaUserErrors {
        field
        message
        code
      }
    }
  }' \
  --variables \
  '{
    "media": [
      {
        "alt": "Some more alt text",
        "id": "gid://shopify/MediaImage/-1"
      }
    ],
    "productId": "gid://shopify/Product/-1"
  }'
  ```

  #### Response

  ```json
  {
    "productUpdateMedia": {
      "product": null,
      "media": null,
      "mediaUserErrors": [
        {
          "field": [
            "productId"
          ],
          "message": "Product does not exist",
          "code": "PRODUCT_DOES_NOT_EXIST"
        }
      ]
    }
  }
  ```

* ### Update non-existent media on a valid product

  #### Description

  Trying to update non-existent media on a valid product returns an error.

  #### Query

  ```graphql
  mutation productUpdateMedia($media: [UpdateMediaInput!]!, $productId: ID!) {
    productUpdateMedia(media: $media, productId: $productId) {
      product {
        id
        title
      }
      media {
        alt
      }
      mediaUserErrors {
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
    "media": [
      {
        "alt": "Some more alt text",
        "id": "gid://shopify/MediaImage/-1"
      }
    ],
    "productId": "gid://shopify/Product/108828309"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation productUpdateMedia($media: [UpdateMediaInput!]!, $productId: ID!) { productUpdateMedia(media: $media, productId: $productId) { product { id title } media { alt } mediaUserErrors { field message code } } }",
   "variables": {
      "media": [
        {
          "alt": "Some more alt text",
          "id": "gid://shopify/MediaImage/-1"
        }
      ],
      "productId": "gid://shopify/Product/108828309"
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
    mutation productUpdateMedia($media: [UpdateMediaInput!]!, $productId: ID!) {
      productUpdateMedia(media: $media, productId: $productId) {
        product {
          id
          title
        }
        media {
          alt
        }
        mediaUserErrors {
          field
          message
          code
        }
      }
    }`,
    {
      variables: {
          "media": [
              {
                  "alt": "Some more alt text",
                  "id": "gid://shopify/MediaImage/-1"
              }
          ],
          "productId": "gid://shopify/Product/108828309"
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
    mutation productUpdateMedia($media: [UpdateMediaInput!]!, $productId: ID!) {
      productUpdateMedia(media: $media, productId: $productId) {
        product {
          id
          title
        }
        media {
          alt
        }
        mediaUserErrors {
          field
          message
          code
        }
      }
    }
  QUERY

  variables = {
    "media": [
      {
        "alt": "Some more alt text",
        "id": "gid://shopify/MediaImage/-1"
      }
    ],
    "productId": "gid://shopify/Product/108828309"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation productUpdateMedia($media: [UpdateMediaInput!]!, $productId: ID!) {
        productUpdateMedia(media: $media, productId: $productId) {
          product {
            id
            title
          }
          media {
            alt
          }
          mediaUserErrors {
            field
            message
            code
          }
        }
      }`,
      "variables": {
          "media": [
              {
                  "alt": "Some more alt text",
                  "id": "gid://shopify/MediaImage/-1"
              }
          ],
          "productId": "gid://shopify/Product/108828309"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation productUpdateMedia($media: [UpdateMediaInput!]!, $productId: ID!) {
    productUpdateMedia(media: $media, productId: $productId) {
      product {
        id
        title
      }
      media {
        alt
      }
      mediaUserErrors {
        field
        message
        code
      }
    }
  }' \
  --variables \
  '{
    "media": [
      {
        "alt": "Some more alt text",
        "id": "gid://shopify/MediaImage/-1"
      }
    ],
    "productId": "gid://shopify/Product/108828309"
  }'
  ```

  #### Response

  ```json
  {
    "productUpdateMedia": {
      "product": {
        "id": "gid://shopify/Product/108828309",
        "title": "Draft"
      },
      "media": null,
      "mediaUserErrors": [
        {
          "field": [
            "media"
          ],
          "message": "Media id gid://shopify/MediaImage/-1 does not exist",
          "code": "MEDIA_DOES_NOT_EXIST"
        }
      ]
    }
  }
  ```

* ### productUpdateMedia reference
