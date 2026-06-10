---
title: productCreateMedia - GraphQL Admin
description: >-
  Adds media files to a
  [`Product`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product),
  such as images, videos, or 3D models. Media files enhance product listings by
  providing visual representations that help customers understand the product.


  The mutation accepts an array of
  [`CreateMediaInput`](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/CreateMediaInput)
  objects, each specifying the source URL, content type, and optional alt text.


  You can add multiple media files in a single request. The mutation adds all
  valid files and returns errors for any invalid ones.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/productCreateMedia
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/productCreateMedia.md
---

# product​Create​Media

mutation

Requires `write_products` access scope. Also: The user must have a permission to create media for a product.

Deprecated. Use [productUpdate](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productUpdate) or [productSet](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productSet) instead.

Adds media files to a [`Product`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product), such as images, videos, or 3D models. Media files enhance product listings by providing visual representations that help customers understand the product.

The mutation accepts an array of [`CreateMediaInput`](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/CreateMediaInput) objects, each specifying the source URL, content type, and optional alt text.

You can add multiple media files in a single request. The mutation adds all valid files and returns errors for any invalid ones.

## Arguments

* media

  [\[Create​Media​Input!\]!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/CreateMediaInput)

  required

  List of new media to be added to a product.

* product​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  Specifies the product associated with the media.

***

## Product​Create​Media​Payload returns

* media

  [\[Media!\]](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/Media)

  The newly created media.

* media​User​Errors

  [\[Media​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MediaUserError)

  non-null

  The list of errors that occurred from executing the mutation.

* product

  [Product](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product)

  The product associated with the media.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-nullDeprecated

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Add both valid and invalid media to an existing product

  #### Description

  Trying to add both valid and invalid media to a product adds the valid media and returns an error for the invalid media.

  #### Query

  ```graphql
  mutation productCreateMedia($media: [CreateMediaInput!]!, $productId: ID!) {
    productCreateMedia(media: $media, productId: $productId) {
      media {
        alt
        mediaContentType
        status
      }
      mediaUserErrors {
        field
        message
      }
      product {
        id
        title
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "media": [
      {
        "alt": "Image",
        "mediaContentType": "EXTERNAL_VIDEO",
        "originalSource": "https://youtu.be/32mGBDk3LSo"
      },
      {
        "alt": "Image",
        "mediaContentType": "IMAGE",
        "originalSource": "invalid_img"
      }
    ],
    "productId": "gid://shopify/Product/121709582"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation productCreateMedia($media: [CreateMediaInput!]!, $productId: ID!) { productCreateMedia(media: $media, productId: $productId) { media { alt mediaContentType status } mediaUserErrors { field message } product { id title } } }",
   "variables": {
      "media": [
        {
          "alt": "Image",
          "mediaContentType": "EXTERNAL_VIDEO",
          "originalSource": "https://youtu.be/32mGBDk3LSo"
        },
        {
          "alt": "Image",
          "mediaContentType": "IMAGE",
          "originalSource": "invalid_img"
        }
      ],
      "productId": "gid://shopify/Product/121709582"
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
    mutation productCreateMedia($media: [CreateMediaInput!]!, $productId: ID!) {
      productCreateMedia(media: $media, productId: $productId) {
        media {
          alt
          mediaContentType
          status
        }
        mediaUserErrors {
          field
          message
        }
        product {
          id
          title
        }
      }
    }`,
    {
      variables: {
          "media": [
              {
                  "alt": "Image",
                  "mediaContentType": "EXTERNAL_VIDEO",
                  "originalSource": "https://youtu.be/32mGBDk3LSo"
              },
              {
                  "alt": "Image",
                  "mediaContentType": "IMAGE",
                  "originalSource": "invalid_img"
              }
          ],
          "productId": "gid://shopify/Product/121709582"
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
    mutation productCreateMedia($media: [CreateMediaInput!]!, $productId: ID!) {
      productCreateMedia(media: $media, productId: $productId) {
        media {
          alt
          mediaContentType
          status
        }
        mediaUserErrors {
          field
          message
        }
        product {
          id
          title
        }
      }
    }
  QUERY

  variables = {
    "media": [
      {
        "alt": "Image",
        "mediaContentType": "EXTERNAL_VIDEO",
        "originalSource": "https://youtu.be/32mGBDk3LSo"
      },
      {
        "alt": "Image",
        "mediaContentType": "IMAGE",
        "originalSource": "invalid_img"
      }
    ],
    "productId": "gid://shopify/Product/121709582"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation productCreateMedia($media: [CreateMediaInput!]!, $productId: ID!) {
        productCreateMedia(media: $media, productId: $productId) {
          media {
            alt
            mediaContentType
            status
          }
          mediaUserErrors {
            field
            message
          }
          product {
            id
            title
          }
        }
      }`,
      "variables": {
          "media": [
              {
                  "alt": "Image",
                  "mediaContentType": "EXTERNAL_VIDEO",
                  "originalSource": "https://youtu.be/32mGBDk3LSo"
              },
              {
                  "alt": "Image",
                  "mediaContentType": "IMAGE",
                  "originalSource": "invalid_img"
              }
          ],
          "productId": "gid://shopify/Product/121709582"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation productCreateMedia($media: [CreateMediaInput!]!, $productId: ID!) {
    productCreateMedia(media: $media, productId: $productId) {
      media {
        alt
        mediaContentType
        status
      }
      mediaUserErrors {
        field
        message
      }
      product {
        id
        title
      }
    }
  }' \
  --variables \
  '{
    "media": [
      {
        "alt": "Image",
        "mediaContentType": "EXTERNAL_VIDEO",
        "originalSource": "https://youtu.be/32mGBDk3LSo"
      },
      {
        "alt": "Image",
        "mediaContentType": "IMAGE",
        "originalSource": "invalid_img"
      }
    ],
    "productId": "gid://shopify/Product/121709582"
  }'
  ```

  #### Response

  ```json
  {
    "productCreateMedia": {
      "media": [
        {
          "alt": "Image",
          "mediaContentType": "EXTERNAL_VIDEO",
          "status": "UPLOADED"
        }
      ],
      "mediaUserErrors": [
        {
          "field": [
            "media",
            "1",
            "originalSource"
          ],
          "message": "Image URL is invalid"
        }
      ],
      "product": {
        "id": "gid://shopify/Product/121709582",
        "title": "Boots"
      }
    }
  }
  ```

* ### Add invalid media to an existing product

  #### Description

  Trying to add invalid media to a product returns an error.

  #### Query

  ```graphql
  mutation productCreateMedia($media: [CreateMediaInput!]!, $productId: ID!) {
    productCreateMedia(media: $media, productId: $productId) {
      media {
        alt
        mediaContentType
        status
      }
      mediaUserErrors {
        field
        message
      }
      product {
        id
        title
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "media": {
      "alt": "Image",
      "mediaContentType": "IMAGE",
      "originalSource": "invalid_img"
    },
    "productId": "gid://shopify/Product/121709582"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation productCreateMedia($media: [CreateMediaInput!]!, $productId: ID!) { productCreateMedia(media: $media, productId: $productId) { media { alt mediaContentType status } mediaUserErrors { field message } product { id title } } }",
   "variables": {
      "media": {
        "alt": "Image",
        "mediaContentType": "IMAGE",
        "originalSource": "invalid_img"
      },
      "productId": "gid://shopify/Product/121709582"
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
    mutation productCreateMedia($media: [CreateMediaInput!]!, $productId: ID!) {
      productCreateMedia(media: $media, productId: $productId) {
        media {
          alt
          mediaContentType
          status
        }
        mediaUserErrors {
          field
          message
        }
        product {
          id
          title
        }
      }
    }`,
    {
      variables: {
          "media": {
              "alt": "Image",
              "mediaContentType": "IMAGE",
              "originalSource": "invalid_img"
          },
          "productId": "gid://shopify/Product/121709582"
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
    mutation productCreateMedia($media: [CreateMediaInput!]!, $productId: ID!) {
      productCreateMedia(media: $media, productId: $productId) {
        media {
          alt
          mediaContentType
          status
        }
        mediaUserErrors {
          field
          message
        }
        product {
          id
          title
        }
      }
    }
  QUERY

  variables = {
    "media": {
      "alt": "Image",
      "mediaContentType": "IMAGE",
      "originalSource": "invalid_img"
    },
    "productId": "gid://shopify/Product/121709582"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation productCreateMedia($media: [CreateMediaInput!]!, $productId: ID!) {
        productCreateMedia(media: $media, productId: $productId) {
          media {
            alt
            mediaContentType
            status
          }
          mediaUserErrors {
            field
            message
          }
          product {
            id
            title
          }
        }
      }`,
      "variables": {
          "media": {
              "alt": "Image",
              "mediaContentType": "IMAGE",
              "originalSource": "invalid_img"
          },
          "productId": "gid://shopify/Product/121709582"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation productCreateMedia($media: [CreateMediaInput!]!, $productId: ID!) {
    productCreateMedia(media: $media, productId: $productId) {
      media {
        alt
        mediaContentType
        status
      }
      mediaUserErrors {
        field
        message
      }
      product {
        id
        title
      }
    }
  }' \
  --variables \
  '{
    "media": {
      "alt": "Image",
      "mediaContentType": "IMAGE",
      "originalSource": "invalid_img"
    },
    "productId": "gid://shopify/Product/121709582"
  }'
  ```

  #### Response

  ```json
  {
    "productCreateMedia": {
      "media": [],
      "mediaUserErrors": [
        {
          "field": [
            "media",
            "0",
            "originalSource"
          ],
          "message": "Image URL is invalid"
        }
      ],
      "product": {
        "id": "gid://shopify/Product/121709582",
        "title": "Boots"
      }
    }
  }
  ```

* ### Add new media to a non-existent product

  #### Description

  Trying to add media to a non-existent product returns an error.

  #### Query

  ```graphql
  mutation productCreateMedia($media: [CreateMediaInput!]!, $productId: ID!) {
    productCreateMedia(media: $media, productId: $productId) {
      media {
        alt
        mediaContentType
        status
      }
      mediaUserErrors {
        field
        message
      }
      product {
        id
        title
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "media": {
      "alt": "Video",
      "mediaContentType": "EXTERNAL_VIDEO",
      "originalSource": "https://youtu.be/32mGBDk3LSo"
    },
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
  "query": "mutation productCreateMedia($media: [CreateMediaInput!]!, $productId: ID!) { productCreateMedia(media: $media, productId: $productId) { media { alt mediaContentType status } mediaUserErrors { field message } product { id title } } }",
   "variables": {
      "media": {
        "alt": "Video",
        "mediaContentType": "EXTERNAL_VIDEO",
        "originalSource": "https://youtu.be/32mGBDk3LSo"
      },
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
    mutation productCreateMedia($media: [CreateMediaInput!]!, $productId: ID!) {
      productCreateMedia(media: $media, productId: $productId) {
        media {
          alt
          mediaContentType
          status
        }
        mediaUserErrors {
          field
          message
        }
        product {
          id
          title
        }
      }
    }`,
    {
      variables: {
          "media": {
              "alt": "Video",
              "mediaContentType": "EXTERNAL_VIDEO",
              "originalSource": "https://youtu.be/32mGBDk3LSo"
          },
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
    mutation productCreateMedia($media: [CreateMediaInput!]!, $productId: ID!) {
      productCreateMedia(media: $media, productId: $productId) {
        media {
          alt
          mediaContentType
          status
        }
        mediaUserErrors {
          field
          message
        }
        product {
          id
          title
        }
      }
    }
  QUERY

  variables = {
    "media": {
      "alt": "Video",
      "mediaContentType": "EXTERNAL_VIDEO",
      "originalSource": "https://youtu.be/32mGBDk3LSo"
    },
    "productId": "gid://shopify/Product/-1"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation productCreateMedia($media: [CreateMediaInput!]!, $productId: ID!) {
        productCreateMedia(media: $media, productId: $productId) {
          media {
            alt
            mediaContentType
            status
          }
          mediaUserErrors {
            field
            message
          }
          product {
            id
            title
          }
        }
      }`,
      "variables": {
          "media": {
              "alt": "Video",
              "mediaContentType": "EXTERNAL_VIDEO",
              "originalSource": "https://youtu.be/32mGBDk3LSo"
          },
          "productId": "gid://shopify/Product/-1"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation productCreateMedia($media: [CreateMediaInput!]!, $productId: ID!) {
    productCreateMedia(media: $media, productId: $productId) {
      media {
        alt
        mediaContentType
        status
      }
      mediaUserErrors {
        field
        message
      }
      product {
        id
        title
      }
    }
  }' \
  --variables \
  '{
    "media": {
      "alt": "Video",
      "mediaContentType": "EXTERNAL_VIDEO",
      "originalSource": "https://youtu.be/32mGBDk3LSo"
    },
    "productId": "gid://shopify/Product/-1"
  }'
  ```

  #### Response

  ```json
  {
    "productCreateMedia": {
      "media": null,
      "mediaUserErrors": [
        {
          "field": [
            "productId"
          ],
          "message": "Product does not exist"
        }
      ],
      "product": null
    }
  }
  ```

* ### Add new media to an existing product

  #### Query

  ```graphql
  mutation productCreateMedia($media: [CreateMediaInput!]!, $productId: ID!) {
    productCreateMedia(media: $media, productId: $productId) {
      media {
        alt
        mediaContentType
        status
      }
      mediaUserErrors {
        field
        message
      }
      product {
        id
        title
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "media": {
      "alt": "Video",
      "mediaContentType": "EXTERNAL_VIDEO",
      "originalSource": "https://youtu.be/32mGBDk3LSo"
    },
    "productId": "gid://shopify/Product/121709582"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation productCreateMedia($media: [CreateMediaInput!]!, $productId: ID!) { productCreateMedia(media: $media, productId: $productId) { media { alt mediaContentType status } mediaUserErrors { field message } product { id title } } }",
   "variables": {
      "media": {
        "alt": "Video",
        "mediaContentType": "EXTERNAL_VIDEO",
        "originalSource": "https://youtu.be/32mGBDk3LSo"
      },
      "productId": "gid://shopify/Product/121709582"
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
    mutation productCreateMedia($media: [CreateMediaInput!]!, $productId: ID!) {
      productCreateMedia(media: $media, productId: $productId) {
        media {
          alt
          mediaContentType
          status
        }
        mediaUserErrors {
          field
          message
        }
        product {
          id
          title
        }
      }
    }`,
    {
      variables: {
          "media": {
              "alt": "Video",
              "mediaContentType": "EXTERNAL_VIDEO",
              "originalSource": "https://youtu.be/32mGBDk3LSo"
          },
          "productId": "gid://shopify/Product/121709582"
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
    mutation productCreateMedia($media: [CreateMediaInput!]!, $productId: ID!) {
      productCreateMedia(media: $media, productId: $productId) {
        media {
          alt
          mediaContentType
          status
        }
        mediaUserErrors {
          field
          message
        }
        product {
          id
          title
        }
      }
    }
  QUERY

  variables = {
    "media": {
      "alt": "Video",
      "mediaContentType": "EXTERNAL_VIDEO",
      "originalSource": "https://youtu.be/32mGBDk3LSo"
    },
    "productId": "gid://shopify/Product/121709582"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation productCreateMedia($media: [CreateMediaInput!]!, $productId: ID!) {
        productCreateMedia(media: $media, productId: $productId) {
          media {
            alt
            mediaContentType
            status
          }
          mediaUserErrors {
            field
            message
          }
          product {
            id
            title
          }
        }
      }`,
      "variables": {
          "media": {
              "alt": "Video",
              "mediaContentType": "EXTERNAL_VIDEO",
              "originalSource": "https://youtu.be/32mGBDk3LSo"
          },
          "productId": "gid://shopify/Product/121709582"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation productCreateMedia($media: [CreateMediaInput!]!, $productId: ID!) {
    productCreateMedia(media: $media, productId: $productId) {
      media {
        alt
        mediaContentType
        status
      }
      mediaUserErrors {
        field
        message
      }
      product {
        id
        title
      }
    }
  }' \
  --variables \
  '{
    "media": {
      "alt": "Video",
      "mediaContentType": "EXTERNAL_VIDEO",
      "originalSource": "https://youtu.be/32mGBDk3LSo"
    },
    "productId": "gid://shopify/Product/121709582"
  }'
  ```

  #### Response

  ```json
  {
    "productCreateMedia": {
      "media": [
        {
          "alt": "Video",
          "mediaContentType": "EXTERNAL_VIDEO",
          "status": "UPLOADED"
        }
      ],
      "mediaUserErrors": [],
      "product": {
        "id": "gid://shopify/Product/121709582",
        "title": "Boots"
      }
    }
  }
  ```

* ### Create a new Product Image

  #### Query

  ```graphql
  mutation ProductImageCreate($id: ID!) {
    productCreateMedia(productId: $id, media: [{mediaContentType: IMAGE, originalSource: "https://path.to/image.jpg", alt: "Alt text."}]) {
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
    "id": "gid://shopify/Product/121709582"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation ProductImageCreate($id: ID!) { productCreateMedia(productId: $id, media: [{mediaContentType: IMAGE, originalSource: \"https://path.to/image.jpg\", alt: \"Alt text.\"}]) { media { id alt status ... on MediaImage { image { url } } } mediaUserErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/Product/121709582"
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
    mutation ProductImageCreate($id: ID!) {
      productCreateMedia(productId: $id, media: [{mediaContentType: IMAGE, originalSource: "https://path.to/image.jpg", alt: "Alt text."}]) {
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
          "id": "gid://shopify/Product/121709582"
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
    mutation ProductImageCreate($id: ID!) {
      productCreateMedia(productId: $id, media: [{mediaContentType: IMAGE, originalSource: "https://path.to/image.jpg", alt: "Alt text."}]) {
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
    "id": "gid://shopify/Product/121709582"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation ProductImageCreate($id: ID!) {
        productCreateMedia(productId: $id, media: [{mediaContentType: IMAGE, originalSource: "https://path.to/image.jpg", alt: "Alt text."}]) {
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
          "id": "gid://shopify/Product/121709582"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation ProductImageCreate($id: ID!) {
    productCreateMedia(productId: $id, media: [{mediaContentType: IMAGE, originalSource: "https://path.to/image.jpg", alt: "Alt text."}]) {
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
    "id": "gid://shopify/Product/121709582"
  }'
  ```

  #### Response

  ```json
  {
    "productCreateMedia": {
      "media": [
        {
          "id": "gid://shopify/MediaImage/1072273196",
          "alt": "Alt text.",
          "status": "UPLOADED",
          "image": null
        }
      ],
      "mediaUserErrors": []
    }
  }
  ```

* ### productCreateMedia reference
