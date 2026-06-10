---
title: productOptionsReorder - GraphQL Admin
description: >-
  Reorders the
  [options](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductOption)
  and

  [option
  values](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductOptionValue)
  on a

  [product](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product),

  updating the order in which [product
  variants](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant)

  are presented to customers.


  The `productOptionsReorder` mutation accepts a list of product options, each
  identified by `id` or `name`, and an

  optional list of values (also by `id` or `name`) specifying the new order. The
  order of options in the

  mutation's input determines their new positions (for example, the first option
  becomes `option1`).

  The order of values within each option determines their new positions. The
  mutation recalculates the order of

  variants based on the new option and value order.


  Suppose a product has the following variants:


  1. `"Red / Small"`

  2. `"Green / Medium"`

  3. `"Blue / Small"`


  You reorder options and values:


  ```

  options: [
    { name: "Size", values: [{ name: "Small" }, { name: "Medium" }] },
    { name: "Color", values: [{ name: "Green" }, { name: "Red" }, { name: "Blue" }] }
  ]

  ```


  The resulting variant order will be:


  1. `"Small / Green"`

  2. `"Small / Red"`

  3. `"Small / Blue"`

  4. `"Medium / Green"`


  Use the `productOptionsReorder` mutation for the following use cases:


  - **Change the order of product options**: For example, display "Color" before
  "Size" in a store.

  - **Reorder option values within an option**: For example, show "Red" before
  "Blue" in a color picker.

  - **Control the order of product variants**: The order of options and their
  values determines the sequence in which variants are listed and selected.

  - **Highlight best-selling options**: Present the most popular or relevant
  options and values first.

  - **Promote merchandising strategies**: Highlight seasonal colors, limited
  editions, or featured sizes.


  > Note:

  > The `productOptionsReorder` mutation enforces strict data integrity for
  product options and variants.

  > All option positions must be sequential, and every option should be used by
  at least one variant.


  After you reorder product options, you can further manage a product's
  configuration using related mutations:


  -
  [`productOptionsCreate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsCreate)

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

  and [managing product
  data](https://shopify.dev/docs/apps/build/graphql/migrate/new-product-model/add-data).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsReorder
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsReorder.md
---

# product​Options​Reorder

mutation

Requires `write_products` access scope. Also: The user must have a permission to update product variants.

Reorders the [options](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductOption) and [option values](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductOptionValue) on a [product](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product), updating the order in which [product variants](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant) are presented to customers.

The `productOptionsReorder` mutation accepts a list of product options, each identified by `id` or `name`, and an optional list of values (also by `id` or `name`) specifying the new order. The order of options in the mutation's input determines their new positions (for example, the first option becomes `option1`). The order of values within each option determines their new positions. The mutation recalculates the order of variants based on the new option and value order.

Suppose a product has the following variants:

1. `"Red / Small"`
2. `"Green / Medium"`
3. `"Blue / Small"`

You reorder options and values:

```
options: [
  { name: "Size", values: [{ name: "Small" }, { name: "Medium" }] },
  { name: "Color", values: [{ name: "Green" }, { name: "Red" }, { name: "Blue" }] }
]
```

The resulting variant order will be:

1. `"Small / Green"`
2. `"Small / Red"`
3. `"Small / Blue"`
4. `"Medium / Green"`

Use the `productOptionsReorder` mutation for the following use cases:

* **Change the order of product options**: For example, display "Color" before "Size" in a store.
* **Reorder option values within an option**: For example, show "Red" before "Blue" in a color picker.
* **Control the order of product variants**: The order of options and their values determines the sequence in which variants are listed and selected.
* **Highlight best-selling options**: Present the most popular or relevant options and values first.
* **Promote merchandising strategies**: Highlight seasonal colors, limited editions, or featured sizes.

***

**Note:** The \<code>\<span class="PreventFireFoxApplyingGapToWBR">product\<wbr/>Options\<wbr/>Reorder\</span>\</code> mutation enforces strict data integrity for product options and variants. All option positions must be sequential, and every option should be used by at least one variant.

***

After you reorder product options, you can further manage a product's configuration using related mutations:

* [`productOptionsCreate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsCreate)
* [`productOptionsDelete`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsDelete)
* [`productVariantsBulkCreate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productVariantsBulkCreate)
* [`productVariantsBulkUpdate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productVariantsBulkUpdate)
* [`productSet`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productSet)

Learn more about the [product model](https://shopify.dev/docs/apps/build/graphql/migrate/new-product-model) and [managing product data](https://shopify.dev/docs/apps/build/graphql/migrate/new-product-model/add-data).

## Arguments

* options

  [\[Option​Reorder​Input!\]!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/OptionReorderInput)

  required

  Options to reorder on the product.

* product​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the product to update.

***

## Product​Options​Reorder​Payload returns

* product

  [Product](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product)

  The updated product object.

* user​Errors

  [\[Product​Options​Reorder​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductOptionsReorderUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Reorder options and change the order of option values

  #### Description

  Reorder the \[product options]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductOption) and the order of their \[option values]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductOptionValue) for an existing product. This example demonstrates how to update a product so that the "Color" option appears before "Size", and the color values are reordered to "Green", "Blue", and "Red". The \`values\` field can be omitted for an option to preserve its existing order. The response returns the product's ID, the updated list of options (with their names, positions, and reordered values), and the details of the product variants generated from the new option order.

  #### Query

  ```graphql
  mutation reorderOptions($options: [OptionReorderInput!]!, $productId: ID!) {
    productOptionsReorder(options: $options, productId: $productId) {
      userErrors {
        field
        message
        code
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
        variants(first: 5) {
          nodes {
            id
            title
            selectedOptions {
              name
              value
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
    "productId": "gid://shopify/Product/1072481177",
    "options": [
      {
        "name": "Color",
        "values": [
          {
            "name": "Green"
          },
          {
            "name": "Blue"
          },
          {
            "name": "Red"
          }
        ]
      },
      {
        "name": "Size"
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
  "query": "mutation reorderOptions($options: [OptionReorderInput!]!, $productId: ID!) { productOptionsReorder(options: $options, productId: $productId) { userErrors { field message code } product { id options { id name values position optionValues { id name hasVariants } } variants(first: 5) { nodes { id title selectedOptions { name value } } } } } }",
   "variables": {
      "productId": "gid://shopify/Product/1072481177",
      "options": [
        {
          "name": "Color",
          "values": [
            {
              "name": "Green"
            },
            {
              "name": "Blue"
            },
            {
              "name": "Red"
            }
          ]
        },
        {
          "name": "Size"
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
    mutation reorderOptions($options: [OptionReorderInput!]!, $productId: ID!) {
      productOptionsReorder(options: $options, productId: $productId) {
        userErrors {
          field
          message
          code
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
          variants(first: 5) {
            nodes {
              id
              title
              selectedOptions {
                name
                value
              }
            }
          }
        }
      }
    }`,
    {
      variables: {
          "productId": "gid://shopify/Product/1072481177",
          "options": [
              {
                  "name": "Color",
                  "values": [
                      {
                          "name": "Green"
                      },
                      {
                          "name": "Blue"
                      },
                      {
                          "name": "Red"
                      }
                  ]
              },
              {
                  "name": "Size"
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
    mutation reorderOptions($options: [OptionReorderInput!]!, $productId: ID!) {
      productOptionsReorder(options: $options, productId: $productId) {
        userErrors {
          field
          message
          code
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
          variants(first: 5) {
            nodes {
              id
              title
              selectedOptions {
                name
                value
              }
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "productId": "gid://shopify/Product/1072481177",
    "options": [
      {
        "name": "Color",
        "values": [
          {
            "name": "Green"
          },
          {
            "name": "Blue"
          },
          {
            "name": "Red"
          }
        ]
      },
      {
        "name": "Size"
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
      "query": `mutation reorderOptions($options: [OptionReorderInput!]!, $productId: ID!) {
        productOptionsReorder(options: $options, productId: $productId) {
          userErrors {
            field
            message
            code
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
            variants(first: 5) {
              nodes {
                id
                title
                selectedOptions {
                  name
                  value
                }
              }
            }
          }
        }
      }`,
      "variables": {
          "productId": "gid://shopify/Product/1072481177",
          "options": [
              {
                  "name": "Color",
                  "values": [
                      {
                          "name": "Green"
                      },
                      {
                          "name": "Blue"
                      },
                      {
                          "name": "Red"
                      }
                  ]
              },
              {
                  "name": "Size"
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
  'mutation reorderOptions($options: [OptionReorderInput!]!, $productId: ID!) {
    productOptionsReorder(options: $options, productId: $productId) {
      userErrors {
        field
        message
        code
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
        variants(first: 5) {
          nodes {
            id
            title
            selectedOptions {
              name
              value
            }
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "productId": "gid://shopify/Product/1072481177",
    "options": [
      {
        "name": "Color",
        "values": [
          {
            "name": "Green"
          },
          {
            "name": "Blue"
          },
          {
            "name": "Red"
          }
        ]
      },
      {
        "name": "Size"
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "productOptionsReorder": {
      "userErrors": [],
      "product": {
        "id": "gid://shopify/Product/1072481177",
        "options": [
          {
            "id": "gid://shopify/ProductOption/1064576699",
            "name": "Color",
            "values": [
              "Green",
              "Blue",
              "Red"
            ],
            "position": 1,
            "optionValues": [
              {
                "name": "Green",
                "hasVariants": true
              },
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
            "id": "gid://shopify/ProductOption/1064576698",
            "name": "Size",
            "values": [
              "L",
              "S",
              "M"
            ],
            "position": 2,
            "optionValues": [
              {
                "name": "L",
                "hasVariants": true
              },
              {
                "name": "S",
                "hasVariants": true
              },
              {
                "name": "M",
                "hasVariants": true
              }
            ]
          }
        ],
        "variants": {
          "nodes": [
            {
              "id": "gid://shopify/ProductVariant/1070325355",
              "title": "Green / L",
              "selectedOptions": [
                {
                  "name": "Color",
                  "value": "Green"
                },
                {
                  "name": "Size",
                  "value": "L"
                }
              ]
            },
            {
              "id": "gid://shopify/ProductVariant/1070325353",
              "title": "Blue / S",
              "selectedOptions": [
                {
                  "name": "Color",
                  "value": "Blue"
                },
                {
                  "name": "Size",
                  "value": "S"
                }
              ]
            },
            {
              "id": "gid://shopify/ProductVariant/1070325354",
              "title": "Red / M",
              "selectedOptions": [
                {
                  "name": "Color",
                  "value": "Red"
                },
                {
                  "name": "Size",
                  "value": "M"
                }
              ]
            }
          ]
        }
      }
    }
  }
  ```

* ### Reordering option values with any value missing in the input returns an error

  #### Description

  This example shows an attempt to reorder the option values for a product, but one of the values is missing from the input. The mutation demonstrates the validation that prevents reordering option values if any value is missing. The response returns the product's ID and a user error indicating that the value is missing, without modifying the existing option values.

  #### Query

  ```graphql
  mutation reorderOptions($options: [OptionReorderInput!]!, $productId: ID!) {
    productOptionsReorder(options: $options, productId: $productId) {
      userErrors {
        field
        message
        code
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
        variants(first: 5) {
          nodes {
            id
            title
            selectedOptions {
              name
              value
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
    "productId": "gid://shopify/Product/20995642",
    "options": [
      {
        "name": "Title",
        "values": [
          {
            "name": "158cm"
          },
          {
            "name": "151cm"
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
  "query": "mutation reorderOptions($options: [OptionReorderInput!]!, $productId: ID!) { productOptionsReorder(options: $options, productId: $productId) { userErrors { field message code } product { id options { id name values position optionValues { id name hasVariants } } variants(first: 5) { nodes { id title selectedOptions { name value } } } } } }",
   "variables": {
      "productId": "gid://shopify/Product/20995642",
      "options": [
        {
          "name": "Title",
          "values": [
            {
              "name": "158cm"
            },
            {
              "name": "151cm"
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
    mutation reorderOptions($options: [OptionReorderInput!]!, $productId: ID!) {
      productOptionsReorder(options: $options, productId: $productId) {
        userErrors {
          field
          message
          code
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
          variants(first: 5) {
            nodes {
              id
              title
              selectedOptions {
                name
                value
              }
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
                  "name": "Title",
                  "values": [
                      {
                          "name": "158cm"
                      },
                      {
                          "name": "151cm"
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
    mutation reorderOptions($options: [OptionReorderInput!]!, $productId: ID!) {
      productOptionsReorder(options: $options, productId: $productId) {
        userErrors {
          field
          message
          code
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
          variants(first: 5) {
            nodes {
              id
              title
              selectedOptions {
                name
                value
              }
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
        "name": "Title",
        "values": [
          {
            "name": "158cm"
          },
          {
            "name": "151cm"
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
      "query": `mutation reorderOptions($options: [OptionReorderInput!]!, $productId: ID!) {
        productOptionsReorder(options: $options, productId: $productId) {
          userErrors {
            field
            message
            code
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
            variants(first: 5) {
              nodes {
                id
                title
                selectedOptions {
                  name
                  value
                }
              }
            }
          }
        }
      }`,
      "variables": {
          "productId": "gid://shopify/Product/20995642",
          "options": [
              {
                  "name": "Title",
                  "values": [
                      {
                          "name": "158cm"
                      },
                      {
                          "name": "151cm"
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
  'mutation reorderOptions($options: [OptionReorderInput!]!, $productId: ID!) {
    productOptionsReorder(options: $options, productId: $productId) {
      userErrors {
        field
        message
        code
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
        variants(first: 5) {
          nodes {
            id
            title
            selectedOptions {
              name
              value
            }
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
        "name": "Title",
        "values": [
          {
            "name": "158cm"
          },
          {
            "name": "151cm"
          }
        ]
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "productOptionsReorder": {
      "userErrors": [
        {
          "field": [
            "options"
          ],
          "message": "Missing option value '155cm'.",
          "code": "MISSING_OPTION_VALUE"
        }
      ],
      "product": {
        "id": "gid://shopify/Product/20995642",
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
        ],
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
        }
      }
    }
  }
  ```

* ### productOptionsReorder reference
