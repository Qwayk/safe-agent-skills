---
title: productOptionUpdate - GraphQL Admin
description: >-
  Updates an
  [option](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductOption)

  on a
  [product](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product),

  such as size, color, or material. Each option includes a name, position, and a
  list of values. The combination

  of a product option and value creates a [product
  variant](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant).


  Use the `productOptionUpdate` mutation for the following use cases:


  - **Update product choices**: Modify an existing option, like "Size" (Small,
  Medium, Large) or

  "Color" (Red, Blue, Green), so customers can select their preferred variant.

  - **Enable personalization features**: Update an option (for example,
  "Engraving text") to let customers customize their purchase.

  - **Offer seasonal or limited edition products**: Update a value

  (for example, "Holiday red") on an existing option to support limited-time or
  seasonal variants.

  - **Integrate with apps that manage product configuration**: Allow third-party
  apps to update options, like

  "Bundle size", when customers select or customize

  [product
  bundles](https://shopify.dev/docs/apps/build/product-merchandising/bundles).

  - **Link options to metafields**: Associate a product option with a custom

  [metafield](https://shopify.dev/docs/apps/build/custom-data), like "Fabric
  code", for

  richer integrations with other systems or apps.


  > Note:

  > The `productOptionUpdate` mutation enforces strict data integrity for
  product options and variants.

  All option positions must be sequential, and every option should be used by at
  least one variant.


  After you update a product option, you can further manage a product's
  configuration using related mutations:


  -
  [`productOptionsCreate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsCreate)

  -
  [`productOptionsDelete`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsDelete)

  -
  [`productOptionsReorder`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsReorder)

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
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionUpdate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionUpdate.md
---

# product​Option​Update

mutation

Requires `write_products` access scope. Also: The user must have a permission to edit products and manage product variants.

Updates an [option](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductOption) on a [product](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product), such as size, color, or material. Each option includes a name, position, and a list of values. The combination of a product option and value creates a [product variant](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant).

Use the `productOptionUpdate` mutation for the following use cases:

* **Update product choices**: Modify an existing option, like "Size" (Small, Medium, Large) or "Color" (Red, Blue, Green), so customers can select their preferred variant.
* **Enable personalization features**: Update an option (for example, "Engraving text") to let customers customize their purchase.
* **Offer seasonal or limited edition products**: Update a value (for example, "Holiday red") on an existing option to support limited-time or seasonal variants.
* **Integrate with apps that manage product configuration**: Allow third-party apps to update options, like "Bundle size", when customers select or customize [product bundles](https://shopify.dev/docs/apps/build/product-merchandising/bundles).
* **Link options to metafields**: Associate a product option with a custom [metafield](https://shopify.dev/docs/apps/build/custom-data), like "Fabric code", for richer integrations with other systems or apps.

***

**Note:** The \<code>\<span class="PreventFireFoxApplyingGapToWBR">product\<wbr/>Option\<wbr/>Update\</span>\</code> mutation enforces strict data integrity for product options and variants. All option positions must be sequential, and every option should be used by at least one variant.

***

After you update a product option, you can further manage a product's configuration using related mutations:

* [`productOptionsCreate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsCreate)
* [`productOptionsDelete`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsDelete)
* [`productOptionsReorder`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsReorder)
* [`productVariantsBulkCreate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productVariantsBulkCreate)
* [`productVariantsBulkUpdate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productVariantsBulkUpdate)
* [`productSet`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productSet)

Learn more about the [product model](https://shopify.dev/docs/apps/build/graphql/migrate/new-product-model) and [adding product data](https://shopify.dev/docs/apps/build/graphql/migrate/new-product-model/add-data).

## Arguments

* option

  [Option​Update​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/OptionUpdateInput)

  required

  Option to update.

* option​Values​To​Add

  [\[Option​Value​Create​Input!\]](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/OptionValueCreateInput)

  New option values to create.

* option​Values​To​Delete

  [\[ID!\]](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  IDs of the existing option values to delete.

* option​Values​To​Update

  [\[Option​Value​Update​Input!\]](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/OptionValueUpdateInput)

  Existing option values to update.

* product​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the Product the Option belongs to.

* variant​Strategy

  [Product​Option​Update​Variant​Strategy](https://shopify.dev/docs/api/admin-graphql/latest/enums/ProductOptionUpdateVariantStrategy)

  The strategy defines which behavior the mutation should observe regarding variants, such as creating variants or deleting them in response to option values to add or to delete. If not provided or set to null, the strategy `LEAVE_AS_IS` will be used.

***

## Product​Option​Update​Payload returns

* product

  [Product](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product)

  The product with which the option being updated is associated.

* user​Errors

  [\[Product​Option​Update​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductOptionUpdateUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Update the name and position of a product option

  #### Description

  Update the name and position of an existing \[product option]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductOption) for a product. This example demonstrates how to change the name of an option (for example, from "Color" to "Tint") and move its position in the list of options. In this case, the "Color" option is moved from position 2 to position 1, which results in "Color" displaying first in the product options list and pushing the "Size" option to position 2. When a position changes, other options automatically shift to accommodate the new ordering. The position must be a positive number between one and the number of options. The name must be a maximum of 255 characters. The response returns the product's ID, the updated options (with their new names, positions, and values), and the details of the product variants reflecting the new option order and names.

  #### Query

  ```graphql
  mutation updateOption(
    $productId: ID!,
    $option: OptionUpdateInput!,
    $optionValuesToAdd: [OptionValueCreateInput!],
    $optionValuesToUpdate: [OptionValueUpdateInput!],
    $optionValuesToDelete: [ID!]
    $variantStrategy: ProductOptionUpdateVariantStrategy
  ) {
    productOptionUpdate(
      productId: $productId,
      option: $option,
      optionValuesToAdd: $optionValuesToAdd,
      optionValuesToUpdate: $optionValuesToUpdate,
      optionValuesToDelete: $optionValuesToDelete,
      variantStrategy: $variantStrategy
    ) {
      userErrors { field message code }
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
        variants(first: 5) {
          nodes {
            id
            title
            selectedOptions { name, value }
          }
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "productId": "gid://shopify/Product/1072481071",
    "option": {
      "id": "gid://shopify/ProductOption/1064576536",
      "position": 1,
      "name": "Tint"
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
  "query": "mutation updateOption( $productId: ID!, $option: OptionUpdateInput!, $optionValuesToAdd: [OptionValueCreateInput!], $optionValuesToUpdate: [OptionValueUpdateInput!], $optionValuesToDelete: [ID!] $variantStrategy: ProductOptionUpdateVariantStrategy ) { productOptionUpdate( productId: $productId, option: $option, optionValuesToAdd: $optionValuesToAdd, optionValuesToUpdate: $optionValuesToUpdate, optionValuesToDelete: $optionValuesToDelete, variantStrategy: $variantStrategy ) { userErrors { field message code } product { id options { id name values position optionValues { id name hasVariants } } variants(first: 5) { nodes { id title selectedOptions { name, value } } } } } }",
   "variables": {
      "productId": "gid://shopify/Product/1072481071",
      "option": {
        "id": "gid://shopify/ProductOption/1064576536",
        "position": 1,
        "name": "Tint"
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
    mutation updateOption(
      $productId: ID!,
      $option: OptionUpdateInput!,
      $optionValuesToAdd: [OptionValueCreateInput!],
      $optionValuesToUpdate: [OptionValueUpdateInput!],
      $optionValuesToDelete: [ID!]
      $variantStrategy: ProductOptionUpdateVariantStrategy
    ) {
      productOptionUpdate(
        productId: $productId,
        option: $option,
        optionValuesToAdd: $optionValuesToAdd,
        optionValuesToUpdate: $optionValuesToUpdate,
        optionValuesToDelete: $optionValuesToDelete,
        variantStrategy: $variantStrategy
      ) {
        userErrors { field message code }
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
          variants(first: 5) {
            nodes {
              id
              title
              selectedOptions { name, value }
            }
          }
        }
      }
    }`,
    {
      variables: {
          "productId": "gid://shopify/Product/1072481071",
          "option": {
              "id": "gid://shopify/ProductOption/1064576536",
              "position": 1,
              "name": "Tint"
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
    mutation updateOption(
      $productId: ID!,
      $option: OptionUpdateInput!,
      $optionValuesToAdd: [OptionValueCreateInput!],
      $optionValuesToUpdate: [OptionValueUpdateInput!],
      $optionValuesToDelete: [ID!]
      $variantStrategy: ProductOptionUpdateVariantStrategy
    ) {
      productOptionUpdate(
        productId: $productId,
        option: $option,
        optionValuesToAdd: $optionValuesToAdd,
        optionValuesToUpdate: $optionValuesToUpdate,
        optionValuesToDelete: $optionValuesToDelete,
        variantStrategy: $variantStrategy
      ) {
        userErrors { field message code }
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
          variants(first: 5) {
            nodes {
              id
              title
              selectedOptions { name, value }
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "productId": "gid://shopify/Product/1072481071",
    "option": {
      "id": "gid://shopify/ProductOption/1064576536",
      "position": 1,
      "name": "Tint"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation updateOption(
        $productId: ID!,
        $option: OptionUpdateInput!,
        $optionValuesToAdd: [OptionValueCreateInput!],
        $optionValuesToUpdate: [OptionValueUpdateInput!],
        $optionValuesToDelete: [ID!]
        $variantStrategy: ProductOptionUpdateVariantStrategy
      ) {
        productOptionUpdate(
          productId: $productId,
          option: $option,
          optionValuesToAdd: $optionValuesToAdd,
          optionValuesToUpdate: $optionValuesToUpdate,
          optionValuesToDelete: $optionValuesToDelete,
          variantStrategy: $variantStrategy
        ) {
          userErrors { field message code }
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
            variants(first: 5) {
              nodes {
                id
                title
                selectedOptions { name, value }
              }
            }
          }
        }
      }`,
      "variables": {
          "productId": "gid://shopify/Product/1072481071",
          "option": {
              "id": "gid://shopify/ProductOption/1064576536",
              "position": 1,
              "name": "Tint"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation updateOption(
    $productId: ID!,
    $option: OptionUpdateInput!,
    $optionValuesToAdd: [OptionValueCreateInput!],
    $optionValuesToUpdate: [OptionValueUpdateInput!],
    $optionValuesToDelete: [ID!]
    $variantStrategy: ProductOptionUpdateVariantStrategy
  ) {
    productOptionUpdate(
      productId: $productId,
      option: $option,
      optionValuesToAdd: $optionValuesToAdd,
      optionValuesToUpdate: $optionValuesToUpdate,
      optionValuesToDelete: $optionValuesToDelete,
      variantStrategy: $variantStrategy
    ) {
      userErrors { field message code }
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
        variants(first: 5) {
          nodes {
            id
            title
            selectedOptions { name, value }
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "productId": "gid://shopify/Product/1072481071",
    "option": {
      "id": "gid://shopify/ProductOption/1064576536",
      "position": 1,
      "name": "Tint"
    }
  }'
  ```

  #### Response

  ```json
  {
    "productOptionUpdate": {
      "userErrors": [],
      "product": {
        "id": "gid://shopify/Product/1072481071",
        "options": [
          {
            "id": "gid://shopify/ProductOption/1064576536",
            "name": "Tint",
            "values": [
              "Blue",
              "Red"
            ],
            "position": 1,
            "optionValues": [
              {
                "name": "Blue",
                "hasVariants": true
              },
              {
                "name": "Red",
                "hasVariants": true
              }
            ]
          },
          {
            "id": "gid://shopify/ProductOption/1064576535",
            "name": "Size",
            "values": [
              "Small",
              "Medium"
            ],
            "position": 2,
            "optionValues": [
              {
                "name": "Small",
                "hasVariants": true
              },
              {
                "name": "Medium",
                "hasVariants": true
              }
            ]
          }
        ],
        "variants": {
          "nodes": [
            {
              "id": "gid://shopify/ProductVariant/1070325117",
              "title": "Blue / Small",
              "selectedOptions": [
                {
                  "name": "Tint",
                  "value": "Blue"
                },
                {
                  "name": "Size",
                  "value": "Small"
                }
              ]
            },
            {
              "id": "gid://shopify/ProductVariant/1070325118",
              "title": "Red / Medium",
              "selectedOptions": [
                {
                  "name": "Tint",
                  "value": "Red"
                },
                {
                  "name": "Size",
                  "value": "Medium"
                }
              ]
            }
          ]
        }
      }
    }
  }
  ```

* ### Add and update product option values

  #### Description

  Add new \[option values]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductOptionValue) to an existing product option and update the name of an existing value. This example demonstrates how to add "Yellow" and "Red" values and rename an existing value from "Blue" to "Purple". The response returns the product's ID, the updated option (with all values and their association to variants), and the updated list of product variants reflecting the changes.

  #### Query

  ```graphql
  mutation updateOption(
    $productId: ID!,
    $option: OptionUpdateInput!,
    $optionValuesToAdd: [OptionValueCreateInput!],
    $optionValuesToUpdate: [OptionValueUpdateInput!],
    $optionValuesToDelete: [ID!]
    $variantStrategy: ProductOptionUpdateVariantStrategy
  ) {
    productOptionUpdate(
      productId: $productId,
      option: $option,
      optionValuesToAdd: $optionValuesToAdd,
      optionValuesToUpdate: $optionValuesToUpdate,
      optionValuesToDelete: $optionValuesToDelete,
      variantStrategy: $variantStrategy
    ) {
      userErrors { field message code }
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
        variants(first: 5) {
          nodes {
            id
            title
            selectedOptions { name, value }
          }
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "productId": "gid://shopify/Product/1072481063",
    "option": {
      "id": "gid://shopify/ProductOption/1064576526"
    },
    "optionValuesToAdd": [
      {
        "name": "Yellow"
      },
      {
        "name": "Red"
      }
    ],
    "optionValuesToUpdate": [
      {
        "id": "gid://shopify/ProductOptionValue/1054672275",
        "name": "Purple"
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
  "query": "mutation updateOption( $productId: ID!, $option: OptionUpdateInput!, $optionValuesToAdd: [OptionValueCreateInput!], $optionValuesToUpdate: [OptionValueUpdateInput!], $optionValuesToDelete: [ID!] $variantStrategy: ProductOptionUpdateVariantStrategy ) { productOptionUpdate( productId: $productId, option: $option, optionValuesToAdd: $optionValuesToAdd, optionValuesToUpdate: $optionValuesToUpdate, optionValuesToDelete: $optionValuesToDelete, variantStrategy: $variantStrategy ) { userErrors { field message code } product { id options { id name values position optionValues { id name hasVariants } } variants(first: 5) { nodes { id title selectedOptions { name, value } } } } } }",
   "variables": {
      "productId": "gid://shopify/Product/1072481063",
      "option": {
        "id": "gid://shopify/ProductOption/1064576526"
      },
      "optionValuesToAdd": [
        {
          "name": "Yellow"
        },
        {
          "name": "Red"
        }
      ],
      "optionValuesToUpdate": [
        {
          "id": "gid://shopify/ProductOptionValue/1054672275",
          "name": "Purple"
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
    mutation updateOption(
      $productId: ID!,
      $option: OptionUpdateInput!,
      $optionValuesToAdd: [OptionValueCreateInput!],
      $optionValuesToUpdate: [OptionValueUpdateInput!],
      $optionValuesToDelete: [ID!]
      $variantStrategy: ProductOptionUpdateVariantStrategy
    ) {
      productOptionUpdate(
        productId: $productId,
        option: $option,
        optionValuesToAdd: $optionValuesToAdd,
        optionValuesToUpdate: $optionValuesToUpdate,
        optionValuesToDelete: $optionValuesToDelete,
        variantStrategy: $variantStrategy
      ) {
        userErrors { field message code }
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
          variants(first: 5) {
            nodes {
              id
              title
              selectedOptions { name, value }
            }
          }
        }
      }
    }`,
    {
      variables: {
          "productId": "gid://shopify/Product/1072481063",
          "option": {
              "id": "gid://shopify/ProductOption/1064576526"
          },
          "optionValuesToAdd": [
              {
                  "name": "Yellow"
              },
              {
                  "name": "Red"
              }
          ],
          "optionValuesToUpdate": [
              {
                  "id": "gid://shopify/ProductOptionValue/1054672275",
                  "name": "Purple"
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
    mutation updateOption(
      $productId: ID!,
      $option: OptionUpdateInput!,
      $optionValuesToAdd: [OptionValueCreateInput!],
      $optionValuesToUpdate: [OptionValueUpdateInput!],
      $optionValuesToDelete: [ID!]
      $variantStrategy: ProductOptionUpdateVariantStrategy
    ) {
      productOptionUpdate(
        productId: $productId,
        option: $option,
        optionValuesToAdd: $optionValuesToAdd,
        optionValuesToUpdate: $optionValuesToUpdate,
        optionValuesToDelete: $optionValuesToDelete,
        variantStrategy: $variantStrategy
      ) {
        userErrors { field message code }
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
          variants(first: 5) {
            nodes {
              id
              title
              selectedOptions { name, value }
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "productId": "gid://shopify/Product/1072481063",
    "option": {
      "id": "gid://shopify/ProductOption/1064576526"
    },
    "optionValuesToAdd": [
      {
        "name": "Yellow"
      },
      {
        "name": "Red"
      }
    ],
    "optionValuesToUpdate": [
      {
        "id": "gid://shopify/ProductOptionValue/1054672275",
        "name": "Purple"
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
      "query": `mutation updateOption(
        $productId: ID!,
        $option: OptionUpdateInput!,
        $optionValuesToAdd: [OptionValueCreateInput!],
        $optionValuesToUpdate: [OptionValueUpdateInput!],
        $optionValuesToDelete: [ID!]
        $variantStrategy: ProductOptionUpdateVariantStrategy
      ) {
        productOptionUpdate(
          productId: $productId,
          option: $option,
          optionValuesToAdd: $optionValuesToAdd,
          optionValuesToUpdate: $optionValuesToUpdate,
          optionValuesToDelete: $optionValuesToDelete,
          variantStrategy: $variantStrategy
        ) {
          userErrors { field message code }
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
            variants(first: 5) {
              nodes {
                id
                title
                selectedOptions { name, value }
              }
            }
          }
        }
      }`,
      "variables": {
          "productId": "gid://shopify/Product/1072481063",
          "option": {
              "id": "gid://shopify/ProductOption/1064576526"
          },
          "optionValuesToAdd": [
              {
                  "name": "Yellow"
              },
              {
                  "name": "Red"
              }
          ],
          "optionValuesToUpdate": [
              {
                  "id": "gid://shopify/ProductOptionValue/1054672275",
                  "name": "Purple"
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
  'mutation updateOption(
    $productId: ID!,
    $option: OptionUpdateInput!,
    $optionValuesToAdd: [OptionValueCreateInput!],
    $optionValuesToUpdate: [OptionValueUpdateInput!],
    $optionValuesToDelete: [ID!]
    $variantStrategy: ProductOptionUpdateVariantStrategy
  ) {
    productOptionUpdate(
      productId: $productId,
      option: $option,
      optionValuesToAdd: $optionValuesToAdd,
      optionValuesToUpdate: $optionValuesToUpdate,
      optionValuesToDelete: $optionValuesToDelete,
      variantStrategy: $variantStrategy
    ) {
      userErrors { field message code }
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
        variants(first: 5) {
          nodes {
            id
            title
            selectedOptions { name, value }
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "productId": "gid://shopify/Product/1072481063",
    "option": {
      "id": "gid://shopify/ProductOption/1064576526"
    },
    "optionValuesToAdd": [
      {
        "name": "Yellow"
      },
      {
        "name": "Red"
      }
    ],
    "optionValuesToUpdate": [
      {
        "id": "gid://shopify/ProductOptionValue/1054672275",
        "name": "Purple"
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "productOptionUpdate": {
      "userErrors": [],
      "product": {
        "id": "gid://shopify/Product/1072481063",
        "options": [
          {
            "id": "gid://shopify/ProductOption/1064576526",
            "name": "Color",
            "values": [
              "Purple"
            ],
            "position": 1,
            "optionValues": [
              {
                "name": "Purple",
                "hasVariants": true
              },
              {
                "name": "Yellow",
                "hasVariants": false
              },
              {
                "name": "Red",
                "hasVariants": false
              }
            ]
          }
        ],
        "variants": {
          "nodes": [
            {
              "id": "gid://shopify/ProductVariant/1070325103",
              "title": "Purple",
              "selectedOptions": [
                {
                  "name": "Color",
                  "value": "Purple"
                }
              ]
            }
          ]
        }
      }
    }
  }
  ```

* ### Update the values of an option linked to a metafield

  #### Description

  Update the values of a \[product option]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductOption) that's linked to a \[metafield]\(https://shopify.dev/docs/apps/build/custom-data). This example demonstrates how to use the \`linkedMetafieldValue\` field to associate \[metaobjects]\(https://shopify.dev/docs/apps/build/custom-data) with option values, ensuring that each value references a valid metaobject for the linked metafield. The response returns the product's options, including the linked metafield details and the updated option values, each with its name and associated metafield value. \[Learn more about metafield-linked product options]\(https://shopify.dev/api/admin/migrate/new-product-model/metafield-linked).

  #### Query

  ```graphql
  mutation updateOption(
    $productId: ID!,
    $option: OptionUpdateInput!,
    $optionValuesToAdd: [OptionValueCreateInput!],
    $optionValuesToUpdate: [OptionValueUpdateInput!],
    $optionValuesToDelete: [ID!]
  ) {
    productOptionUpdate(
      productId: $productId,
      option: $option,
      optionValuesToAdd: $optionValuesToAdd,
      optionValuesToUpdate: $optionValuesToUpdate,
      optionValuesToDelete: $optionValuesToDelete
    ) {
      userErrors { field message code }
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
    "productId": "gid://shopify/Product/1072481065",
    "option": {
      "id": "gid://shopify/ProductOption/1064576528"
    },
    "optionValuesToAdd": [
      {
        "linkedMetafieldValue": "gid://shopify/Metaobject/971662473"
      }
    ],
    "optionValuesToUpdate": [
      {
        "id": "gid://shopify/ProductOptionValue/1054672281",
        "linkedMetafieldValue": "gid://shopify/Metaobject/971662474"
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
  "query": "mutation updateOption( $productId: ID!, $option: OptionUpdateInput!, $optionValuesToAdd: [OptionValueCreateInput!], $optionValuesToUpdate: [OptionValueUpdateInput!], $optionValuesToDelete: [ID!] ) { productOptionUpdate( productId: $productId, option: $option, optionValuesToAdd: $optionValuesToAdd, optionValuesToUpdate: $optionValuesToUpdate, optionValuesToDelete: $optionValuesToDelete ) { userErrors { field message code } product { options { name linkedMetafield { namespace key } optionValues { name linkedMetafieldValue } } } } }",
   "variables": {
      "productId": "gid://shopify/Product/1072481065",
      "option": {
        "id": "gid://shopify/ProductOption/1064576528"
      },
      "optionValuesToAdd": [
        {
          "linkedMetafieldValue": "gid://shopify/Metaobject/971662473"
        }
      ],
      "optionValuesToUpdate": [
        {
          "id": "gid://shopify/ProductOptionValue/1054672281",
          "linkedMetafieldValue": "gid://shopify/Metaobject/971662474"
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
    mutation updateOption(
      $productId: ID!,
      $option: OptionUpdateInput!,
      $optionValuesToAdd: [OptionValueCreateInput!],
      $optionValuesToUpdate: [OptionValueUpdateInput!],
      $optionValuesToDelete: [ID!]
    ) {
      productOptionUpdate(
        productId: $productId,
        option: $option,
        optionValuesToAdd: $optionValuesToAdd,
        optionValuesToUpdate: $optionValuesToUpdate,
        optionValuesToDelete: $optionValuesToDelete
      ) {
        userErrors { field message code }
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
          "productId": "gid://shopify/Product/1072481065",
          "option": {
              "id": "gid://shopify/ProductOption/1064576528"
          },
          "optionValuesToAdd": [
              {
                  "linkedMetafieldValue": "gid://shopify/Metaobject/971662473"
              }
          ],
          "optionValuesToUpdate": [
              {
                  "id": "gid://shopify/ProductOptionValue/1054672281",
                  "linkedMetafieldValue": "gid://shopify/Metaobject/971662474"
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
    mutation updateOption(
      $productId: ID!,
      $option: OptionUpdateInput!,
      $optionValuesToAdd: [OptionValueCreateInput!],
      $optionValuesToUpdate: [OptionValueUpdateInput!],
      $optionValuesToDelete: [ID!]
    ) {
      productOptionUpdate(
        productId: $productId,
        option: $option,
        optionValuesToAdd: $optionValuesToAdd,
        optionValuesToUpdate: $optionValuesToUpdate,
        optionValuesToDelete: $optionValuesToDelete
      ) {
        userErrors { field message code }
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
    "productId": "gid://shopify/Product/1072481065",
    "option": {
      "id": "gid://shopify/ProductOption/1064576528"
    },
    "optionValuesToAdd": [
      {
        "linkedMetafieldValue": "gid://shopify/Metaobject/971662473"
      }
    ],
    "optionValuesToUpdate": [
      {
        "id": "gid://shopify/ProductOptionValue/1054672281",
        "linkedMetafieldValue": "gid://shopify/Metaobject/971662474"
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
      "query": `mutation updateOption(
        $productId: ID!,
        $option: OptionUpdateInput!,
        $optionValuesToAdd: [OptionValueCreateInput!],
        $optionValuesToUpdate: [OptionValueUpdateInput!],
        $optionValuesToDelete: [ID!]
      ) {
        productOptionUpdate(
          productId: $productId,
          option: $option,
          optionValuesToAdd: $optionValuesToAdd,
          optionValuesToUpdate: $optionValuesToUpdate,
          optionValuesToDelete: $optionValuesToDelete
        ) {
          userErrors { field message code }
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
          "productId": "gid://shopify/Product/1072481065",
          "option": {
              "id": "gid://shopify/ProductOption/1064576528"
          },
          "optionValuesToAdd": [
              {
                  "linkedMetafieldValue": "gid://shopify/Metaobject/971662473"
              }
          ],
          "optionValuesToUpdate": [
              {
                  "id": "gid://shopify/ProductOptionValue/1054672281",
                  "linkedMetafieldValue": "gid://shopify/Metaobject/971662474"
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
  'mutation updateOption(
    $productId: ID!,
    $option: OptionUpdateInput!,
    $optionValuesToAdd: [OptionValueCreateInput!],
    $optionValuesToUpdate: [OptionValueUpdateInput!],
    $optionValuesToDelete: [ID!]
  ) {
    productOptionUpdate(
      productId: $productId,
      option: $option,
      optionValuesToAdd: $optionValuesToAdd,
      optionValuesToUpdate: $optionValuesToUpdate,
      optionValuesToDelete: $optionValuesToDelete
    ) {
      userErrors { field message code }
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
    "productId": "gid://shopify/Product/1072481065",
    "option": {
      "id": "gid://shopify/ProductOption/1064576528"
    },
    "optionValuesToAdd": [
      {
        "linkedMetafieldValue": "gid://shopify/Metaobject/971662473"
      }
    ],
    "optionValuesToUpdate": [
      {
        "id": "gid://shopify/ProductOptionValue/1054672281",
        "linkedMetafieldValue": "gid://shopify/Metaobject/971662474"
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "productOptionUpdate": {
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
                "name": "White",
                "linkedMetafieldValue": "gid://shopify/Metaobject/971662474"
              },
              {
                "name": "Blue",
                "linkedMetafieldValue": "gid://shopify/Metaobject/971662472"
              },
              {
                "name": "Yellow",
                "linkedMetafieldValue": "gid://shopify/Metaobject/971662473"
              }
            ]
          }
        ]
      }
    }
  }
  ```

* ### Replace an option value with another value

  #### Description

  Replace an existing \[option value]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductOptionValue) with a new name and add the old name as a new value. In this example, the value "Small" is renamed to "Medium", and "Small" is re-added as a new value without any associated variants. The response returns the product's ID, the updated options (with their names, positions, and values), and the product variants reflecting the new value assignments.

  #### Query

  ```graphql
  mutation updateOption(
    $productId: ID!,
    $option: OptionUpdateInput!,
    $optionValuesToAdd: [OptionValueCreateInput!],
    $optionValuesToUpdate: [OptionValueUpdateInput!],
    $optionValuesToDelete: [ID!]
    $variantStrategy: ProductOptionUpdateVariantStrategy
  ) {
    productOptionUpdate(
      productId: $productId,
      option: $option,
      optionValuesToAdd: $optionValuesToAdd,
      optionValuesToUpdate: $optionValuesToUpdate,
      optionValuesToDelete: $optionValuesToDelete,
      variantStrategy: $variantStrategy
    ) {
      userErrors { field message code }
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
        variants(first: 5) {
          nodes {
            id
            title
            selectedOptions { name, value }
          }
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "productId": "gid://shopify/Product/1072481069",
    "option": {
      "id": "gid://shopify/ProductOption/1064576533"
    },
    "optionValuesToAdd": [
      {
        "name": "Small"
      }
    ],
    "optionValuesToUpdate": [
      {
        "id": "gid://shopify/ProductOptionValue/1054672293",
        "name": "Medium"
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
  "query": "mutation updateOption( $productId: ID!, $option: OptionUpdateInput!, $optionValuesToAdd: [OptionValueCreateInput!], $optionValuesToUpdate: [OptionValueUpdateInput!], $optionValuesToDelete: [ID!] $variantStrategy: ProductOptionUpdateVariantStrategy ) { productOptionUpdate( productId: $productId, option: $option, optionValuesToAdd: $optionValuesToAdd, optionValuesToUpdate: $optionValuesToUpdate, optionValuesToDelete: $optionValuesToDelete, variantStrategy: $variantStrategy ) { userErrors { field message code } product { id options { id name values position optionValues { id name hasVariants } } variants(first: 5) { nodes { id title selectedOptions { name, value } } } } } }",
   "variables": {
      "productId": "gid://shopify/Product/1072481069",
      "option": {
        "id": "gid://shopify/ProductOption/1064576533"
      },
      "optionValuesToAdd": [
        {
          "name": "Small"
        }
      ],
      "optionValuesToUpdate": [
        {
          "id": "gid://shopify/ProductOptionValue/1054672293",
          "name": "Medium"
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
    mutation updateOption(
      $productId: ID!,
      $option: OptionUpdateInput!,
      $optionValuesToAdd: [OptionValueCreateInput!],
      $optionValuesToUpdate: [OptionValueUpdateInput!],
      $optionValuesToDelete: [ID!]
      $variantStrategy: ProductOptionUpdateVariantStrategy
    ) {
      productOptionUpdate(
        productId: $productId,
        option: $option,
        optionValuesToAdd: $optionValuesToAdd,
        optionValuesToUpdate: $optionValuesToUpdate,
        optionValuesToDelete: $optionValuesToDelete,
        variantStrategy: $variantStrategy
      ) {
        userErrors { field message code }
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
          variants(first: 5) {
            nodes {
              id
              title
              selectedOptions { name, value }
            }
          }
        }
      }
    }`,
    {
      variables: {
          "productId": "gid://shopify/Product/1072481069",
          "option": {
              "id": "gid://shopify/ProductOption/1064576533"
          },
          "optionValuesToAdd": [
              {
                  "name": "Small"
              }
          ],
          "optionValuesToUpdate": [
              {
                  "id": "gid://shopify/ProductOptionValue/1054672293",
                  "name": "Medium"
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
    mutation updateOption(
      $productId: ID!,
      $option: OptionUpdateInput!,
      $optionValuesToAdd: [OptionValueCreateInput!],
      $optionValuesToUpdate: [OptionValueUpdateInput!],
      $optionValuesToDelete: [ID!]
      $variantStrategy: ProductOptionUpdateVariantStrategy
    ) {
      productOptionUpdate(
        productId: $productId,
        option: $option,
        optionValuesToAdd: $optionValuesToAdd,
        optionValuesToUpdate: $optionValuesToUpdate,
        optionValuesToDelete: $optionValuesToDelete,
        variantStrategy: $variantStrategy
      ) {
        userErrors { field message code }
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
          variants(first: 5) {
            nodes {
              id
              title
              selectedOptions { name, value }
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "productId": "gid://shopify/Product/1072481069",
    "option": {
      "id": "gid://shopify/ProductOption/1064576533"
    },
    "optionValuesToAdd": [
      {
        "name": "Small"
      }
    ],
    "optionValuesToUpdate": [
      {
        "id": "gid://shopify/ProductOptionValue/1054672293",
        "name": "Medium"
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
      "query": `mutation updateOption(
        $productId: ID!,
        $option: OptionUpdateInput!,
        $optionValuesToAdd: [OptionValueCreateInput!],
        $optionValuesToUpdate: [OptionValueUpdateInput!],
        $optionValuesToDelete: [ID!]
        $variantStrategy: ProductOptionUpdateVariantStrategy
      ) {
        productOptionUpdate(
          productId: $productId,
          option: $option,
          optionValuesToAdd: $optionValuesToAdd,
          optionValuesToUpdate: $optionValuesToUpdate,
          optionValuesToDelete: $optionValuesToDelete,
          variantStrategy: $variantStrategy
        ) {
          userErrors { field message code }
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
            variants(first: 5) {
              nodes {
                id
                title
                selectedOptions { name, value }
              }
            }
          }
        }
      }`,
      "variables": {
          "productId": "gid://shopify/Product/1072481069",
          "option": {
              "id": "gid://shopify/ProductOption/1064576533"
          },
          "optionValuesToAdd": [
              {
                  "name": "Small"
              }
          ],
          "optionValuesToUpdate": [
              {
                  "id": "gid://shopify/ProductOptionValue/1054672293",
                  "name": "Medium"
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
  'mutation updateOption(
    $productId: ID!,
    $option: OptionUpdateInput!,
    $optionValuesToAdd: [OptionValueCreateInput!],
    $optionValuesToUpdate: [OptionValueUpdateInput!],
    $optionValuesToDelete: [ID!]
    $variantStrategy: ProductOptionUpdateVariantStrategy
  ) {
    productOptionUpdate(
      productId: $productId,
      option: $option,
      optionValuesToAdd: $optionValuesToAdd,
      optionValuesToUpdate: $optionValuesToUpdate,
      optionValuesToDelete: $optionValuesToDelete,
      variantStrategy: $variantStrategy
    ) {
      userErrors { field message code }
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
        variants(first: 5) {
          nodes {
            id
            title
            selectedOptions { name, value }
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "productId": "gid://shopify/Product/1072481069",
    "option": {
      "id": "gid://shopify/ProductOption/1064576533"
    },
    "optionValuesToAdd": [
      {
        "name": "Small"
      }
    ],
    "optionValuesToUpdate": [
      {
        "id": "gid://shopify/ProductOptionValue/1054672293",
        "name": "Medium"
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "productOptionUpdate": {
      "userErrors": [],
      "product": {
        "id": "gid://shopify/Product/1072481069",
        "options": [
          {
            "id": "gid://shopify/ProductOption/1064576532",
            "name": "Color",
            "values": [
              "Blue",
              "Green"
            ],
            "position": 1,
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
          },
          {
            "id": "gid://shopify/ProductOption/1064576533",
            "name": "Size",
            "values": [
              "Medium"
            ],
            "position": 2,
            "optionValues": [
              {
                "name": "Medium",
                "hasVariants": true
              },
              {
                "name": "Small",
                "hasVariants": false
              }
            ]
          }
        ],
        "variants": {
          "nodes": [
            {
              "id": "gid://shopify/ProductVariant/1070325113",
              "title": "Blue / Medium",
              "selectedOptions": [
                {
                  "name": "Color",
                  "value": "Blue"
                },
                {
                  "name": "Size",
                  "value": "Medium"
                }
              ]
            },
            {
              "id": "gid://shopify/ProductVariant/1070325114",
              "title": "Green / Medium",
              "selectedOptions": [
                {
                  "name": "Color",
                  "value": "Green"
                },
                {
                  "name": "Size",
                  "value": "Medium"
                }
              ]
            }
          ]
        }
      }
    }
  }
  ```

* ### Adding a duplicate name for an option value returns an error

  #### Description

  This example demonstrates an attempt to add a new \[option value]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductOptionValue) with a name that already exists for the option. The mutation demonstrates the validation that prevents duplicate option value names within the same option. The response returns the product's ID and a user error indicating that the option value already exists, without modifying the existing option values.

  #### Query

  ```graphql
  mutation updateOption(
    $productId: ID!,
    $option: OptionUpdateInput!,
    $optionValuesToAdd: [OptionValueCreateInput!],
    $optionValuesToUpdate: [OptionValueUpdateInput!],
    $optionValuesToDelete: [ID!]
    $variantStrategy: ProductOptionUpdateVariantStrategy
  ) {
    productOptionUpdate(
      productId: $productId,
      option: $option,
      optionValuesToAdd: $optionValuesToAdd,
      optionValuesToUpdate: $optionValuesToUpdate,
      optionValuesToDelete: $optionValuesToDelete,
      variantStrategy: $variantStrategy
    ) {
      userErrors { field message code }
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
        variants(first: 5) {
          nodes {
            id
            title
            selectedOptions { name, value }
          }
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "productId": "gid://shopify/Product/1072481067",
    "option": {
      "id": "gid://shopify/ProductOption/1064576530"
    },
    "optionValuesToAdd": [
      {
        "name": "Red"
      },
      {
        "name": "Blue"
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
  "query": "mutation updateOption( $productId: ID!, $option: OptionUpdateInput!, $optionValuesToAdd: [OptionValueCreateInput!], $optionValuesToUpdate: [OptionValueUpdateInput!], $optionValuesToDelete: [ID!] $variantStrategy: ProductOptionUpdateVariantStrategy ) { productOptionUpdate( productId: $productId, option: $option, optionValuesToAdd: $optionValuesToAdd, optionValuesToUpdate: $optionValuesToUpdate, optionValuesToDelete: $optionValuesToDelete, variantStrategy: $variantStrategy ) { userErrors { field message code } product { id options { id name values position optionValues { id name hasVariants } } variants(first: 5) { nodes { id title selectedOptions { name, value } } } } } }",
   "variables": {
      "productId": "gid://shopify/Product/1072481067",
      "option": {
        "id": "gid://shopify/ProductOption/1064576530"
      },
      "optionValuesToAdd": [
        {
          "name": "Red"
        },
        {
          "name": "Blue"
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
    mutation updateOption(
      $productId: ID!,
      $option: OptionUpdateInput!,
      $optionValuesToAdd: [OptionValueCreateInput!],
      $optionValuesToUpdate: [OptionValueUpdateInput!],
      $optionValuesToDelete: [ID!]
      $variantStrategy: ProductOptionUpdateVariantStrategy
    ) {
      productOptionUpdate(
        productId: $productId,
        option: $option,
        optionValuesToAdd: $optionValuesToAdd,
        optionValuesToUpdate: $optionValuesToUpdate,
        optionValuesToDelete: $optionValuesToDelete,
        variantStrategy: $variantStrategy
      ) {
        userErrors { field message code }
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
          variants(first: 5) {
            nodes {
              id
              title
              selectedOptions { name, value }
            }
          }
        }
      }
    }`,
    {
      variables: {
          "productId": "gid://shopify/Product/1072481067",
          "option": {
              "id": "gid://shopify/ProductOption/1064576530"
          },
          "optionValuesToAdd": [
              {
                  "name": "Red"
              },
              {
                  "name": "Blue"
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
    mutation updateOption(
      $productId: ID!,
      $option: OptionUpdateInput!,
      $optionValuesToAdd: [OptionValueCreateInput!],
      $optionValuesToUpdate: [OptionValueUpdateInput!],
      $optionValuesToDelete: [ID!]
      $variantStrategy: ProductOptionUpdateVariantStrategy
    ) {
      productOptionUpdate(
        productId: $productId,
        option: $option,
        optionValuesToAdd: $optionValuesToAdd,
        optionValuesToUpdate: $optionValuesToUpdate,
        optionValuesToDelete: $optionValuesToDelete,
        variantStrategy: $variantStrategy
      ) {
        userErrors { field message code }
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
          variants(first: 5) {
            nodes {
              id
              title
              selectedOptions { name, value }
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "productId": "gid://shopify/Product/1072481067",
    "option": {
      "id": "gid://shopify/ProductOption/1064576530"
    },
    "optionValuesToAdd": [
      {
        "name": "Red"
      },
      {
        "name": "Blue"
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
      "query": `mutation updateOption(
        $productId: ID!,
        $option: OptionUpdateInput!,
        $optionValuesToAdd: [OptionValueCreateInput!],
        $optionValuesToUpdate: [OptionValueUpdateInput!],
        $optionValuesToDelete: [ID!]
        $variantStrategy: ProductOptionUpdateVariantStrategy
      ) {
        productOptionUpdate(
          productId: $productId,
          option: $option,
          optionValuesToAdd: $optionValuesToAdd,
          optionValuesToUpdate: $optionValuesToUpdate,
          optionValuesToDelete: $optionValuesToDelete,
          variantStrategy: $variantStrategy
        ) {
          userErrors { field message code }
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
            variants(first: 5) {
              nodes {
                id
                title
                selectedOptions { name, value }
              }
            }
          }
        }
      }`,
      "variables": {
          "productId": "gid://shopify/Product/1072481067",
          "option": {
              "id": "gid://shopify/ProductOption/1064576530"
          },
          "optionValuesToAdd": [
              {
                  "name": "Red"
              },
              {
                  "name": "Blue"
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
  'mutation updateOption(
    $productId: ID!,
    $option: OptionUpdateInput!,
    $optionValuesToAdd: [OptionValueCreateInput!],
    $optionValuesToUpdate: [OptionValueUpdateInput!],
    $optionValuesToDelete: [ID!]
    $variantStrategy: ProductOptionUpdateVariantStrategy
  ) {
    productOptionUpdate(
      productId: $productId,
      option: $option,
      optionValuesToAdd: $optionValuesToAdd,
      optionValuesToUpdate: $optionValuesToUpdate,
      optionValuesToDelete: $optionValuesToDelete,
      variantStrategy: $variantStrategy
    ) {
      userErrors { field message code }
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
        variants(first: 5) {
          nodes {
            id
            title
            selectedOptions { name, value }
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "productId": "gid://shopify/Product/1072481067",
    "option": {
      "id": "gid://shopify/ProductOption/1064576530"
    },
    "optionValuesToAdd": [
      {
        "name": "Red"
      },
      {
        "name": "Blue"
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "productOptionUpdate": {
      "userErrors": [
        {
          "field": [
            "optionValuesToAdd",
            "1",
            "name"
          ],
          "message": "Option value already exists.",
          "code": "OPTION_VALUE_ALREADY_EXISTS"
        }
      ],
      "product": {
        "id": "gid://shopify/Product/1072481067",
        "options": [
          {
            "id": "gid://shopify/ProductOption/1064576530",
            "name": "Color",
            "values": [
              "Blue"
            ],
            "position": 1,
            "optionValues": [
              {
                "id": "gid://shopify/ProductOptionValue/1054672288",
                "name": "Blue",
                "hasVariants": true
              }
            ]
          }
        ],
        "variants": {
          "nodes": [
            {
              "id": "gid://shopify/ProductVariant/1070325110",
              "title": "Blue",
              "selectedOptions": [
                {
                  "name": "Color",
                  "value": "Blue"
                }
              ]
            }
          ]
        }
      }
    }
  }
  ```

* ### productOptionUpdate reference
