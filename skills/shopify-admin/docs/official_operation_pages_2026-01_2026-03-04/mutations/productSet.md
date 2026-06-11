---
title: productSet - GraphQL Admin
description: >-
  Performs multiple operations to create or update products in a single request.


  Use the `productSet` mutation to sync information from an external data source
  into Shopify, manage large

  product catalogs, and perform batch updates. The mutation is helpful for bulk
  product management, including price

  adjustments, inventory updates, and product lifecycle management.


  The behavior of `productSet` depends on the type of field it's modifying:


  - **For list fields**: Creates new entries, updates existing entries, and
  deletes existing entries

  that aren't included in the mutation's input. Common examples of list fields
  include

  [`collections`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productSet#arguments-input.fields.collections),

  [`metafields`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productSet#arguments-input.fields.metafields),

  and
  [`variants`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productSet#arguments-input.fields.variants).


  - **For all other field types**: Updates only the included fields. Any omitted
  fields will remain unchanged.


  > Note:

  > By default, stores have a limit of 2048 product variants for each product.


  You can run `productSet` in one of the following modes:


  - **Synchronously**: Returns the updated product in the response.

  - **Asynchronously**: Returns a
  [`ProductSetOperation`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductSetOperation)
  object.

  Use the
  [`productOperation`](https://shopify.dev/api/admin-graphql/latest/queries/productOperation)
  query to check the status of the operation and

  retrieve details of the updated product and its product variants.


  If you need to only manage product variants, then use one of the following
  mutations:


  -
  [`productVariantsBulkCreate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productVariantsBulkCreate)

  -
  [`productVariantsBulkUpdate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productVariantsBulkUpdate)

  -
  [`productVariantsBulkDelete`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productVariantsBulkDelete)


  If you need to only manage product options, then use one of the following
  mutations:


  -
  [`productOptionsCreate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsCreate)

  -
  [`productOptionUpdate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionUpdate)

  -
  [`productOptionsReorder`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsReorder)

  -
  [`productOptionsDelete`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsDelete)


  Learn more about [syncing product data from an external
  source](https://shopify.dev/docs/apps/build/graphql/migrate/new-product-model/sync-data).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/productSet'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/productSet.md'
---

# product​Set

mutation

Requires `write_products` access scope. Also: The user must have a permission to create products.

Performs multiple operations to create or update products in a single request.

Use the `productSet` mutation to sync information from an external data source into Shopify, manage large product catalogs, and perform batch updates. The mutation is helpful for bulk product management, including price adjustments, inventory updates, and product lifecycle management.

The behavior of `productSet` depends on the type of field it's modifying:

* **For list fields**: Creates new entries, updates existing entries, and deletes existing entries that aren't included in the mutation's input. Common examples of list fields include [`collections`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productSet#arguments-input.fields.collections), [`metafields`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productSet#arguments-input.fields.metafields), and [`variants`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productSet#arguments-input.fields.variants).

* **For all other field types**: Updates only the included fields. Any omitted fields will remain unchanged.

***

**Note:** By default, stores have a limit of 2048 product variants for each product.

***

You can run `productSet` in one of the following modes:

* **Synchronously**: Returns the updated product in the response.
* **Asynchronously**: Returns a [`ProductSetOperation`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductSetOperation) object. Use the [`productOperation`](https://shopify.dev/api/admin-graphql/latest/queries/productOperation) query to check the status of the operation and retrieve details of the updated product and its product variants.

If you need to only manage product variants, then use one of the following mutations:

* [`productVariantsBulkCreate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productVariantsBulkCreate)
* [`productVariantsBulkUpdate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productVariantsBulkUpdate)
* [`productVariantsBulkDelete`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productVariantsBulkDelete)

If you need to only manage product options, then use one of the following mutations:

* [`productOptionsCreate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsCreate)
* [`productOptionUpdate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionUpdate)
* [`productOptionsReorder`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsReorder)
* [`productOptionsDelete`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productOptionsDelete)

Learn more about [syncing product data from an external source](https://shopify.dev/docs/apps/build/graphql/migrate/new-product-model/sync-data).

## Arguments

* identifier

  [Product​Set​Identifiers](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/ProductSetIdentifiers)

  Specifies the identifier that will be used to lookup the resource.

* input

  [Product​Set​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/ProductSetInput)

  required

  The properties of the newly created or updated product.

* synchronous

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:true

  Whether the mutation should be run synchronously or asynchronously.

  If `true`, the mutation will return the updated `product`.

  If `false`, the mutation will return a `productSetOperation`.

  Defaults to `true`.

  Setting `synchronous: false` may be desirable depending on the input complexity/size, and should be used if you are experiencing timeouts.

  **Note**: When run in the context of a [bulk operation](https://shopify.dev/api/usage/bulk-operations/imports), the mutation will always run synchronously and this argument will be ignored.

***

## Product​Set​Payload returns

* product

  [Product](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product)

  The product object.

* product​Set​Operation

  [Product​Set​Operation](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductSetOperation)

  The product set operation, returned when run in asynchronous mode.

* user​Errors

  [\[Product​Set​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductSetUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Asynchronously create a product with two variants

  #### Description

  Create a product with two variants asynchronously using different \[option values]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductOptionValue). This example returns a \[\`productSetOperation\`]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductSetOperation) with the status \`CREATED\`.

  #### Query

  ```graphql
  mutation createProductAsynchronous($productSet: ProductSetInput!, $synchronous: Boolean!) {
    productSet(synchronous: $synchronous, input: $productSet) {
      product {
        id
      }
      productSetOperation {
        id
        status
        userErrors {
          code
          field
          message
        }
      }
      userErrors {
        code
        field
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "synchronous": false,
    "productSet": {
      "title": "Winter hat",
      "productOptions": [
        {
          "name": "Color",
          "position": 1,
          "values": [
            {
              "name": "Grey"
            },
            {
              "name": "Black"
            }
          ]
        }
      ],
      "variants": [
        {
          "optionValues": [
            {
              "optionName": "Color",
              "name": "Grey"
            }
          ],
          "price": 79.99
        },
        {
          "optionValues": [
            {
              "optionName": "Color",
              "name": "Black"
            }
          ],
          "price": 69.99
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
  "query": "mutation createProductAsynchronous($productSet: ProductSetInput!, $synchronous: Boolean!) { productSet(synchronous: $synchronous, input: $productSet) { product { id } productSetOperation { id status userErrors { code field message } } userErrors { code field message } } }",
   "variables": {
      "synchronous": false,
      "productSet": {
        "title": "Winter hat",
        "productOptions": [
          {
            "name": "Color",
            "position": 1,
            "values": [
              {
                "name": "Grey"
              },
              {
                "name": "Black"
              }
            ]
          }
        ],
        "variants": [
          {
            "optionValues": [
              {
                "optionName": "Color",
                "name": "Grey"
              }
            ],
            "price": 79.99
          },
          {
            "optionValues": [
              {
                "optionName": "Color",
                "name": "Black"
              }
            ],
            "price": 69.99
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
    mutation createProductAsynchronous($productSet: ProductSetInput!, $synchronous: Boolean!) {
      productSet(synchronous: $synchronous, input: $productSet) {
        product {
          id
        }
        productSetOperation {
          id
          status
          userErrors {
            code
            field
            message
          }
        }
        userErrors {
          code
          field
          message
        }
      }
    }`,
    {
      variables: {
          "synchronous": false,
          "productSet": {
              "title": "Winter hat",
              "productOptions": [
                  {
                      "name": "Color",
                      "position": 1,
                      "values": [
                          {
                              "name": "Grey"
                          },
                          {
                              "name": "Black"
                          }
                      ]
                  }
              ],
              "variants": [
                  {
                      "optionValues": [
                          {
                              "optionName": "Color",
                              "name": "Grey"
                          }
                      ],
                      "price": 79.99
                  },
                  {
                      "optionValues": [
                          {
                              "optionName": "Color",
                              "name": "Black"
                          }
                      ],
                      "price": 69.99
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
    mutation createProductAsynchronous($productSet: ProductSetInput!, $synchronous: Boolean!) {
      productSet(synchronous: $synchronous, input: $productSet) {
        product {
          id
        }
        productSetOperation {
          id
          status
          userErrors {
            code
            field
            message
          }
        }
        userErrors {
          code
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "synchronous": false,
    "productSet": {
      "title": "Winter hat",
      "productOptions": [
        {
          "name": "Color",
          "position": 1,
          "values": [
            {
              "name": "Grey"
            },
            {
              "name": "Black"
            }
          ]
        }
      ],
      "variants": [
        {
          "optionValues": [
            {
              "optionName": "Color",
              "name": "Grey"
            }
          ],
          "price": 79.99
        },
        {
          "optionValues": [
            {
              "optionName": "Color",
              "name": "Black"
            }
          ],
          "price": 69.99
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
      "query": `mutation createProductAsynchronous($productSet: ProductSetInput!, $synchronous: Boolean!) {
        productSet(synchronous: $synchronous, input: $productSet) {
          product {
            id
          }
          productSetOperation {
            id
            status
            userErrors {
              code
              field
              message
            }
          }
          userErrors {
            code
            field
            message
          }
        }
      }`,
      "variables": {
          "synchronous": false,
          "productSet": {
              "title": "Winter hat",
              "productOptions": [
                  {
                      "name": "Color",
                      "position": 1,
                      "values": [
                          {
                              "name": "Grey"
                          },
                          {
                              "name": "Black"
                          }
                      ]
                  }
              ],
              "variants": [
                  {
                      "optionValues": [
                          {
                              "optionName": "Color",
                              "name": "Grey"
                          }
                      ],
                      "price": 79.99
                  },
                  {
                      "optionValues": [
                          {
                              "optionName": "Color",
                              "name": "Black"
                          }
                      ],
                      "price": 69.99
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
  'mutation createProductAsynchronous($productSet: ProductSetInput!, $synchronous: Boolean!) {
    productSet(synchronous: $synchronous, input: $productSet) {
      product {
        id
      }
      productSetOperation {
        id
        status
        userErrors {
          code
          field
          message
        }
      }
      userErrors {
        code
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "synchronous": false,
    "productSet": {
      "title": "Winter hat",
      "productOptions": [
        {
          "name": "Color",
          "position": 1,
          "values": [
            {
              "name": "Grey"
            },
            {
              "name": "Black"
            }
          ]
        }
      ],
      "variants": [
        {
          "optionValues": [
            {
              "optionName": "Color",
              "name": "Grey"
            }
          ],
          "price": 79.99
        },
        {
          "optionValues": [
            {
              "optionName": "Color",
              "name": "Black"
            }
          ],
          "price": 69.99
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "productSet": {
      "product": null,
      "productSetOperation": {
        "id": "gid://shopify/ProductSetOperation/1010603851",
        "status": "CREATED",
        "userErrors": []
      },
      "userErrors": []
    }
  }
  ```

* ### Create a product and associate files

  #### Description

  Create a product and associate file attachments (like images or videos). This example returns the product and its associated image files.

  #### Query

  ```graphql
  mutation createProduct($productSet: ProductSetInput!, $synchronous: Boolean!) {
    productSet(synchronous: $synchronous, input: $productSet) {
      product {
        id
        media(first: 5) {
          nodes {
            id
            alt
            mediaContentType
            status
          }
        }
        variants(first: 5) {
          nodes {
            title
            price
            media(first: 5) {
              nodes {
                id
                alt
                mediaContentType
                status
              }
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
    "synchronous": true,
    "productSet": {
      "title": "Winter hat",
      "productOptions": [
        {
          "name": "Color",
          "values": [
            {
              "name": "Grey"
            },
            {
              "name": "Black"
            }
          ]
        }
      ],
      "files": [
        {
          "originalSource": "https://example.com/hats/grey-hat.jpg",
          "alt": "An elegant grey hat",
          "filename": "grey-hat.jpg",
          "contentType": "IMAGE"
        },
        {
          "originalSource": "https://example.com/hats/black-hat.jpg",
          "alt": "An elegant black hat",
          "filename": "black-hat.jpg",
          "contentType": "IMAGE"
        }
      ],
      "variants": [
        {
          "optionValues": [
            {
              "optionName": "Color",
              "name": "Grey"
            }
          ],
          "file": {
            "originalSource": "https://example.com/hats/grey-hat.jpg",
            "alt": "An elegant grey hat",
            "filename": "grey-hat.jpg",
            "contentType": "IMAGE"
          },
          "price": 11.99
        },
        {
          "optionValues": [
            {
              "optionName": "Color",
              "name": "Black"
            }
          ],
          "file": {
            "originalSource": "https://example.com/hats/black-hat.jpg",
            "alt": "An elegant black hat",
            "filename": "black-hat.jpg",
            "contentType": "IMAGE"
          },
          "price": 11.99
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
  "query": "mutation createProduct($productSet: ProductSetInput!, $synchronous: Boolean!) { productSet(synchronous: $synchronous, input: $productSet) { product { id media(first: 5) { nodes { id alt mediaContentType status } } variants(first: 5) { nodes { title price media(first: 5) { nodes { id alt mediaContentType status } } } } } userErrors { field message } } }",
   "variables": {
      "synchronous": true,
      "productSet": {
        "title": "Winter hat",
        "productOptions": [
          {
            "name": "Color",
            "values": [
              {
                "name": "Grey"
              },
              {
                "name": "Black"
              }
            ]
          }
        ],
        "files": [
          {
            "originalSource": "https://example.com/hats/grey-hat.jpg",
            "alt": "An elegant grey hat",
            "filename": "grey-hat.jpg",
            "contentType": "IMAGE"
          },
          {
            "originalSource": "https://example.com/hats/black-hat.jpg",
            "alt": "An elegant black hat",
            "filename": "black-hat.jpg",
            "contentType": "IMAGE"
          }
        ],
        "variants": [
          {
            "optionValues": [
              {
                "optionName": "Color",
                "name": "Grey"
              }
            ],
            "file": {
              "originalSource": "https://example.com/hats/grey-hat.jpg",
              "alt": "An elegant grey hat",
              "filename": "grey-hat.jpg",
              "contentType": "IMAGE"
            },
            "price": 11.99
          },
          {
            "optionValues": [
              {
                "optionName": "Color",
                "name": "Black"
              }
            ],
            "file": {
              "originalSource": "https://example.com/hats/black-hat.jpg",
              "alt": "An elegant black hat",
              "filename": "black-hat.jpg",
              "contentType": "IMAGE"
            },
            "price": 11.99
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
    mutation createProduct($productSet: ProductSetInput!, $synchronous: Boolean!) {
      productSet(synchronous: $synchronous, input: $productSet) {
        product {
          id
          media(first: 5) {
            nodes {
              id
              alt
              mediaContentType
              status
            }
          }
          variants(first: 5) {
            nodes {
              title
              price
              media(first: 5) {
                nodes {
                  id
                  alt
                  mediaContentType
                  status
                }
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
          "synchronous": true,
          "productSet": {
              "title": "Winter hat",
              "productOptions": [
                  {
                      "name": "Color",
                      "values": [
                          {
                              "name": "Grey"
                          },
                          {
                              "name": "Black"
                          }
                      ]
                  }
              ],
              "files": [
                  {
                      "originalSource": "https://example.com/hats/grey-hat.jpg",
                      "alt": "An elegant grey hat",
                      "filename": "grey-hat.jpg",
                      "contentType": "IMAGE"
                  },
                  {
                      "originalSource": "https://example.com/hats/black-hat.jpg",
                      "alt": "An elegant black hat",
                      "filename": "black-hat.jpg",
                      "contentType": "IMAGE"
                  }
              ],
              "variants": [
                  {
                      "optionValues": [
                          {
                              "optionName": "Color",
                              "name": "Grey"
                          }
                      ],
                      "file": {
                          "originalSource": "https://example.com/hats/grey-hat.jpg",
                          "alt": "An elegant grey hat",
                          "filename": "grey-hat.jpg",
                          "contentType": "IMAGE"
                      },
                      "price": 11.99
                  },
                  {
                      "optionValues": [
                          {
                              "optionName": "Color",
                              "name": "Black"
                          }
                      ],
                      "file": {
                          "originalSource": "https://example.com/hats/black-hat.jpg",
                          "alt": "An elegant black hat",
                          "filename": "black-hat.jpg",
                          "contentType": "IMAGE"
                      },
                      "price": 11.99
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
    mutation createProduct($productSet: ProductSetInput!, $synchronous: Boolean!) {
      productSet(synchronous: $synchronous, input: $productSet) {
        product {
          id
          media(first: 5) {
            nodes {
              id
              alt
              mediaContentType
              status
            }
          }
          variants(first: 5) {
            nodes {
              title
              price
              media(first: 5) {
                nodes {
                  id
                  alt
                  mediaContentType
                  status
                }
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
    "synchronous": true,
    "productSet": {
      "title": "Winter hat",
      "productOptions": [
        {
          "name": "Color",
          "values": [
            {
              "name": "Grey"
            },
            {
              "name": "Black"
            }
          ]
        }
      ],
      "files": [
        {
          "originalSource": "https://example.com/hats/grey-hat.jpg",
          "alt": "An elegant grey hat",
          "filename": "grey-hat.jpg",
          "contentType": "IMAGE"
        },
        {
          "originalSource": "https://example.com/hats/black-hat.jpg",
          "alt": "An elegant black hat",
          "filename": "black-hat.jpg",
          "contentType": "IMAGE"
        }
      ],
      "variants": [
        {
          "optionValues": [
            {
              "optionName": "Color",
              "name": "Grey"
            }
          ],
          "file": {
            "originalSource": "https://example.com/hats/grey-hat.jpg",
            "alt": "An elegant grey hat",
            "filename": "grey-hat.jpg",
            "contentType": "IMAGE"
          },
          "price": 11.99
        },
        {
          "optionValues": [
            {
              "optionName": "Color",
              "name": "Black"
            }
          ],
          "file": {
            "originalSource": "https://example.com/hats/black-hat.jpg",
            "alt": "An elegant black hat",
            "filename": "black-hat.jpg",
            "contentType": "IMAGE"
          },
          "price": 11.99
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
      "query": `mutation createProduct($productSet: ProductSetInput!, $synchronous: Boolean!) {
        productSet(synchronous: $synchronous, input: $productSet) {
          product {
            id
            media(first: 5) {
              nodes {
                id
                alt
                mediaContentType
                status
              }
            }
            variants(first: 5) {
              nodes {
                title
                price
                media(first: 5) {
                  nodes {
                    id
                    alt
                    mediaContentType
                    status
                  }
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
          "synchronous": true,
          "productSet": {
              "title": "Winter hat",
              "productOptions": [
                  {
                      "name": "Color",
                      "values": [
                          {
                              "name": "Grey"
                          },
                          {
                              "name": "Black"
                          }
                      ]
                  }
              ],
              "files": [
                  {
                      "originalSource": "https://example.com/hats/grey-hat.jpg",
                      "alt": "An elegant grey hat",
                      "filename": "grey-hat.jpg",
                      "contentType": "IMAGE"
                  },
                  {
                      "originalSource": "https://example.com/hats/black-hat.jpg",
                      "alt": "An elegant black hat",
                      "filename": "black-hat.jpg",
                      "contentType": "IMAGE"
                  }
              ],
              "variants": [
                  {
                      "optionValues": [
                          {
                              "optionName": "Color",
                              "name": "Grey"
                          }
                      ],
                      "file": {
                          "originalSource": "https://example.com/hats/grey-hat.jpg",
                          "alt": "An elegant grey hat",
                          "filename": "grey-hat.jpg",
                          "contentType": "IMAGE"
                      },
                      "price": 11.99
                  },
                  {
                      "optionValues": [
                          {
                              "optionName": "Color",
                              "name": "Black"
                          }
                      ],
                      "file": {
                          "originalSource": "https://example.com/hats/black-hat.jpg",
                          "alt": "An elegant black hat",
                          "filename": "black-hat.jpg",
                          "contentType": "IMAGE"
                      },
                      "price": 11.99
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
  'mutation createProduct($productSet: ProductSetInput!, $synchronous: Boolean!) {
    productSet(synchronous: $synchronous, input: $productSet) {
      product {
        id
        media(first: 5) {
          nodes {
            id
            alt
            mediaContentType
            status
          }
        }
        variants(first: 5) {
          nodes {
            title
            price
            media(first: 5) {
              nodes {
                id
                alt
                mediaContentType
                status
              }
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
    "synchronous": true,
    "productSet": {
      "title": "Winter hat",
      "productOptions": [
        {
          "name": "Color",
          "values": [
            {
              "name": "Grey"
            },
            {
              "name": "Black"
            }
          ]
        }
      ],
      "files": [
        {
          "originalSource": "https://example.com/hats/grey-hat.jpg",
          "alt": "An elegant grey hat",
          "filename": "grey-hat.jpg",
          "contentType": "IMAGE"
        },
        {
          "originalSource": "https://example.com/hats/black-hat.jpg",
          "alt": "An elegant black hat",
          "filename": "black-hat.jpg",
          "contentType": "IMAGE"
        }
      ],
      "variants": [
        {
          "optionValues": [
            {
              "optionName": "Color",
              "name": "Grey"
            }
          ],
          "file": {
            "originalSource": "https://example.com/hats/grey-hat.jpg",
            "alt": "An elegant grey hat",
            "filename": "grey-hat.jpg",
            "contentType": "IMAGE"
          },
          "price": 11.99
        },
        {
          "optionValues": [
            {
              "optionName": "Color",
              "name": "Black"
            }
          ],
          "file": {
            "originalSource": "https://example.com/hats/black-hat.jpg",
            "alt": "An elegant black hat",
            "filename": "black-hat.jpg",
            "contentType": "IMAGE"
          },
          "price": 11.99
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "productSet": {
      "product": {
        "id": "gid://shopify/Product/1072481957",
        "media": {
          "nodes": [
            {
              "alt": "An elegant grey hat",
              "mediaContentType": "IMAGE",
              "status": "UPLOADED"
            },
            {
              "alt": "An elegant black hat",
              "mediaContentType": "IMAGE",
              "status": "UPLOADED"
            }
          ]
        },
        "variants": {
          "nodes": [
            {
              "title": "Grey",
              "price": "11.99",
              "media": {
                "nodes": [
                  {
                    "alt": "An elegant grey hat",
                    "mediaContentType": "IMAGE",
                    "status": "UPLOADED"
                  }
                ]
              }
            },
            {
              "title": "Black",
              "price": "11.99",
              "media": {
                "nodes": [
                  {
                    "alt": "An elegant black hat",
                    "mediaContentType": "IMAGE",
                    "status": "UPLOADED"
                  }
                ]
              }
            }
          ]
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Create a product with customized inventory quantities

  #### Description

  Create a product with \[inventory quantities]\(https://shopify.dev/docs/apps/build/orders-fulfillment/inventory-management-apps/manage-quantities-states). This example returns the product with the specified inventory quantities configured for the variants.

  #### Query

  ```graphql
  mutation createProduct($productSet: ProductSetInput!, $synchronous: Boolean!) {
    productSet(synchronous: $synchronous, input: $productSet) {
      product {
        id
        variants(first: 5) {
          nodes {
            title
            price
            inventoryQuantity
            inventoryItem {
              inventoryLevels(first: 5) {
                nodes {
                  location {
                    id
                    name
                  }
                }
              }
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
    "synchronous": true,
    "productSet": {
      "title": "Winter hat",
      "productOptions": [
        {
          "name": "Color",
          "position": 1,
          "values": [
            {
              "name": "Grey"
            },
            {
              "name": "Black"
            }
          ]
        }
      ],
      "variants": [
        {
          "optionValues": [
            {
              "optionName": "Color",
              "name": "Grey"
            }
          ],
          "inventoryQuantities": [
            {
              "locationId": "gid://shopify/Location/415211365",
              "name": "available",
              "quantity": 12
            },
            {
              "locationId": "gid://shopify/Location/346779380",
              "name": "available",
              "quantity": 19
            }
          ],
          "price": 79.99
        },
        {
          "optionValues": [
            {
              "optionName": "Color",
              "name": "Black"
            }
          ],
          "inventoryQuantities": [
            {
              "locationId": "gid://shopify/Location/346779380",
              "name": "available",
              "quantity": 976
            },
            {
              "locationId": "gid://shopify/Location/415211365",
              "name": "available",
              "quantity": 844
            }
          ],
          "price": 11.99
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
  "query": "mutation createProduct($productSet: ProductSetInput!, $synchronous: Boolean!) { productSet(synchronous: $synchronous, input: $productSet) { product { id variants(first: 5) { nodes { title price inventoryQuantity inventoryItem { inventoryLevels(first: 5) { nodes { location { id name } } } } } } } userErrors { field message } } }",
   "variables": {
      "synchronous": true,
      "productSet": {
        "title": "Winter hat",
        "productOptions": [
          {
            "name": "Color",
            "position": 1,
            "values": [
              {
                "name": "Grey"
              },
              {
                "name": "Black"
              }
            ]
          }
        ],
        "variants": [
          {
            "optionValues": [
              {
                "optionName": "Color",
                "name": "Grey"
              }
            ],
            "inventoryQuantities": [
              {
                "locationId": "gid://shopify/Location/415211365",
                "name": "available",
                "quantity": 12
              },
              {
                "locationId": "gid://shopify/Location/346779380",
                "name": "available",
                "quantity": 19
              }
            ],
            "price": 79.99
          },
          {
            "optionValues": [
              {
                "optionName": "Color",
                "name": "Black"
              }
            ],
            "inventoryQuantities": [
              {
                "locationId": "gid://shopify/Location/346779380",
                "name": "available",
                "quantity": 976
              },
              {
                "locationId": "gid://shopify/Location/415211365",
                "name": "available",
                "quantity": 844
              }
            ],
            "price": 11.99
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
    mutation createProduct($productSet: ProductSetInput!, $synchronous: Boolean!) {
      productSet(synchronous: $synchronous, input: $productSet) {
        product {
          id
          variants(first: 5) {
            nodes {
              title
              price
              inventoryQuantity
              inventoryItem {
                inventoryLevels(first: 5) {
                  nodes {
                    location {
                      id
                      name
                    }
                  }
                }
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
          "synchronous": true,
          "productSet": {
              "title": "Winter hat",
              "productOptions": [
                  {
                      "name": "Color",
                      "position": 1,
                      "values": [
                          {
                              "name": "Grey"
                          },
                          {
                              "name": "Black"
                          }
                      ]
                  }
              ],
              "variants": [
                  {
                      "optionValues": [
                          {
                              "optionName": "Color",
                              "name": "Grey"
                          }
                      ],
                      "inventoryQuantities": [
                          {
                              "locationId": "gid://shopify/Location/415211365",
                              "name": "available",
                              "quantity": 12
                          },
                          {
                              "locationId": "gid://shopify/Location/346779380",
                              "name": "available",
                              "quantity": 19
                          }
                      ],
                      "price": 79.99
                  },
                  {
                      "optionValues": [
                          {
                              "optionName": "Color",
                              "name": "Black"
                          }
                      ],
                      "inventoryQuantities": [
                          {
                              "locationId": "gid://shopify/Location/346779380",
                              "name": "available",
                              "quantity": 976
                          },
                          {
                              "locationId": "gid://shopify/Location/415211365",
                              "name": "available",
                              "quantity": 844
                          }
                      ],
                      "price": 11.99
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
    mutation createProduct($productSet: ProductSetInput!, $synchronous: Boolean!) {
      productSet(synchronous: $synchronous, input: $productSet) {
        product {
          id
          variants(first: 5) {
            nodes {
              title
              price
              inventoryQuantity
              inventoryItem {
                inventoryLevels(first: 5) {
                  nodes {
                    location {
                      id
                      name
                    }
                  }
                }
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
    "synchronous": true,
    "productSet": {
      "title": "Winter hat",
      "productOptions": [
        {
          "name": "Color",
          "position": 1,
          "values": [
            {
              "name": "Grey"
            },
            {
              "name": "Black"
            }
          ]
        }
      ],
      "variants": [
        {
          "optionValues": [
            {
              "optionName": "Color",
              "name": "Grey"
            }
          ],
          "inventoryQuantities": [
            {
              "locationId": "gid://shopify/Location/415211365",
              "name": "available",
              "quantity": 12
            },
            {
              "locationId": "gid://shopify/Location/346779380",
              "name": "available",
              "quantity": 19
            }
          ],
          "price": 79.99
        },
        {
          "optionValues": [
            {
              "optionName": "Color",
              "name": "Black"
            }
          ],
          "inventoryQuantities": [
            {
              "locationId": "gid://shopify/Location/346779380",
              "name": "available",
              "quantity": 976
            },
            {
              "locationId": "gid://shopify/Location/415211365",
              "name": "available",
              "quantity": 844
            }
          ],
          "price": 11.99
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
      "query": `mutation createProduct($productSet: ProductSetInput!, $synchronous: Boolean!) {
        productSet(synchronous: $synchronous, input: $productSet) {
          product {
            id
            variants(first: 5) {
              nodes {
                title
                price
                inventoryQuantity
                inventoryItem {
                  inventoryLevels(first: 5) {
                    nodes {
                      location {
                        id
                        name
                      }
                    }
                  }
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
          "synchronous": true,
          "productSet": {
              "title": "Winter hat",
              "productOptions": [
                  {
                      "name": "Color",
                      "position": 1,
                      "values": [
                          {
                              "name": "Grey"
                          },
                          {
                              "name": "Black"
                          }
                      ]
                  }
              ],
              "variants": [
                  {
                      "optionValues": [
                          {
                              "optionName": "Color",
                              "name": "Grey"
                          }
                      ],
                      "inventoryQuantities": [
                          {
                              "locationId": "gid://shopify/Location/415211365",
                              "name": "available",
                              "quantity": 12
                          },
                          {
                              "locationId": "gid://shopify/Location/346779380",
                              "name": "available",
                              "quantity": 19
                          }
                      ],
                      "price": 79.99
                  },
                  {
                      "optionValues": [
                          {
                              "optionName": "Color",
                              "name": "Black"
                          }
                      ],
                      "inventoryQuantities": [
                          {
                              "locationId": "gid://shopify/Location/346779380",
                              "name": "available",
                              "quantity": 976
                          },
                          {
                              "locationId": "gid://shopify/Location/415211365",
                              "name": "available",
                              "quantity": 844
                          }
                      ],
                      "price": 11.99
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
  'mutation createProduct($productSet: ProductSetInput!, $synchronous: Boolean!) {
    productSet(synchronous: $synchronous, input: $productSet) {
      product {
        id
        variants(first: 5) {
          nodes {
            title
            price
            inventoryQuantity
            inventoryItem {
              inventoryLevels(first: 5) {
                nodes {
                  location {
                    id
                    name
                  }
                }
              }
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
    "synchronous": true,
    "productSet": {
      "title": "Winter hat",
      "productOptions": [
        {
          "name": "Color",
          "position": 1,
          "values": [
            {
              "name": "Grey"
            },
            {
              "name": "Black"
            }
          ]
        }
      ],
      "variants": [
        {
          "optionValues": [
            {
              "optionName": "Color",
              "name": "Grey"
            }
          ],
          "inventoryQuantities": [
            {
              "locationId": "gid://shopify/Location/415211365",
              "name": "available",
              "quantity": 12
            },
            {
              "locationId": "gid://shopify/Location/346779380",
              "name": "available",
              "quantity": 19
            }
          ],
          "price": 79.99
        },
        {
          "optionValues": [
            {
              "optionName": "Color",
              "name": "Black"
            }
          ],
          "inventoryQuantities": [
            {
              "locationId": "gid://shopify/Location/346779380",
              "name": "available",
              "quantity": 976
            },
            {
              "locationId": "gid://shopify/Location/415211365",
              "name": "available",
              "quantity": 844
            }
          ],
          "price": 11.99
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "productSet": {
      "product": {
        "id": "gid://shopify/Product/1072481937",
        "variants": {
          "nodes": [
            {
              "title": "Grey",
              "price": "79.99",
              "inventoryQuantity": 31,
              "inventoryItem": {
                "inventoryLevels": {
                  "nodes": [
                    {
                      "location": {
                        "id": "gid://shopify/Location/346779380",
                        "name": "Ottawa Store"
                      }
                    },
                    {
                      "location": {
                        "id": "gid://shopify/Location/415211365",
                        "name": "US Store"
                      }
                    }
                  ]
                }
              }
            },
            {
              "title": "Black",
              "price": "11.99",
              "inventoryQuantity": 1820,
              "inventoryItem": {
                "inventoryLevels": {
                  "nodes": [
                    {
                      "location": {
                        "id": "gid://shopify/Location/346779380",
                        "name": "Ottawa Store"
                      }
                    },
                    {
                      "location": {
                        "id": "gid://shopify/Location/415211365",
                        "name": "US Store"
                      }
                    }
                  ]
                }
              }
            }
          ]
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Create a product with two options and four variants

  #### Description

  Create a product with \[multiple options]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductOption) and all possible \[variant]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant) combinations. This example returns a product with two options and four variants, representing all \[option value]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductOptionValue) combinations.

  #### Query

  ```graphql
  mutation createProductWithTwoOptionsAndVariants($productSet: ProductSetInput!, $synchronous: Boolean!) {
    productSet(synchronous: $synchronous, input: $productSet) {
      product {
        id
        title
        options(first: 5) {
          name
          position
          optionValues {
            name
          }
        }
        variants(first: 5) {
          nodes {
            price
            selectedOptions {
              name
              optionValue {
                id
                name
              }
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
    "synchronous": true,
    "productSet": {
      "title": "A humble tie",
      "productOptions": [
        {
          "name": "Pattern",
          "position": 1,
          "values": [
            {
              "name": "Plain"
            },
            {
              "name": "Stripes"
            }
          ]
        },
        {
          "name": "Width",
          "position": 2,
          "values": [
            {
              "name": "Slim"
            },
            {
              "name": "Classic"
            }
          ]
        }
      ],
      "variants": [
        {
          "optionValues": [
            {
              "optionName": "Pattern",
              "name": "Plain"
            },
            {
              "optionName": "Width",
              "name": "Slim"
            }
          ],
          "price": 15
        },
        {
          "optionValues": [
            {
              "optionName": "Pattern",
              "name": "Plain"
            },
            {
              "optionName": "Width",
              "name": "Classic"
            }
          ],
          "price": 15
        },
        {
          "optionValues": [
            {
              "optionName": "Pattern",
              "name": "Stripes"
            },
            {
              "optionName": "Width",
              "name": "Slim"
            }
          ],
          "price": 15
        },
        {
          "optionValues": [
            {
              "optionName": "Pattern",
              "name": "Stripes"
            },
            {
              "optionName": "Width",
              "name": "Classic"
            }
          ],
          "price": 15
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
  "query": "mutation createProductWithTwoOptionsAndVariants($productSet: ProductSetInput!, $synchronous: Boolean!) { productSet(synchronous: $synchronous, input: $productSet) { product { id title options(first: 5) { name position optionValues { name } } variants(first: 5) { nodes { price selectedOptions { name optionValue { id name } } } } } userErrors { field message } } }",
   "variables": {
      "synchronous": true,
      "productSet": {
        "title": "A humble tie",
        "productOptions": [
          {
            "name": "Pattern",
            "position": 1,
            "values": [
              {
                "name": "Plain"
              },
              {
                "name": "Stripes"
              }
            ]
          },
          {
            "name": "Width",
            "position": 2,
            "values": [
              {
                "name": "Slim"
              },
              {
                "name": "Classic"
              }
            ]
          }
        ],
        "variants": [
          {
            "optionValues": [
              {
                "optionName": "Pattern",
                "name": "Plain"
              },
              {
                "optionName": "Width",
                "name": "Slim"
              }
            ],
            "price": 15
          },
          {
            "optionValues": [
              {
                "optionName": "Pattern",
                "name": "Plain"
              },
              {
                "optionName": "Width",
                "name": "Classic"
              }
            ],
            "price": 15
          },
          {
            "optionValues": [
              {
                "optionName": "Pattern",
                "name": "Stripes"
              },
              {
                "optionName": "Width",
                "name": "Slim"
              }
            ],
            "price": 15
          },
          {
            "optionValues": [
              {
                "optionName": "Pattern",
                "name": "Stripes"
              },
              {
                "optionName": "Width",
                "name": "Classic"
              }
            ],
            "price": 15
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
    mutation createProductWithTwoOptionsAndVariants($productSet: ProductSetInput!, $synchronous: Boolean!) {
      productSet(synchronous: $synchronous, input: $productSet) {
        product {
          id
          title
          options(first: 5) {
            name
            position
            optionValues {
              name
            }
          }
          variants(first: 5) {
            nodes {
              price
              selectedOptions {
                name
                optionValue {
                  id
                  name
                }
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
          "synchronous": true,
          "productSet": {
              "title": "A humble tie",
              "productOptions": [
                  {
                      "name": "Pattern",
                      "position": 1,
                      "values": [
                          {
                              "name": "Plain"
                          },
                          {
                              "name": "Stripes"
                          }
                      ]
                  },
                  {
                      "name": "Width",
                      "position": 2,
                      "values": [
                          {
                              "name": "Slim"
                          },
                          {
                              "name": "Classic"
                          }
                      ]
                  }
              ],
              "variants": [
                  {
                      "optionValues": [
                          {
                              "optionName": "Pattern",
                              "name": "Plain"
                          },
                          {
                              "optionName": "Width",
                              "name": "Slim"
                          }
                      ],
                      "price": 15
                  },
                  {
                      "optionValues": [
                          {
                              "optionName": "Pattern",
                              "name": "Plain"
                          },
                          {
                              "optionName": "Width",
                              "name": "Classic"
                          }
                      ],
                      "price": 15
                  },
                  {
                      "optionValues": [
                          {
                              "optionName": "Pattern",
                              "name": "Stripes"
                          },
                          {
                              "optionName": "Width",
                              "name": "Slim"
                          }
                      ],
                      "price": 15
                  },
                  {
                      "optionValues": [
                          {
                              "optionName": "Pattern",
                              "name": "Stripes"
                          },
                          {
                              "optionName": "Width",
                              "name": "Classic"
                          }
                      ],
                      "price": 15
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
    mutation createProductWithTwoOptionsAndVariants($productSet: ProductSetInput!, $synchronous: Boolean!) {
      productSet(synchronous: $synchronous, input: $productSet) {
        product {
          id
          title
          options(first: 5) {
            name
            position
            optionValues {
              name
            }
          }
          variants(first: 5) {
            nodes {
              price
              selectedOptions {
                name
                optionValue {
                  id
                  name
                }
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
    "synchronous": true,
    "productSet": {
      "title": "A humble tie",
      "productOptions": [
        {
          "name": "Pattern",
          "position": 1,
          "values": [
            {
              "name": "Plain"
            },
            {
              "name": "Stripes"
            }
          ]
        },
        {
          "name": "Width",
          "position": 2,
          "values": [
            {
              "name": "Slim"
            },
            {
              "name": "Classic"
            }
          ]
        }
      ],
      "variants": [
        {
          "optionValues": [
            {
              "optionName": "Pattern",
              "name": "Plain"
            },
            {
              "optionName": "Width",
              "name": "Slim"
            }
          ],
          "price": 15
        },
        {
          "optionValues": [
            {
              "optionName": "Pattern",
              "name": "Plain"
            },
            {
              "optionName": "Width",
              "name": "Classic"
            }
          ],
          "price": 15
        },
        {
          "optionValues": [
            {
              "optionName": "Pattern",
              "name": "Stripes"
            },
            {
              "optionName": "Width",
              "name": "Slim"
            }
          ],
          "price": 15
        },
        {
          "optionValues": [
            {
              "optionName": "Pattern",
              "name": "Stripes"
            },
            {
              "optionName": "Width",
              "name": "Classic"
            }
          ],
          "price": 15
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
      "query": `mutation createProductWithTwoOptionsAndVariants($productSet: ProductSetInput!, $synchronous: Boolean!) {
        productSet(synchronous: $synchronous, input: $productSet) {
          product {
            id
            title
            options(first: 5) {
              name
              position
              optionValues {
                name
              }
            }
            variants(first: 5) {
              nodes {
                price
                selectedOptions {
                  name
                  optionValue {
                    id
                    name
                  }
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
          "synchronous": true,
          "productSet": {
              "title": "A humble tie",
              "productOptions": [
                  {
                      "name": "Pattern",
                      "position": 1,
                      "values": [
                          {
                              "name": "Plain"
                          },
                          {
                              "name": "Stripes"
                          }
                      ]
                  },
                  {
                      "name": "Width",
                      "position": 2,
                      "values": [
                          {
                              "name": "Slim"
                          },
                          {
                              "name": "Classic"
                          }
                      ]
                  }
              ],
              "variants": [
                  {
                      "optionValues": [
                          {
                              "optionName": "Pattern",
                              "name": "Plain"
                          },
                          {
                              "optionName": "Width",
                              "name": "Slim"
                          }
                      ],
                      "price": 15
                  },
                  {
                      "optionValues": [
                          {
                              "optionName": "Pattern",
                              "name": "Plain"
                          },
                          {
                              "optionName": "Width",
                              "name": "Classic"
                          }
                      ],
                      "price": 15
                  },
                  {
                      "optionValues": [
                          {
                              "optionName": "Pattern",
                              "name": "Stripes"
                          },
                          {
                              "optionName": "Width",
                              "name": "Slim"
                          }
                      ],
                      "price": 15
                  },
                  {
                      "optionValues": [
                          {
                              "optionName": "Pattern",
                              "name": "Stripes"
                          },
                          {
                              "optionName": "Width",
                              "name": "Classic"
                          }
                      ],
                      "price": 15
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
  'mutation createProductWithTwoOptionsAndVariants($productSet: ProductSetInput!, $synchronous: Boolean!) {
    productSet(synchronous: $synchronous, input: $productSet) {
      product {
        id
        title
        options(first: 5) {
          name
          position
          optionValues {
            name
          }
        }
        variants(first: 5) {
          nodes {
            price
            selectedOptions {
              name
              optionValue {
                id
                name
              }
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
    "synchronous": true,
    "productSet": {
      "title": "A humble tie",
      "productOptions": [
        {
          "name": "Pattern",
          "position": 1,
          "values": [
            {
              "name": "Plain"
            },
            {
              "name": "Stripes"
            }
          ]
        },
        {
          "name": "Width",
          "position": 2,
          "values": [
            {
              "name": "Slim"
            },
            {
              "name": "Classic"
            }
          ]
        }
      ],
      "variants": [
        {
          "optionValues": [
            {
              "optionName": "Pattern",
              "name": "Plain"
            },
            {
              "optionName": "Width",
              "name": "Slim"
            }
          ],
          "price": 15
        },
        {
          "optionValues": [
            {
              "optionName": "Pattern",
              "name": "Plain"
            },
            {
              "optionName": "Width",
              "name": "Classic"
            }
          ],
          "price": 15
        },
        {
          "optionValues": [
            {
              "optionName": "Pattern",
              "name": "Stripes"
            },
            {
              "optionName": "Width",
              "name": "Slim"
            }
          ],
          "price": 15
        },
        {
          "optionValues": [
            {
              "optionName": "Pattern",
              "name": "Stripes"
            },
            {
              "optionName": "Width",
              "name": "Classic"
            }
          ],
          "price": 15
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "productSet": {
      "product": {
        "id": "gid://shopify/Product/1072481953",
        "title": "A humble tie",
        "options": [
          {
            "name": "Pattern",
            "position": 1,
            "optionValues": [
              {
                "name": "Plain"
              },
              {
                "name": "Stripes"
              }
            ]
          },
          {
            "name": "Width",
            "position": 2,
            "optionValues": [
              {
                "name": "Slim"
              },
              {
                "name": "Classic"
              }
            ]
          }
        ],
        "variants": {
          "nodes": [
            {
              "price": "15.00",
              "selectedOptions": [
                {
                  "name": "Pattern",
                  "optionValue": {
                    "id": "gid://shopify/ProductOptionValue/1054677147",
                    "name": "Plain"
                  }
                },
                {
                  "name": "Width",
                  "optionValue": {
                    "id": "gid://shopify/ProductOptionValue/1054677149",
                    "name": "Slim"
                  }
                }
              ]
            },
            {
              "price": "15.00",
              "selectedOptions": [
                {
                  "name": "Pattern",
                  "optionValue": {
                    "id": "gid://shopify/ProductOptionValue/1054677147",
                    "name": "Plain"
                  }
                },
                {
                  "name": "Width",
                  "optionValue": {
                    "id": "gid://shopify/ProductOptionValue/1054677150",
                    "name": "Classic"
                  }
                }
              ]
            },
            {
              "price": "15.00",
              "selectedOptions": [
                {
                  "name": "Pattern",
                  "optionValue": {
                    "id": "gid://shopify/ProductOptionValue/1054677148",
                    "name": "Stripes"
                  }
                },
                {
                  "name": "Width",
                  "optionValue": {
                    "id": "gid://shopify/ProductOptionValue/1054677149",
                    "name": "Slim"
                  }
                }
              ]
            },
            {
              "price": "15.00",
              "selectedOptions": [
                {
                  "name": "Pattern",
                  "optionValue": {
                    "id": "gid://shopify/ProductOptionValue/1054677148",
                    "name": "Stripes"
                  }
                },
                {
                  "name": "Width",
                  "optionValue": {
                    "id": "gid://shopify/ProductOptionValue/1054677150",
                    "name": "Classic"
                  }
                }
              ]
            }
          ]
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Remove custom options and variants from a product

  #### Description

  Remove existing \[options]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductOption) and \[variants]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant) from a product by updating the product's configuration. This example returns the updated product, with the specified options and variants removed.

  #### Query

  ```graphql
  mutation updateProductToLeaveDefaultVariant($productSet: ProductSetInput!, $synchronous: Boolean!, $identifier: ProductSetIdentifiers) {
    productSet(synchronous: $synchronous, input: $productSet, identifier: $identifier) {
      product {
        id
        hasOnlyDefaultVariant
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
    "synchronous": true,
    "identifier": {
      "id": "gid://shopify/Product/20995642"
    },
    "productSet": {
      "productOptions": [],
      "variants": []
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
  "query": "mutation updateProductToLeaveDefaultVariant($productSet: ProductSetInput!, $synchronous: Boolean!, $identifier: ProductSetIdentifiers) { productSet(synchronous: $synchronous, input: $productSet, identifier: $identifier) { product { id hasOnlyDefaultVariant } userErrors { field message } } }",
   "variables": {
      "synchronous": true,
      "identifier": {
        "id": "gid://shopify/Product/20995642"
      },
      "productSet": {
        "productOptions": [],
        "variants": []
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
    mutation updateProductToLeaveDefaultVariant($productSet: ProductSetInput!, $synchronous: Boolean!, $identifier: ProductSetIdentifiers) {
      productSet(synchronous: $synchronous, input: $productSet, identifier: $identifier) {
        product {
          id
          hasOnlyDefaultVariant
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "synchronous": true,
          "identifier": {
              "id": "gid://shopify/Product/20995642"
          },
          "productSet": {
              "productOptions": [],
              "variants": []
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
    mutation updateProductToLeaveDefaultVariant($productSet: ProductSetInput!, $synchronous: Boolean!, $identifier: ProductSetIdentifiers) {
      productSet(synchronous: $synchronous, input: $productSet, identifier: $identifier) {
        product {
          id
          hasOnlyDefaultVariant
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "synchronous": true,
    "identifier": {
      "id": "gid://shopify/Product/20995642"
    },
    "productSet": {
      "productOptions": [],
      "variants": []
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation updateProductToLeaveDefaultVariant($productSet: ProductSetInput!, $synchronous: Boolean!, $identifier: ProductSetIdentifiers) {
        productSet(synchronous: $synchronous, input: $productSet, identifier: $identifier) {
          product {
            id
            hasOnlyDefaultVariant
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "synchronous": true,
          "identifier": {
              "id": "gid://shopify/Product/20995642"
          },
          "productSet": {
              "productOptions": [],
              "variants": []
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation updateProductToLeaveDefaultVariant($productSet: ProductSetInput!, $synchronous: Boolean!, $identifier: ProductSetIdentifiers) {
    productSet(synchronous: $synchronous, input: $productSet, identifier: $identifier) {
      product {
        id
        hasOnlyDefaultVariant
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "synchronous": true,
    "identifier": {
      "id": "gid://shopify/Product/20995642"
    },
    "productSet": {
      "productOptions": [],
      "variants": []
    }
  }'
  ```

  #### Response

  ```json
  {
    "productSet": {
      "product": {
        "id": "gid://shopify/Product/20995642",
        "hasOnlyDefaultVariant": true
      },
      "userErrors": []
    }
  }
  ```

* ### Update the price of variants by IDs

  #### Description

  Update the price of variants using their IDs. This example returns the updated variant pricing, while maintaining the existing options and variants.

  #### Query

  ```graphql
  mutation updateProductVariantPricing($input: ProductSetInput!, $synchronous: Boolean!, $identifier: ProductSetIdentifiers) {
    productSet(synchronous: $synchronous, input: $input, identifier: $identifier) {
      product {
        id
        title
        description
        handle
        options(first: 5) {
          name
          position
          optionValues {
            name
          }
        }
        variants(first: 5) {
          nodes {
            price
            compareAtPrice
            selectedOptions {
              name
              optionValue {
                id
                name
              }
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
    "synchronous": true,
    "identifier": {
      "id": "gid://shopify/Product/1072481936"
    },
    "input": {
      "title": "Bike frame",
      "descriptionHtml": "Blending durability with aerodynamics",
      "handle": "bike-frame",
      "productType": "parts",
      "tags": [
        "cycling",
        "bike",
        "parts"
      ],
      "vendor": "Your cycling company",
      "status": "ACTIVE",
      "productOptions": [
        {
          "id": "gid://shopify/ProductOption/1064578002",
          "values": [
            {
              "id": "gid://shopify/ProductOptionValue/1054676956"
            },
            {
              "id": "gid://shopify/ProductOptionValue/1054676957"
            },
            {
              "id": "gid://shopify/ProductOptionValue/1054676958"
            }
          ]
        },
        {
          "id": "gid://shopify/ProductOption/1064578003",
          "values": [
            {
              "id": "gid://shopify/ProductOptionValue/1054676960"
            },
            {
              "id": "gid://shopify/ProductOptionValue/1054676959"
            },
            {
              "id": "gid://shopify/ProductOptionValue/1054676961"
            }
          ]
        }
      ],
      "variants": [
        {
          "id": "gid://shopify/ProductVariant/1070328469",
          "position": 1,
          "price": 94.99,
          "compareAtPrice": 99.99,
          "optionValues": [
            {
              "id": "gid://shopify/ProductOptionValue/1054676956",
              "optionId": "gid://shopify/ProductOption/1064578002"
            },
            {
              "id": "gid://shopify/ProductOptionValue/1054676959",
              "optionId": "gid://shopify/ProductOption/1064578003"
            }
          ]
        },
        {
          "id": "gid://shopify/ProductVariant/1070328470",
          "position": 2,
          "price": 259.99,
          "compareAtPrice": 299.99,
          "optionValues": [
            {
              "id": "gid://shopify/ProductOptionValue/1054676957",
              "optionId": "gid://shopify/ProductOption/1064578002"
            },
            {
              "id": "gid://shopify/ProductOptionValue/1054676960",
              "optionId": "gid://shopify/ProductOption/1064578003"
            }
          ]
        },
        {
          "id": "gid://shopify/ProductVariant/1070328471",
          "position": 3,
          "price": 169.99,
          "compareAtPrice": 199.99,
          "optionValues": [
            {
              "id": "gid://shopify/ProductOptionValue/1054676958",
              "optionId": "gid://shopify/ProductOption/1064578002"
            },
            {
              "id": "gid://shopify/ProductOptionValue/1054676961",
              "optionId": "gid://shopify/ProductOption/1064578003"
            }
          ]
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
  "query": "mutation updateProductVariantPricing($input: ProductSetInput!, $synchronous: Boolean!, $identifier: ProductSetIdentifiers) { productSet(synchronous: $synchronous, input: $input, identifier: $identifier) { product { id title description handle options(first: 5) { name position optionValues { name } } variants(first: 5) { nodes { price compareAtPrice selectedOptions { name optionValue { id name } } } } } userErrors { field message } } }",
   "variables": {
      "synchronous": true,
      "identifier": {
        "id": "gid://shopify/Product/1072481936"
      },
      "input": {
        "title": "Bike frame",
        "descriptionHtml": "Blending durability with aerodynamics",
        "handle": "bike-frame",
        "productType": "parts",
        "tags": [
          "cycling",
          "bike",
          "parts"
        ],
        "vendor": "Your cycling company",
        "status": "ACTIVE",
        "productOptions": [
          {
            "id": "gid://shopify/ProductOption/1064578002",
            "values": [
              {
                "id": "gid://shopify/ProductOptionValue/1054676956"
              },
              {
                "id": "gid://shopify/ProductOptionValue/1054676957"
              },
              {
                "id": "gid://shopify/ProductOptionValue/1054676958"
              }
            ]
          },
          {
            "id": "gid://shopify/ProductOption/1064578003",
            "values": [
              {
                "id": "gid://shopify/ProductOptionValue/1054676960"
              },
              {
                "id": "gid://shopify/ProductOptionValue/1054676959"
              },
              {
                "id": "gid://shopify/ProductOptionValue/1054676961"
              }
            ]
          }
        ],
        "variants": [
          {
            "id": "gid://shopify/ProductVariant/1070328469",
            "position": 1,
            "price": 94.99,
            "compareAtPrice": 99.99,
            "optionValues": [
              {
                "id": "gid://shopify/ProductOptionValue/1054676956",
                "optionId": "gid://shopify/ProductOption/1064578002"
              },
              {
                "id": "gid://shopify/ProductOptionValue/1054676959",
                "optionId": "gid://shopify/ProductOption/1064578003"
              }
            ]
          },
          {
            "id": "gid://shopify/ProductVariant/1070328470",
            "position": 2,
            "price": 259.99,
            "compareAtPrice": 299.99,
            "optionValues": [
              {
                "id": "gid://shopify/ProductOptionValue/1054676957",
                "optionId": "gid://shopify/ProductOption/1064578002"
              },
              {
                "id": "gid://shopify/ProductOptionValue/1054676960",
                "optionId": "gid://shopify/ProductOption/1064578003"
              }
            ]
          },
          {
            "id": "gid://shopify/ProductVariant/1070328471",
            "position": 3,
            "price": 169.99,
            "compareAtPrice": 199.99,
            "optionValues": [
              {
                "id": "gid://shopify/ProductOptionValue/1054676958",
                "optionId": "gid://shopify/ProductOption/1064578002"
              },
              {
                "id": "gid://shopify/ProductOptionValue/1054676961",
                "optionId": "gid://shopify/ProductOption/1064578003"
              }
            ]
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
    mutation updateProductVariantPricing($input: ProductSetInput!, $synchronous: Boolean!, $identifier: ProductSetIdentifiers) {
      productSet(synchronous: $synchronous, input: $input, identifier: $identifier) {
        product {
          id
          title
          description
          handle
          options(first: 5) {
            name
            position
            optionValues {
              name
            }
          }
          variants(first: 5) {
            nodes {
              price
              compareAtPrice
              selectedOptions {
                name
                optionValue {
                  id
                  name
                }
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
          "synchronous": true,
          "identifier": {
              "id": "gid://shopify/Product/1072481936"
          },
          "input": {
              "title": "Bike frame",
              "descriptionHtml": "Blending durability with aerodynamics",
              "handle": "bike-frame",
              "productType": "parts",
              "tags": [
                  "cycling",
                  "bike",
                  "parts"
              ],
              "vendor": "Your cycling company",
              "status": "ACTIVE",
              "productOptions": [
                  {
                      "id": "gid://shopify/ProductOption/1064578002",
                      "values": [
                          {
                              "id": "gid://shopify/ProductOptionValue/1054676956"
                          },
                          {
                              "id": "gid://shopify/ProductOptionValue/1054676957"
                          },
                          {
                              "id": "gid://shopify/ProductOptionValue/1054676958"
                          }
                      ]
                  },
                  {
                      "id": "gid://shopify/ProductOption/1064578003",
                      "values": [
                          {
                              "id": "gid://shopify/ProductOptionValue/1054676960"
                          },
                          {
                              "id": "gid://shopify/ProductOptionValue/1054676959"
                          },
                          {
                              "id": "gid://shopify/ProductOptionValue/1054676961"
                          }
                      ]
                  }
              ],
              "variants": [
                  {
                      "id": "gid://shopify/ProductVariant/1070328469",
                      "position": 1,
                      "price": 94.99,
                      "compareAtPrice": 99.99,
                      "optionValues": [
                          {
                              "id": "gid://shopify/ProductOptionValue/1054676956",
                              "optionId": "gid://shopify/ProductOption/1064578002"
                          },
                          {
                              "id": "gid://shopify/ProductOptionValue/1054676959",
                              "optionId": "gid://shopify/ProductOption/1064578003"
                          }
                      ]
                  },
                  {
                      "id": "gid://shopify/ProductVariant/1070328470",
                      "position": 2,
                      "price": 259.99,
                      "compareAtPrice": 299.99,
                      "optionValues": [
                          {
                              "id": "gid://shopify/ProductOptionValue/1054676957",
                              "optionId": "gid://shopify/ProductOption/1064578002"
                          },
                          {
                              "id": "gid://shopify/ProductOptionValue/1054676960",
                              "optionId": "gid://shopify/ProductOption/1064578003"
                          }
                      ]
                  },
                  {
                      "id": "gid://shopify/ProductVariant/1070328471",
                      "position": 3,
                      "price": 169.99,
                      "compareAtPrice": 199.99,
                      "optionValues": [
                          {
                              "id": "gid://shopify/ProductOptionValue/1054676958",
                              "optionId": "gid://shopify/ProductOption/1064578002"
                          },
                          {
                              "id": "gid://shopify/ProductOptionValue/1054676961",
                              "optionId": "gid://shopify/ProductOption/1064578003"
                          }
                      ]
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
    mutation updateProductVariantPricing($input: ProductSetInput!, $synchronous: Boolean!, $identifier: ProductSetIdentifiers) {
      productSet(synchronous: $synchronous, input: $input, identifier: $identifier) {
        product {
          id
          title
          description
          handle
          options(first: 5) {
            name
            position
            optionValues {
              name
            }
          }
          variants(first: 5) {
            nodes {
              price
              compareAtPrice
              selectedOptions {
                name
                optionValue {
                  id
                  name
                }
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
    "synchronous": true,
    "identifier": {
      "id": "gid://shopify/Product/1072481936"
    },
    "input": {
      "title": "Bike frame",
      "descriptionHtml": "Blending durability with aerodynamics",
      "handle": "bike-frame",
      "productType": "parts",
      "tags": [
        "cycling",
        "bike",
        "parts"
      ],
      "vendor": "Your cycling company",
      "status": "ACTIVE",
      "productOptions": [
        {
          "id": "gid://shopify/ProductOption/1064578002",
          "values": [
            {
              "id": "gid://shopify/ProductOptionValue/1054676956"
            },
            {
              "id": "gid://shopify/ProductOptionValue/1054676957"
            },
            {
              "id": "gid://shopify/ProductOptionValue/1054676958"
            }
          ]
        },
        {
          "id": "gid://shopify/ProductOption/1064578003",
          "values": [
            {
              "id": "gid://shopify/ProductOptionValue/1054676960"
            },
            {
              "id": "gid://shopify/ProductOptionValue/1054676959"
            },
            {
              "id": "gid://shopify/ProductOptionValue/1054676961"
            }
          ]
        }
      ],
      "variants": [
        {
          "id": "gid://shopify/ProductVariant/1070328469",
          "position": 1,
          "price": 94.99,
          "compareAtPrice": 99.99,
          "optionValues": [
            {
              "id": "gid://shopify/ProductOptionValue/1054676956",
              "optionId": "gid://shopify/ProductOption/1064578002"
            },
            {
              "id": "gid://shopify/ProductOptionValue/1054676959",
              "optionId": "gid://shopify/ProductOption/1064578003"
            }
          ]
        },
        {
          "id": "gid://shopify/ProductVariant/1070328470",
          "position": 2,
          "price": 259.99,
          "compareAtPrice": 299.99,
          "optionValues": [
            {
              "id": "gid://shopify/ProductOptionValue/1054676957",
              "optionId": "gid://shopify/ProductOption/1064578002"
            },
            {
              "id": "gid://shopify/ProductOptionValue/1054676960",
              "optionId": "gid://shopify/ProductOption/1064578003"
            }
          ]
        },
        {
          "id": "gid://shopify/ProductVariant/1070328471",
          "position": 3,
          "price": 169.99,
          "compareAtPrice": 199.99,
          "optionValues": [
            {
              "id": "gid://shopify/ProductOptionValue/1054676958",
              "optionId": "gid://shopify/ProductOption/1064578002"
            },
            {
              "id": "gid://shopify/ProductOptionValue/1054676961",
              "optionId": "gid://shopify/ProductOption/1064578003"
            }
          ]
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
      "query": `mutation updateProductVariantPricing($input: ProductSetInput!, $synchronous: Boolean!, $identifier: ProductSetIdentifiers) {
        productSet(synchronous: $synchronous, input: $input, identifier: $identifier) {
          product {
            id
            title
            description
            handle
            options(first: 5) {
              name
              position
              optionValues {
                name
              }
            }
            variants(first: 5) {
              nodes {
                price
                compareAtPrice
                selectedOptions {
                  name
                  optionValue {
                    id
                    name
                  }
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
          "synchronous": true,
          "identifier": {
              "id": "gid://shopify/Product/1072481936"
          },
          "input": {
              "title": "Bike frame",
              "descriptionHtml": "Blending durability with aerodynamics",
              "handle": "bike-frame",
              "productType": "parts",
              "tags": [
                  "cycling",
                  "bike",
                  "parts"
              ],
              "vendor": "Your cycling company",
              "status": "ACTIVE",
              "productOptions": [
                  {
                      "id": "gid://shopify/ProductOption/1064578002",
                      "values": [
                          {
                              "id": "gid://shopify/ProductOptionValue/1054676956"
                          },
                          {
                              "id": "gid://shopify/ProductOptionValue/1054676957"
                          },
                          {
                              "id": "gid://shopify/ProductOptionValue/1054676958"
                          }
                      ]
                  },
                  {
                      "id": "gid://shopify/ProductOption/1064578003",
                      "values": [
                          {
                              "id": "gid://shopify/ProductOptionValue/1054676960"
                          },
                          {
                              "id": "gid://shopify/ProductOptionValue/1054676959"
                          },
                          {
                              "id": "gid://shopify/ProductOptionValue/1054676961"
                          }
                      ]
                  }
              ],
              "variants": [
                  {
                      "id": "gid://shopify/ProductVariant/1070328469",
                      "position": 1,
                      "price": 94.99,
                      "compareAtPrice": 99.99,
                      "optionValues": [
                          {
                              "id": "gid://shopify/ProductOptionValue/1054676956",
                              "optionId": "gid://shopify/ProductOption/1064578002"
                          },
                          {
                              "id": "gid://shopify/ProductOptionValue/1054676959",
                              "optionId": "gid://shopify/ProductOption/1064578003"
                          }
                      ]
                  },
                  {
                      "id": "gid://shopify/ProductVariant/1070328470",
                      "position": 2,
                      "price": 259.99,
                      "compareAtPrice": 299.99,
                      "optionValues": [
                          {
                              "id": "gid://shopify/ProductOptionValue/1054676957",
                              "optionId": "gid://shopify/ProductOption/1064578002"
                          },
                          {
                              "id": "gid://shopify/ProductOptionValue/1054676960",
                              "optionId": "gid://shopify/ProductOption/1064578003"
                          }
                      ]
                  },
                  {
                      "id": "gid://shopify/ProductVariant/1070328471",
                      "position": 3,
                      "price": 169.99,
                      "compareAtPrice": 199.99,
                      "optionValues": [
                          {
                              "id": "gid://shopify/ProductOptionValue/1054676958",
                              "optionId": "gid://shopify/ProductOption/1064578002"
                          },
                          {
                              "id": "gid://shopify/ProductOptionValue/1054676961",
                              "optionId": "gid://shopify/ProductOption/1064578003"
                          }
                      ]
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
  'mutation updateProductVariantPricing($input: ProductSetInput!, $synchronous: Boolean!, $identifier: ProductSetIdentifiers) {
    productSet(synchronous: $synchronous, input: $input, identifier: $identifier) {
      product {
        id
        title
        description
        handle
        options(first: 5) {
          name
          position
          optionValues {
            name
          }
        }
        variants(first: 5) {
          nodes {
            price
            compareAtPrice
            selectedOptions {
              name
              optionValue {
                id
                name
              }
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
    "synchronous": true,
    "identifier": {
      "id": "gid://shopify/Product/1072481936"
    },
    "input": {
      "title": "Bike frame",
      "descriptionHtml": "Blending durability with aerodynamics",
      "handle": "bike-frame",
      "productType": "parts",
      "tags": [
        "cycling",
        "bike",
        "parts"
      ],
      "vendor": "Your cycling company",
      "status": "ACTIVE",
      "productOptions": [
        {
          "id": "gid://shopify/ProductOption/1064578002",
          "values": [
            {
              "id": "gid://shopify/ProductOptionValue/1054676956"
            },
            {
              "id": "gid://shopify/ProductOptionValue/1054676957"
            },
            {
              "id": "gid://shopify/ProductOptionValue/1054676958"
            }
          ]
        },
        {
          "id": "gid://shopify/ProductOption/1064578003",
          "values": [
            {
              "id": "gid://shopify/ProductOptionValue/1054676960"
            },
            {
              "id": "gid://shopify/ProductOptionValue/1054676959"
            },
            {
              "id": "gid://shopify/ProductOptionValue/1054676961"
            }
          ]
        }
      ],
      "variants": [
        {
          "id": "gid://shopify/ProductVariant/1070328469",
          "position": 1,
          "price": 94.99,
          "compareAtPrice": 99.99,
          "optionValues": [
            {
              "id": "gid://shopify/ProductOptionValue/1054676956",
              "optionId": "gid://shopify/ProductOption/1064578002"
            },
            {
              "id": "gid://shopify/ProductOptionValue/1054676959",
              "optionId": "gid://shopify/ProductOption/1064578003"
            }
          ]
        },
        {
          "id": "gid://shopify/ProductVariant/1070328470",
          "position": 2,
          "price": 259.99,
          "compareAtPrice": 299.99,
          "optionValues": [
            {
              "id": "gid://shopify/ProductOptionValue/1054676957",
              "optionId": "gid://shopify/ProductOption/1064578002"
            },
            {
              "id": "gid://shopify/ProductOptionValue/1054676960",
              "optionId": "gid://shopify/ProductOption/1064578003"
            }
          ]
        },
        {
          "id": "gid://shopify/ProductVariant/1070328471",
          "position": 3,
          "price": 169.99,
          "compareAtPrice": 199.99,
          "optionValues": [
            {
              "id": "gid://shopify/ProductOptionValue/1054676958",
              "optionId": "gid://shopify/ProductOption/1064578002"
            },
            {
              "id": "gid://shopify/ProductOptionValue/1054676961",
              "optionId": "gid://shopify/ProductOption/1064578003"
            }
          ]
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "productSet": {
      "product": {
        "id": "gid://shopify/Product/1072481936",
        "title": "Bike frame",
        "description": "Blending durability with aerodynamics",
        "handle": "bike-frame",
        "options": [
          {
            "name": "Material",
            "position": 1,
            "optionValues": [
              {
                "name": "Aluminium"
              },
              {
                "name": "Carbon"
              },
              {
                "name": "Steel"
              }
            ]
          },
          {
            "name": "Color",
            "position": 2,
            "optionValues": [
              {
                "name": "Grey"
              },
              {
                "name": "Black"
              },
              {
                "name": "Silver"
              }
            ]
          }
        ],
        "variants": {
          "nodes": [
            {
              "price": "94.99",
              "compareAtPrice": "99.99",
              "selectedOptions": [
                {
                  "name": "Material",
                  "optionValue": {
                    "id": "gid://shopify/ProductOptionValue/1054676956",
                    "name": "Aluminium"
                  }
                },
                {
                  "name": "Color",
                  "optionValue": {
                    "id": "gid://shopify/ProductOptionValue/1054676959",
                    "name": "Grey"
                  }
                }
              ]
            },
            {
              "price": "259.99",
              "compareAtPrice": "299.99",
              "selectedOptions": [
                {
                  "name": "Material",
                  "optionValue": {
                    "id": "gid://shopify/ProductOptionValue/1054676957",
                    "name": "Carbon"
                  }
                },
                {
                  "name": "Color",
                  "optionValue": {
                    "id": "gid://shopify/ProductOptionValue/1054676960",
                    "name": "Black"
                  }
                }
              ]
            },
            {
              "price": "169.99",
              "compareAtPrice": "199.99",
              "selectedOptions": [
                {
                  "name": "Material",
                  "optionValue": {
                    "id": "gid://shopify/ProductOptionValue/1054676958",
                    "name": "Steel"
                  }
                },
                {
                  "name": "Color",
                  "optionValue": {
                    "id": "gid://shopify/ProductOptionValue/1054676961",
                    "name": "Silver"
                  }
                }
              ]
            }
          ]
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Upsert a product by its custom ID

  #### Description

  Upsert (update or insert) a product using its \[custom ID]\(https://shopify.dev/docs/api/admin-graphql/latest/input-objects/UniqueMetafieldValueInput) as the identifier. Custom IDs are unique metafield values that can be used to identify products across systems. This example returns the newly created product or the updated existing product based on the custom ID match.

  #### Query

  ```graphql
  mutation UpsertProductByCustomId($input: ProductSetInput!, $identifier: ProductSetIdentifiers) {
    productSet(input: $input, identifier: $identifier) {
      product {
        id
        title
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
    "input": {
      "title": "Summer sandals"
    },
    "identifier": {
      "customId": {
        "namespace": "custom",
        "key": "id",
        "value": "12345"
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
  "query": "mutation UpsertProductByCustomId($input: ProductSetInput!, $identifier: ProductSetIdentifiers) { productSet(input: $input, identifier: $identifier) { product { id title } userErrors { field message } } }",
   "variables": {
      "input": {
        "title": "Summer sandals"
      },
      "identifier": {
        "customId": {
          "namespace": "custom",
          "key": "id",
          "value": "12345"
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
    mutation UpsertProductByCustomId($input: ProductSetInput!, $identifier: ProductSetIdentifiers) {
      productSet(input: $input, identifier: $identifier) {
        product {
          id
          title
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "input": {
              "title": "Summer sandals"
          },
          "identifier": {
              "customId": {
                  "namespace": "custom",
                  "key": "id",
                  "value": "12345"
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
    mutation UpsertProductByCustomId($input: ProductSetInput!, $identifier: ProductSetIdentifiers) {
      productSet(input: $input, identifier: $identifier) {
        product {
          id
          title
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "title": "Summer sandals"
    },
    "identifier": {
      "customId": {
        "namespace": "custom",
        "key": "id",
        "value": "12345"
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
      "query": `mutation UpsertProductByCustomId($input: ProductSetInput!, $identifier: ProductSetIdentifiers) {
        productSet(input: $input, identifier: $identifier) {
          product {
            id
            title
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "input": {
              "title": "Summer sandals"
          },
          "identifier": {
              "customId": {
                  "namespace": "custom",
                  "key": "id",
                  "value": "12345"
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
  'mutation UpsertProductByCustomId($input: ProductSetInput!, $identifier: ProductSetIdentifiers) {
    productSet(input: $input, identifier: $identifier) {
      product {
        id
        title
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "title": "Summer sandals"
    },
    "identifier": {
      "customId": {
        "namespace": "custom",
        "key": "id",
        "value": "12345"
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "productSet": {
      "product": {
        "id": "gid://shopify/Product/1072481925",
        "title": "Summer sandals"
      },
      "userErrors": []
    }
  }
  ```

* ### Upsert a product by its handle

  #### Description

  Upsert (update or insert) a product using its \[handle]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/Product#field-Product.fields.handle) as the identifier. This example returns the newly created product or the updated existing product based on the handle match.

  #### Query

  ```graphql
  mutation UpsertProductByHandle($input: ProductSetInput!, $identifier: ProductSetIdentifiers) {
    productSet(input: $input, identifier: $identifier) {
      product {
        id
        title
        handle
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
    "input": {
      "title": "Winter hat",
      "handle": "winter-hat"
    },
    "identifier": {
      "handle": "winter-hat"
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
  "query": "mutation UpsertProductByHandle($input: ProductSetInput!, $identifier: ProductSetIdentifiers) { productSet(input: $input, identifier: $identifier) { product { id title handle } userErrors { field message } } }",
   "variables": {
      "input": {
        "title": "Winter hat",
        "handle": "winter-hat"
      },
      "identifier": {
        "handle": "winter-hat"
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
    mutation UpsertProductByHandle($input: ProductSetInput!, $identifier: ProductSetIdentifiers) {
      productSet(input: $input, identifier: $identifier) {
        product {
          id
          title
          handle
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "input": {
              "title": "Winter hat",
              "handle": "winter-hat"
          },
          "identifier": {
              "handle": "winter-hat"
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
    mutation UpsertProductByHandle($input: ProductSetInput!, $identifier: ProductSetIdentifiers) {
      productSet(input: $input, identifier: $identifier) {
        product {
          id
          title
          handle
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "title": "Winter hat",
      "handle": "winter-hat"
    },
    "identifier": {
      "handle": "winter-hat"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation UpsertProductByHandle($input: ProductSetInput!, $identifier: ProductSetIdentifiers) {
        productSet(input: $input, identifier: $identifier) {
          product {
            id
            title
            handle
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "input": {
              "title": "Winter hat",
              "handle": "winter-hat"
          },
          "identifier": {
              "handle": "winter-hat"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation UpsertProductByHandle($input: ProductSetInput!, $identifier: ProductSetIdentifiers) {
    productSet(input: $input, identifier: $identifier) {
      product {
        id
        title
        handle
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "title": "Winter hat",
      "handle": "winter-hat"
    },
    "identifier": {
      "handle": "winter-hat"
    }
  }'
  ```

  #### Response

  ```json
  {
    "productSet": {
      "product": {
        "id": "gid://shopify/Product/1072481952",
        "title": "Winter hat",
        "handle": "winter-hat"
      },
      "userErrors": []
    }
  }
  ```

* ### productSet reference
