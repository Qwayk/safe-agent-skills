---
title: productOptionsCreate - GraphQL Admin
description: >-
  Creates one or more
  [options](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductOption)

  on a
  [product](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product),

  such as size, color, or material. Each option includes a name, position, and a
  list of values. The combination

  of a product option and value creates a [product
  variant](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant).


  Use the `productOptionsCreate` mutation for the following use cases:


  - **Add product choices**: Add a new option, like "Size" (Small, Medium,
  Large) or

  "Color" (Red, Blue, Green), to an existing product so customers can select
  their preferred variant.

  - **Enable personalization features**: Add options such as "Engraving text" to
  let customers customize their purchase.

  - **Offer seasonal or limited edition products**: Add a new value

  (for example, "Holiday red") to an existing option to support limited-time or
  seasonal variants.

  - **Integrate with apps that manage product configuration**: Allow third-party
  apps to add options, like

  "Bundle size", when customers select or customize

  [product
  bundles](https://shopify.dev/docs/apps/build/product-merchandising/bundles).

  - **Link options to metafields**: Associate a product option with a custom

  [metafield](https://shopify.dev/docs/apps/build/custom-data), like "Fabric
  code", for

  richer integrations with other systems or apps.


  > Note:

  > The `productOptionsCreate` mutation enforces strict data integrity for
  product options and variants.

  All option positions must be sequential, and every option should be used by at
  least one variant.

  If you use the [`CREATE` variant
  strategy](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsCreate#arguments-variantStrategy.enums.CREATE),
  consider the maximum allowed number of variants for each product is 2048.


  After you create product options, you can further manage a product's
  configuration using related mutations:


  -
  [`productOptionUpdate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionUpdate)

  -
  [`productOptionsReorder`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsReorder)

  -
  [`productOptionsDelete`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsDelete)

  -
  [`productVariantsBulkCreate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productVariantsBulkCreate)

  -
  [`productVariantsBulkUpdate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productVariantsBulkUpdate)

  -
  [`productSet`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productSet)


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
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsCreate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsCreate.md
---

# product​Options​Create

mutation

Requires `write_products` access scope. Also: The user must have a permission to create product variants.

Creates one or more [options](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductOption) on a [product](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product), such as size, color, or material. Each option includes a name, position, and a list of values. The combination of a product option and value creates a [product variant](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant).

Use the `productOptionsCreate` mutation for the following use cases:

* **Add product choices**: Add a new option, like "Size" (Small, Medium, Large) or "Color" (Red, Blue, Green), to an existing product so customers can select their preferred variant.
* **Enable personalization features**: Add options such as "Engraving text" to let customers customize their purchase.
* **Offer seasonal or limited edition products**: Add a new value (for example, "Holiday red") to an existing option to support limited-time or seasonal variants.
* **Integrate with apps that manage product configuration**: Allow third-party apps to add options, like "Bundle size", when customers select or customize [product bundles](https://shopify.dev/docs/apps/build/product-merchandising/bundles).
* **Link options to metafields**: Associate a product option with a custom [metafield](https://shopify.dev/docs/apps/build/custom-data), like "Fabric code", for richer integrations with other systems or apps.

***

**Note:** The \<code>\<span class="PreventFireFoxApplyingGapToWBR">product\<wbr/>Options\<wbr/>Create\</span>\</code> mutation enforces strict data integrity for product options and variants. All option positions must be sequential, and every option should be used by at least one variant. If you use the \<a href="https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsCreate#arguments-variantStrategy.enums.CREATE">\<code>\<span class="PreventFireFoxApplyingGapToWBR">C\<wbr/>R\<wbr/>E\<wbr/>A\<wbr/>T\<wbr/>E\</span>\</code> variant strategy\</a>, consider the maximum allowed number of variants for each product is 2048.

***

After you create product options, you can further manage a product's configuration using related mutations:

* [`productOptionUpdate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionUpdate)
* [`productOptionsReorder`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsReorder)
* [`productOptionsDelete`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsDelete)
* [`productVariantsBulkCreate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productVariantsBulkCreate)
* [`productVariantsBulkUpdate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productVariantsBulkUpdate)
* [`productSet`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productSet)

Learn more about the [product model](https://shopify.dev/docs/apps/build/graphql/migrate/new-product-model) and [adding product data](https://shopify.dev/docs/apps/build/graphql/migrate/new-product-model/add-data).

## Arguments

* options

  [\[Option​Create​Input!\]!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/OptionCreateInput)

  required

  Options to add to the product.

* product​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the product to update.

* variant​Strategy

  [Product​Option​Create​Variant​Strategy](https://shopify.dev/docs/api/admin-graphql/latest/enums/ProductOptionCreateVariantStrategy)

  Default:LEAVE\_AS\_IS

  The strategy defines which behavior the mutation should observe regarding variants. If not provided or set to null, the strategy `LEAVE_AS_IS` will be used.

***

## Product​Options​Create​Payload returns

* product

  [Product](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product)

  The updated product object.

* user​Errors

  [\[Product​Options​Create​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductOptionsCreateUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create a new product option with an explicit position

  #### Description

  Create a new \[product option]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductOption) with an explicitly specified position. The example shows how to create a new option ("Color") with a position of 1, which makes it the first option (appearing first in variant titles and option ordering). This causes existing options to be repositioned accordingly. The response includes the product's ID, the created option (with its name, position, and value), and the details of the first product variant generated from the new option.

  #### Query

  ```graphql
  mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!, $variantStrategy: ProductOptionCreateVariantStrategy) {
    productOptionsCreate(productId: $productId, options: $options, variantStrategy: $variantStrategy) {
      userErrors {
        field
        message
        code
      }
      product {
        id
        variants(first: 10) {
          nodes {
            id
            title
            selectedOptions {
              name
              value
            }
          }
        }
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
    }
  }
  ```

  #### Variables

  ```json
  {
    "productId": "gid://shopify/Product/20995642",
    "options": [
      {
        "name": "Color",
        "position": 1,
        "values": [
          {
            "name": "Blue"
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
  "query": "mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!, $variantStrategy: ProductOptionCreateVariantStrategy) { productOptionsCreate(productId: $productId, options: $options, variantStrategy: $variantStrategy) { userErrors { field message code } product { id variants(first: 10) { nodes { id title selectedOptions { name value } } } options { id name values position optionValues { id name hasVariants } } } } }",
   "variables": {
      "productId": "gid://shopify/Product/20995642",
      "options": [
        {
          "name": "Color",
          "position": 1,
          "values": [
            {
              "name": "Blue"
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
    mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!, $variantStrategy: ProductOptionCreateVariantStrategy) {
      productOptionsCreate(productId: $productId, options: $options, variantStrategy: $variantStrategy) {
        userErrors {
          field
          message
          code
        }
        product {
          id
          variants(first: 10) {
            nodes {
              id
              title
              selectedOptions {
                name
                value
              }
            }
          }
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
      }
    }`,
    {
      variables: {
          "productId": "gid://shopify/Product/20995642",
          "options": [
              {
                  "name": "Color",
                  "position": 1,
                  "values": [
                      {
                          "name": "Blue"
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
    mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!, $variantStrategy: ProductOptionCreateVariantStrategy) {
      productOptionsCreate(productId: $productId, options: $options, variantStrategy: $variantStrategy) {
        userErrors {
          field
          message
          code
        }
        product {
          id
          variants(first: 10) {
            nodes {
              id
              title
              selectedOptions {
                name
                value
              }
            }
          }
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
      }
    }
  QUERY

  variables = {
    "productId": "gid://shopify/Product/20995642",
    "options": [
      {
        "name": "Color",
        "position": 1,
        "values": [
          {
            "name": "Blue"
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
      "query": `mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!, $variantStrategy: ProductOptionCreateVariantStrategy) {
        productOptionsCreate(productId: $productId, options: $options, variantStrategy: $variantStrategy) {
          userErrors {
            field
            message
            code
          }
          product {
            id
            variants(first: 10) {
              nodes {
                id
                title
                selectedOptions {
                  name
                  value
                }
              }
            }
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
        }
      }`,
      "variables": {
          "productId": "gid://shopify/Product/20995642",
          "options": [
              {
                  "name": "Color",
                  "position": 1,
                  "values": [
                      {
                          "name": "Blue"
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
  'mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!, $variantStrategy: ProductOptionCreateVariantStrategy) {
    productOptionsCreate(productId: $productId, options: $options, variantStrategy: $variantStrategy) {
      userErrors {
        field
        message
        code
      }
      product {
        id
        variants(first: 10) {
          nodes {
            id
            title
            selectedOptions {
              name
              value
            }
          }
        }
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
    }
  }' \
  --variables \
  '{
    "productId": "gid://shopify/Product/20995642",
    "options": [
      {
        "name": "Color",
        "position": 1,
        "values": [
          {
            "name": "Blue"
          }
        ]
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "productOptionsCreate": {
      "userErrors": [],
      "product": {
        "id": "gid://shopify/Product/20995642",
        "variants": {
          "nodes": [
            {
              "id": "gid://shopify/ProductVariant/30322695",
              "title": "Blue / 151cm",
              "selectedOptions": [
                {
                  "name": "Color",
                  "value": "Blue"
                },
                {
                  "name": "Title",
                  "value": "151cm"
                }
              ]
            },
            {
              "id": "gid://shopify/ProductVariant/113711323",
              "title": "Blue / 155cm",
              "selectedOptions": [
                {
                  "name": "Color",
                  "value": "Blue"
                },
                {
                  "name": "Title",
                  "value": "155cm"
                }
              ]
            },
            {
              "id": "gid://shopify/ProductVariant/236948360",
              "title": "Blue / 158cm",
              "selectedOptions": [
                {
                  "name": "Color",
                  "value": "Blue"
                },
                {
                  "name": "Title",
                  "value": "158cm"
                }
              ]
            }
          ]
        },
        "options": [
          {
            "id": "gid://shopify/ProductOption/1064576661",
            "name": "Color",
            "values": [
              "Blue"
            ],
            "position": 1,
            "optionValues": [
              {
                "name": "Blue",
                "hasVariants": true
              }
            ]
          },
          {
            "id": "gid://shopify/ProductOption/328272167",
            "name": "Title",
            "values": [
              "151cm",
              "155cm",
              "158cm"
            ],
            "position": 2,
            "optionValues": [
              {
                "name": "151cm",
                "hasVariants": true
              },
              {
                "name": "155cm",
                "hasVariants": true
              },
              {
                "name": "158cm",
                "hasVariants": true
              }
            ]
          }
        ]
      }
    }
  }
  ```

* ### Create new product options and values

  #### Description

  Create new \[product options]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductOption) and \[option values]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductOptionValue) for an existing product. The example shows how to update a product to have two options: "Color" (with values "Blue" and "Red") and "Size" (with values "Small" and "Medium"). Only the first value for each option is linked to the product variant. The response returns the product's ID, the created options (with their names, positions, and values), and the details of the first product variant generated from the new options.

  #### Query

  ```graphql
  mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!, $variantStrategy: ProductOptionCreateVariantStrategy) {
    productOptionsCreate(productId: $productId, options: $options, variantStrategy: $variantStrategy) {
      userErrors {
        field
        message
        code
      }
      product {
        id
        variants(first: 10) {
          nodes {
            id
            title
            selectedOptions {
              name
              value
            }
          }
        }
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
    }
  }
  ```

  #### Variables

  ```json
  {
    "productId": "gid://shopify/Product/1072481154",
    "options": [
      {
        "name": "Color",
        "values": [
          {
            "name": "Blue"
          },
          {
            "name": "Red"
          }
        ]
      },
      {
        "name": "Size",
        "values": [
          {
            "name": "Small"
          },
          {
            "name": "Medium"
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
  "query": "mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!, $variantStrategy: ProductOptionCreateVariantStrategy) { productOptionsCreate(productId: $productId, options: $options, variantStrategy: $variantStrategy) { userErrors { field message code } product { id variants(first: 10) { nodes { id title selectedOptions { name value } } } options { id name values position optionValues { id name hasVariants } } } } }",
   "variables": {
      "productId": "gid://shopify/Product/1072481154",
      "options": [
        {
          "name": "Color",
          "values": [
            {
              "name": "Blue"
            },
            {
              "name": "Red"
            }
          ]
        },
        {
          "name": "Size",
          "values": [
            {
              "name": "Small"
            },
            {
              "name": "Medium"
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
    mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!, $variantStrategy: ProductOptionCreateVariantStrategy) {
      productOptionsCreate(productId: $productId, options: $options, variantStrategy: $variantStrategy) {
        userErrors {
          field
          message
          code
        }
        product {
          id
          variants(first: 10) {
            nodes {
              id
              title
              selectedOptions {
                name
                value
              }
            }
          }
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
      }
    }`,
    {
      variables: {
          "productId": "gid://shopify/Product/1072481154",
          "options": [
              {
                  "name": "Color",
                  "values": [
                      {
                          "name": "Blue"
                      },
                      {
                          "name": "Red"
                      }
                  ]
              },
              {
                  "name": "Size",
                  "values": [
                      {
                          "name": "Small"
                      },
                      {
                          "name": "Medium"
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
    mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!, $variantStrategy: ProductOptionCreateVariantStrategy) {
      productOptionsCreate(productId: $productId, options: $options, variantStrategy: $variantStrategy) {
        userErrors {
          field
          message
          code
        }
        product {
          id
          variants(first: 10) {
            nodes {
              id
              title
              selectedOptions {
                name
                value
              }
            }
          }
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
      }
    }
  QUERY

  variables = {
    "productId": "gid://shopify/Product/1072481154",
    "options": [
      {
        "name": "Color",
        "values": [
          {
            "name": "Blue"
          },
          {
            "name": "Red"
          }
        ]
      },
      {
        "name": "Size",
        "values": [
          {
            "name": "Small"
          },
          {
            "name": "Medium"
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
      "query": `mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!, $variantStrategy: ProductOptionCreateVariantStrategy) {
        productOptionsCreate(productId: $productId, options: $options, variantStrategy: $variantStrategy) {
          userErrors {
            field
            message
            code
          }
          product {
            id
            variants(first: 10) {
              nodes {
                id
                title
                selectedOptions {
                  name
                  value
                }
              }
            }
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
        }
      }`,
      "variables": {
          "productId": "gid://shopify/Product/1072481154",
          "options": [
              {
                  "name": "Color",
                  "values": [
                      {
                          "name": "Blue"
                      },
                      {
                          "name": "Red"
                      }
                  ]
              },
              {
                  "name": "Size",
                  "values": [
                      {
                          "name": "Small"
                      },
                      {
                          "name": "Medium"
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
  'mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!, $variantStrategy: ProductOptionCreateVariantStrategy) {
    productOptionsCreate(productId: $productId, options: $options, variantStrategy: $variantStrategy) {
      userErrors {
        field
        message
        code
      }
      product {
        id
        variants(first: 10) {
          nodes {
            id
            title
            selectedOptions {
              name
              value
            }
          }
        }
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
    }
  }' \
  --variables \
  '{
    "productId": "gid://shopify/Product/1072481154",
    "options": [
      {
        "name": "Color",
        "values": [
          {
            "name": "Blue"
          },
          {
            "name": "Red"
          }
        ]
      },
      {
        "name": "Size",
        "values": [
          {
            "name": "Small"
          },
          {
            "name": "Medium"
          }
        ]
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "productOptionsCreate": {
      "userErrors": [],
      "product": {
        "id": "gid://shopify/Product/1072481154",
        "variants": {
          "nodes": [
            {
              "id": "gid://shopify/ProductVariant/1070325307",
              "title": "Blue / Small",
              "selectedOptions": [
                {
                  "name": "Color",
                  "value": "Blue"
                },
                {
                  "name": "Size",
                  "value": "Small"
                }
              ]
            }
          ]
        },
        "options": [
          {
            "id": "gid://shopify/ProductOption/1064576667",
            "name": "Color",
            "values": [
              "Blue"
            ],
            "position": 1,
            "optionValues": [
              {
                "name": "Blue",
                "hasVariants": true
              },
              {
                "name": "Red",
                "hasVariants": false
              }
            ]
          },
          {
            "id": "gid://shopify/ProductOption/1064576668",
            "name": "Size",
            "values": [
              "Small"
            ],
            "position": 2,
            "optionValues": [
              {
                "name": "Small",
                "hasVariants": true
              },
              {
                "name": "Medium",
                "hasVariants": false
              }
            ]
          }
        ]
      }
    }
  }
  ```

* ### Create product options and product variants

  #### Description

  Use the \`CREATE\` value for the \`variantStrategy\` input to create new product variants for each combination of option values. The response includes the product's ID, the created options (with their names, positions, and values), and the details of the product variants generated from the new options.

  #### Query

  ```graphql
  mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!, $variantStrategy: ProductOptionCreateVariantStrategy) {
    productOptionsCreate(productId: $productId, options: $options, variantStrategy: $variantStrategy) {
      userErrors {
        field
        message
        code
      }
      product {
        id
        variants(first: 10) {
          nodes {
            id
            title
            selectedOptions {
              name
              value
            }
          }
        }
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
    }
  }
  ```

  #### Variables

  ```json
  {
    "productId": "gid://shopify/Product/20995642",
    "options": [
      {
        "name": "Color",
        "values": [
          {
            "name": "Blue"
          },
          {
            "name": "Green"
          }
        ]
      }
    ],
    "variantStrategy": "CREATE"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!, $variantStrategy: ProductOptionCreateVariantStrategy) { productOptionsCreate(productId: $productId, options: $options, variantStrategy: $variantStrategy) { userErrors { field message code } product { id variants(first: 10) { nodes { id title selectedOptions { name value } } } options { id name values position optionValues { id name hasVariants } } } } }",
   "variables": {
      "productId": "gid://shopify/Product/20995642",
      "options": [
        {
          "name": "Color",
          "values": [
            {
              "name": "Blue"
            },
            {
              "name": "Green"
            }
          ]
        }
      ],
      "variantStrategy": "CREATE"
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
    mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!, $variantStrategy: ProductOptionCreateVariantStrategy) {
      productOptionsCreate(productId: $productId, options: $options, variantStrategy: $variantStrategy) {
        userErrors {
          field
          message
          code
        }
        product {
          id
          variants(first: 10) {
            nodes {
              id
              title
              selectedOptions {
                name
                value
              }
            }
          }
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
      }
    }`,
    {
      variables: {
          "productId": "gid://shopify/Product/20995642",
          "options": [
              {
                  "name": "Color",
                  "values": [
                      {
                          "name": "Blue"
                      },
                      {
                          "name": "Green"
                      }
                  ]
              }
          ],
          "variantStrategy": "CREATE"
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
    mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!, $variantStrategy: ProductOptionCreateVariantStrategy) {
      productOptionsCreate(productId: $productId, options: $options, variantStrategy: $variantStrategy) {
        userErrors {
          field
          message
          code
        }
        product {
          id
          variants(first: 10) {
            nodes {
              id
              title
              selectedOptions {
                name
                value
              }
            }
          }
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
      }
    }
  QUERY

  variables = {
    "productId": "gid://shopify/Product/20995642",
    "options": [
      {
        "name": "Color",
        "values": [
          {
            "name": "Blue"
          },
          {
            "name": "Green"
          }
        ]
      }
    ],
    "variantStrategy": "CREATE"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!, $variantStrategy: ProductOptionCreateVariantStrategy) {
        productOptionsCreate(productId: $productId, options: $options, variantStrategy: $variantStrategy) {
          userErrors {
            field
            message
            code
          }
          product {
            id
            variants(first: 10) {
              nodes {
                id
                title
                selectedOptions {
                  name
                  value
                }
              }
            }
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
        }
      }`,
      "variables": {
          "productId": "gid://shopify/Product/20995642",
          "options": [
              {
                  "name": "Color",
                  "values": [
                      {
                          "name": "Blue"
                      },
                      {
                          "name": "Green"
                      }
                  ]
              }
          ],
          "variantStrategy": "CREATE"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!, $variantStrategy: ProductOptionCreateVariantStrategy) {
    productOptionsCreate(productId: $productId, options: $options, variantStrategy: $variantStrategy) {
      userErrors {
        field
        message
        code
      }
      product {
        id
        variants(first: 10) {
          nodes {
            id
            title
            selectedOptions {
              name
              value
            }
          }
        }
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
    }
  }' \
  --variables \
  '{
    "productId": "gid://shopify/Product/20995642",
    "options": [
      {
        "name": "Color",
        "values": [
          {
            "name": "Blue"
          },
          {
            "name": "Green"
          }
        ]
      }
    ],
    "variantStrategy": "CREATE"
  }'
  ```

  #### Response

  ```json
  {
    "productOptionsCreate": {
      "userErrors": [],
      "product": {
        "id": "gid://shopify/Product/20995642",
        "variants": {
          "nodes": [
            {
              "id": "gid://shopify/ProductVariant/30322695",
              "title": "151cm / Blue",
              "selectedOptions": [
                {
                  "name": "Title",
                  "value": "151cm"
                },
                {
                  "name": "Color",
                  "value": "Blue"
                }
              ]
            },
            {
              "id": "gid://shopify/ProductVariant/113711323",
              "title": "155cm / Blue",
              "selectedOptions": [
                {
                  "name": "Title",
                  "value": "155cm"
                },
                {
                  "name": "Color",
                  "value": "Blue"
                }
              ]
            },
            {
              "id": "gid://shopify/ProductVariant/236948360",
              "title": "158cm / Blue",
              "selectedOptions": [
                {
                  "name": "Title",
                  "value": "158cm"
                },
                {
                  "name": "Color",
                  "value": "Blue"
                }
              ]
            },
            {
              "id": "gid://shopify/ProductVariant/1070325308",
              "title": "151cm / Green",
              "selectedOptions": [
                {
                  "name": "Title",
                  "value": "151cm"
                },
                {
                  "name": "Color",
                  "value": "Green"
                }
              ]
            },
            {
              "id": "gid://shopify/ProductVariant/1070325309",
              "title": "155cm / Green",
              "selectedOptions": [
                {
                  "name": "Title",
                  "value": "155cm"
                },
                {
                  "name": "Color",
                  "value": "Green"
                }
              ]
            },
            {
              "id": "gid://shopify/ProductVariant/1070325310",
              "title": "158cm / Green",
              "selectedOptions": [
                {
                  "name": "Title",
                  "value": "158cm"
                },
                {
                  "name": "Color",
                  "value": "Green"
                }
              ]
            }
          ]
        },
        "options": [
          {
            "id": "gid://shopify/ProductOption/328272167",
            "name": "Title",
            "values": [
              "151cm",
              "155cm",
              "158cm"
            ],
            "position": 1,
            "optionValues": [
              {
                "name": "151cm",
                "hasVariants": true
              },
              {
                "name": "155cm",
                "hasVariants": true
              },
              {
                "name": "158cm",
                "hasVariants": true
              }
            ]
          },
          {
            "id": "gid://shopify/ProductOption/1064576670",
            "name": "Color",
            "values": [
              "Blue",
              "Green"
            ],
            "position": 2,
            "optionValues": [
              {
                "name": "Blue",
                "hasVariants": true
              },
              {
                "name": "Green",
                "hasVariants": true
              }
            ]
          }
        ]
      }
    }
  }
  ```

* ### Create product options without creating new product variants

  #### Description

  Use the \`LEAVE\_AS\_IS\` value for the \`variantStrategy\` input to add new \[options]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductOption) to a product and update existing \[variants]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant) to remain valid, without creating any new variants. The response includes the product's ID, the updated options (with their names, positions, and values), and the unchanged list of variants, showing how the new option is integrated without expanding the variant set.

  #### Query

  ```graphql
  mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!, $variantStrategy: ProductOptionCreateVariantStrategy) {
    productOptionsCreate(productId: $productId, options: $options, variantStrategy: $variantStrategy) {
      userErrors {
        field
        message
        code
      }
      product {
        id
        variants(first: 10) {
          nodes {
            id
            title
            selectedOptions {
              name
              value
            }
          }
        }
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
    }
  }
  ```

  #### Variables

  ```json
  {
    "productId": "gid://shopify/Product/20995642",
    "options": [
      {
        "name": "Color",
        "values": [
          {
            "name": "Blue"
          },
          {
            "name": "Green"
          }
        ]
      }
    ],
    "variantStrategy": "LEAVE_AS_IS"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!, $variantStrategy: ProductOptionCreateVariantStrategy) { productOptionsCreate(productId: $productId, options: $options, variantStrategy: $variantStrategy) { userErrors { field message code } product { id variants(first: 10) { nodes { id title selectedOptions { name value } } } options { id name values position optionValues { id name hasVariants } } } } }",
   "variables": {
      "productId": "gid://shopify/Product/20995642",
      "options": [
        {
          "name": "Color",
          "values": [
            {
              "name": "Blue"
            },
            {
              "name": "Green"
            }
          ]
        }
      ],
      "variantStrategy": "LEAVE_AS_IS"
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
    mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!, $variantStrategy: ProductOptionCreateVariantStrategy) {
      productOptionsCreate(productId: $productId, options: $options, variantStrategy: $variantStrategy) {
        userErrors {
          field
          message
          code
        }
        product {
          id
          variants(first: 10) {
            nodes {
              id
              title
              selectedOptions {
                name
                value
              }
            }
          }
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
      }
    }`,
    {
      variables: {
          "productId": "gid://shopify/Product/20995642",
          "options": [
              {
                  "name": "Color",
                  "values": [
                      {
                          "name": "Blue"
                      },
                      {
                          "name": "Green"
                      }
                  ]
              }
          ],
          "variantStrategy": "LEAVE_AS_IS"
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
    mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!, $variantStrategy: ProductOptionCreateVariantStrategy) {
      productOptionsCreate(productId: $productId, options: $options, variantStrategy: $variantStrategy) {
        userErrors {
          field
          message
          code
        }
        product {
          id
          variants(first: 10) {
            nodes {
              id
              title
              selectedOptions {
                name
                value
              }
            }
          }
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
      }
    }
  QUERY

  variables = {
    "productId": "gid://shopify/Product/20995642",
    "options": [
      {
        "name": "Color",
        "values": [
          {
            "name": "Blue"
          },
          {
            "name": "Green"
          }
        ]
      }
    ],
    "variantStrategy": "LEAVE_AS_IS"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!, $variantStrategy: ProductOptionCreateVariantStrategy) {
        productOptionsCreate(productId: $productId, options: $options, variantStrategy: $variantStrategy) {
          userErrors {
            field
            message
            code
          }
          product {
            id
            variants(first: 10) {
              nodes {
                id
                title
                selectedOptions {
                  name
                  value
                }
              }
            }
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
        }
      }`,
      "variables": {
          "productId": "gid://shopify/Product/20995642",
          "options": [
              {
                  "name": "Color",
                  "values": [
                      {
                          "name": "Blue"
                      },
                      {
                          "name": "Green"
                      }
                  ]
              }
          ],
          "variantStrategy": "LEAVE_AS_IS"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!, $variantStrategy: ProductOptionCreateVariantStrategy) {
    productOptionsCreate(productId: $productId, options: $options, variantStrategy: $variantStrategy) {
      userErrors {
        field
        message
        code
      }
      product {
        id
        variants(first: 10) {
          nodes {
            id
            title
            selectedOptions {
              name
              value
            }
          }
        }
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
    }
  }' \
  --variables \
  '{
    "productId": "gid://shopify/Product/20995642",
    "options": [
      {
        "name": "Color",
        "values": [
          {
            "name": "Blue"
          },
          {
            "name": "Green"
          }
        ]
      }
    ],
    "variantStrategy": "LEAVE_AS_IS"
  }'
  ```

  #### Response

  ```json
  {
    "productOptionsCreate": {
      "userErrors": [],
      "product": {
        "id": "gid://shopify/Product/20995642",
        "variants": {
          "nodes": [
            {
              "id": "gid://shopify/ProductVariant/30322695",
              "title": "151cm / Blue",
              "selectedOptions": [
                {
                  "name": "Title",
                  "value": "151cm"
                },
                {
                  "name": "Color",
                  "value": "Blue"
                }
              ]
            },
            {
              "id": "gid://shopify/ProductVariant/113711323",
              "title": "155cm / Blue",
              "selectedOptions": [
                {
                  "name": "Title",
                  "value": "155cm"
                },
                {
                  "name": "Color",
                  "value": "Blue"
                }
              ]
            },
            {
              "id": "gid://shopify/ProductVariant/236948360",
              "title": "158cm / Blue",
              "selectedOptions": [
                {
                  "name": "Title",
                  "value": "158cm"
                },
                {
                  "name": "Color",
                  "value": "Blue"
                }
              ]
            }
          ]
        },
        "options": [
          {
            "id": "gid://shopify/ProductOption/328272167",
            "name": "Title",
            "values": [
              "151cm",
              "155cm",
              "158cm"
            ],
            "position": 1,
            "optionValues": [
              {
                "name": "151cm",
                "hasVariants": true
              },
              {
                "name": "155cm",
                "hasVariants": true
              },
              {
                "name": "158cm",
                "hasVariants": true
              }
            ]
          },
          {
            "id": "gid://shopify/ProductOption/1064576669",
            "name": "Color",
            "values": [
              "Blue"
            ],
            "position": 2,
            "optionValues": [
              {
                "name": "Blue",
                "hasVariants": true
              },
              {
                "name": "Green",
                "hasVariants": false
              }
            ]
          }
        ]
      }
    }
  }
  ```

* ### Creating too many product options returns an error

  #### Description

  This example shows an attempt to add more options to a product than the allowed limit, and demonstrates validation for the maximum number of product options. The response includes the product's ID and a user error indicating that the options limit has been exceeded, with the error code, message, and field path.

  #### Query

  ```graphql
  mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!, $variantStrategy: ProductOptionCreateVariantStrategy) {
    productOptionsCreate(productId: $productId, options: $options, variantStrategy: $variantStrategy) {
      userErrors {
        field
        message
        code
      }
      product {
        id
        variants(first: 10) {
          nodes {
            id
            title
            selectedOptions {
              name
              value
            }
          }
        }
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
    }
  }
  ```

  #### Variables

  ```json
  {
    "productId": "gid://shopify/Product/20995642",
    "options": [
      {
        "name": "Color",
        "values": [
          {
            "name": "Blue"
          }
        ]
      },
      {
        "name": "Style",
        "values": [
          {
            "name": "Classic"
          }
        ]
      },
      {
        "name": "Size",
        "values": [
          {
            "name": "Small"
          }
        ]
      },
      {
        "name": "Material",
        "values": [
          {
            "name": "Linen"
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
  "query": "mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!, $variantStrategy: ProductOptionCreateVariantStrategy) { productOptionsCreate(productId: $productId, options: $options, variantStrategy: $variantStrategy) { userErrors { field message code } product { id variants(first: 10) { nodes { id title selectedOptions { name value } } } options { id name values position optionValues { id name hasVariants } } } } }",
   "variables": {
      "productId": "gid://shopify/Product/20995642",
      "options": [
        {
          "name": "Color",
          "values": [
            {
              "name": "Blue"
            }
          ]
        },
        {
          "name": "Style",
          "values": [
            {
              "name": "Classic"
            }
          ]
        },
        {
          "name": "Size",
          "values": [
            {
              "name": "Small"
            }
          ]
        },
        {
          "name": "Material",
          "values": [
            {
              "name": "Linen"
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
    mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!, $variantStrategy: ProductOptionCreateVariantStrategy) {
      productOptionsCreate(productId: $productId, options: $options, variantStrategy: $variantStrategy) {
        userErrors {
          field
          message
          code
        }
        product {
          id
          variants(first: 10) {
            nodes {
              id
              title
              selectedOptions {
                name
                value
              }
            }
          }
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
      }
    }`,
    {
      variables: {
          "productId": "gid://shopify/Product/20995642",
          "options": [
              {
                  "name": "Color",
                  "values": [
                      {
                          "name": "Blue"
                      }
                  ]
              },
              {
                  "name": "Style",
                  "values": [
                      {
                          "name": "Classic"
                      }
                  ]
              },
              {
                  "name": "Size",
                  "values": [
                      {
                          "name": "Small"
                      }
                  ]
              },
              {
                  "name": "Material",
                  "values": [
                      {
                          "name": "Linen"
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
    mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!, $variantStrategy: ProductOptionCreateVariantStrategy) {
      productOptionsCreate(productId: $productId, options: $options, variantStrategy: $variantStrategy) {
        userErrors {
          field
          message
          code
        }
        product {
          id
          variants(first: 10) {
            nodes {
              id
              title
              selectedOptions {
                name
                value
              }
            }
          }
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
      }
    }
  QUERY

  variables = {
    "productId": "gid://shopify/Product/20995642",
    "options": [
      {
        "name": "Color",
        "values": [
          {
            "name": "Blue"
          }
        ]
      },
      {
        "name": "Style",
        "values": [
          {
            "name": "Classic"
          }
        ]
      },
      {
        "name": "Size",
        "values": [
          {
            "name": "Small"
          }
        ]
      },
      {
        "name": "Material",
        "values": [
          {
            "name": "Linen"
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
      "query": `mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!, $variantStrategy: ProductOptionCreateVariantStrategy) {
        productOptionsCreate(productId: $productId, options: $options, variantStrategy: $variantStrategy) {
          userErrors {
            field
            message
            code
          }
          product {
            id
            variants(first: 10) {
              nodes {
                id
                title
                selectedOptions {
                  name
                  value
                }
              }
            }
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
        }
      }`,
      "variables": {
          "productId": "gid://shopify/Product/20995642",
          "options": [
              {
                  "name": "Color",
                  "values": [
                      {
                          "name": "Blue"
                      }
                  ]
              },
              {
                  "name": "Style",
                  "values": [
                      {
                          "name": "Classic"
                      }
                  ]
              },
              {
                  "name": "Size",
                  "values": [
                      {
                          "name": "Small"
                      }
                  ]
              },
              {
                  "name": "Material",
                  "values": [
                      {
                          "name": "Linen"
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
  'mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!, $variantStrategy: ProductOptionCreateVariantStrategy) {
    productOptionsCreate(productId: $productId, options: $options, variantStrategy: $variantStrategy) {
      userErrors {
        field
        message
        code
      }
      product {
        id
        variants(first: 10) {
          nodes {
            id
            title
            selectedOptions {
              name
              value
            }
          }
        }
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
    }
  }' \
  --variables \
  '{
    "productId": "gid://shopify/Product/20995642",
    "options": [
      {
        "name": "Color",
        "values": [
          {
            "name": "Blue"
          }
        ]
      },
      {
        "name": "Style",
        "values": [
          {
            "name": "Classic"
          }
        ]
      },
      {
        "name": "Size",
        "values": [
          {
            "name": "Small"
          }
        ]
      },
      {
        "name": "Material",
        "values": [
          {
            "name": "Linen"
          }
        ]
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "productOptionsCreate": {
      "userErrors": [
        {
          "field": [
            "options"
          ],
          "message": "Can only specify a maximum of 3 options",
          "code": "OPTIONS_OVER_LIMIT"
        }
      ],
      "product": {
        "id": "gid://shopify/Product/20995642",
        "variants": {
          "nodes": [
            {
              "id": "gid://shopify/ProductVariant/30322695",
              "title": "151cm",
              "selectedOptions": [
                {
                  "name": "Title",
                  "value": "151cm"
                }
              ]
            },
            {
              "id": "gid://shopify/ProductVariant/113711323",
              "title": "155cm",
              "selectedOptions": [
                {
                  "name": "Title",
                  "value": "155cm"
                }
              ]
            },
            {
              "id": "gid://shopify/ProductVariant/236948360",
              "title": "158cm",
              "selectedOptions": [
                {
                  "name": "Title",
                  "value": "158cm"
                }
              ]
            }
          ]
        },
        "options": [
          {
            "id": "gid://shopify/ProductOption/328272167",
            "name": "Title",
            "values": [
              "151cm",
              "155cm",
              "158cm"
            ],
            "position": 1,
            "optionValues": [
              {
                "id": "gid://shopify/ProductOptionValue/141051426",
                "name": "151cm",
                "hasVariants": true
              },
              {
                "id": "gid://shopify/ProductOptionValue/258076414",
                "name": "155cm",
                "hasVariants": true
              },
              {
                "id": "gid://shopify/ProductOptionValue/129596849",
                "name": "158cm",
                "hasVariants": true
              }
            ]
          }
        ]
      }
    }
  }
  ```

* ### Duplicating product option names returns an error

  #### Description

  This example demonstrates an attempt to create a \[product option]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductOption) with a name that already exists on the product. The validation prevents duplicate option names within the same product. When you try to create an option with a name that already exists (in this case, "Color"), the mutation returns a validation error instead of creating the option. The response includes the product's ID and a user error with the specific error code, message, and field path indicating which option caused the conflict.

  #### Query

  ```graphql
  mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!, $variantStrategy: ProductOptionCreateVariantStrategy) {
    productOptionsCreate(productId: $productId, options: $options, variantStrategy: $variantStrategy) {
      userErrors {
        field
        message
        code
      }
      product {
        id
        variants(first: 10) {
          nodes {
            id
            title
            selectedOptions {
              name
              value
            }
          }
        }
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
    }
  }
  ```

  #### Variables

  ```json
  {
    "productId": "gid://shopify/Product/20995642",
    "options": [
      {
        "name": "Color",
        "values": [
          {
            "name": "Blue"
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
  "query": "mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!, $variantStrategy: ProductOptionCreateVariantStrategy) { productOptionsCreate(productId: $productId, options: $options, variantStrategy: $variantStrategy) { userErrors { field message code } product { id variants(first: 10) { nodes { id title selectedOptions { name value } } } options { id name values position optionValues { id name hasVariants } } } } }",
   "variables": {
      "productId": "gid://shopify/Product/20995642",
      "options": [
        {
          "name": "Color",
          "values": [
            {
              "name": "Blue"
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
    mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!, $variantStrategy: ProductOptionCreateVariantStrategy) {
      productOptionsCreate(productId: $productId, options: $options, variantStrategy: $variantStrategy) {
        userErrors {
          field
          message
          code
        }
        product {
          id
          variants(first: 10) {
            nodes {
              id
              title
              selectedOptions {
                name
                value
              }
            }
          }
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
      }
    }`,
    {
      variables: {
          "productId": "gid://shopify/Product/20995642",
          "options": [
              {
                  "name": "Color",
                  "values": [
                      {
                          "name": "Blue"
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
    mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!, $variantStrategy: ProductOptionCreateVariantStrategy) {
      productOptionsCreate(productId: $productId, options: $options, variantStrategy: $variantStrategy) {
        userErrors {
          field
          message
          code
        }
        product {
          id
          variants(first: 10) {
            nodes {
              id
              title
              selectedOptions {
                name
                value
              }
            }
          }
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
      }
    }
  QUERY

  variables = {
    "productId": "gid://shopify/Product/20995642",
    "options": [
      {
        "name": "Color",
        "values": [
          {
            "name": "Blue"
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
      "query": `mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!, $variantStrategy: ProductOptionCreateVariantStrategy) {
        productOptionsCreate(productId: $productId, options: $options, variantStrategy: $variantStrategy) {
          userErrors {
            field
            message
            code
          }
          product {
            id
            variants(first: 10) {
              nodes {
                id
                title
                selectedOptions {
                  name
                  value
                }
              }
            }
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
        }
      }`,
      "variables": {
          "productId": "gid://shopify/Product/20995642",
          "options": [
              {
                  "name": "Color",
                  "values": [
                      {
                          "name": "Blue"
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
  'mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!, $variantStrategy: ProductOptionCreateVariantStrategy) {
    productOptionsCreate(productId: $productId, options: $options, variantStrategy: $variantStrategy) {
      userErrors {
        field
        message
        code
      }
      product {
        id
        variants(first: 10) {
          nodes {
            id
            title
            selectedOptions {
              name
              value
            }
          }
        }
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
    }
  }' \
  --variables \
  '{
    "productId": "gid://shopify/Product/20995642",
    "options": [
      {
        "name": "Color",
        "values": [
          {
            "name": "Blue"
          }
        ]
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "productOptionsCreate": {
      "userErrors": [
        {
          "field": [
            "options",
            "0"
          ],
          "message": "Option 'Color' already exists.",
          "code": "OPTION_ALREADY_EXISTS"
        }
      ],
      "product": {
        "id": "gid://shopify/Product/20995642",
        "variants": {
          "nodes": [
            {
              "id": "gid://shopify/ProductVariant/30322695",
              "title": "151cm / Green",
              "selectedOptions": [
                {
                  "name": "Title",
                  "value": "151cm"
                },
                {
                  "name": "Color",
                  "value": "Green"
                }
              ]
            },
            {
              "id": "gid://shopify/ProductVariant/113711323",
              "title": "155cm / Green",
              "selectedOptions": [
                {
                  "name": "Title",
                  "value": "155cm"
                },
                {
                  "name": "Color",
                  "value": "Green"
                }
              ]
            },
            {
              "id": "gid://shopify/ProductVariant/236948360",
              "title": "158cm / Green",
              "selectedOptions": [
                {
                  "name": "Title",
                  "value": "158cm"
                },
                {
                  "name": "Color",
                  "value": "Green"
                }
              ]
            }
          ]
        },
        "options": [
          {
            "id": "gid://shopify/ProductOption/328272167",
            "name": "Title",
            "values": [
              "151cm",
              "155cm",
              "158cm"
            ],
            "position": 1,
            "optionValues": [
              {
                "id": "gid://shopify/ProductOptionValue/141051426",
                "name": "151cm",
                "hasVariants": true
              },
              {
                "id": "gid://shopify/ProductOptionValue/258076414",
                "name": "155cm",
                "hasVariants": true
              },
              {
                "id": "gid://shopify/ProductOptionValue/129596849",
                "name": "158cm",
                "hasVariants": true
              }
            ]
          },
          {
            "id": "gid://shopify/ProductOption/1064576663",
            "name": "Color",
            "values": [
              "Green"
            ],
            "position": 2,
            "optionValues": [
              {
                "id": "gid://shopify/ProductOptionValue/1054672581",
                "name": "Green",
                "hasVariants": true
              }
            ]
          }
        ]
      }
    }
  }
  ```

* ### Link a product option to a category metafield

  #### Description

  Link a new \[product option]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductOption) to a \[category metafield]\(https://help.shopify.com/manual/products/details/product-category#category-metafields) using the \`linkedMetafield\` input. The example shows how to associate a product option ("Color") with a metafield, and specify option values using metaobjects. The response returns the product's options, including the linked metafield details and the option values, each with its name and associated metafield value. \[Learn more about metafield-linked product options]\(https://shopify.dev/api/admin/migrate/new-product-model/metafield-linked).

  #### Query

  ```graphql
  mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!) {
    productOptionsCreate(productId: $productId, options: $options) {
      userErrors {
        field
        message
        code
      }
      product {
        options {
          name
          linkedMetafield {
            namespace
            key
          }
          optionValues {
            name
            linkedMetafieldValue
          }
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "productId": "gid://shopify/Product/1072481153",
    "options": [
      {
        "name": "Color",
        "linkedMetafield": {
          "namespace": "shopify",
          "key": "color-pattern",
          "values": [
            "gid://shopify/Metaobject/971662499",
            "gid://shopify/Metaobject/971662500",
            "gid://shopify/Metaobject/971662501"
          ]
        }
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
  "query": "mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!) { productOptionsCreate(productId: $productId, options: $options) { userErrors { field message code } product { options { name linkedMetafield { namespace key } optionValues { name linkedMetafieldValue } } } } }",
   "variables": {
      "productId": "gid://shopify/Product/1072481153",
      "options": [
        {
          "name": "Color",
          "linkedMetafield": {
            "namespace": "shopify",
            "key": "color-pattern",
            "values": [
              "gid://shopify/Metaobject/971662499",
              "gid://shopify/Metaobject/971662500",
              "gid://shopify/Metaobject/971662501"
            ]
          }
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
    mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!) {
      productOptionsCreate(productId: $productId, options: $options) {
        userErrors {
          field
          message
          code
        }
        product {
          options {
            name
            linkedMetafield {
              namespace
              key
            }
            optionValues {
              name
              linkedMetafieldValue
            }
          }
        }
      }
    }`,
    {
      variables: {
          "productId": "gid://shopify/Product/1072481153",
          "options": [
              {
                  "name": "Color",
                  "linkedMetafield": {
                      "namespace": "shopify",
                      "key": "color-pattern",
                      "values": [
                          "gid://shopify/Metaobject/971662499",
                          "gid://shopify/Metaobject/971662500",
                          "gid://shopify/Metaobject/971662501"
                      ]
                  }
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
    mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!) {
      productOptionsCreate(productId: $productId, options: $options) {
        userErrors {
          field
          message
          code
        }
        product {
          options {
            name
            linkedMetafield {
              namespace
              key
            }
            optionValues {
              name
              linkedMetafieldValue
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "productId": "gid://shopify/Product/1072481153",
    "options": [
      {
        "name": "Color",
        "linkedMetafield": {
          "namespace": "shopify",
          "key": "color-pattern",
          "values": [
            "gid://shopify/Metaobject/971662499",
            "gid://shopify/Metaobject/971662500",
            "gid://shopify/Metaobject/971662501"
          ]
        }
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
      "query": `mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!) {
        productOptionsCreate(productId: $productId, options: $options) {
          userErrors {
            field
            message
            code
          }
          product {
            options {
              name
              linkedMetafield {
                namespace
                key
              }
              optionValues {
                name
                linkedMetafieldValue
              }
            }
          }
        }
      }`,
      "variables": {
          "productId": "gid://shopify/Product/1072481153",
          "options": [
              {
                  "name": "Color",
                  "linkedMetafield": {
                      "namespace": "shopify",
                      "key": "color-pattern",
                      "values": [
                          "gid://shopify/Metaobject/971662499",
                          "gid://shopify/Metaobject/971662500",
                          "gid://shopify/Metaobject/971662501"
                      ]
                  }
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
  'mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!) {
    productOptionsCreate(productId: $productId, options: $options) {
      userErrors {
        field
        message
        code
      }
      product {
        options {
          name
          linkedMetafield {
            namespace
            key
          }
          optionValues {
            name
            linkedMetafieldValue
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "productId": "gid://shopify/Product/1072481153",
    "options": [
      {
        "name": "Color",
        "linkedMetafield": {
          "namespace": "shopify",
          "key": "color-pattern",
          "values": [
            "gid://shopify/Metaobject/971662499",
            "gid://shopify/Metaobject/971662500",
            "gid://shopify/Metaobject/971662501"
          ]
        }
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "productOptionsCreate": {
      "userErrors": [],
      "product": {
        "options": [
          {
            "name": "Color",
            "linkedMetafield": {
              "namespace": "shopify",
              "key": "color-pattern"
            },
            "optionValues": [
              {
                "name": "Red",
                "linkedMetafieldValue": "gid://shopify/Metaobject/971662499"
              },
              {
                "name": "Blue",
                "linkedMetafieldValue": "gid://shopify/Metaobject/971662500"
              },
              {
                "name": "Yellow",
                "linkedMetafieldValue": "gid://shopify/Metaobject/971662501"
              }
            ]
          }
        ]
      }
    }
  }
  ```

* ### Link a product option to a metafield with existing values

  #### Description

  Link a \[product option]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductOption) to a \[category metafield]\(https://help.shopify.com/manual/products/details/product-category#category-metafields) when the product already has metafield values set. The example uses all metaobjects referenced by the product's category metafield to create option values. The response includes the product's options, the linked metafield information, and the generated option values with their names and metafield references. \[Learn more about metafield-linked product options]\(https://shopify.dev/api/admin/migrate/new-product-model/metafield-linked).

  #### Query

  ```graphql
  mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!) {
    productOptionsCreate(productId: $productId, options: $options) {
      userErrors {
        field
        message
        code
      }
      product {
        options {
          name
          linkedMetafield {
            namespace
            key
          }
          optionValues {
            name
            linkedMetafieldValue
          }
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "productId": "gid://shopify/Product/1072481152",
    "options": [
      {
        "name": "Color",
        "linkedMetafield": {
          "namespace": "shopify",
          "key": "color-pattern"
        }
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
  "query": "mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!) { productOptionsCreate(productId: $productId, options: $options) { userErrors { field message code } product { options { name linkedMetafield { namespace key } optionValues { name linkedMetafieldValue } } } } }",
   "variables": {
      "productId": "gid://shopify/Product/1072481152",
      "options": [
        {
          "name": "Color",
          "linkedMetafield": {
            "namespace": "shopify",
            "key": "color-pattern"
          }
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
    mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!) {
      productOptionsCreate(productId: $productId, options: $options) {
        userErrors {
          field
          message
          code
        }
        product {
          options {
            name
            linkedMetafield {
              namespace
              key
            }
            optionValues {
              name
              linkedMetafieldValue
            }
          }
        }
      }
    }`,
    {
      variables: {
          "productId": "gid://shopify/Product/1072481152",
          "options": [
              {
                  "name": "Color",
                  "linkedMetafield": {
                      "namespace": "shopify",
                      "key": "color-pattern"
                  }
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
    mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!) {
      productOptionsCreate(productId: $productId, options: $options) {
        userErrors {
          field
          message
          code
        }
        product {
          options {
            name
            linkedMetafield {
              namespace
              key
            }
            optionValues {
              name
              linkedMetafieldValue
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "productId": "gid://shopify/Product/1072481152",
    "options": [
      {
        "name": "Color",
        "linkedMetafield": {
          "namespace": "shopify",
          "key": "color-pattern"
        }
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
      "query": `mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!) {
        productOptionsCreate(productId: $productId, options: $options) {
          userErrors {
            field
            message
            code
          }
          product {
            options {
              name
              linkedMetafield {
                namespace
                key
              }
              optionValues {
                name
                linkedMetafieldValue
              }
            }
          }
        }
      }`,
      "variables": {
          "productId": "gid://shopify/Product/1072481152",
          "options": [
              {
                  "name": "Color",
                  "linkedMetafield": {
                      "namespace": "shopify",
                      "key": "color-pattern"
                  }
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
  'mutation createOptions($productId: ID!, $options: [OptionCreateInput!]!) {
    productOptionsCreate(productId: $productId, options: $options) {
      userErrors {
        field
        message
        code
      }
      product {
        options {
          name
          linkedMetafield {
            namespace
            key
          }
          optionValues {
            name
            linkedMetafieldValue
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "productId": "gid://shopify/Product/1072481152",
    "options": [
      {
        "name": "Color",
        "linkedMetafield": {
          "namespace": "shopify",
          "key": "color-pattern"
        }
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "productOptionsCreate": {
      "userErrors": [],
      "product": {
        "options": [
          {
            "name": "Color",
            "linkedMetafield": {
              "namespace": "shopify",
              "key": "color-pattern"
            },
            "optionValues": [
              {
                "name": "Red",
                "linkedMetafieldValue": "gid://shopify/Metaobject/971662496"
              },
              {
                "name": "Blue",
                "linkedMetafieldValue": "gid://shopify/Metaobject/971662497"
              },
              {
                "name": "Yellow",
                "linkedMetafieldValue": "gid://shopify/Metaobject/971662498"
              }
            ]
          }
        ]
      }
    }
  }
  ```

* ### productOptionsCreate reference
