---
title: combinedListingUpdate - GraphQL Admin
description: >-
  Add, remove and update `CombinedListing`s of a given Product.


  `CombinedListing`s are comprised of multiple products to create a single
  listing. There are two kinds of products used in a `CombinedListing`:


  1. Parent products

  2. Child products


  The parent product is created with a `productCreate` with a
  `CombinedListingRole` of `PARENT`. Once created, you can associate child
  products with the parent product using this mutation. Parent products
  represent the idea of a product (e.g. Shoe).


  Child products represent a particular option value (or combination of option
  values) of a parent product. For instance, with your Shoe parent product, you
  may have several child products representing specific colors of the shoe (e.g.
  Shoe - Blue). You could also have child products representing more than a
  single option (e.g. Shoe - Blue/Canvas, Shoe - Blue/Leather, etc...).


  The combined listing is the association of parent product to one or more child
  products.


  Learn more about [Combined
  Listings](https://shopify.dev/apps/selling-strategies/combined-listings).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/combinedListingUpdate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/combinedListingUpdate.md
---

# combined​Listing​Update

mutation

Requires `write_products` access scope. Also: The user must have permission to manage products.

Add, remove and update `CombinedListing`s of a given Product.

`CombinedListing`s are comprised of multiple products to create a single listing. There are two kinds of products used in a `CombinedListing`:

1. Parent products
2. Child products

The parent product is created with a `productCreate` with a `CombinedListingRole` of `PARENT`. Once created, you can associate child products with the parent product using this mutation. Parent products represent the idea of a product (e.g. Shoe).

Child products represent a particular option value (or combination of option values) of a parent product. For instance, with your Shoe parent product, you may have several child products representing specific colors of the shoe (e.g. Shoe - Blue). You could also have child products representing more than a single option (e.g. Shoe - Blue/Canvas, Shoe - Blue/Leather, etc...).

The combined listing is the association of parent product to one or more child products.

Learn more about [Combined Listings](https://shopify.dev/apps/selling-strategies/combined-listings).

## Arguments

* options​And​Values

  [\[Option​And​Value​Input!\]](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/OptionAndValueInput)

  The ordered options and values to be used by the combined listing. Options and values will be reordered to match the order specified here.

* parent​Product​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the parent product.

* products​Added

  [\[Child​Product​Relation​Input!\]](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/ChildProductRelationInput)

  The child products to add and their assigned options and option values.

* products​Edited

  [\[Child​Product​Relation​Input!\]](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/ChildProductRelationInput)

  The child products to edit and their assigned options and option values.

* products​Removed​Ids

  [\[ID!\]](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The IDs of products to be removed from the combined listing.

* title

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The updated title for the combined listing.

***

## Combined​Listing​Update​Payload returns

* product

  [Product](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product)

  The parent product.

* user​Errors

  [\[Combined​Listing​Update​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CombinedListingUpdateUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Add child products to a combined listing

  #### Description

  Add new child products to an existing combined listing product.

  #### Query

  ```graphql
  mutation AddChildProductsToCombinedListing($parentProductId: ID!, $productsAdded: [ChildProductRelationInput!], $optionsAndValues: [OptionAndValueInput!]) {
    combinedListingUpdate(parentProductId: $parentProductId, productsAdded: $productsAdded, optionsAndValues: $optionsAndValues) {
      product {
        id
        combinedListing {
          combinedListingChildren(first: 10) {
            nodes {
              product {
                id
              }
              parentVariant {
                selectedOptions {
                  value
                }
              }
            }
          }
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
    "parentProductId": "gid://shopify/Product/108828309",
    "productsAdded": [
      {
        "childProductId": "gid://shopify/Product/121709582",
        "selectedParentOptionValues": [
          {
            "name": "color",
            "value": "Blue"
          },
          {
            "name": "size",
            "value": "12"
          }
        ]
      },
      {
        "childProductId": "gid://shopify/Product/912855135",
        "selectedParentOptionValues": [
          {
            "name": "color",
            "value": "Red"
          },
          {
            "name": "size",
            "value": "12"
          }
        ]
      }
    ],
    "optionsAndValues": [
      {
        "name": "color",
        "values": [
          "Blue",
          "Red"
        ]
      },
      {
        "name": "size",
        "values": [
          "12"
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
  "query": "mutation AddChildProductsToCombinedListing($parentProductId: ID!, $productsAdded: [ChildProductRelationInput!], $optionsAndValues: [OptionAndValueInput!]) { combinedListingUpdate(parentProductId: $parentProductId, productsAdded: $productsAdded, optionsAndValues: $optionsAndValues) { product { id combinedListing { combinedListingChildren(first: 10) { nodes { product { id } parentVariant { selectedOptions { value } } } } } } userErrors { code field message } } }",
   "variables": {
      "parentProductId": "gid://shopify/Product/108828309",
      "productsAdded": [
        {
          "childProductId": "gid://shopify/Product/121709582",
          "selectedParentOptionValues": [
            {
              "name": "color",
              "value": "Blue"
            },
            {
              "name": "size",
              "value": "12"
            }
          ]
        },
        {
          "childProductId": "gid://shopify/Product/912855135",
          "selectedParentOptionValues": [
            {
              "name": "color",
              "value": "Red"
            },
            {
              "name": "size",
              "value": "12"
            }
          ]
        }
      ],
      "optionsAndValues": [
        {
          "name": "color",
          "values": [
            "Blue",
            "Red"
          ]
        },
        {
          "name": "size",
          "values": [
            "12"
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
    mutation AddChildProductsToCombinedListing($parentProductId: ID!, $productsAdded: [ChildProductRelationInput!], $optionsAndValues: [OptionAndValueInput!]) {
      combinedListingUpdate(parentProductId: $parentProductId, productsAdded: $productsAdded, optionsAndValues: $optionsAndValues) {
        product {
          id
          combinedListing {
            combinedListingChildren(first: 10) {
              nodes {
                product {
                  id
                }
                parentVariant {
                  selectedOptions {
                    value
                  }
                }
              }
            }
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
          "parentProductId": "gid://shopify/Product/108828309",
          "productsAdded": [
              {
                  "childProductId": "gid://shopify/Product/121709582",
                  "selectedParentOptionValues": [
                      {
                          "name": "color",
                          "value": "Blue"
                      },
                      {
                          "name": "size",
                          "value": "12"
                      }
                  ]
              },
              {
                  "childProductId": "gid://shopify/Product/912855135",
                  "selectedParentOptionValues": [
                      {
                          "name": "color",
                          "value": "Red"
                      },
                      {
                          "name": "size",
                          "value": "12"
                      }
                  ]
              }
          ],
          "optionsAndValues": [
              {
                  "name": "color",
                  "values": [
                      "Blue",
                      "Red"
                  ]
              },
              {
                  "name": "size",
                  "values": [
                      "12"
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
    mutation AddChildProductsToCombinedListing($parentProductId: ID!, $productsAdded: [ChildProductRelationInput!], $optionsAndValues: [OptionAndValueInput!]) {
      combinedListingUpdate(parentProductId: $parentProductId, productsAdded: $productsAdded, optionsAndValues: $optionsAndValues) {
        product {
          id
          combinedListing {
            combinedListingChildren(first: 10) {
              nodes {
                product {
                  id
                }
                parentVariant {
                  selectedOptions {
                    value
                  }
                }
              }
            }
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
    "parentProductId": "gid://shopify/Product/108828309",
    "productsAdded": [
      {
        "childProductId": "gid://shopify/Product/121709582",
        "selectedParentOptionValues": [
          {
            "name": "color",
            "value": "Blue"
          },
          {
            "name": "size",
            "value": "12"
          }
        ]
      },
      {
        "childProductId": "gid://shopify/Product/912855135",
        "selectedParentOptionValues": [
          {
            "name": "color",
            "value": "Red"
          },
          {
            "name": "size",
            "value": "12"
          }
        ]
      }
    ],
    "optionsAndValues": [
      {
        "name": "color",
        "values": [
          "Blue",
          "Red"
        ]
      },
      {
        "name": "size",
        "values": [
          "12"
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
      "query": `mutation AddChildProductsToCombinedListing($parentProductId: ID!, $productsAdded: [ChildProductRelationInput!], $optionsAndValues: [OptionAndValueInput!]) {
        combinedListingUpdate(parentProductId: $parentProductId, productsAdded: $productsAdded, optionsAndValues: $optionsAndValues) {
          product {
            id
            combinedListing {
              combinedListingChildren(first: 10) {
                nodes {
                  product {
                    id
                  }
                  parentVariant {
                    selectedOptions {
                      value
                    }
                  }
                }
              }
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
          "parentProductId": "gid://shopify/Product/108828309",
          "productsAdded": [
              {
                  "childProductId": "gid://shopify/Product/121709582",
                  "selectedParentOptionValues": [
                      {
                          "name": "color",
                          "value": "Blue"
                      },
                      {
                          "name": "size",
                          "value": "12"
                      }
                  ]
              },
              {
                  "childProductId": "gid://shopify/Product/912855135",
                  "selectedParentOptionValues": [
                      {
                          "name": "color",
                          "value": "Red"
                      },
                      {
                          "name": "size",
                          "value": "12"
                      }
                  ]
              }
          ],
          "optionsAndValues": [
              {
                  "name": "color",
                  "values": [
                      "Blue",
                      "Red"
                  ]
              },
              {
                  "name": "size",
                  "values": [
                      "12"
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
  'mutation AddChildProductsToCombinedListing($parentProductId: ID!, $productsAdded: [ChildProductRelationInput!], $optionsAndValues: [OptionAndValueInput!]) {
    combinedListingUpdate(parentProductId: $parentProductId, productsAdded: $productsAdded, optionsAndValues: $optionsAndValues) {
      product {
        id
        combinedListing {
          combinedListingChildren(first: 10) {
            nodes {
              product {
                id
              }
              parentVariant {
                selectedOptions {
                  value
                }
              }
            }
          }
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
    "parentProductId": "gid://shopify/Product/108828309",
    "productsAdded": [
      {
        "childProductId": "gid://shopify/Product/121709582",
        "selectedParentOptionValues": [
          {
            "name": "color",
            "value": "Blue"
          },
          {
            "name": "size",
            "value": "12"
          }
        ]
      },
      {
        "childProductId": "gid://shopify/Product/912855135",
        "selectedParentOptionValues": [
          {
            "name": "color",
            "value": "Red"
          },
          {
            "name": "size",
            "value": "12"
          }
        ]
      }
    ],
    "optionsAndValues": [
      {
        "name": "color",
        "values": [
          "Blue",
          "Red"
        ]
      },
      {
        "name": "size",
        "values": [
          "12"
        ]
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "combinedListingUpdate": {
      "product": {
        "id": "gid://shopify/Product/108828309",
        "combinedListing": {
          "combinedListingChildren": {
            "nodes": [
              {
                "product": {
                  "id": "gid://shopify/Product/121709582"
                },
                "parentVariant": {
                  "selectedOptions": [
                    {
                      "value": "Blue"
                    },
                    {
                      "value": "12"
                    }
                  ]
                }
              },
              {
                "product": {
                  "id": "gid://shopify/Product/912855135"
                },
                "parentVariant": {
                  "selectedOptions": [
                    {
                      "value": "Red"
                    },
                    {
                      "value": "12"
                    }
                  ]
                }
              }
            ]
          }
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Add child products with options associated with a metafield to a combined listing

  #### Description

  Add new child products with options associated with a metafield to an existing combined listing product.

  #### Query

  ```graphql
  mutation AddChildProductsToCombinedListing($parentProductId: ID!, $productsAdded: [ChildProductRelationInput!], $optionsAndValues: [OptionAndValueInput!]) {
    combinedListingUpdate(parentProductId: $parentProductId, productsAdded: $productsAdded, optionsAndValues: $optionsAndValues) {
      product {
        id
        combinedListing {
          combinedListingChildren(first: 10) {
            nodes {
              product {
                id
              }
              parentVariant {
                selectedOptions {
                  value
                }
              }
            }
          }
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
    "parentProductId": "gid://shopify/Product/108828309",
    "productsAdded": [
      {
        "childProductId": "gid://shopify/Product/121709582",
        "selectedParentOptionValues": [
          {
            "name": "Color",
            "value": "Blue",
            "linkedMetafieldValue": "gid://shopify/Metaobject/1"
          },
          {
            "name": "Fabric",
            "value": "Cotton",
            "linkedMetafieldValue": "gid://shopify/Metaobject/3"
          }
        ]
      },
      {
        "childProductId": "gid://shopify/Product/912855135",
        "selectedParentOptionValues": [
          {
            "name": "Color",
            "value": "Red",
            "linkedMetafieldValue": "gid://shopify/Metaobject/2"
          },
          {
            "name": "Fabric",
            "value": "Polyester",
            "linkedMetafieldValue": "gid://shopify/Metaobject/4"
          }
        ]
      }
    ],
    "optionsAndValues": [
      {
        "name": "Color",
        "values": [
          "Blue",
          "Red"
        ],
        "optionId": "gid://shopify/ProductOption/1",
        "linkedMetafield": {
          "namespace": "shopify",
          "key": "color-pattern",
          "values": [
            "gid://shopify/Metaobject/1",
            "gid://shopify/Metaobject/2"
          ]
        }
      },
      {
        "name": "Fabric",
        "values": [
          "Cotton",
          "Polyester"
        ],
        "optionId": "gid://shopify/ProductOption/2",
        "linkedMetafield": {
          "namespace": "shopify",
          "key": "fabric",
          "values": [
            "gid://shopify/Metaobject/3",
            "gid://shopify/Metaobject/4"
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
  "query": "mutation AddChildProductsToCombinedListing($parentProductId: ID!, $productsAdded: [ChildProductRelationInput!], $optionsAndValues: [OptionAndValueInput!]) { combinedListingUpdate(parentProductId: $parentProductId, productsAdded: $productsAdded, optionsAndValues: $optionsAndValues) { product { id combinedListing { combinedListingChildren(first: 10) { nodes { product { id } parentVariant { selectedOptions { value } } } } } } userErrors { code field message } } }",
   "variables": {
      "parentProductId": "gid://shopify/Product/108828309",
      "productsAdded": [
        {
          "childProductId": "gid://shopify/Product/121709582",
          "selectedParentOptionValues": [
            {
              "name": "Color",
              "value": "Blue",
              "linkedMetafieldValue": "gid://shopify/Metaobject/1"
            },
            {
              "name": "Fabric",
              "value": "Cotton",
              "linkedMetafieldValue": "gid://shopify/Metaobject/3"
            }
          ]
        },
        {
          "childProductId": "gid://shopify/Product/912855135",
          "selectedParentOptionValues": [
            {
              "name": "Color",
              "value": "Red",
              "linkedMetafieldValue": "gid://shopify/Metaobject/2"
            },
            {
              "name": "Fabric",
              "value": "Polyester",
              "linkedMetafieldValue": "gid://shopify/Metaobject/4"
            }
          ]
        }
      ],
      "optionsAndValues": [
        {
          "name": "Color",
          "values": [
            "Blue",
            "Red"
          ],
          "optionId": "gid://shopify/ProductOption/1",
          "linkedMetafield": {
            "namespace": "shopify",
            "key": "color-pattern",
            "values": [
              "gid://shopify/Metaobject/1",
              "gid://shopify/Metaobject/2"
            ]
          }
        },
        {
          "name": "Fabric",
          "values": [
            "Cotton",
            "Polyester"
          ],
          "optionId": "gid://shopify/ProductOption/2",
          "linkedMetafield": {
            "namespace": "shopify",
            "key": "fabric",
            "values": [
              "gid://shopify/Metaobject/3",
              "gid://shopify/Metaobject/4"
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
    mutation AddChildProductsToCombinedListing($parentProductId: ID!, $productsAdded: [ChildProductRelationInput!], $optionsAndValues: [OptionAndValueInput!]) {
      combinedListingUpdate(parentProductId: $parentProductId, productsAdded: $productsAdded, optionsAndValues: $optionsAndValues) {
        product {
          id
          combinedListing {
            combinedListingChildren(first: 10) {
              nodes {
                product {
                  id
                }
                parentVariant {
                  selectedOptions {
                    value
                  }
                }
              }
            }
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
          "parentProductId": "gid://shopify/Product/108828309",
          "productsAdded": [
              {
                  "childProductId": "gid://shopify/Product/121709582",
                  "selectedParentOptionValues": [
                      {
                          "name": "Color",
                          "value": "Blue",
                          "linkedMetafieldValue": "gid://shopify/Metaobject/1"
                      },
                      {
                          "name": "Fabric",
                          "value": "Cotton",
                          "linkedMetafieldValue": "gid://shopify/Metaobject/3"
                      }
                  ]
              },
              {
                  "childProductId": "gid://shopify/Product/912855135",
                  "selectedParentOptionValues": [
                      {
                          "name": "Color",
                          "value": "Red",
                          "linkedMetafieldValue": "gid://shopify/Metaobject/2"
                      },
                      {
                          "name": "Fabric",
                          "value": "Polyester",
                          "linkedMetafieldValue": "gid://shopify/Metaobject/4"
                      }
                  ]
              }
          ],
          "optionsAndValues": [
              {
                  "name": "Color",
                  "values": [
                      "Blue",
                      "Red"
                  ],
                  "optionId": "gid://shopify/ProductOption/1",
                  "linkedMetafield": {
                      "namespace": "shopify",
                      "key": "color-pattern",
                      "values": [
                          "gid://shopify/Metaobject/1",
                          "gid://shopify/Metaobject/2"
                      ]
                  }
              },
              {
                  "name": "Fabric",
                  "values": [
                      "Cotton",
                      "Polyester"
                  ],
                  "optionId": "gid://shopify/ProductOption/2",
                  "linkedMetafield": {
                      "namespace": "shopify",
                      "key": "fabric",
                      "values": [
                          "gid://shopify/Metaobject/3",
                          "gid://shopify/Metaobject/4"
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
    mutation AddChildProductsToCombinedListing($parentProductId: ID!, $productsAdded: [ChildProductRelationInput!], $optionsAndValues: [OptionAndValueInput!]) {
      combinedListingUpdate(parentProductId: $parentProductId, productsAdded: $productsAdded, optionsAndValues: $optionsAndValues) {
        product {
          id
          combinedListing {
            combinedListingChildren(first: 10) {
              nodes {
                product {
                  id
                }
                parentVariant {
                  selectedOptions {
                    value
                  }
                }
              }
            }
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
    "parentProductId": "gid://shopify/Product/108828309",
    "productsAdded": [
      {
        "childProductId": "gid://shopify/Product/121709582",
        "selectedParentOptionValues": [
          {
            "name": "Color",
            "value": "Blue",
            "linkedMetafieldValue": "gid://shopify/Metaobject/1"
          },
          {
            "name": "Fabric",
            "value": "Cotton",
            "linkedMetafieldValue": "gid://shopify/Metaobject/3"
          }
        ]
      },
      {
        "childProductId": "gid://shopify/Product/912855135",
        "selectedParentOptionValues": [
          {
            "name": "Color",
            "value": "Red",
            "linkedMetafieldValue": "gid://shopify/Metaobject/2"
          },
          {
            "name": "Fabric",
            "value": "Polyester",
            "linkedMetafieldValue": "gid://shopify/Metaobject/4"
          }
        ]
      }
    ],
    "optionsAndValues": [
      {
        "name": "Color",
        "values": [
          "Blue",
          "Red"
        ],
        "optionId": "gid://shopify/ProductOption/1",
        "linkedMetafield": {
          "namespace": "shopify",
          "key": "color-pattern",
          "values": [
            "gid://shopify/Metaobject/1",
            "gid://shopify/Metaobject/2"
          ]
        }
      },
      {
        "name": "Fabric",
        "values": [
          "Cotton",
          "Polyester"
        ],
        "optionId": "gid://shopify/ProductOption/2",
        "linkedMetafield": {
          "namespace": "shopify",
          "key": "fabric",
          "values": [
            "gid://shopify/Metaobject/3",
            "gid://shopify/Metaobject/4"
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
      "query": `mutation AddChildProductsToCombinedListing($parentProductId: ID!, $productsAdded: [ChildProductRelationInput!], $optionsAndValues: [OptionAndValueInput!]) {
        combinedListingUpdate(parentProductId: $parentProductId, productsAdded: $productsAdded, optionsAndValues: $optionsAndValues) {
          product {
            id
            combinedListing {
              combinedListingChildren(first: 10) {
                nodes {
                  product {
                    id
                  }
                  parentVariant {
                    selectedOptions {
                      value
                    }
                  }
                }
              }
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
          "parentProductId": "gid://shopify/Product/108828309",
          "productsAdded": [
              {
                  "childProductId": "gid://shopify/Product/121709582",
                  "selectedParentOptionValues": [
                      {
                          "name": "Color",
                          "value": "Blue",
                          "linkedMetafieldValue": "gid://shopify/Metaobject/1"
                      },
                      {
                          "name": "Fabric",
                          "value": "Cotton",
                          "linkedMetafieldValue": "gid://shopify/Metaobject/3"
                      }
                  ]
              },
              {
                  "childProductId": "gid://shopify/Product/912855135",
                  "selectedParentOptionValues": [
                      {
                          "name": "Color",
                          "value": "Red",
                          "linkedMetafieldValue": "gid://shopify/Metaobject/2"
                      },
                      {
                          "name": "Fabric",
                          "value": "Polyester",
                          "linkedMetafieldValue": "gid://shopify/Metaobject/4"
                      }
                  ]
              }
          ],
          "optionsAndValues": [
              {
                  "name": "Color",
                  "values": [
                      "Blue",
                      "Red"
                  ],
                  "optionId": "gid://shopify/ProductOption/1",
                  "linkedMetafield": {
                      "namespace": "shopify",
                      "key": "color-pattern",
                      "values": [
                          "gid://shopify/Metaobject/1",
                          "gid://shopify/Metaobject/2"
                      ]
                  }
              },
              {
                  "name": "Fabric",
                  "values": [
                      "Cotton",
                      "Polyester"
                  ],
                  "optionId": "gid://shopify/ProductOption/2",
                  "linkedMetafield": {
                      "namespace": "shopify",
                      "key": "fabric",
                      "values": [
                          "gid://shopify/Metaobject/3",
                          "gid://shopify/Metaobject/4"
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
  'mutation AddChildProductsToCombinedListing($parentProductId: ID!, $productsAdded: [ChildProductRelationInput!], $optionsAndValues: [OptionAndValueInput!]) {
    combinedListingUpdate(parentProductId: $parentProductId, productsAdded: $productsAdded, optionsAndValues: $optionsAndValues) {
      product {
        id
        combinedListing {
          combinedListingChildren(first: 10) {
            nodes {
              product {
                id
              }
              parentVariant {
                selectedOptions {
                  value
                }
              }
            }
          }
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
    "parentProductId": "gid://shopify/Product/108828309",
    "productsAdded": [
      {
        "childProductId": "gid://shopify/Product/121709582",
        "selectedParentOptionValues": [
          {
            "name": "Color",
            "value": "Blue",
            "linkedMetafieldValue": "gid://shopify/Metaobject/1"
          },
          {
            "name": "Fabric",
            "value": "Cotton",
            "linkedMetafieldValue": "gid://shopify/Metaobject/3"
          }
        ]
      },
      {
        "childProductId": "gid://shopify/Product/912855135",
        "selectedParentOptionValues": [
          {
            "name": "Color",
            "value": "Red",
            "linkedMetafieldValue": "gid://shopify/Metaobject/2"
          },
          {
            "name": "Fabric",
            "value": "Polyester",
            "linkedMetafieldValue": "gid://shopify/Metaobject/4"
          }
        ]
      }
    ],
    "optionsAndValues": [
      {
        "name": "Color",
        "values": [
          "Blue",
          "Red"
        ],
        "optionId": "gid://shopify/ProductOption/1",
        "linkedMetafield": {
          "namespace": "shopify",
          "key": "color-pattern",
          "values": [
            "gid://shopify/Metaobject/1",
            "gid://shopify/Metaobject/2"
          ]
        }
      },
      {
        "name": "Fabric",
        "values": [
          "Cotton",
          "Polyester"
        ],
        "optionId": "gid://shopify/ProductOption/2",
        "linkedMetafield": {
          "namespace": "shopify",
          "key": "fabric",
          "values": [
            "gid://shopify/Metaobject/3",
            "gid://shopify/Metaobject/4"
          ]
        }
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "combinedListingUpdate": {
      "product": {
        "id": "gid://shopify/Product/108828309",
        "combinedListing": {
          "combinedListingChildren": {
            "nodes": [
              {
                "product": {
                  "id": "gid://shopify/Product/121709582"
                },
                "parentVariant": {
                  "selectedOptions": [
                    {
                      "name": "Color",
                      "value": "Blue",
                      "optionValue": {
                        "linkedMetafieldValue": "gid://shopify/Metaobject/1"
                      }
                    },
                    {
                      "name": "Fabric",
                      "value": "Cotton",
                      "optionValue": {
                        "linkedMetafieldValue": "gid://shopify/Metaobject/3"
                      }
                    }
                  ]
                }
              },
              {
                "product": {
                  "id": "gid://shopify/Product/912855135"
                },
                "parentVariant": {
                  "selectedOptions": [
                    {
                      "name": "Color",
                      "value": "Red",
                      "optionValue": {
                        "linkedMetafieldValue": "gid://shopify/Metaobject/2"
                      }
                    },
                    {
                      "name": "Fabric",
                      "value": "Polyester",
                      "optionValue": {
                        "linkedMetafieldValue": "gid://shopify/Metaobject/4"
                      }
                    }
                  ]
                }
              }
            ]
          }
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Remove child products from a combined listing

  #### Description

  Remove child products from an existing combined listing product.

  #### Query

  ```graphql
  mutation RemoveChildProductsFromCombinedListing($parentProductId: ID!, $productsRemovedIds: [ID!]) {
    combinedListingUpdate(parentProductId: $parentProductId, productsRemovedIds: $productsRemovedIds) {
      product {
        id
        combinedListing {
          combinedListingChildren(first: 10) {
            nodes {
              product {
                id
              }
            }
          }
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
    "parentProductId": "gid://shopify/Product/362339553",
    "productsRemovedIds": [
      "gid://shopify/Product/223392616"
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
  "query": "mutation RemoveChildProductsFromCombinedListing($parentProductId: ID!, $productsRemovedIds: [ID!]) { combinedListingUpdate(parentProductId: $parentProductId, productsRemovedIds: $productsRemovedIds) { product { id combinedListing { combinedListingChildren(first: 10) { nodes { product { id } } } } } userErrors { code field message } } }",
   "variables": {
      "parentProductId": "gid://shopify/Product/362339553",
      "productsRemovedIds": [
        "gid://shopify/Product/223392616"
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
    mutation RemoveChildProductsFromCombinedListing($parentProductId: ID!, $productsRemovedIds: [ID!]) {
      combinedListingUpdate(parentProductId: $parentProductId, productsRemovedIds: $productsRemovedIds) {
        product {
          id
          combinedListing {
            combinedListingChildren(first: 10) {
              nodes {
                product {
                  id
                }
              }
            }
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
          "parentProductId": "gid://shopify/Product/362339553",
          "productsRemovedIds": [
              "gid://shopify/Product/223392616"
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
    mutation RemoveChildProductsFromCombinedListing($parentProductId: ID!, $productsRemovedIds: [ID!]) {
      combinedListingUpdate(parentProductId: $parentProductId, productsRemovedIds: $productsRemovedIds) {
        product {
          id
          combinedListing {
            combinedListingChildren(first: 10) {
              nodes {
                product {
                  id
                }
              }
            }
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
    "parentProductId": "gid://shopify/Product/362339553",
    "productsRemovedIds": [
      "gid://shopify/Product/223392616"
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation RemoveChildProductsFromCombinedListing($parentProductId: ID!, $productsRemovedIds: [ID!]) {
        combinedListingUpdate(parentProductId: $parentProductId, productsRemovedIds: $productsRemovedIds) {
          product {
            id
            combinedListing {
              combinedListingChildren(first: 10) {
                nodes {
                  product {
                    id
                  }
                }
              }
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
          "parentProductId": "gid://shopify/Product/362339553",
          "productsRemovedIds": [
              "gid://shopify/Product/223392616"
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation RemoveChildProductsFromCombinedListing($parentProductId: ID!, $productsRemovedIds: [ID!]) {
    combinedListingUpdate(parentProductId: $parentProductId, productsRemovedIds: $productsRemovedIds) {
      product {
        id
        combinedListing {
          combinedListingChildren(first: 10) {
            nodes {
              product {
                id
              }
            }
          }
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
    "parentProductId": "gid://shopify/Product/362339553",
    "productsRemovedIds": [
      "gid://shopify/Product/223392616"
    ]
  }'
  ```

  #### Response

  ```json
  {
    "combinedListingUpdate": {
      "product": {
        "id": "gid://shopify/Product/362339553",
        "combinedListing": {
          "combinedListingChildren": {
            "nodes": [
              {
                "product": {
                  "id": "gid://shopify/Product/555575834"
                }
              }
            ]
          }
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Update option values of combined listing child product

  #### Description

  Update child products of an existing combined listing product.

  #### Query

  ```graphql
  mutation UpdateChildProductsOfCombinedListing($parentProductId: ID!, $productsEdited: [ChildProductRelationInput!]) {
    combinedListingUpdate(parentProductId: $parentProductId, productsEdited: $productsEdited) {
      product {
        id
        combinedListing {
          combinedListingChildren(first: 10) {
            nodes {
              product {
                id
              }
              parentVariant {
                selectedOptions {
                  value
                }
              }
            }
          }
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
    "parentProductId": "gid://shopify/Product/362339553",
    "productsEdited": [
      {
        "childProductId": "gid://shopify/Product/223392616",
        "selectedParentOptionValues": [
          {
            "name": "Color",
            "value": "green"
          }
        ]
      },
      {
        "childProductId": "gid://shopify/Product/555575834",
        "selectedParentOptionValues": [
          {
            "name": "Color",
            "value": "blue"
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
  "query": "mutation UpdateChildProductsOfCombinedListing($parentProductId: ID!, $productsEdited: [ChildProductRelationInput!]) { combinedListingUpdate(parentProductId: $parentProductId, productsEdited: $productsEdited) { product { id combinedListing { combinedListingChildren(first: 10) { nodes { product { id } parentVariant { selectedOptions { value } } } } } } userErrors { code field message } } }",
   "variables": {
      "parentProductId": "gid://shopify/Product/362339553",
      "productsEdited": [
        {
          "childProductId": "gid://shopify/Product/223392616",
          "selectedParentOptionValues": [
            {
              "name": "Color",
              "value": "green"
            }
          ]
        },
        {
          "childProductId": "gid://shopify/Product/555575834",
          "selectedParentOptionValues": [
            {
              "name": "Color",
              "value": "blue"
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
    mutation UpdateChildProductsOfCombinedListing($parentProductId: ID!, $productsEdited: [ChildProductRelationInput!]) {
      combinedListingUpdate(parentProductId: $parentProductId, productsEdited: $productsEdited) {
        product {
          id
          combinedListing {
            combinedListingChildren(first: 10) {
              nodes {
                product {
                  id
                }
                parentVariant {
                  selectedOptions {
                    value
                  }
                }
              }
            }
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
          "parentProductId": "gid://shopify/Product/362339553",
          "productsEdited": [
              {
                  "childProductId": "gid://shopify/Product/223392616",
                  "selectedParentOptionValues": [
                      {
                          "name": "Color",
                          "value": "green"
                      }
                  ]
              },
              {
                  "childProductId": "gid://shopify/Product/555575834",
                  "selectedParentOptionValues": [
                      {
                          "name": "Color",
                          "value": "blue"
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
    mutation UpdateChildProductsOfCombinedListing($parentProductId: ID!, $productsEdited: [ChildProductRelationInput!]) {
      combinedListingUpdate(parentProductId: $parentProductId, productsEdited: $productsEdited) {
        product {
          id
          combinedListing {
            combinedListingChildren(first: 10) {
              nodes {
                product {
                  id
                }
                parentVariant {
                  selectedOptions {
                    value
                  }
                }
              }
            }
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
    "parentProductId": "gid://shopify/Product/362339553",
    "productsEdited": [
      {
        "childProductId": "gid://shopify/Product/223392616",
        "selectedParentOptionValues": [
          {
            "name": "Color",
            "value": "green"
          }
        ]
      },
      {
        "childProductId": "gid://shopify/Product/555575834",
        "selectedParentOptionValues": [
          {
            "name": "Color",
            "value": "blue"
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
      "query": `mutation UpdateChildProductsOfCombinedListing($parentProductId: ID!, $productsEdited: [ChildProductRelationInput!]) {
        combinedListingUpdate(parentProductId: $parentProductId, productsEdited: $productsEdited) {
          product {
            id
            combinedListing {
              combinedListingChildren(first: 10) {
                nodes {
                  product {
                    id
                  }
                  parentVariant {
                    selectedOptions {
                      value
                    }
                  }
                }
              }
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
          "parentProductId": "gid://shopify/Product/362339553",
          "productsEdited": [
              {
                  "childProductId": "gid://shopify/Product/223392616",
                  "selectedParentOptionValues": [
                      {
                          "name": "Color",
                          "value": "green"
                      }
                  ]
              },
              {
                  "childProductId": "gid://shopify/Product/555575834",
                  "selectedParentOptionValues": [
                      {
                          "name": "Color",
                          "value": "blue"
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
  'mutation UpdateChildProductsOfCombinedListing($parentProductId: ID!, $productsEdited: [ChildProductRelationInput!]) {
    combinedListingUpdate(parentProductId: $parentProductId, productsEdited: $productsEdited) {
      product {
        id
        combinedListing {
          combinedListingChildren(first: 10) {
            nodes {
              product {
                id
              }
              parentVariant {
                selectedOptions {
                  value
                }
              }
            }
          }
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
    "parentProductId": "gid://shopify/Product/362339553",
    "productsEdited": [
      {
        "childProductId": "gid://shopify/Product/223392616",
        "selectedParentOptionValues": [
          {
            "name": "Color",
            "value": "green"
          }
        ]
      },
      {
        "childProductId": "gid://shopify/Product/555575834",
        "selectedParentOptionValues": [
          {
            "name": "Color",
            "value": "blue"
          }
        ]
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "combinedListingUpdate": {
      "product": {
        "id": "gid://shopify/Product/362339553",
        "combinedListing": {
          "combinedListingChildren": {
            "nodes": [
              {
                "product": {
                  "id": "gid://shopify/Product/555575834"
                },
                "parentVariant": {
                  "selectedOptions": [
                    {
                      "value": "blue"
                    }
                  ]
                }
              },
              {
                "product": {
                  "id": "gid://shopify/Product/223392616"
                },
                "parentVariant": {
                  "selectedOptions": [
                    {
                      "value": "green"
                    }
                  ]
                }
              }
            ]
          }
        }
      },
      "userErrors": []
    }
  }
  ```

* ### combinedListingUpdate reference
