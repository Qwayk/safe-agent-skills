---
title: productVariantsBulkCreate - GraphQL Admin
description: >-
  Creates multiple [product
  variants](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant)

  for a single
  [product](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product)
  in one operation.

  You can run this mutation directly or as part of a [bulk
  operation](https://shopify.dev/docs/api/usage/bulk-operations/imports)

  for large-scale catalog updates.


  Use the `productVariantsBulkCreate` mutation to efficiently add new product
  variants—such as different sizes,

  colors, or materials—to an existing product. The mutation is helpful if you
  need to add product variants in bulk,

  such as importing from an external system.


  The mutation supports:


  - Creating variants with custom option values

  - Associating media (for example, images, videos, and 3D models) with the
  product or its variants

  - Handling complex product configurations


  > Note:

  > By default, stores have a limit of 2048 product variants for each product.


  After creating variants, you can make additional changes using one of the
  following mutations:


  -
  [`productVariantsBulkUpdate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productVariantsBulkUpdate):

  Updates multiple product variants for a single product in one operation.

  -
  [`productSet`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productSet):

  Used to perform multiple operations on products, such as creating or modifying
  product options and variants.


  You can also specifically manage product options through related mutations:


  -
  [`productOptionsCreate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsCreate)

  -
  [`productOptionUpdate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionUpdate)

  -
  [`productOptionsReorder`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsReorder)

  -
  [`productOptionsDelete`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsDelete)


  Learn more about the [product
  model](https://shopify.dev/docs/apps/build/graphql/migrate/new-product-model)

  and [adding product
  data](https://shopify.dev/docs/apps/build/graphql/migrate/new-product-model/add-data).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/productVariantsBulkCreate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/productVariantsBulkCreate.md
---

# product​Variants​Bulk​Create

mutation

Requires `write_products` access scope. Also: The user must have a permission to create product variants.

Creates multiple [product variants](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant) for a single [product](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product) in one operation. You can run this mutation directly or as part of a [bulk operation](https://shopify.dev/docs/api/usage/bulk-operations/imports) for large-scale catalog updates.

Use the `productVariantsBulkCreate` mutation to efficiently add new product variants—such as different sizes, colors, or materials—to an existing product. The mutation is helpful if you need to add product variants in bulk, such as importing from an external system.

The mutation supports:

* Creating variants with custom option values
* Associating media (for example, images, videos, and 3D models) with the product or its variants
* Handling complex product configurations

***

**Note:** By default, stores have a limit of 2048 product variants for each product.

***

After creating variants, you can make additional changes using one of the following mutations:

* [`productVariantsBulkUpdate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productVariantsBulkUpdate): Updates multiple product variants for a single product in one operation.
* [`productSet`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productSet): Used to perform multiple operations on products, such as creating or modifying product options and variants.

You can also specifically manage product options through related mutations:

* [`productOptionsCreate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsCreate)
* [`productOptionUpdate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionUpdate)
* [`productOptionsReorder`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsReorder)
* [`productOptionsDelete`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsDelete)

Learn more about the [product model](https://shopify.dev/docs/apps/build/graphql/migrate/new-product-model) and [adding product data](https://shopify.dev/docs/apps/build/graphql/migrate/new-product-model/add-data).

## Arguments

* media

  [\[Create​Media​Input!\]](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/CreateMediaInput)

  List of new media to be added to the product.

* product​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the product on which to create the variants.

* strategy

  [Product​Variants​Bulk​Create​Strategy](https://shopify.dev/docs/api/admin-graphql/latest/enums/ProductVariantsBulkCreateStrategy)

  Default:DEFAULT

  The strategy defines which behavior the mutation should observe, such as whether to keep or delete the standalone variant (when product has only a single or default variant) when creating new variants in bulk.

* variants

  [\[Product​Variants​Bulk​Input!\]!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/ProductVariantsBulkInput)

  required

  An array of product variants to be created.

***

## Product​Variants​Bulk​Create​Payload returns

* product

  [Product](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product)

  The updated product object.

* product​Variants

  [\[Product​Variant!\]](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant)

  The newly created variants.

* user​Errors

  [\[Product​Variants​Bulk​Create​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariantsBulkCreateUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create a single product variant

  #### Description

  Create a "Golden" color variant for an existing product, setting a sale price of $15.99 and an original compare-at price of $19.99. The response returns the created product variant with its price, compare-at price, and selected option.

  #### Query

  ```graphql
  mutation ProductVariantsCreate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
    productVariantsBulkCreate(productId: $productId, variants: $variants) {
      productVariants {
        id
        title
        selectedOptions {
          name
          value
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
    "productId": "gid://shopify/Product/20995642",
    "variants": [
      {
        "price": 15.99,
        "compareAtPrice": 19.99,
        "optionValues": [
          {
            "name": "Golden",
            "optionId": "gid://shopify/ProductOption/328272167"
          }
        ]
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
  "query": "mutation ProductVariantsCreate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) { productVariantsBulkCreate(productId: $productId, variants: $variants) { productVariants { id title selectedOptions { name value } } userErrors { field message } } }",
   "variables": {
      "productId": "gid://shopify/Product/20995642",
      "variants": [
        {
          "price": 15.99,
          "compareAtPrice": 19.99,
          "optionValues": [
            {
              "name": "Golden",
              "optionId": "gid://shopify/ProductOption/328272167"
            }
          ]
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
    mutation ProductVariantsCreate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
      productVariantsBulkCreate(productId: $productId, variants: $variants) {
        productVariants {
          id
          title
          selectedOptions {
            name
            value
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
          "productId": "gid://shopify/Product/20995642",
          "variants": [
              {
                  "price": 15.99,
                  "compareAtPrice": 19.99,
                  "optionValues": [
                      {
                          "name": "Golden",
                          "optionId": "gid://shopify/ProductOption/328272167"
                      }
                  ]
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
    mutation ProductVariantsCreate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
      productVariantsBulkCreate(productId: $productId, variants: $variants) {
        productVariants {
          id
          title
          selectedOptions {
            name
            value
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
    "productId": "gid://shopify/Product/20995642",
    "variants": [
      {
        "price": 15.99,
        "compareAtPrice": 19.99,
        "optionValues": [
          {
            "name": "Golden",
            "optionId": "gid://shopify/ProductOption/328272167"
          }
        ]
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
      "query": `mutation ProductVariantsCreate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
        productVariantsBulkCreate(productId: $productId, variants: $variants) {
          productVariants {
            id
            title
            selectedOptions {
              name
              value
            }
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "productId": "gid://shopify/Product/20995642",
          "variants": [
              {
                  "price": 15.99,
                  "compareAtPrice": 19.99,
                  "optionValues": [
                      {
                          "name": "Golden",
                          "optionId": "gid://shopify/ProductOption/328272167"
                      }
                  ]
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
  'mutation ProductVariantsCreate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
    productVariantsBulkCreate(productId: $productId, variants: $variants) {
      productVariants {
        id
        title
        selectedOptions {
          name
          value
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
    "productId": "gid://shopify/Product/20995642",
    "variants": [
      {
        "price": 15.99,
        "compareAtPrice": 19.99,
        "optionValues": [
          {
            "name": "Golden",
            "optionId": "gid://shopify/ProductOption/328272167"
          }
        ]
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "productVariantsBulkCreate": {
      "productVariants": [
        {
          "id": "gid://shopify/ProductVariant/1070325338",
          "title": "Golden",
          "selectedOptions": [
            {
              "name": "Title",
              "value": "Golden"
            }
          ]
        }
      ],
      "userErrors": []
    }
  }
  ```

* ### Create metafields when creating product variants in bulk

  #### Description

  Create a new metafield \`my\_fields.liner\_material\` with different values for new product variants created in bulk on a specific product. The response returns the created product variants with their associated metafields, demonstrating how metafields are successfully attached to variants during bulk creation.

  #### Query

  ```graphql
  mutation productVariantsBulkCreate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
    productVariantsBulkCreate(productId: $productId, variants: $variants) {
      product {
        id
      }
      productVariants {
        id
        metafields(first: 1) {
          edges {
            node {
              namespace
              key
              value
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
    "productId": "gid://shopify/Product/20995642",
    "variants": [
      {
        "optionValues": [
          {
            "name": "Fashionable",
            "optionName": "Title"
          }
        ],
        "metafields": [
          {
            "namespace": "my_fields",
            "key": "liner_material",
            "type": "single_line_text_field",
            "value": "Synthetic Leather"
          }
        ]
      },
      {
        "optionValues": [
          {
            "name": "Rugged",
            "optionName": "Title"
          }
        ],
        "metafields": [
          {
            "namespace": "my_fields",
            "key": "liner_material",
            "type": "single_line_text_field",
            "value": "Reinforced Polyethylene"
          }
        ]
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
  "query": "mutation productVariantsBulkCreate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) { productVariantsBulkCreate(productId: $productId, variants: $variants) { product { id } productVariants { id metafields(first: 1) { edges { node { namespace key value } } } } userErrors { field message } } }",
   "variables": {
      "productId": "gid://shopify/Product/20995642",
      "variants": [
        {
          "optionValues": [
            {
              "name": "Fashionable",
              "optionName": "Title"
            }
          ],
          "metafields": [
            {
              "namespace": "my_fields",
              "key": "liner_material",
              "type": "single_line_text_field",
              "value": "Synthetic Leather"
            }
          ]
        },
        {
          "optionValues": [
            {
              "name": "Rugged",
              "optionName": "Title"
            }
          ],
          "metafields": [
            {
              "namespace": "my_fields",
              "key": "liner_material",
              "type": "single_line_text_field",
              "value": "Reinforced Polyethylene"
            }
          ]
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
    mutation productVariantsBulkCreate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
      productVariantsBulkCreate(productId: $productId, variants: $variants) {
        product {
          id
        }
        productVariants {
          id
          metafields(first: 1) {
            edges {
              node {
                namespace
                key
                value
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
          "productId": "gid://shopify/Product/20995642",
          "variants": [
              {
                  "optionValues": [
                      {
                          "name": "Fashionable",
                          "optionName": "Title"
                      }
                  ],
                  "metafields": [
                      {
                          "namespace": "my_fields",
                          "key": "liner_material",
                          "type": "single_line_text_field",
                          "value": "Synthetic Leather"
                      }
                  ]
              },
              {
                  "optionValues": [
                      {
                          "name": "Rugged",
                          "optionName": "Title"
                      }
                  ],
                  "metafields": [
                      {
                          "namespace": "my_fields",
                          "key": "liner_material",
                          "type": "single_line_text_field",
                          "value": "Reinforced Polyethylene"
                      }
                  ]
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
    mutation productVariantsBulkCreate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
      productVariantsBulkCreate(productId: $productId, variants: $variants) {
        product {
          id
        }
        productVariants {
          id
          metafields(first: 1) {
            edges {
              node {
                namespace
                key
                value
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
    "productId": "gid://shopify/Product/20995642",
    "variants": [
      {
        "optionValues": [
          {
            "name": "Fashionable",
            "optionName": "Title"
          }
        ],
        "metafields": [
          {
            "namespace": "my_fields",
            "key": "liner_material",
            "type": "single_line_text_field",
            "value": "Synthetic Leather"
          }
        ]
      },
      {
        "optionValues": [
          {
            "name": "Rugged",
            "optionName": "Title"
          }
        ],
        "metafields": [
          {
            "namespace": "my_fields",
            "key": "liner_material",
            "type": "single_line_text_field",
            "value": "Reinforced Polyethylene"
          }
        ]
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
      "query": `mutation productVariantsBulkCreate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
        productVariantsBulkCreate(productId: $productId, variants: $variants) {
          product {
            id
          }
          productVariants {
            id
            metafields(first: 1) {
              edges {
                node {
                  namespace
                  key
                  value
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
          "productId": "gid://shopify/Product/20995642",
          "variants": [
              {
                  "optionValues": [
                      {
                          "name": "Fashionable",
                          "optionName": "Title"
                      }
                  ],
                  "metafields": [
                      {
                          "namespace": "my_fields",
                          "key": "liner_material",
                          "type": "single_line_text_field",
                          "value": "Synthetic Leather"
                      }
                  ]
              },
              {
                  "optionValues": [
                      {
                          "name": "Rugged",
                          "optionName": "Title"
                      }
                  ],
                  "metafields": [
                      {
                          "namespace": "my_fields",
                          "key": "liner_material",
                          "type": "single_line_text_field",
                          "value": "Reinforced Polyethylene"
                      }
                  ]
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
  'mutation productVariantsBulkCreate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
    productVariantsBulkCreate(productId: $productId, variants: $variants) {
      product {
        id
      }
      productVariants {
        id
        metafields(first: 1) {
          edges {
            node {
              namespace
              key
              value
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
    "productId": "gid://shopify/Product/20995642",
    "variants": [
      {
        "optionValues": [
          {
            "name": "Fashionable",
            "optionName": "Title"
          }
        ],
        "metafields": [
          {
            "namespace": "my_fields",
            "key": "liner_material",
            "type": "single_line_text_field",
            "value": "Synthetic Leather"
          }
        ]
      },
      {
        "optionValues": [
          {
            "name": "Rugged",
            "optionName": "Title"
          }
        ],
        "metafields": [
          {
            "namespace": "my_fields",
            "key": "liner_material",
            "type": "single_line_text_field",
            "value": "Reinforced Polyethylene"
          }
        ]
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "productVariantsBulkCreate": {
      "product": {
        "id": "gid://shopify/Product/20995642"
      },
      "productVariants": [
        {
          "id": "gid://shopify/ProductVariant/1070325341",
          "metafields": {
            "edges": [
              {
                "node": {
                  "namespace": "my_fields",
                  "key": "liner_material",
                  "value": "Synthetic Leather"
                }
              }
            ]
          }
        },
        {
          "id": "gid://shopify/ProductVariant/1070325342",
          "metafields": {
            "edges": [
              {
                "node": {
                  "namespace": "my_fields",
                  "key": "liner_material",
                  "value": "Reinforced Polyethylene"
                }
              }
            ]
          }
        }
      ],
      "userErrors": []
    }
  }
  ```

* ### Create product variants and attach existing media

  #### Description

  Create two variants, with one variant attached to existing media that is associated with the product, and the other variant without any media attached. The response returns the created variants showing the media association, with one variant containing media nodes and the other containing an empty media array.

  #### Query

  ```graphql
  mutation CreateProductVariantsInBulkWithExistingMedia($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
    productVariantsBulkCreate(productId: $productId, variants: $variants) {
      product {
        id
      }
      productVariants {
        id
        title
        media(first: 10) {
          nodes {
            id
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
    "productId": "gid://shopify/Product/20995642",
    "variants": [
      {
        "optionValues": [
          {
            "name": "one",
            "optionName": "Title"
          }
        ],
        "mediaId": "gid://shopify/MediaImage/730211239"
      },
      {
        "optionValues": [
          {
            "name": "two",
            "optionName": "Title"
          }
        ]
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
  "query": "mutation CreateProductVariantsInBulkWithExistingMedia($productId: ID!, $variants: [ProductVariantsBulkInput!]!) { productVariantsBulkCreate(productId: $productId, variants: $variants) { product { id } productVariants { id title media(first: 10) { nodes { id alt mediaContentType preview { status } } } } userErrors { field message } } }",
   "variables": {
      "productId": "gid://shopify/Product/20995642",
      "variants": [
        {
          "optionValues": [
            {
              "name": "one",
              "optionName": "Title"
            }
          ],
          "mediaId": "gid://shopify/MediaImage/730211239"
        },
        {
          "optionValues": [
            {
              "name": "two",
              "optionName": "Title"
            }
          ]
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
    mutation CreateProductVariantsInBulkWithExistingMedia($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
      productVariantsBulkCreate(productId: $productId, variants: $variants) {
        product {
          id
        }
        productVariants {
          id
          title
          media(first: 10) {
            nodes {
              id
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
          "productId": "gid://shopify/Product/20995642",
          "variants": [
              {
                  "optionValues": [
                      {
                          "name": "one",
                          "optionName": "Title"
                      }
                  ],
                  "mediaId": "gid://shopify/MediaImage/730211239"
              },
              {
                  "optionValues": [
                      {
                          "name": "two",
                          "optionName": "Title"
                      }
                  ]
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
    mutation CreateProductVariantsInBulkWithExistingMedia($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
      productVariantsBulkCreate(productId: $productId, variants: $variants) {
        product {
          id
        }
        productVariants {
          id
          title
          media(first: 10) {
            nodes {
              id
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
    "productId": "gid://shopify/Product/20995642",
    "variants": [
      {
        "optionValues": [
          {
            "name": "one",
            "optionName": "Title"
          }
        ],
        "mediaId": "gid://shopify/MediaImage/730211239"
      },
      {
        "optionValues": [
          {
            "name": "two",
            "optionName": "Title"
          }
        ]
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
      "query": `mutation CreateProductVariantsInBulkWithExistingMedia($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
        productVariantsBulkCreate(productId: $productId, variants: $variants) {
          product {
            id
          }
          productVariants {
            id
            title
            media(first: 10) {
              nodes {
                id
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
          "productId": "gid://shopify/Product/20995642",
          "variants": [
              {
                  "optionValues": [
                      {
                          "name": "one",
                          "optionName": "Title"
                      }
                  ],
                  "mediaId": "gid://shopify/MediaImage/730211239"
              },
              {
                  "optionValues": [
                      {
                          "name": "two",
                          "optionName": "Title"
                      }
                  ]
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
  'mutation CreateProductVariantsInBulkWithExistingMedia($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
    productVariantsBulkCreate(productId: $productId, variants: $variants) {
      product {
        id
      }
      productVariants {
        id
        title
        media(first: 10) {
          nodes {
            id
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
    "productId": "gid://shopify/Product/20995642",
    "variants": [
      {
        "optionValues": [
          {
            "name": "one",
            "optionName": "Title"
          }
        ],
        "mediaId": "gid://shopify/MediaImage/730211239"
      },
      {
        "optionValues": [
          {
            "name": "two",
            "optionName": "Title"
          }
        ]
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "productVariantsBulkCreate": {
      "product": {
        "id": "gid://shopify/Product/20995642"
      },
      "productVariants": [
        {
          "id": "gid://shopify/ProductVariant/1070325343",
          "title": "one",
          "media": {
            "nodes": [
              {
                "id": "gid://shopify/MediaImage/730211239",
                "alt": "a snowboard",
                "mediaContentType": "IMAGE",
                "preview": {
                  "status": "READY"
                }
              }
            ]
          }
        },
        {
          "id": "gid://shopify/ProductVariant/1070325344",
          "title": "two",
          "media": {
            "nodes": []
          }
        }
      ],
      "userErrors": []
    }
  }
  ```

* ### Create product variants with and without compare-at prices

  #### Description

  Create two variants that each cost $15.99, with one variant that has a compare-at price set to $19.99, and the other variant that doesn't have a price set. The response returns both product variants with their price and compare-at price fields.

  #### Query

  ```graphql
  mutation productVariantsBulkCreate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
    productVariantsBulkCreate(productId: $productId, variants: $variants) {
      product {
        id
      }
      productVariants {
        id
        title
        price
        compareAtPrice
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
    "productId": "gid://shopify/Product/20995642",
    "variants": [
      {
        "optionValues": [
          {
            "name": "Golden",
            "optionName": "Title"
          }
        ],
        "price": 15.99,
        "compareAtPrice": 19.99
      },
      {
        "optionValues": [
          {
            "name": "Silver",
            "optionName": "Title"
          }
        ],
        "price": 15.99,
        "compareAtPrice": null
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
  "query": "mutation productVariantsBulkCreate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) { productVariantsBulkCreate(productId: $productId, variants: $variants) { product { id } productVariants { id title price compareAtPrice } userErrors { field message } } }",
   "variables": {
      "productId": "gid://shopify/Product/20995642",
      "variants": [
        {
          "optionValues": [
            {
              "name": "Golden",
              "optionName": "Title"
            }
          ],
          "price": 15.99,
          "compareAtPrice": 19.99
        },
        {
          "optionValues": [
            {
              "name": "Silver",
              "optionName": "Title"
            }
          ],
          "price": 15.99,
          "compareAtPrice": null
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
    mutation productVariantsBulkCreate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
      productVariantsBulkCreate(productId: $productId, variants: $variants) {
        product {
          id
        }
        productVariants {
          id
          title
          price
          compareAtPrice
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "productId": "gid://shopify/Product/20995642",
          "variants": [
              {
                  "optionValues": [
                      {
                          "name": "Golden",
                          "optionName": "Title"
                      }
                  ],
                  "price": 15.99,
                  "compareAtPrice": 19.99
              },
              {
                  "optionValues": [
                      {
                          "name": "Silver",
                          "optionName": "Title"
                      }
                  ],
                  "price": 15.99,
                  "compareAtPrice": null
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
    mutation productVariantsBulkCreate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
      productVariantsBulkCreate(productId: $productId, variants: $variants) {
        product {
          id
        }
        productVariants {
          id
          title
          price
          compareAtPrice
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "productId": "gid://shopify/Product/20995642",
    "variants": [
      {
        "optionValues": [
          {
            "name": "Golden",
            "optionName": "Title"
          }
        ],
        "price": 15.99,
        "compareAtPrice": 19.99
      },
      {
        "optionValues": [
          {
            "name": "Silver",
            "optionName": "Title"
          }
        ],
        "price": 15.99,
        "compareAtPrice": null
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
      "query": `mutation productVariantsBulkCreate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
        productVariantsBulkCreate(productId: $productId, variants: $variants) {
          product {
            id
          }
          productVariants {
            id
            title
            price
            compareAtPrice
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "productId": "gid://shopify/Product/20995642",
          "variants": [
              {
                  "optionValues": [
                      {
                          "name": "Golden",
                          "optionName": "Title"
                      }
                  ],
                  "price": 15.99,
                  "compareAtPrice": 19.99
              },
              {
                  "optionValues": [
                      {
                          "name": "Silver",
                          "optionName": "Title"
                      }
                  ],
                  "price": 15.99,
                  "compareAtPrice": null
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
  'mutation productVariantsBulkCreate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
    productVariantsBulkCreate(productId: $productId, variants: $variants) {
      product {
        id
      }
      productVariants {
        id
        title
        price
        compareAtPrice
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "productId": "gid://shopify/Product/20995642",
    "variants": [
      {
        "optionValues": [
          {
            "name": "Golden",
            "optionName": "Title"
          }
        ],
        "price": 15.99,
        "compareAtPrice": 19.99
      },
      {
        "optionValues": [
          {
            "name": "Silver",
            "optionName": "Title"
          }
        ],
        "price": 15.99,
        "compareAtPrice": null
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "productVariantsBulkCreate": {
      "product": {
        "id": "gid://shopify/Product/20995642"
      },
      "productVariants": [
        {
          "id": "gid://shopify/ProductVariant/1070325350",
          "title": "Golden",
          "price": "15.99",
          "compareAtPrice": "19.99"
        },
        {
          "id": "gid://shopify/ProductVariant/1070325351",
          "title": "Silver",
          "price": "15.99",
          "compareAtPrice": null
        }
      ],
      "userErrors": []
    }
  }
  ```

* ### Create product variants with new and existing option values

  #### Description

  Creates variants with the option values specified. Both the option and the option value can be specified with either an ID or a name, and these can be freely combined. An option referenced with either the \`optionId\` or \`optionName\` field must exist on the product. An option value specified with the \`id\` field must exist on the option. When using the \`optionValue\` field to specify an option value by \`name\`, an existing value is linked to the new variant if an option value with the name exists on the option. Otherwise, a new option value is created. All variants must have one value specified for every existing product option. The response returns the product with its updated options and option values, as well as the created variants with their selected options.

  #### Query

  ```graphql
  mutation productVariantsBulkCreate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
    productVariantsBulkCreate(productId: $productId, variants: $variants) {
      userErrors {
        field
        message
      }
      product {
        id
        options {
          id
          name
          values
          position
          optionValues {
            id
            name
            hasVariants
          }
        }
      }
      productVariants {
        id
        title
        selectedOptions {
          name
          value
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "productId": "gid://shopify/Product/1072481087",
    "variants": [
      {
        "optionValues": [
          {
            "name": "Red",
            "optionName": "Color"
          },
          {
            "name": "Brand new style",
            "optionId": "gid://shopify/ProductOption/1064576573"
          },
          {
            "name": "Silk",
            "optionName": "Material"
          }
        ],
        "price": 22
      },
      {
        "optionValues": [
          {
            "name": "Brand new style",
            "optionName": "Style"
          },
          {
            "id": "gid://shopify/ProductOptionValue/1054672624",
            "optionName": "Color"
          },
          {
            "name": "Silk",
            "optionName": "Material"
          }
        ],
        "price": 23.5
      },
      {
        "optionValues": [
          {
            "name": "Brand new style",
            "optionId": "gid://shopify/ProductOption/1064576573"
          },
          {
            "id": "gid://shopify/ProductOptionValue/1054672625",
            "optionId": "gid://shopify/ProductOption/1064576572"
          },
          {
            "id": "gid://shopify/ProductOptionValue/1054672627",
            "optionId": "gid://shopify/ProductOption/1064576574"
          }
        ],
        "price": 29.5
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
  "query": "mutation productVariantsBulkCreate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) { productVariantsBulkCreate(productId: $productId, variants: $variants) { userErrors { field message } product { id options { id name values position optionValues { id name hasVariants } } } productVariants { id title selectedOptions { name value } } } }",
   "variables": {
      "productId": "gid://shopify/Product/1072481087",
      "variants": [
        {
          "optionValues": [
            {
              "name": "Red",
              "optionName": "Color"
            },
            {
              "name": "Brand new style",
              "optionId": "gid://shopify/ProductOption/1064576573"
            },
            {
              "name": "Silk",
              "optionName": "Material"
            }
          ],
          "price": 22
        },
        {
          "optionValues": [
            {
              "name": "Brand new style",
              "optionName": "Style"
            },
            {
              "id": "gid://shopify/ProductOptionValue/1054672624",
              "optionName": "Color"
            },
            {
              "name": "Silk",
              "optionName": "Material"
            }
          ],
          "price": 23.5
        },
        {
          "optionValues": [
            {
              "name": "Brand new style",
              "optionId": "gid://shopify/ProductOption/1064576573"
            },
            {
              "id": "gid://shopify/ProductOptionValue/1054672625",
              "optionId": "gid://shopify/ProductOption/1064576572"
            },
            {
              "id": "gid://shopify/ProductOptionValue/1054672627",
              "optionId": "gid://shopify/ProductOption/1064576574"
            }
          ],
          "price": 29.5
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
    mutation productVariantsBulkCreate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
      productVariantsBulkCreate(productId: $productId, variants: $variants) {
        userErrors {
          field
          message
        }
        product {
          id
          options {
            id
            name
            values
            position
            optionValues {
              id
              name
              hasVariants
            }
          }
        }
        productVariants {
          id
          title
          selectedOptions {
            name
            value
          }
        }
      }
    }`,
    {
      variables: {
          "productId": "gid://shopify/Product/1072481087",
          "variants": [
              {
                  "optionValues": [
                      {
                          "name": "Red",
                          "optionName": "Color"
                      },
                      {
                          "name": "Brand new style",
                          "optionId": "gid://shopify/ProductOption/1064576573"
                      },
                      {
                          "name": "Silk",
                          "optionName": "Material"
                      }
                  ],
                  "price": 22
              },
              {
                  "optionValues": [
                      {
                          "name": "Brand new style",
                          "optionName": "Style"
                      },
                      {
                          "id": "gid://shopify/ProductOptionValue/1054672624",
                          "optionName": "Color"
                      },
                      {
                          "name": "Silk",
                          "optionName": "Material"
                      }
                  ],
                  "price": 23.5
              },
              {
                  "optionValues": [
                      {
                          "name": "Brand new style",
                          "optionId": "gid://shopify/ProductOption/1064576573"
                      },
                      {
                          "id": "gid://shopify/ProductOptionValue/1054672625",
                          "optionId": "gid://shopify/ProductOption/1064576572"
                      },
                      {
                          "id": "gid://shopify/ProductOptionValue/1054672627",
                          "optionId": "gid://shopify/ProductOption/1064576574"
                      }
                  ],
                  "price": 29.5
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
    mutation productVariantsBulkCreate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
      productVariantsBulkCreate(productId: $productId, variants: $variants) {
        userErrors {
          field
          message
        }
        product {
          id
          options {
            id
            name
            values
            position
            optionValues {
              id
              name
              hasVariants
            }
          }
        }
        productVariants {
          id
          title
          selectedOptions {
            name
            value
          }
        }
      }
    }
  QUERY

  variables = {
    "productId": "gid://shopify/Product/1072481087",
    "variants": [
      {
        "optionValues": [
          {
            "name": "Red",
            "optionName": "Color"
          },
          {
            "name": "Brand new style",
            "optionId": "gid://shopify/ProductOption/1064576573"
          },
          {
            "name": "Silk",
            "optionName": "Material"
          }
        ],
        "price": 22
      },
      {
        "optionValues": [
          {
            "name": "Brand new style",
            "optionName": "Style"
          },
          {
            "id": "gid://shopify/ProductOptionValue/1054672624",
            "optionName": "Color"
          },
          {
            "name": "Silk",
            "optionName": "Material"
          }
        ],
        "price": 23.5
      },
      {
        "optionValues": [
          {
            "name": "Brand new style",
            "optionId": "gid://shopify/ProductOption/1064576573"
          },
          {
            "id": "gid://shopify/ProductOptionValue/1054672625",
            "optionId": "gid://shopify/ProductOption/1064576572"
          },
          {
            "id": "gid://shopify/ProductOptionValue/1054672627",
            "optionId": "gid://shopify/ProductOption/1064576574"
          }
        ],
        "price": 29.5
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
      "query": `mutation productVariantsBulkCreate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
        productVariantsBulkCreate(productId: $productId, variants: $variants) {
          userErrors {
            field
            message
          }
          product {
            id
            options {
              id
              name
              values
              position
              optionValues {
                id
                name
                hasVariants
              }
            }
          }
          productVariants {
            id
            title
            selectedOptions {
              name
              value
            }
          }
        }
      }`,
      "variables": {
          "productId": "gid://shopify/Product/1072481087",
          "variants": [
              {
                  "optionValues": [
                      {
                          "name": "Red",
                          "optionName": "Color"
                      },
                      {
                          "name": "Brand new style",
                          "optionId": "gid://shopify/ProductOption/1064576573"
                      },
                      {
                          "name": "Silk",
                          "optionName": "Material"
                      }
                  ],
                  "price": 22
              },
              {
                  "optionValues": [
                      {
                          "name": "Brand new style",
                          "optionName": "Style"
                      },
                      {
                          "id": "gid://shopify/ProductOptionValue/1054672624",
                          "optionName": "Color"
                      },
                      {
                          "name": "Silk",
                          "optionName": "Material"
                      }
                  ],
                  "price": 23.5
              },
              {
                  "optionValues": [
                      {
                          "name": "Brand new style",
                          "optionId": "gid://shopify/ProductOption/1064576573"
                      },
                      {
                          "id": "gid://shopify/ProductOptionValue/1054672625",
                          "optionId": "gid://shopify/ProductOption/1064576572"
                      },
                      {
                          "id": "gid://shopify/ProductOptionValue/1054672627",
                          "optionId": "gid://shopify/ProductOption/1064576574"
                      }
                  ],
                  "price": 29.5
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
  'mutation productVariantsBulkCreate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
    productVariantsBulkCreate(productId: $productId, variants: $variants) {
      userErrors {
        field
        message
      }
      product {
        id
        options {
          id
          name
          values
          position
          optionValues {
            id
            name
            hasVariants
          }
        }
      }
      productVariants {
        id
        title
        selectedOptions {
          name
          value
        }
      }
    }
  }' \
  --variables \
  '{
    "productId": "gid://shopify/Product/1072481087",
    "variants": [
      {
        "optionValues": [
          {
            "name": "Red",
            "optionName": "Color"
          },
          {
            "name": "Brand new style",
            "optionId": "gid://shopify/ProductOption/1064576573"
          },
          {
            "name": "Silk",
            "optionName": "Material"
          }
        ],
        "price": 22
      },
      {
        "optionValues": [
          {
            "name": "Brand new style",
            "optionName": "Style"
          },
          {
            "id": "gid://shopify/ProductOptionValue/1054672624",
            "optionName": "Color"
          },
          {
            "name": "Silk",
            "optionName": "Material"
          }
        ],
        "price": 23.5
      },
      {
        "optionValues": [
          {
            "name": "Brand new style",
            "optionId": "gid://shopify/ProductOption/1064576573"
          },
          {
            "id": "gid://shopify/ProductOptionValue/1054672625",
            "optionId": "gid://shopify/ProductOption/1064576572"
          },
          {
            "id": "gid://shopify/ProductOptionValue/1054672627",
            "optionId": "gid://shopify/ProductOption/1064576574"
          }
        ],
        "price": 29.5
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "productVariantsBulkCreate": {
      "userErrors": [],
      "product": {
        "id": "gid://shopify/Product/1072481087",
        "options": [
          {
            "id": "gid://shopify/ProductOption/1064576572",
            "name": "Color",
            "values": [
              "Blue",
              "Red"
            ],
            "position": 1,
            "optionValues": [
              {
                "id": "gid://shopify/ProductOptionValue/1054672624",
                "name": "Blue",
                "hasVariants": true
              },
              {
                "id": "gid://shopify/ProductOptionValue/1054672625",
                "name": "Red",
                "hasVariants": true
              }
            ]
          },
          {
            "id": "gid://shopify/ProductOption/1064576573",
            "name": "Style",
            "values": [
              "Old style",
              "Brand new style"
            ],
            "position": 2,
            "optionValues": [
              {
                "id": "gid://shopify/ProductOptionValue/1054672626",
                "name": "Old style",
                "hasVariants": true
              },
              {
                "id": "gid://shopify/ProductOptionValue/1054672629",
                "name": "Brand new style",
                "hasVariants": true
              }
            ]
          },
          {
            "id": "gid://shopify/ProductOption/1064576574",
            "name": "Material",
            "values": [
              "Polyester",
              "Silk"
            ],
            "position": 3,
            "optionValues": [
              {
                "id": "gid://shopify/ProductOptionValue/1054672627",
                "name": "Polyester",
                "hasVariants": true
              },
              {
                "id": "gid://shopify/ProductOptionValue/1054672628",
                "name": "Silk",
                "hasVariants": true
              }
            ]
          }
        ]
      },
      "productVariants": [
        {
          "id": "gid://shopify/ProductVariant/1070325347",
          "title": "Red / Brand new style / Silk",
          "selectedOptions": [
            {
              "name": "Color",
              "value": "Red"
            },
            {
              "name": "Style",
              "value": "Brand new style"
            },
            {
              "name": "Material",
              "value": "Silk"
            }
          ]
        },
        {
          "id": "gid://shopify/ProductVariant/1070325348",
          "title": "Blue / Brand new style / Silk",
          "selectedOptions": [
            {
              "name": "Color",
              "value": "Blue"
            },
            {
              "name": "Style",
              "value": "Brand new style"
            },
            {
              "name": "Material",
              "value": "Silk"
            }
          ]
        },
        {
          "id": "gid://shopify/ProductVariant/1070325349",
          "title": "Red / Brand new style / Polyester",
          "selectedOptions": [
            {
              "name": "Color",
              "value": "Red"
            },
            {
              "name": "Style",
              "value": "Brand new style"
            },
            {
              "name": "Material",
              "value": "Polyester"
            }
          ]
        }
      ]
    }
  }
  ```

* ### Handle non-existent product errors

  #### Description

  Trying to create product variants with non-existent product IDs returns \`null\`. The response demonstrates error handling by returning \`null\` for the \`product\` field, an empty array for \`productVariants\`, and a user error with the message "Product does not exist".

  #### Query

  ```graphql
  mutation productVariantsBulkCreate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
    productVariantsBulkCreate(productId: $productId, variants: $variants) {
      product {
        id
      }
      productVariants {
        id
        title
        price
        compareAtPrice
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
    "productId": "gid://shopify/Product/-1",
    "variants": [
      {
        "optionValues": [
          {
            "name": "Golden",
            "optionName": "Title"
          }
        ],
        "price": 15.99,
        "compareAtPrice": 19.99
      },
      {
        "optionValues": [
          {
            "name": "Silver",
            "optionName": "Title"
          }
        ],
        "price": 13.99,
        "compareAtPrice": null
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
  "query": "mutation productVariantsBulkCreate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) { productVariantsBulkCreate(productId: $productId, variants: $variants) { product { id } productVariants { id title price compareAtPrice } userErrors { field message } } }",
   "variables": {
      "productId": "gid://shopify/Product/-1",
      "variants": [
        {
          "optionValues": [
            {
              "name": "Golden",
              "optionName": "Title"
            }
          ],
          "price": 15.99,
          "compareAtPrice": 19.99
        },
        {
          "optionValues": [
            {
              "name": "Silver",
              "optionName": "Title"
            }
          ],
          "price": 13.99,
          "compareAtPrice": null
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
    mutation productVariantsBulkCreate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
      productVariantsBulkCreate(productId: $productId, variants: $variants) {
        product {
          id
        }
        productVariants {
          id
          title
          price
          compareAtPrice
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "productId": "gid://shopify/Product/-1",
          "variants": [
              {
                  "optionValues": [
                      {
                          "name": "Golden",
                          "optionName": "Title"
                      }
                  ],
                  "price": 15.99,
                  "compareAtPrice": 19.99
              },
              {
                  "optionValues": [
                      {
                          "name": "Silver",
                          "optionName": "Title"
                      }
                  ],
                  "price": 13.99,
                  "compareAtPrice": null
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
    mutation productVariantsBulkCreate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
      productVariantsBulkCreate(productId: $productId, variants: $variants) {
        product {
          id
        }
        productVariants {
          id
          title
          price
          compareAtPrice
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "productId": "gid://shopify/Product/-1",
    "variants": [
      {
        "optionValues": [
          {
            "name": "Golden",
            "optionName": "Title"
          }
        ],
        "price": 15.99,
        "compareAtPrice": 19.99
      },
      {
        "optionValues": [
          {
            "name": "Silver",
            "optionName": "Title"
          }
        ],
        "price": 13.99,
        "compareAtPrice": null
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
      "query": `mutation productVariantsBulkCreate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
        productVariantsBulkCreate(productId: $productId, variants: $variants) {
          product {
            id
          }
          productVariants {
            id
            title
            price
            compareAtPrice
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "productId": "gid://shopify/Product/-1",
          "variants": [
              {
                  "optionValues": [
                      {
                          "name": "Golden",
                          "optionName": "Title"
                      }
                  ],
                  "price": 15.99,
                  "compareAtPrice": 19.99
              },
              {
                  "optionValues": [
                      {
                          "name": "Silver",
                          "optionName": "Title"
                      }
                  ],
                  "price": 13.99,
                  "compareAtPrice": null
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
  'mutation productVariantsBulkCreate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
    productVariantsBulkCreate(productId: $productId, variants: $variants) {
      product {
        id
      }
      productVariants {
        id
        title
        price
        compareAtPrice
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "productId": "gid://shopify/Product/-1",
    "variants": [
      {
        "optionValues": [
          {
            "name": "Golden",
            "optionName": "Title"
          }
        ],
        "price": 15.99,
        "compareAtPrice": 19.99
      },
      {
        "optionValues": [
          {
            "name": "Silver",
            "optionName": "Title"
          }
        ],
        "price": 13.99,
        "compareAtPrice": null
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "productVariantsBulkCreate": {
      "product": null,
      "productVariants": [],
      "userErrors": [
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

* ### productVariantsBulkCreate reference
