---
title: productUpdate - GraphQL Admin
description: >-
  Updates a
  [product](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product)

  with attributes such as title, description, vendor, and media.


  The `productUpdate` mutation helps you modify many products at once, avoiding
  the tedious or time-consuming

  process of updating them one by one in the Shopify admin. Common examples
  including updating

  product details like status or tags.


  The `productUpdate` mutation doesn't support updating

  [product
  variants](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant).

  To update multiple product variants for a single product and manage prices,
  use the

  [`productVariantsBulkUpdate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productVariantsBulkUpdate)

  mutation.


  > Note:

  > The `productUpdate` mutation has a
  [throttle](https://shopify.dev/docs/api/usage/rate-limits#resource-based-rate-limits)

  > that takes effect when a store has 50,000 product variants. After this
  threshold is reached, no more than

  > 1,000 new product variants can be updated per day.


  After updating a product, you can make additional changes using one of the
  following mutations:


  -
  [`productSet`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productSet):

  Used to perform multiple operations on products, such as creating or modifying
  product options and variants.

  -
  [`publishablePublish`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/publishablePublish):

  Used to publish the product and make it available to customers, if the product
  is currently unpublished.


  Learn more about the [product
  model](https://shopify.dev/docs/apps/build/graphql/migrate/new-product-model)

  and [adding product
  data](https://shopify.dev/docs/apps/build/graphql/migrate/new-product-model/add-data).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/productUpdate'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/productUpdate.md'
---

# product​Update

mutation

Requires `write_products` access scope. Also: The user must have a permission to update products.

Updates a [product](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product) with attributes such as title, description, vendor, and media.

The `productUpdate` mutation helps you modify many products at once, avoiding the tedious or time-consuming process of updating them one by one in the Shopify admin. Common examples including updating product details like status or tags.

The `productUpdate` mutation doesn't support updating [product variants](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant). To update multiple product variants for a single product and manage prices, use the [`productVariantsBulkUpdate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productVariantsBulkUpdate) mutation.

***

**Note:** The \<code>\<span class="PreventFireFoxApplyingGapToWBR">product\<wbr/>Update\</span>\</code> mutation has a \<a href="https://shopify.dev/docs/api/usage/rate-limits#resource-based-rate-limits">throttle\</a> that takes effect when a store has 50,000 product variants. After this threshold is reached, no more than 1,000 new product variants can be updated per day.

***

After updating a product, you can make additional changes using one of the following mutations:

* [`productSet`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productSet): Used to perform multiple operations on products, such as creating or modifying product options and variants.
* [`publishablePublish`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/publishablePublish): Used to publish the product and make it available to customers, if the product is currently unpublished.

Learn more about the [product model](https://shopify.dev/docs/apps/build/graphql/migrate/new-product-model) and [adding product data](https://shopify.dev/docs/apps/build/graphql/migrate/new-product-model/add-data).

## Arguments

* media

  [\[Create​Media​Input!\]](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/CreateMediaInput)

  List of new media to be added to the product.

* product

  [Product​Update​Input](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/ProductUpdateInput)

  The updated properties for a product.

* input

  [Product​Input](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/ProductInput)

  Deprecated

***

## Product​Update​Payload returns

* product

  [Product](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product)

  The updated product object.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Add new media to an existing product

  #### Description

  Add new media, such as an image and a video, to an existing product. The media is \[asynchronously]\(https://shopify.dev/docs/apps/build/graphql/migrate/new-product-model/product-model-components#asynchronous-media-management) uploaded and associated with the product. This example returns the product's ID, title, and media. Learn more about \[managing media for products]\(https://shopify.dev/docs/apps/build/online-store/product-media).

  #### Query

  ```graphql
  mutation UpdateProductWithNewMedia($product: ProductUpdateInput!, $media: [CreateMediaInput!]) {
    productUpdate(product: $product, media: $media) {
      product {
        id
        media(first: 10) {
          nodes {
            alt
            mediaContentType
            preview {
              status
            }
          }
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
    "product": {
      "id": "gid://shopify/Product/912855135"
    },
    "media": [
      {
        "originalSource": "https://cdn.shopify.com/shopifycloud/brochure/assets/sell/image/image-@artdirection-large-1ba8d5de56c361cec6bc487b747c8774b9ec8203f392a99f53c028df8d0fb3fc.png",
        "alt": "Gray helmet for bikers",
        "mediaContentType": "IMAGE"
      },
      {
        "originalSource": "https://www.youtube.com/watch?v=4L8VbGRibj8&list=PLlMkWQ65HlcEoPyG9QayqEaAu0ftj0MMz",
        "alt": "Testing helmet resistance against impacts",
        "mediaContentType": "EXTERNAL_VIDEO"
      }
    ]
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation UpdateProductWithNewMedia($product: ProductUpdateInput!, $media: [CreateMediaInput!]) { productUpdate(product: $product, media: $media) { product { id media(first: 10) { nodes { alt mediaContentType preview { status } } } } userErrors { field message } } }",
   "variables": {
      "product": {
        "id": "gid://shopify/Product/912855135"
      },
      "media": [
        {
          "originalSource": "https://cdn.shopify.com/shopifycloud/brochure/assets/sell/image/image-@artdirection-large-1ba8d5de56c361cec6bc487b747c8774b9ec8203f392a99f53c028df8d0fb3fc.png",
          "alt": "Gray helmet for bikers",
          "mediaContentType": "IMAGE"
        },
        {
          "originalSource": "https://www.youtube.com/watch?v=4L8VbGRibj8&list=PLlMkWQ65HlcEoPyG9QayqEaAu0ftj0MMz",
          "alt": "Testing helmet resistance against impacts",
          "mediaContentType": "EXTERNAL_VIDEO"
        }
      ]
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
    mutation UpdateProductWithNewMedia($product: ProductUpdateInput!, $media: [CreateMediaInput!]) {
      productUpdate(product: $product, media: $media) {
        product {
          id
          media(first: 10) {
            nodes {
              alt
              mediaContentType
              preview {
                status
              }
            }
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
          "product": {
              "id": "gid://shopify/Product/912855135"
          },
          "media": [
              {
                  "originalSource": "https://cdn.shopify.com/shopifycloud/brochure/assets/sell/image/image-@artdirection-large-1ba8d5de56c361cec6bc487b747c8774b9ec8203f392a99f53c028df8d0fb3fc.png",
                  "alt": "Gray helmet for bikers",
                  "mediaContentType": "IMAGE"
              },
              {
                  "originalSource": "https://www.youtube.com/watch?v=4L8VbGRibj8&list=PLlMkWQ65HlcEoPyG9QayqEaAu0ftj0MMz",
                  "alt": "Testing helmet resistance against impacts",
                  "mediaContentType": "EXTERNAL_VIDEO"
              }
          ]
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
    mutation UpdateProductWithNewMedia($product: ProductUpdateInput!, $media: [CreateMediaInput!]) {
      productUpdate(product: $product, media: $media) {
        product {
          id
          media(first: 10) {
            nodes {
              alt
              mediaContentType
              preview {
                status
              }
            }
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
    "product": {
      "id": "gid://shopify/Product/912855135"
    },
    "media": [
      {
        "originalSource": "https://cdn.shopify.com/shopifycloud/brochure/assets/sell/image/image-@artdirection-large-1ba8d5de56c361cec6bc487b747c8774b9ec8203f392a99f53c028df8d0fb3fc.png",
        "alt": "Gray helmet for bikers",
        "mediaContentType": "IMAGE"
      },
      {
        "originalSource": "https://www.youtube.com/watch?v=4L8VbGRibj8&list=PLlMkWQ65HlcEoPyG9QayqEaAu0ftj0MMz",
        "alt": "Testing helmet resistance against impacts",
        "mediaContentType": "EXTERNAL_VIDEO"
      }
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation UpdateProductWithNewMedia($product: ProductUpdateInput!, $media: [CreateMediaInput!]) {
        productUpdate(product: $product, media: $media) {
          product {
            id
            media(first: 10) {
              nodes {
                alt
                mediaContentType
                preview {
                  status
                }
              }
            }
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "product": {
              "id": "gid://shopify/Product/912855135"
          },
          "media": [
              {
                  "originalSource": "https://cdn.shopify.com/shopifycloud/brochure/assets/sell/image/image-@artdirection-large-1ba8d5de56c361cec6bc487b747c8774b9ec8203f392a99f53c028df8d0fb3fc.png",
                  "alt": "Gray helmet for bikers",
                  "mediaContentType": "IMAGE"
              },
              {
                  "originalSource": "https://www.youtube.com/watch?v=4L8VbGRibj8&list=PLlMkWQ65HlcEoPyG9QayqEaAu0ftj0MMz",
                  "alt": "Testing helmet resistance against impacts",
                  "mediaContentType": "EXTERNAL_VIDEO"
              }
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation UpdateProductWithNewMedia($product: ProductUpdateInput!, $media: [CreateMediaInput!]) {
    productUpdate(product: $product, media: $media) {
      product {
        id
        media(first: 10) {
          nodes {
            alt
            mediaContentType
            preview {
              status
            }
          }
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
    "product": {
      "id": "gid://shopify/Product/912855135"
    },
    "media": [
      {
        "originalSource": "https://cdn.shopify.com/shopifycloud/brochure/assets/sell/image/image-@artdirection-large-1ba8d5de56c361cec6bc487b747c8774b9ec8203f392a99f53c028df8d0fb3fc.png",
        "alt": "Gray helmet for bikers",
        "mediaContentType": "IMAGE"
      },
      {
        "originalSource": "https://www.youtube.com/watch?v=4L8VbGRibj8&list=PLlMkWQ65HlcEoPyG9QayqEaAu0ftj0MMz",
        "alt": "Testing helmet resistance against impacts",
        "mediaContentType": "EXTERNAL_VIDEO"
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "productUpdate": {
      "product": {
        "id": "gid://shopify/Product/912855135",
        "media": {
          "nodes": [
            {
              "alt": "Gray helmet for bikers",
              "mediaContentType": "IMAGE",
              "preview": {
                "status": "UPLOADED"
              }
            },
            {
              "alt": "Testing helmet resistance against impacts",
              "mediaContentType": "EXTERNAL_VIDEO",
              "preview": {
                "status": "UPLOADED"
              }
            }
          ]
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Update a product with comprehensive details

  #### Description

  Update a product to include information such as SEO settings, vendor details, and tags. This example returns the product's ID, title, handle, vendor, product type, status, tags, and SEO settings. Learn more about the \[product model]\(https://shopify.dev/docs/apps/build/graphql/migrate/new-product-model) and \[adding product data]\(https://shopify.dev/docs/apps/build/graphql/migrate/new-product-model/add-data).

  #### Query

  ```graphql
  mutation UpdateProductComprehensive($product: ProductUpdateInput!) {
    productUpdate(product: $product) {
      userErrors {
        field
        message
      }
      product {
        id
        title
        handle
        vendor
        productType
        status
        tags
        seo {
          title
          description
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "product": {
      "id": "gid://shopify/Product/108828309",
      "title": "Eco-Friendly Bamboo Water Bottle",
      "handle": "eco-bamboo-water-bottle",
      "vendor": "EcoLife Products",
      "productType": "Water Bottles",
      "status": "ACTIVE",
      "tags": [
        "eco-friendly",
        "bamboo",
        "sustainable",
        "water bottle",
        "reusable"
      ],
      "seo": {
        "title": "Eco-Friendly Bamboo Water Bottle - Sustainable Hydration | EcoLife",
        "description": "Discover our premium bamboo water bottle made from 100% natural materials. Perfect for sustainable living. Free shipping available."
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
  "query": "mutation UpdateProductComprehensive($product: ProductUpdateInput!) { productUpdate(product: $product) { userErrors { field message } product { id title handle vendor productType status tags seo { title description } } } }",
   "variables": {
      "product": {
        "id": "gid://shopify/Product/108828309",
        "title": "Eco-Friendly Bamboo Water Bottle",
        "handle": "eco-bamboo-water-bottle",
        "vendor": "EcoLife Products",
        "productType": "Water Bottles",
        "status": "ACTIVE",
        "tags": [
          "eco-friendly",
          "bamboo",
          "sustainable",
          "water bottle",
          "reusable"
        ],
        "seo": {
          "title": "Eco-Friendly Bamboo Water Bottle - Sustainable Hydration | EcoLife",
          "description": "Discover our premium bamboo water bottle made from 100% natural materials. Perfect for sustainable living. Free shipping available."
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
    mutation UpdateProductComprehensive($product: ProductUpdateInput!) {
      productUpdate(product: $product) {
        userErrors {
          field
          message
        }
        product {
          id
          title
          handle
          vendor
          productType
          status
          tags
          seo {
            title
            description
          }
        }
      }
    }`,
    {
      variables: {
          "product": {
              "id": "gid://shopify/Product/108828309",
              "title": "Eco-Friendly Bamboo Water Bottle",
              "handle": "eco-bamboo-water-bottle",
              "vendor": "EcoLife Products",
              "productType": "Water Bottles",
              "status": "ACTIVE",
              "tags": [
                  "eco-friendly",
                  "bamboo",
                  "sustainable",
                  "water bottle",
                  "reusable"
              ],
              "seo": {
                  "title": "Eco-Friendly Bamboo Water Bottle - Sustainable Hydration | EcoLife",
                  "description": "Discover our premium bamboo water bottle made from 100% natural materials. Perfect for sustainable living. Free shipping available."
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
    mutation UpdateProductComprehensive($product: ProductUpdateInput!) {
      productUpdate(product: $product) {
        userErrors {
          field
          message
        }
        product {
          id
          title
          handle
          vendor
          productType
          status
          tags
          seo {
            title
            description
          }
        }
      }
    }
  QUERY

  variables = {
    "product": {
      "id": "gid://shopify/Product/108828309",
      "title": "Eco-Friendly Bamboo Water Bottle",
      "handle": "eco-bamboo-water-bottle",
      "vendor": "EcoLife Products",
      "productType": "Water Bottles",
      "status": "ACTIVE",
      "tags": [
        "eco-friendly",
        "bamboo",
        "sustainable",
        "water bottle",
        "reusable"
      ],
      "seo": {
        "title": "Eco-Friendly Bamboo Water Bottle - Sustainable Hydration | EcoLife",
        "description": "Discover our premium bamboo water bottle made from 100% natural materials. Perfect for sustainable living. Free shipping available."
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
      "query": `mutation UpdateProductComprehensive($product: ProductUpdateInput!) {
        productUpdate(product: $product) {
          userErrors {
            field
            message
          }
          product {
            id
            title
            handle
            vendor
            productType
            status
            tags
            seo {
              title
              description
            }
          }
        }
      }`,
      "variables": {
          "product": {
              "id": "gid://shopify/Product/108828309",
              "title": "Eco-Friendly Bamboo Water Bottle",
              "handle": "eco-bamboo-water-bottle",
              "vendor": "EcoLife Products",
              "productType": "Water Bottles",
              "status": "ACTIVE",
              "tags": [
                  "eco-friendly",
                  "bamboo",
                  "sustainable",
                  "water bottle",
                  "reusable"
              ],
              "seo": {
                  "title": "Eco-Friendly Bamboo Water Bottle - Sustainable Hydration | EcoLife",
                  "description": "Discover our premium bamboo water bottle made from 100% natural materials. Perfect for sustainable living. Free shipping available."
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
  'mutation UpdateProductComprehensive($product: ProductUpdateInput!) {
    productUpdate(product: $product) {
      userErrors {
        field
        message
      }
      product {
        id
        title
        handle
        vendor
        productType
        status
        tags
        seo {
          title
          description
        }
      }
    }
  }' \
  --variables \
  '{
    "product": {
      "id": "gid://shopify/Product/108828309",
      "title": "Eco-Friendly Bamboo Water Bottle",
      "handle": "eco-bamboo-water-bottle",
      "vendor": "EcoLife Products",
      "productType": "Water Bottles",
      "status": "ACTIVE",
      "tags": [
        "eco-friendly",
        "bamboo",
        "sustainable",
        "water bottle",
        "reusable"
      ],
      "seo": {
        "title": "Eco-Friendly Bamboo Water Bottle - Sustainable Hydration | EcoLife",
        "description": "Discover our premium bamboo water bottle made from 100% natural materials. Perfect for sustainable living. Free shipping available."
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "productUpdate": {
      "userErrors": [],
      "product": {
        "id": "gid://shopify/Product/108828309",
        "title": "Eco-Friendly Bamboo Water Bottle",
        "handle": "eco-bamboo-water-bottle",
        "vendor": "EcoLife Products",
        "productType": "Water Bottles",
        "status": "ACTIVE",
        "tags": [
          "bamboo",
          "eco-friendly",
          "reusable",
          "sustainable",
          "water bottle"
        ],
        "seo": {
          "title": "Eco-Friendly Bamboo Water Bottle - Sustainable Hydration | EcoLife",
          "description": "Discover our premium bamboo water bottle made from 100% natural materials. Perfect for sustainable living. Free shipping available."
        }
      }
    }
  }
  ```

* ### Update a product with custom metafields

  #### Description

  Update a product with custom metafields to track additional product information like care instructions, material composition, and warranty details. This example returns the product's ID, title, handle, and metafields. Learn more about using \[metafields]\(https://shopify.dev/docs/apps/build/custom-data).

  #### Query

  ```graphql
  mutation UpdateProductWithMetafields($product: ProductUpdateInput!) {
    productUpdate(product: $product) {
      userErrors {
        field
        message
      }
      product {
        id
        title
        handle
        metafields(first: 10) {
          edges {
            node {
              id
              namespace
              key
              value
              type
            }
          }
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "product": {
      "id": "gid://shopify/Product/108828309",
      "title": "Premium Cotton T-Shirt",
      "handle": "premium-cotton-tshirt",
      "metafields": [
        {
          "namespace": "custom",
          "key": "care_instructions",
          "value": "Machine wash cold, tumble dry low, do not bleach",
          "type": "single_line_text_field"
        },
        {
          "namespace": "custom",
          "key": "material_composition",
          "value": "100% Organic Cotton",
          "type": "single_line_text_field"
        },
        {
          "namespace": "warranty",
          "key": "warranty_period",
          "value": "12",
          "type": "number_integer"
        },
        {
          "namespace": "inventory",
          "key": "supplier_code",
          "value": "SUP-001-TCH",
          "type": "single_line_text_field"
        }
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
  "query": "mutation UpdateProductWithMetafields($product: ProductUpdateInput!) { productUpdate(product: $product) { userErrors { field message } product { id title handle metafields(first: 10) { edges { node { id namespace key value type } } } } } }",
   "variables": {
      "product": {
        "id": "gid://shopify/Product/108828309",
        "title": "Premium Cotton T-Shirt",
        "handle": "premium-cotton-tshirt",
        "metafields": [
          {
            "namespace": "custom",
            "key": "care_instructions",
            "value": "Machine wash cold, tumble dry low, do not bleach",
            "type": "single_line_text_field"
          },
          {
            "namespace": "custom",
            "key": "material_composition",
            "value": "100% Organic Cotton",
            "type": "single_line_text_field"
          },
          {
            "namespace": "warranty",
            "key": "warranty_period",
            "value": "12",
            "type": "number_integer"
          },
          {
            "namespace": "inventory",
            "key": "supplier_code",
            "value": "SUP-001-TCH",
            "type": "single_line_text_field"
          }
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
    mutation UpdateProductWithMetafields($product: ProductUpdateInput!) {
      productUpdate(product: $product) {
        userErrors {
          field
          message
        }
        product {
          id
          title
          handle
          metafields(first: 10) {
            edges {
              node {
                id
                namespace
                key
                value
                type
              }
            }
          }
        }
      }
    }`,
    {
      variables: {
          "product": {
              "id": "gid://shopify/Product/108828309",
              "title": "Premium Cotton T-Shirt",
              "handle": "premium-cotton-tshirt",
              "metafields": [
                  {
                      "namespace": "custom",
                      "key": "care_instructions",
                      "value": "Machine wash cold, tumble dry low, do not bleach",
                      "type": "single_line_text_field"
                  },
                  {
                      "namespace": "custom",
                      "key": "material_composition",
                      "value": "100% Organic Cotton",
                      "type": "single_line_text_field"
                  },
                  {
                      "namespace": "warranty",
                      "key": "warranty_period",
                      "value": "12",
                      "type": "number_integer"
                  },
                  {
                      "namespace": "inventory",
                      "key": "supplier_code",
                      "value": "SUP-001-TCH",
                      "type": "single_line_text_field"
                  }
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
    mutation UpdateProductWithMetafields($product: ProductUpdateInput!) {
      productUpdate(product: $product) {
        userErrors {
          field
          message
        }
        product {
          id
          title
          handle
          metafields(first: 10) {
            edges {
              node {
                id
                namespace
                key
                value
                type
              }
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "product": {
      "id": "gid://shopify/Product/108828309",
      "title": "Premium Cotton T-Shirt",
      "handle": "premium-cotton-tshirt",
      "metafields": [
        {
          "namespace": "custom",
          "key": "care_instructions",
          "value": "Machine wash cold, tumble dry low, do not bleach",
          "type": "single_line_text_field"
        },
        {
          "namespace": "custom",
          "key": "material_composition",
          "value": "100% Organic Cotton",
          "type": "single_line_text_field"
        },
        {
          "namespace": "warranty",
          "key": "warranty_period",
          "value": "12",
          "type": "number_integer"
        },
        {
          "namespace": "inventory",
          "key": "supplier_code",
          "value": "SUP-001-TCH",
          "type": "single_line_text_field"
        }
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
      "query": `mutation UpdateProductWithMetafields($product: ProductUpdateInput!) {
        productUpdate(product: $product) {
          userErrors {
            field
            message
          }
          product {
            id
            title
            handle
            metafields(first: 10) {
              edges {
                node {
                  id
                  namespace
                  key
                  value
                  type
                }
              }
            }
          }
        }
      }`,
      "variables": {
          "product": {
              "id": "gid://shopify/Product/108828309",
              "title": "Premium Cotton T-Shirt",
              "handle": "premium-cotton-tshirt",
              "metafields": [
                  {
                      "namespace": "custom",
                      "key": "care_instructions",
                      "value": "Machine wash cold, tumble dry low, do not bleach",
                      "type": "single_line_text_field"
                  },
                  {
                      "namespace": "custom",
                      "key": "material_composition",
                      "value": "100% Organic Cotton",
                      "type": "single_line_text_field"
                  },
                  {
                      "namespace": "warranty",
                      "key": "warranty_period",
                      "value": "12",
                      "type": "number_integer"
                  },
                  {
                      "namespace": "inventory",
                      "key": "supplier_code",
                      "value": "SUP-001-TCH",
                      "type": "single_line_text_field"
                  }
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
  'mutation UpdateProductWithMetafields($product: ProductUpdateInput!) {
    productUpdate(product: $product) {
      userErrors {
        field
        message
      }
      product {
        id
        title
        handle
        metafields(first: 10) {
          edges {
            node {
              id
              namespace
              key
              value
              type
            }
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "product": {
      "id": "gid://shopify/Product/108828309",
      "title": "Premium Cotton T-Shirt",
      "handle": "premium-cotton-tshirt",
      "metafields": [
        {
          "namespace": "custom",
          "key": "care_instructions",
          "value": "Machine wash cold, tumble dry low, do not bleach",
          "type": "single_line_text_field"
        },
        {
          "namespace": "custom",
          "key": "material_composition",
          "value": "100% Organic Cotton",
          "type": "single_line_text_field"
        },
        {
          "namespace": "warranty",
          "key": "warranty_period",
          "value": "12",
          "type": "number_integer"
        },
        {
          "namespace": "inventory",
          "key": "supplier_code",
          "value": "SUP-001-TCH",
          "type": "single_line_text_field"
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "productUpdate": {
      "userErrors": [],
      "product": {
        "id": "gid://shopify/Product/108828309",
        "title": "Premium Cotton T-Shirt",
        "handle": "premium-cotton-tshirt",
        "metafields": {
          "edges": [
            {
              "node": {
                "id": "gid://shopify/Metafield/61655654",
                "namespace": "translations",
                "key": "title_de",
                "value": "produkt",
                "type": "single_line_text_field"
              }
            },
            {
              "node": {
                "id": "gid://shopify/Metafield/147010266",
                "namespace": "information",
                "key": "exporters",
                "value": "[\"Brazil\",\"USA\",\"Mexico\",\"Canada\"]",
                "type": "list.single_line_text_field"
              }
            },
            {
              "node": {
                "id": "gid://shopify/Metafield/204658793",
                "namespace": "information",
                "key": "recyclable",
                "value": "false",
                "type": "boolean"
              }
            },
            {
              "node": {
                "id": "gid://shopify/Metafield/485513001",
                "namespace": "information",
                "key": "model",
                "value": "Ski Magic",
                "type": "single_line_text_field"
              }
            },
            {
              "node": {
                "id": "gid://shopify/Metafield/632448133",
                "namespace": "information",
                "key": "materials",
                "value": "[\"carbon fiber 4\",\"plastic - HDPE\",\"velcro\"]",
                "type": "list.single_line_text_field"
              }
            },
            {
              "node": {
                "id": "gid://shopify/Metafield/911569663",
                "namespace": "information",
                "key": "competitor_cost",
                "value": "50.35",
                "type": "float"
              }
            },
            {
              "node": {
                "id": "gid://shopify/Metafield/1007023387",
                "namespace": "information",
                "key": "year_released",
                "value": "2019",
                "type": "number_integer"
              }
            },
            {
              "node": {
                "id": "gid://shopify/Metafield/1069229912",
                "namespace": "custom",
                "key": "care_instructions",
                "value": "Machine wash cold, tumble dry low, do not bleach",
                "type": "single_line_text_field"
              }
            },
            {
              "node": {
                "id": "gid://shopify/Metafield/1069229913",
                "namespace": "custom",
                "key": "material_composition",
                "value": "100% Organic Cotton",
                "type": "single_line_text_field"
              }
            },
            {
              "node": {
                "id": "gid://shopify/Metafield/1069229914",
                "namespace": "warranty",
                "key": "warranty_period",
                "value": "12",
                "type": "number_integer"
              }
            }
          ]
        }
      }
    }
  }
  ```

* ### Update a product's title

  #### Description

  Update a product's title and return the product's ID. Learn more about \[editing product data]\(https://shopify.dev/docs/apps/build/graphql/migrate/new-product-model/edit-data).

  #### Query

  ```graphql
  mutation {
    productUpdate(product: {id: "gid://shopify/Product/108828309", title: "Sweet new product - GraphQL Edition"}) {
      product {
        id
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
  "query": "mutation { productUpdate(product: {id: \"gid://shopify/Product/108828309\", title: \"Sweet new product - GraphQL Edition\"}) { product { id } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    mutation {
      productUpdate(product: {id: "gid://shopify/Product/108828309", title: "Sweet new product - GraphQL Edition"}) {
        product {
          id
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
    mutation {
      productUpdate(product: {id: "gid://shopify/Product/108828309", title: "Sweet new product - GraphQL Edition"}) {
        product {
          id
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
    data: `mutation {
      productUpdate(product: {id: "gid://shopify/Product/108828309", title: "Sweet new product - GraphQL Edition"}) {
        product {
          id
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation {
    productUpdate(product: {id: "gid://shopify/Product/108828309", title: "Sweet new product - GraphQL Edition"}) {
      product {
        id
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "productUpdate": {
      "product": {
        "id": "gid://shopify/Product/108828309"
      }
    }
  }
  ```

* ### productUpdate reference
