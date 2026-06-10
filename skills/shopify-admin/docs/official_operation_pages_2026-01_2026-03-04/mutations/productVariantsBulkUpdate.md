---
title: productVariantsBulkUpdate - GraphQL Admin
description: >-
  Updates multiple [product
  variants](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant)

  for a single
  [product](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product)
  in one operation.

  You can run this mutation directly or as part of a [bulk
  operation](https://shopify.dev/docs/api/usage/bulk-operations/imports)

  for large-scale catalog updates.


  Use the `productVariantsBulkUpdate` mutation to efficiently modify product
  variants—such as different sizes,

  colors, or materials—associated with an existing product. The mutation is
  helpful if you need to update a

  product's variants in bulk, such as importing from an external system.


  The mutation supports:


  - Updating variants with custom option values

  - Associating media (for example, images, videos, and 3D models) with the
  product or its variants

  - Handling complex product configurations


  > Note:

  > By default, stores have a limit of 2048 product variants for each product.


  After creating variants, you can make additional changes using the

  [`productSet`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productSet)
  mutation,

  which is used to perform multiple operations on products, such as creating or
  modifying product options and variants.


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
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/productVariantsBulkUpdate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/productVariantsBulkUpdate.md
---

# product​Variants​Bulk​Update

mutation

Requires `write_products` access scope. Also: The user must have a permission to update product variants.

Updates multiple [product variants](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant) for a single [product](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product) in one operation. You can run this mutation directly or as part of a [bulk operation](https://shopify.dev/docs/api/usage/bulk-operations/imports) for large-scale catalog updates.

Use the `productVariantsBulkUpdate` mutation to efficiently modify product variants—such as different sizes, colors, or materials—associated with an existing product. The mutation is helpful if you need to update a product's variants in bulk, such as importing from an external system.

The mutation supports:

* Updating variants with custom option values
* Associating media (for example, images, videos, and 3D models) with the product or its variants
* Handling complex product configurations

***

**Note:** By default, stores have a limit of 2048 product variants for each product.

***

After creating variants, you can make additional changes using the [`productSet`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productSet) mutation, which is used to perform multiple operations on products, such as creating or modifying product options and variants.

You can also specifically manage product options through related mutations:

* [`productOptionsCreate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsCreate)
* [`productOptionUpdate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionUpdate)
* [`productOptionsReorder`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsReorder)
* [`productOptionsDelete`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsDelete)

Learn more about the [product model](https://shopify.dev/docs/apps/build/graphql/migrate/new-product-model) and [adding product data](https://shopify.dev/docs/apps/build/graphql/migrate/new-product-model/add-data).

## Arguments

* allow​Partial​Updates

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  When partial updates are allowed, valid variant changes may be persisted even if some of the variants updated have invalid data and cannot be persisted. When partial updates are not allowed, any error will prevent all variants from updating.

* media

  [\[Create​Media​Input!\]](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/CreateMediaInput)

  List of new media to be added to the product.

* product​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the product associated with the variants to update.

* variants

  [\[Product​Variants​Bulk​Input!\]!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/ProductVariantsBulkInput)

  required

  An array of product variants to update.

***

## Product​Variants​Bulk​Update​Payload returns

* product

  [Product](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product)

  The updated product object.

* product​Variants

  [\[Product​Variant!\]](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant)

  The updated variants.

* user​Errors

  [\[Product​Variants​Bulk​Update​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariantsBulkUpdateUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create and update metafields when updating product variants in bulk

  #### Description

  Update metadata for multiple product variants in a single request. This example modifies existing metafields under \`my\_fields.liner\_material\` and adds new metafields under \`my\_fields.sole\_material\` for variants of a specific product. The response includes the product with its updated metafields and the variants.

  #### Query

  ```graphql
  mutation productVariantsBulkUpdate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
    productVariantsBulkUpdate(productId: $productId, variants: $variants) {
      product {
        id
      }
      productVariants {
        id
        metafields(first: 2) {
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
        "id": "gid://shopify/ProductVariant/1070325197",
        "metafields": [
          {
            "id": "gid://shopify/Metafield/1069229095",
            "value": "SYNTHETIC LEATHER"
          },
          {
            "namespace": "my_fields",
            "key": "sole_material",
            "value": "RUBBER",
            "type": "single_line_text_field"
          }
        ]
      },
      {
        "id": "gid://shopify/ProductVariant/1070325198",
        "metafields": [
          {
            "id": "gid://shopify/Metafield/1069229096",
            "value": "SYNTHETIC LEATHER"
          },
          {
            "namespace": "my_fields",
            "key": "sole_material",
            "value": "CREPE",
            "type": "single_line_text_field"
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
  "query": "mutation productVariantsBulkUpdate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) { productVariantsBulkUpdate(productId: $productId, variants: $variants) { product { id } productVariants { id metafields(first: 2) { edges { node { namespace key value } } } } userErrors { field message } } }",
   "variables": {
      "productId": "gid://shopify/Product/20995642",
      "variants": [
        {
          "id": "gid://shopify/ProductVariant/1070325197",
          "metafields": [
            {
              "id": "gid://shopify/Metafield/1069229095",
              "value": "SYNTHETIC LEATHER"
            },
            {
              "namespace": "my_fields",
              "key": "sole_material",
              "value": "RUBBER",
              "type": "single_line_text_field"
            }
          ]
        },
        {
          "id": "gid://shopify/ProductVariant/1070325198",
          "metafields": [
            {
              "id": "gid://shopify/Metafield/1069229096",
              "value": "SYNTHETIC LEATHER"
            },
            {
              "namespace": "my_fields",
              "key": "sole_material",
              "value": "CREPE",
              "type": "single_line_text_field"
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
    mutation productVariantsBulkUpdate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
      productVariantsBulkUpdate(productId: $productId, variants: $variants) {
        product {
          id
        }
        productVariants {
          id
          metafields(first: 2) {
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
                  "id": "gid://shopify/ProductVariant/1070325197",
                  "metafields": [
                      {
                          "id": "gid://shopify/Metafield/1069229095",
                          "value": "SYNTHETIC LEATHER"
                      },
                      {
                          "namespace": "my_fields",
                          "key": "sole_material",
                          "value": "RUBBER",
                          "type": "single_line_text_field"
                      }
                  ]
              },
              {
                  "id": "gid://shopify/ProductVariant/1070325198",
                  "metafields": [
                      {
                          "id": "gid://shopify/Metafield/1069229096",
                          "value": "SYNTHETIC LEATHER"
                      },
                      {
                          "namespace": "my_fields",
                          "key": "sole_material",
                          "value": "CREPE",
                          "type": "single_line_text_field"
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
    mutation productVariantsBulkUpdate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
      productVariantsBulkUpdate(productId: $productId, variants: $variants) {
        product {
          id
        }
        productVariants {
          id
          metafields(first: 2) {
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
        "id": "gid://shopify/ProductVariant/1070325197",
        "metafields": [
          {
            "id": "gid://shopify/Metafield/1069229095",
            "value": "SYNTHETIC LEATHER"
          },
          {
            "namespace": "my_fields",
            "key": "sole_material",
            "value": "RUBBER",
            "type": "single_line_text_field"
          }
        ]
      },
      {
        "id": "gid://shopify/ProductVariant/1070325198",
        "metafields": [
          {
            "id": "gid://shopify/Metafield/1069229096",
            "value": "SYNTHETIC LEATHER"
          },
          {
            "namespace": "my_fields",
            "key": "sole_material",
            "value": "CREPE",
            "type": "single_line_text_field"
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
      "query": `mutation productVariantsBulkUpdate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
        productVariantsBulkUpdate(productId: $productId, variants: $variants) {
          product {
            id
          }
          productVariants {
            id
            metafields(first: 2) {
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
                  "id": "gid://shopify/ProductVariant/1070325197",
                  "metafields": [
                      {
                          "id": "gid://shopify/Metafield/1069229095",
                          "value": "SYNTHETIC LEATHER"
                      },
                      {
                          "namespace": "my_fields",
                          "key": "sole_material",
                          "value": "RUBBER",
                          "type": "single_line_text_field"
                      }
                  ]
              },
              {
                  "id": "gid://shopify/ProductVariant/1070325198",
                  "metafields": [
                      {
                          "id": "gid://shopify/Metafield/1069229096",
                          "value": "SYNTHETIC LEATHER"
                      },
                      {
                          "namespace": "my_fields",
                          "key": "sole_material",
                          "value": "CREPE",
                          "type": "single_line_text_field"
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
  'mutation productVariantsBulkUpdate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
    productVariantsBulkUpdate(productId: $productId, variants: $variants) {
      product {
        id
      }
      productVariants {
        id
        metafields(first: 2) {
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
        "id": "gid://shopify/ProductVariant/1070325197",
        "metafields": [
          {
            "id": "gid://shopify/Metafield/1069229095",
            "value": "SYNTHETIC LEATHER"
          },
          {
            "namespace": "my_fields",
            "key": "sole_material",
            "value": "RUBBER",
            "type": "single_line_text_field"
          }
        ]
      },
      {
        "id": "gid://shopify/ProductVariant/1070325198",
        "metafields": [
          {
            "id": "gid://shopify/Metafield/1069229096",
            "value": "SYNTHETIC LEATHER"
          },
          {
            "namespace": "my_fields",
            "key": "sole_material",
            "value": "CREPE",
            "type": "single_line_text_field"
          }
        ]
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "productVariantsBulkUpdate": {
      "product": {
        "id": "gid://shopify/Product/20995642"
      },
      "productVariants": [
        {
          "id": "gid://shopify/ProductVariant/1070325197",
          "metafields": {
            "edges": [
              {
                "node": {
                  "namespace": "my_fields",
                  "key": "liner_material",
                  "value": "SYNTHETIC LEATHER"
                }
              },
              {
                "node": {
                  "namespace": "my_fields",
                  "key": "sole_material",
                  "value": "RUBBER"
                }
              }
            ]
          }
        },
        {
          "id": "gid://shopify/ProductVariant/1070325198",
          "metafields": {
            "edges": [
              {
                "node": {
                  "namespace": "my_fields",
                  "key": "liner_material",
                  "value": "SYNTHETIC LEATHER"
                }
              },
              {
                "node": {
                  "namespace": "my_fields",
                  "key": "sole_material",
                  "value": "CREPE"
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

* ### Update product variants with option values

  #### Description

  Update existing product variants with new size and color combinations. This example shows different ways to reference options and values (by name or ID). The response includes the product with its updated variants.

  #### Query

  ```graphql
  mutation UpdateProductVariantsOptionValuesInBulk($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
    productVariantsBulkUpdate(productId: $productId, variants: $variants) {
      product {
        id
        title
        options {
          id
          position
          name
          values
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
    "productId": "gid://shopify/Product/1072481069",
    "variants": [
      {
        "id": "gid://shopify/ProductVariant/1070325199",
        "optionValues": [
          {
            "name": "Green",
            "optionName": "Color"
          }
        ]
      },
      {
        "id": "gid://shopify/ProductVariant/1070325200",
        "optionValues": [
          {
            "name": "Large",
            "optionId": "gid://shopify/ProductOption/1064576536"
          },
          {
            "id": "gid://shopify/ProductOptionValue/1054672367",
            "optionId": "gid://shopify/ProductOption/1064576537"
          }
        ]
      },
      {
        "id": "gid://shopify/ProductVariant/1070325201",
        "optionValues": [
          {
            "name": "Medium",
            "optionName": "Size"
          },
          {
            "id": "gid://shopify/ProductOptionValue/1054672367",
            "optionName": "Color"
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
  "query": "mutation UpdateProductVariantsOptionValuesInBulk($productId: ID!, $variants: [ProductVariantsBulkInput!]!) { productVariantsBulkUpdate(productId: $productId, variants: $variants) { product { id title options { id position name values optionValues { id name hasVariants } } } productVariants { id title selectedOptions { name value } } userErrors { field message } } }",
   "variables": {
      "productId": "gid://shopify/Product/1072481069",
      "variants": [
        {
          "id": "gid://shopify/ProductVariant/1070325199",
          "optionValues": [
            {
              "name": "Green",
              "optionName": "Color"
            }
          ]
        },
        {
          "id": "gid://shopify/ProductVariant/1070325200",
          "optionValues": [
            {
              "name": "Large",
              "optionId": "gid://shopify/ProductOption/1064576536"
            },
            {
              "id": "gid://shopify/ProductOptionValue/1054672367",
              "optionId": "gid://shopify/ProductOption/1064576537"
            }
          ]
        },
        {
          "id": "gid://shopify/ProductVariant/1070325201",
          "optionValues": [
            {
              "name": "Medium",
              "optionName": "Size"
            },
            {
              "id": "gid://shopify/ProductOptionValue/1054672367",
              "optionName": "Color"
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
    mutation UpdateProductVariantsOptionValuesInBulk($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
      productVariantsBulkUpdate(productId: $productId, variants: $variants) {
        product {
          id
          title
          options {
            id
            position
            name
            values
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
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "productId": "gid://shopify/Product/1072481069",
          "variants": [
              {
                  "id": "gid://shopify/ProductVariant/1070325199",
                  "optionValues": [
                      {
                          "name": "Green",
                          "optionName": "Color"
                      }
                  ]
              },
              {
                  "id": "gid://shopify/ProductVariant/1070325200",
                  "optionValues": [
                      {
                          "name": "Large",
                          "optionId": "gid://shopify/ProductOption/1064576536"
                      },
                      {
                          "id": "gid://shopify/ProductOptionValue/1054672367",
                          "optionId": "gid://shopify/ProductOption/1064576537"
                      }
                  ]
              },
              {
                  "id": "gid://shopify/ProductVariant/1070325201",
                  "optionValues": [
                      {
                          "name": "Medium",
                          "optionName": "Size"
                      },
                      {
                          "id": "gid://shopify/ProductOptionValue/1054672367",
                          "optionName": "Color"
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
    mutation UpdateProductVariantsOptionValuesInBulk($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
      productVariantsBulkUpdate(productId: $productId, variants: $variants) {
        product {
          id
          title
          options {
            id
            position
            name
            values
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
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "productId": "gid://shopify/Product/1072481069",
    "variants": [
      {
        "id": "gid://shopify/ProductVariant/1070325199",
        "optionValues": [
          {
            "name": "Green",
            "optionName": "Color"
          }
        ]
      },
      {
        "id": "gid://shopify/ProductVariant/1070325200",
        "optionValues": [
          {
            "name": "Large",
            "optionId": "gid://shopify/ProductOption/1064576536"
          },
          {
            "id": "gid://shopify/ProductOptionValue/1054672367",
            "optionId": "gid://shopify/ProductOption/1064576537"
          }
        ]
      },
      {
        "id": "gid://shopify/ProductVariant/1070325201",
        "optionValues": [
          {
            "name": "Medium",
            "optionName": "Size"
          },
          {
            "id": "gid://shopify/ProductOptionValue/1054672367",
            "optionName": "Color"
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
      "query": `mutation UpdateProductVariantsOptionValuesInBulk($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
        productVariantsBulkUpdate(productId: $productId, variants: $variants) {
          product {
            id
            title
            options {
              id
              position
              name
              values
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
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "productId": "gid://shopify/Product/1072481069",
          "variants": [
              {
                  "id": "gid://shopify/ProductVariant/1070325199",
                  "optionValues": [
                      {
                          "name": "Green",
                          "optionName": "Color"
                      }
                  ]
              },
              {
                  "id": "gid://shopify/ProductVariant/1070325200",
                  "optionValues": [
                      {
                          "name": "Large",
                          "optionId": "gid://shopify/ProductOption/1064576536"
                      },
                      {
                          "id": "gid://shopify/ProductOptionValue/1054672367",
                          "optionId": "gid://shopify/ProductOption/1064576537"
                      }
                  ]
              },
              {
                  "id": "gid://shopify/ProductVariant/1070325201",
                  "optionValues": [
                      {
                          "name": "Medium",
                          "optionName": "Size"
                      },
                      {
                          "id": "gid://shopify/ProductOptionValue/1054672367",
                          "optionName": "Color"
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
  'mutation UpdateProductVariantsOptionValuesInBulk($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
    productVariantsBulkUpdate(productId: $productId, variants: $variants) {
      product {
        id
        title
        options {
          id
          position
          name
          values
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
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "productId": "gid://shopify/Product/1072481069",
    "variants": [
      {
        "id": "gid://shopify/ProductVariant/1070325199",
        "optionValues": [
          {
            "name": "Green",
            "optionName": "Color"
          }
        ]
      },
      {
        "id": "gid://shopify/ProductVariant/1070325200",
        "optionValues": [
          {
            "name": "Large",
            "optionId": "gid://shopify/ProductOption/1064576536"
          },
          {
            "id": "gid://shopify/ProductOptionValue/1054672367",
            "optionId": "gid://shopify/ProductOption/1064576537"
          }
        ]
      },
      {
        "id": "gid://shopify/ProductVariant/1070325201",
        "optionValues": [
          {
            "name": "Medium",
            "optionName": "Size"
          },
          {
            "id": "gid://shopify/ProductOptionValue/1054672367",
            "optionName": "Color"
          }
        ]
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "productVariantsBulkUpdate": {
      "product": {
        "id": "gid://shopify/Product/1072481069",
        "title": "A shirt",
        "options": [
          {
            "id": "gid://shopify/ProductOption/1064576536",
            "position": 1,
            "name": "Size",
            "values": [
              "Small",
              "Large",
              "Medium"
            ],
            "optionValues": [
              {
                "id": "gid://shopify/ProductOptionValue/1054672364",
                "name": "Small",
                "hasVariants": true
              },
              {
                "id": "gid://shopify/ProductOptionValue/1054672366",
                "name": "Large",
                "hasVariants": true
              },
              {
                "id": "gid://shopify/ProductOptionValue/1054672365",
                "name": "Medium",
                "hasVariants": true
              }
            ]
          },
          {
            "id": "gid://shopify/ProductOption/1064576537",
            "position": 2,
            "name": "Color",
            "values": [
              "Green",
              "Red"
            ],
            "optionValues": [
              {
                "id": "gid://shopify/ProductOptionValue/1054672369",
                "name": "Green",
                "hasVariants": true
              },
              {
                "id": "gid://shopify/ProductOptionValue/1054672367",
                "name": "Red",
                "hasVariants": true
              }
            ]
          }
        ]
      },
      "productVariants": [
        {
          "id": "gid://shopify/ProductVariant/1070325199",
          "title": "Small / Green",
          "selectedOptions": [
            {
              "name": "Size",
              "value": "Small"
            },
            {
              "name": "Color",
              "value": "Green"
            }
          ]
        },
        {
          "id": "gid://shopify/ProductVariant/1070325200",
          "title": "Large / Red",
          "selectedOptions": [
            {
              "name": "Size",
              "value": "Large"
            },
            {
              "name": "Color",
              "value": "Red"
            }
          ]
        },
        {
          "id": "gid://shopify/ProductVariant/1070325201",
          "title": "Medium / Red",
          "selectedOptions": [
            {
              "name": "Size",
              "value": "Medium"
            },
            {
              "name": "Color",
              "value": "Red"
            }
          ]
        }
      ],
      "userErrors": []
    }
  }
  ```

* ### Update product variants and add media to a product

  #### Description

  Update three product variants and upload new media \[asynchronously]\(https://shopify.dev/docs/apps/build/graphql/migrate/new-product-model/product-model-components#asynchronous-media-management). The media is associated with the product that the variants belong to. The response returns both the product with its newly created media and the product variants.

  #### Query

  ```graphql
  mutation UpdateProductVariantsInBulkAndMedia(
    $productId: ID!,
    $variants: [ProductVariantsBulkInput!]!,
    $media: [CreateMediaInput!]
  ) {
    productVariantsBulkUpdate(productId: $productId, variants: $variants, media: $media) {
      product {
        id
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
      productVariants {
        id
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
        "id": "gid://shopify/ProductVariant/1070325197"
      },
      {
        "id": "gid://shopify/ProductVariant/1070325198"
      },
      {
        "id": "gid://shopify/ProductVariant/1070325199"
      }
    ],
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
  "query": "mutation UpdateProductVariantsInBulkAndMedia( $productId: ID!, $variants: [ProductVariantsBulkInput!]!, $media: [CreateMediaInput!] ) { productVariantsBulkUpdate(productId: $productId, variants: $variants, media: $media) { product { id media(first: 10) { nodes { id alt mediaContentType preview { status } } } } productVariants { id media(first: 10) { nodes { id alt mediaContentType preview { status } } } } userErrors { field message } } }",
   "variables": {
      "productId": "gid://shopify/Product/20995642",
      "variants": [
        {
          "id": "gid://shopify/ProductVariant/1070325197"
        },
        {
          "id": "gid://shopify/ProductVariant/1070325198"
        },
        {
          "id": "gid://shopify/ProductVariant/1070325199"
        }
      ],
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
    mutation UpdateProductVariantsInBulkAndMedia(
      $productId: ID!,
      $variants: [ProductVariantsBulkInput!]!,
      $media: [CreateMediaInput!]
    ) {
      productVariantsBulkUpdate(productId: $productId, variants: $variants, media: $media) {
        product {
          id
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
        productVariants {
          id
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
                  "id": "gid://shopify/ProductVariant/1070325197"
              },
              {
                  "id": "gid://shopify/ProductVariant/1070325198"
              },
              {
                  "id": "gid://shopify/ProductVariant/1070325199"
              }
          ],
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
    mutation UpdateProductVariantsInBulkAndMedia(
      $productId: ID!,
      $variants: [ProductVariantsBulkInput!]!,
      $media: [CreateMediaInput!]
    ) {
      productVariantsBulkUpdate(productId: $productId, variants: $variants, media: $media) {
        product {
          id
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
        productVariants {
          id
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
        "id": "gid://shopify/ProductVariant/1070325197"
      },
      {
        "id": "gid://shopify/ProductVariant/1070325198"
      },
      {
        "id": "gid://shopify/ProductVariant/1070325199"
      }
    ],
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
      "query": `mutation UpdateProductVariantsInBulkAndMedia(
        $productId: ID!,
        $variants: [ProductVariantsBulkInput!]!,
        $media: [CreateMediaInput!]
      ) {
        productVariantsBulkUpdate(productId: $productId, variants: $variants, media: $media) {
          product {
            id
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
          productVariants {
            id
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
                  "id": "gid://shopify/ProductVariant/1070325197"
              },
              {
                  "id": "gid://shopify/ProductVariant/1070325198"
              },
              {
                  "id": "gid://shopify/ProductVariant/1070325199"
              }
          ],
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
  'mutation UpdateProductVariantsInBulkAndMedia(
    $productId: ID!,
    $variants: [ProductVariantsBulkInput!]!,
    $media: [CreateMediaInput!]
  ) {
    productVariantsBulkUpdate(productId: $productId, variants: $variants, media: $media) {
      product {
        id
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
      productVariants {
        id
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
        "id": "gid://shopify/ProductVariant/1070325197"
      },
      {
        "id": "gid://shopify/ProductVariant/1070325198"
      },
      {
        "id": "gid://shopify/ProductVariant/1070325199"
      }
    ],
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
    "productVariantsBulkUpdate": {
      "product": {
        "id": "gid://shopify/Product/20995642",
        "media": {
          "nodes": [
            {
              "id": "gid://shopify/MediaImage/1023119543",
              "alt": "Gray helmet for bikers",
              "mediaContentType": "IMAGE",
              "preview": {
                "status": "UPLOADED"
              }
            },
            {
              "id": "gid://shopify/ExternalVideo/1023119544",
              "alt": "Testing helmet resistance against impacts",
              "mediaContentType": "EXTERNAL_VIDEO",
              "preview": {
                "status": "UPLOADED"
              }
            }
          ]
        }
      },
      "productVariants": [
        {
          "id": "gid://shopify/ProductVariant/1070325197",
          "media": {
            "nodes": []
          }
        },
        {
          "id": "gid://shopify/ProductVariant/1070325198",
          "media": {
            "nodes": []
          }
        },
        {
          "id": "gid://shopify/ProductVariant/1070325199",
          "media": {
            "nodes": []
          }
        }
      ],
      "userErrors": []
    }
  }
  ```

* ### Update product variants and attach existing media

  #### Description

  Update two product variants, with one variant attached to existing media that is associated with the product, and the other variant without any media attached. The response returns both the product with its updated variants.

  #### Query

  ```graphql
  mutation UpdateProductVariantsInBulkWithExistingMedia(
    $productId: ID!,
    $variants: [ProductVariantsBulkInput!]!
  ) {
    productVariantsBulkUpdate(productId: $productId, variants: $variants) {
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
        "id": "gid://shopify/ProductVariant/1070325197",
        "mediaId": "gid://shopify/MediaImage/1023119543"
      },
      {
        "id": "gid://shopify/ProductVariant/1070325198"
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
  "query": "mutation UpdateProductVariantsInBulkWithExistingMedia( $productId: ID!, $variants: [ProductVariantsBulkInput!]! ) { productVariantsBulkUpdate(productId: $productId, variants: $variants) { product { id } productVariants { id title media(first: 10) { nodes { id alt mediaContentType preview { status } } } } userErrors { field message } } }",
   "variables": {
      "productId": "gid://shopify/Product/20995642",
      "variants": [
        {
          "id": "gid://shopify/ProductVariant/1070325197",
          "mediaId": "gid://shopify/MediaImage/1023119543"
        },
        {
          "id": "gid://shopify/ProductVariant/1070325198"
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
    mutation UpdateProductVariantsInBulkWithExistingMedia(
      $productId: ID!,
      $variants: [ProductVariantsBulkInput!]!
    ) {
      productVariantsBulkUpdate(productId: $productId, variants: $variants) {
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
                  "id": "gid://shopify/ProductVariant/1070325197",
                  "mediaId": "gid://shopify/MediaImage/1023119543"
              },
              {
                  "id": "gid://shopify/ProductVariant/1070325198"
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
    mutation UpdateProductVariantsInBulkWithExistingMedia(
      $productId: ID!,
      $variants: [ProductVariantsBulkInput!]!
    ) {
      productVariantsBulkUpdate(productId: $productId, variants: $variants) {
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
        "id": "gid://shopify/ProductVariant/1070325197",
        "mediaId": "gid://shopify/MediaImage/1023119543"
      },
      {
        "id": "gid://shopify/ProductVariant/1070325198"
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
      "query": `mutation UpdateProductVariantsInBulkWithExistingMedia(
        $productId: ID!,
        $variants: [ProductVariantsBulkInput!]!
      ) {
        productVariantsBulkUpdate(productId: $productId, variants: $variants) {
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
                  "id": "gid://shopify/ProductVariant/1070325197",
                  "mediaId": "gid://shopify/MediaImage/1023119543"
              },
              {
                  "id": "gid://shopify/ProductVariant/1070325198"
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
  'mutation UpdateProductVariantsInBulkWithExistingMedia(
    $productId: ID!,
    $variants: [ProductVariantsBulkInput!]!
  ) {
    productVariantsBulkUpdate(productId: $productId, variants: $variants) {
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
        "id": "gid://shopify/ProductVariant/1070325197",
        "mediaId": "gid://shopify/MediaImage/1023119543"
      },
      {
        "id": "gid://shopify/ProductVariant/1070325198"
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "productVariantsBulkUpdate": {
      "product": {
        "id": "gid://shopify/Product/20995642"
      },
      "productVariants": [
        {
          "id": "gid://shopify/ProductVariant/1070325197",
          "title": "Default Title",
          "media": {
            "nodes": [
              {
                "id": "gid://shopify/MediaImage/1023119543",
                "alt": "Product image",
                "mediaContentType": "IMAGE",
                "preview": {
                  "status": "READY"
                }
              }
            ]
          }
        },
        {
          "id": "gid://shopify/ProductVariant/1070325198",
          "title": "Default Title",
          "media": {
            "nodes": []
          }
        }
      ],
      "userErrors": []
    }
  }
  ```

* ### productVariantsBulkUpdate reference
