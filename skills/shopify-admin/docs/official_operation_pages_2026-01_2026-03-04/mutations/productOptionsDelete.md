---
title: productOptionsDelete - GraphQL Admin
description: >-
  Deletes one or more
  [options](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductOption)

  from a
  [product](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product).
  Product options

  define the choices available for a product, such as size, color, or material.


  > Caution:

  > Removing an option can affect a product's

  >
  [variants](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant)
  and their

  > configuration. Deleting an option might also delete associated option values
  and, depending on the chosen

  >
  [strategy](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productoptionsdelete#arguments-strategy),

  > might affect variants.


  Use the `productOptionsDelete` mutation for the following use cases:


  - **Simplify product configuration**: Remove obsolete or unnecessary options

  (for example, discontinue "Material" if all variants are now the same
  material).

  - **Clean up after seasonal or limited-time offerings**: Delete options that
  are no longer

  relevant (for example, "Holiday edition").

  - **Automate catalog management**: Enable apps or integrations to
  programmatically remove options as product

  data changes.


  > Note:

  > The `productOptionsDelete` mutation enforces strict data integrity for
  product options and variants.

  > All option positions must remain sequential, and every remaining option must
  be used by at least one variant.


  After you delete a product option, you can further manage a product's
  configuration using related mutations:


  -
  [`productOptionsCreate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsCreate)

  -
  [`productOptionUpdate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionUpdate)

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
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsDelete
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsDelete.md
---

# product​Options​Delete

mutation

Requires `write_products` access scope. Also: The user must have a permission to edit products and delete product variants.

Deletes one or more [options](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductOption) from a [product](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product). Product options define the choices available for a product, such as size, color, or material.

***

**Caution:** Removing an option can affect a product\&#39;s \<a href="https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant">variants\</a> and their configuration. Deleting an option might also delete associated option values and, depending on the chosen \<a href="https://shopify.dev/docs/api/admin-graphql/latest/mutations/productoptionsdelete#arguments-strategy">strategy\</a>, might affect variants.

***

Use the `productOptionsDelete` mutation for the following use cases:

* **Simplify product configuration**: Remove obsolete or unnecessary options (for example, discontinue "Material" if all variants are now the same material).
* **Clean up after seasonal or limited-time offerings**: Delete options that are no longer relevant (for example, "Holiday edition").
* **Automate catalog management**: Enable apps or integrations to programmatically remove options as product data changes.

***

**Note:** The \<code>\<span class="PreventFireFoxApplyingGapToWBR">product\<wbr/>Options\<wbr/>Delete\</span>\</code> mutation enforces strict data integrity for product options and variants. All option positions must remain sequential, and every remaining option must be used by at least one variant.

***

After you delete a product option, you can further manage a product's configuration using related mutations:

* [`productOptionsCreate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsCreate)
* [`productOptionUpdate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionUpdate)
* [`productOptionsReorder`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsReorder)
* [`productVariantsBulkCreate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productVariantsBulkCreate)
* [`productVariantsBulkUpdate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productVariantsBulkUpdate)
* [`productSet`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productSet)

Learn more about the [product model](https://shopify.dev/docs/apps/build/graphql/migrate/new-product-model) and [adding product data](https://shopify.dev/docs/apps/build/graphql/migrate/new-product-model/add-data).

## Arguments

* options

  [\[ID!\]!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  IDs of the options to delete from the product.

* product​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  ID of the product from which to delete the options.

* strategy

  [Product​Option​Delete​Strategy](https://shopify.dev/docs/api/admin-graphql/latest/enums/ProductOptionDeleteStrategy)

  Default:DEFAULT

  The strategy defines which behavior the mutation should observe,such as how to handle a situation where deleting an option would result in duplicate variants.

***

## Product​Options​Delete​Payload returns

* deleted​Options​Ids

  [\[ID!\]](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  IDs of the options deleted.

* product

  [Product](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product)

  The updated product object.

* user​Errors

  [\[Product​Options​Delete​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductOptionsDeleteUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Delete a product option that doesn't have associated variants

  #### Description

  Delete a \[product option]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductOption) from an existing product. This example demonstrates how to remove an option that doesn't have associated variants. When the \`strategy\` field isn't specified or is set to \`DEFAULT\`, the mutation only deletes options that don't conflict with existing product variants. If deleting an option results in conflicting variants, then an error is returned instead. The response includes the product's updated option list and the IDs of the successfully deleted options.

  #### Query

  ```graphql
  mutation deleteOptions($productId: ID!, $options: [ID!]!, $strategy: ProductOptionDeleteStrategy) {
    productOptionsDelete(productId: $productId, options: $options, strategy: $strategy) {
      userErrors {
        field
        message
        code
      }
      deletedOptionsIds
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
    }
  }
  ```

  #### Variables

  ```json
  {
    "productId": "gid://shopify/Product/20995642",
    "options": [
      "gid://shopify/ProductOption/328272168"
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
  "query": "mutation deleteOptions($productId: ID!, $options: [ID!]!, $strategy: ProductOptionDeleteStrategy) { productOptionsDelete(productId: $productId, options: $options, strategy: $strategy) { userErrors { field message code } deletedOptionsIds product { id options { id name values position optionValues { id name hasVariants } } } } }",
   "variables": {
      "productId": "gid://shopify/Product/20995642",
      "options": [
        "gid://shopify/ProductOption/328272168"
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
    mutation deleteOptions($productId: ID!, $options: [ID!]!, $strategy: ProductOptionDeleteStrategy) {
      productOptionsDelete(productId: $productId, options: $options, strategy: $strategy) {
        userErrors {
          field
          message
          code
        }
        deletedOptionsIds
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
      }
    }`,
    {
      variables: {
          "productId": "gid://shopify/Product/20995642",
          "options": [
              "gid://shopify/ProductOption/328272168"
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
    mutation deleteOptions($productId: ID!, $options: [ID!]!, $strategy: ProductOptionDeleteStrategy) {
      productOptionsDelete(productId: $productId, options: $options, strategy: $strategy) {
        userErrors {
          field
          message
          code
        }
        deletedOptionsIds
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
      }
    }
  QUERY

  variables = {
    "productId": "gid://shopify/Product/20995642",
    "options": [
      "gid://shopify/ProductOption/328272168"
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation deleteOptions($productId: ID!, $options: [ID!]!, $strategy: ProductOptionDeleteStrategy) {
        productOptionsDelete(productId: $productId, options: $options, strategy: $strategy) {
          userErrors {
            field
            message
            code
          }
          deletedOptionsIds
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
        }
      }`,
      "variables": {
          "productId": "gid://shopify/Product/20995642",
          "options": [
              "gid://shopify/ProductOption/328272168"
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation deleteOptions($productId: ID!, $options: [ID!]!, $strategy: ProductOptionDeleteStrategy) {
    productOptionsDelete(productId: $productId, options: $options, strategy: $strategy) {
      userErrors {
        field
        message
        code
      }
      deletedOptionsIds
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
    }
  }' \
  --variables \
  '{
    "productId": "gid://shopify/Product/20995642",
    "options": [
      "gid://shopify/ProductOption/328272168"
    ]
  }'
  ```

  #### Response

  ```json
  {
    "productOptionsDelete": {
      "userErrors": [],
      "deletedOptionsIds": [
        "gid://shopify/ProductOption/328272168"
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
        ]
      }
    }
  }
  ```

* ### Delete a product option that has associated variants

  #### Description

  Delete a \[product option]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductOption) using the \`POSITION\` delete strategy. This example demonstrates how to remove an option that has multiple values and is associated with existing product variants. When the strategy is set to \`POSITION\`, the mutation deletes duplicate variants that would result from removing the option, keeping only variants with unique combinations of the remaining option values. Variants with the lowest position are prioritized when duplicates are found. The response returns the updated product with its remaining options and variants, along with the IDs of the successfully deleted options.

  #### Query

  ```graphql
  mutation deleteOptions($productId: ID!, $options: [ID!]!, $strategy: ProductOptionDeleteStrategy) {
    productOptionsDelete(productId: $productId, options: $options, strategy: $strategy) {
      userErrors {
        field
        message
        code
      }
      deletedOptionsIds
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
    }
  }
  ```

  #### Variables

  ```json
  {
    "productId": "gid://shopify/Product/20995642",
    "options": [
      "gid://shopify/ProductOption/328272167"
    ],
    "strategy": "POSITION"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation deleteOptions($productId: ID!, $options: [ID!]!, $strategy: ProductOptionDeleteStrategy) { productOptionsDelete(productId: $productId, options: $options, strategy: $strategy) { userErrors { field message code } deletedOptionsIds product { id options { id name values position optionValues { id name hasVariants } } } } }",
   "variables": {
      "productId": "gid://shopify/Product/20995642",
      "options": [
        "gid://shopify/ProductOption/328272167"
      ],
      "strategy": "POSITION"
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
    mutation deleteOptions($productId: ID!, $options: [ID!]!, $strategy: ProductOptionDeleteStrategy) {
      productOptionsDelete(productId: $productId, options: $options, strategy: $strategy) {
        userErrors {
          field
          message
          code
        }
        deletedOptionsIds
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
      }
    }`,
    {
      variables: {
          "productId": "gid://shopify/Product/20995642",
          "options": [
              "gid://shopify/ProductOption/328272167"
          ],
          "strategy": "POSITION"
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
    mutation deleteOptions($productId: ID!, $options: [ID!]!, $strategy: ProductOptionDeleteStrategy) {
      productOptionsDelete(productId: $productId, options: $options, strategy: $strategy) {
        userErrors {
          field
          message
          code
        }
        deletedOptionsIds
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
      }
    }
  QUERY

  variables = {
    "productId": "gid://shopify/Product/20995642",
    "options": [
      "gid://shopify/ProductOption/328272167"
    ],
    "strategy": "POSITION"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation deleteOptions($productId: ID!, $options: [ID!]!, $strategy: ProductOptionDeleteStrategy) {
        productOptionsDelete(productId: $productId, options: $options, strategy: $strategy) {
          userErrors {
            field
            message
            code
          }
          deletedOptionsIds
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
        }
      }`,
      "variables": {
          "productId": "gid://shopify/Product/20995642",
          "options": [
              "gid://shopify/ProductOption/328272167"
          ],
          "strategy": "POSITION"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation deleteOptions($productId: ID!, $options: [ID!]!, $strategy: ProductOptionDeleteStrategy) {
    productOptionsDelete(productId: $productId, options: $options, strategy: $strategy) {
      userErrors {
        field
        message
        code
      }
      deletedOptionsIds
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
    }
  }' \
  --variables \
  '{
    "productId": "gid://shopify/Product/20995642",
    "options": [
      "gid://shopify/ProductOption/328272167"
    ],
    "strategy": "POSITION"
  }'
  ```

  #### Response

  ```json
  {
    "productOptionsDelete": {
      "userErrors": [],
      "deletedOptionsIds": [
        "gid://shopify/ProductOption/328272167"
      ],
      "product": {
        "id": "gid://shopify/Product/20995642",
        "options": [
          {
            "id": "gid://shopify/ProductOption/328272169",
            "name": "Title",
            "values": [
              "Default Title"
            ],
            "position": 1,
            "optionValues": [
              {
                "id": "gid://shopify/ProductOptionValue/141051427",
                "name": "Default Title",
                "hasVariants": true
              }
            ]
          }
        ]
      }
    }
  }
  ```

* ### Deleting an option linked to variants without a strategy returns an error

  #### Description

  This example shows an attempt to delete a \[product option]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductOption) that has multiple option values associated with existing product variants, without specifying a delete strategy. The mutation demonstrates the validation that prevents deleting options when it would result in conflicting or duplicate variants. Since no \`strategy\` field is provided (defaulting to \`DEFAULT\` behavior), the mutation can't safely remove the option without potentially creating variant conflicts. The response returns the product's ID, an empty list of deleted options, and a user error indicating that the option cannot be deleted due to its multiple values being linked to variants.

  #### Query

  ```graphql
  mutation deleteOptions($productId: ID!, $options: [ID!]!, $strategy: ProductOptionDeleteStrategy) {
    productOptionsDelete(productId: $productId, options: $options, strategy: $strategy) {
      userErrors {
        field
        message
        code
      }
      deletedOptionsIds
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
    }
  }
  ```

  #### Variables

  ```json
  {
    "productId": "gid://shopify/Product/20995642",
    "options": [
      "gid://shopify/ProductOption/328272167"
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
  "query": "mutation deleteOptions($productId: ID!, $options: [ID!]!, $strategy: ProductOptionDeleteStrategy) { productOptionsDelete(productId: $productId, options: $options, strategy: $strategy) { userErrors { field message code } deletedOptionsIds product { id options { id name values position optionValues { id name hasVariants } } } } }",
   "variables": {
      "productId": "gid://shopify/Product/20995642",
      "options": [
        "gid://shopify/ProductOption/328272167"
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
    mutation deleteOptions($productId: ID!, $options: [ID!]!, $strategy: ProductOptionDeleteStrategy) {
      productOptionsDelete(productId: $productId, options: $options, strategy: $strategy) {
        userErrors {
          field
          message
          code
        }
        deletedOptionsIds
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
      }
    }`,
    {
      variables: {
          "productId": "gid://shopify/Product/20995642",
          "options": [
              "gid://shopify/ProductOption/328272167"
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
    mutation deleteOptions($productId: ID!, $options: [ID!]!, $strategy: ProductOptionDeleteStrategy) {
      productOptionsDelete(productId: $productId, options: $options, strategy: $strategy) {
        userErrors {
          field
          message
          code
        }
        deletedOptionsIds
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
      }
    }
  QUERY

  variables = {
    "productId": "gid://shopify/Product/20995642",
    "options": [
      "gid://shopify/ProductOption/328272167"
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation deleteOptions($productId: ID!, $options: [ID!]!, $strategy: ProductOptionDeleteStrategy) {
        productOptionsDelete(productId: $productId, options: $options, strategy: $strategy) {
          userErrors {
            field
            message
            code
          }
          deletedOptionsIds
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
        }
      }`,
      "variables": {
          "productId": "gid://shopify/Product/20995642",
          "options": [
              "gid://shopify/ProductOption/328272167"
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation deleteOptions($productId: ID!, $options: [ID!]!, $strategy: ProductOptionDeleteStrategy) {
    productOptionsDelete(productId: $productId, options: $options, strategy: $strategy) {
      userErrors {
        field
        message
        code
      }
      deletedOptionsIds
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
    }
  }' \
  --variables \
  '{
    "productId": "gid://shopify/Product/20995642",
    "options": [
      "gid://shopify/ProductOption/328272167"
    ]
  }'
  ```

  #### Response

  ```json
  {
    "productOptionsDelete": {
      "userErrors": [
        {
          "field": [
            "options"
          ],
          "message": "Cannot delete an option with multiple values.",
          "code": "CANNOT_DELETE_OPTION_WITH_MULTIPLE_VALUES"
        }
      ],
      "deletedOptionsIds": [],
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
        ]
      }
    }
  }
  ```

* ### productOptionsDelete reference
