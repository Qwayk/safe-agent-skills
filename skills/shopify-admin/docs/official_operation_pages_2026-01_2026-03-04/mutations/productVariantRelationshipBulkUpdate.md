---
title: productVariantRelationshipBulkUpdate - GraphQL Admin
description: >-
  Creates new bundles, updates component quantities in existing bundles, and
  removes bundle components for one or multiple
  [`ProductVariant`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant)
  objects.


  Each bundle variant can contain up to 30 component variants with specified
  quantities. After an app assigns components to a bundle, only that app can
  manage those components.


  > Note:

  > For most use cases, use
  [`productBundleCreate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/productBundleCreate)
  instead, which creates product fixed bundles.
  `productVariantRelationshipBulkUpdate` is for [variant fixed
  bundles](https://shopify.dev/docs/apps/build/product-merchandising/bundles/add-variant-fixed-bundle),
  where each variant has its own component configuration.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/productVariantRelationshipBulkUpdate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/productVariantRelationshipBulkUpdate.md
---

# product​Variant​Relationship​Bulk​Update

mutation

Requires `write_products` access scope. Also: The shop must have access to bundles feature.

Creates new bundles, updates component quantities in existing bundles, and removes bundle components for one or multiple [`ProductVariant`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant) objects.

Each bundle variant can contain up to 30 component variants with specified quantities. After an app assigns components to a bundle, only that app can manage those components.

***

**Note:** For most use cases, use \<a href="https://shopify.dev/docs/api/admin-graphql/latest/mutations/productBundleCreate">\<code>\<span class="PreventFireFoxApplyingGapToWBR">product\<wbr/>Bundle\<wbr/>Create\</span>\</code>\</a> instead, which creates product fixed bundles. \<code>\<span class="PreventFireFoxApplyingGapToWBR">product\<wbr/>Variant\<wbr/>Relationship\<wbr/>Bulk\<wbr/>Update\</span>\</code> is for \<a href="https://shopify.dev/docs/apps/build/product-merchandising/bundles/add-variant-fixed-bundle">variant fixed bundles\</a>, where each variant has its own component configuration.

***

## Arguments

* input

  [\[Product​Variant​Relationship​Update​Input!\]!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/ProductVariantRelationshipUpdateInput)

  required

  The input options for the product variant being updated.

***

## Product​Variant​Relationship​Bulk​Update​Payload returns

* parent​Product​Variants

  [\[Product​Variant!\]](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant)

  The product variants with successfully updated product variant relationships.

* user​Errors

  [\[Product​Variant​Relationship​Bulk​Update​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariantRelationshipBulkUpdateUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create a bundle by adding components to a product variant

  #### Description

  Creates a new product variant relationship between the parent variant and the child variant passed in the input.

  #### Query

  ```graphql
  mutation CreateBundle($input: [ProductVariantRelationshipUpdateInput!]!) {
    productVariantRelationshipBulkUpdate(input: $input) {
      parentProductVariants {
        id
        productVariantComponents(first: 10) {
          nodes {
            id
            productVariant {
              id
              displayName
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
    "input": [
      {
        "parentProductVariantId": "gid://shopify/ProductVariant/799757249",
        "productVariantRelationshipsToCreate": [
          {
            "id": "gid://shopify/ProductVariant/149896808",
            "quantity": 1
          },
          {
            "id": "gid://shopify/ProductVariant/709406719",
            "quantity": 1
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
  "query": "mutation CreateBundle($input: [ProductVariantRelationshipUpdateInput!]!) { productVariantRelationshipBulkUpdate(input: $input) { parentProductVariants { id productVariantComponents(first: 10) { nodes { id productVariant { id displayName } } } } userErrors { code field message } } }",
   "variables": {
      "input": [
        {
          "parentProductVariantId": "gid://shopify/ProductVariant/799757249",
          "productVariantRelationshipsToCreate": [
            {
              "id": "gid://shopify/ProductVariant/149896808",
              "quantity": 1
            },
            {
              "id": "gid://shopify/ProductVariant/709406719",
              "quantity": 1
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
    mutation CreateBundle($input: [ProductVariantRelationshipUpdateInput!]!) {
      productVariantRelationshipBulkUpdate(input: $input) {
        parentProductVariants {
          id
          productVariantComponents(first: 10) {
            nodes {
              id
              productVariant {
                id
                displayName
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
          "input": [
              {
                  "parentProductVariantId": "gid://shopify/ProductVariant/799757249",
                  "productVariantRelationshipsToCreate": [
                      {
                          "id": "gid://shopify/ProductVariant/149896808",
                          "quantity": 1
                      },
                      {
                          "id": "gid://shopify/ProductVariant/709406719",
                          "quantity": 1
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
    mutation CreateBundle($input: [ProductVariantRelationshipUpdateInput!]!) {
      productVariantRelationshipBulkUpdate(input: $input) {
        parentProductVariants {
          id
          productVariantComponents(first: 10) {
            nodes {
              id
              productVariant {
                id
                displayName
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
    "input": [
      {
        "parentProductVariantId": "gid://shopify/ProductVariant/799757249",
        "productVariantRelationshipsToCreate": [
          {
            "id": "gid://shopify/ProductVariant/149896808",
            "quantity": 1
          },
          {
            "id": "gid://shopify/ProductVariant/709406719",
            "quantity": 1
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
      "query": `mutation CreateBundle($input: [ProductVariantRelationshipUpdateInput!]!) {
        productVariantRelationshipBulkUpdate(input: $input) {
          parentProductVariants {
            id
            productVariantComponents(first: 10) {
              nodes {
                id
                productVariant {
                  id
                  displayName
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
          "input": [
              {
                  "parentProductVariantId": "gid://shopify/ProductVariant/799757249",
                  "productVariantRelationshipsToCreate": [
                      {
                          "id": "gid://shopify/ProductVariant/149896808",
                          "quantity": 1
                      },
                      {
                          "id": "gid://shopify/ProductVariant/709406719",
                          "quantity": 1
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
  'mutation CreateBundle($input: [ProductVariantRelationshipUpdateInput!]!) {
    productVariantRelationshipBulkUpdate(input: $input) {
      parentProductVariants {
        id
        productVariantComponents(first: 10) {
          nodes {
            id
            productVariant {
              id
              displayName
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
    "input": [
      {
        "parentProductVariantId": "gid://shopify/ProductVariant/799757249",
        "productVariantRelationshipsToCreate": [
          {
            "id": "gid://shopify/ProductVariant/149896808",
            "quantity": 1
          },
          {
            "id": "gid://shopify/ProductVariant/709406719",
            "quantity": 1
          }
        ]
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "productVariantRelationshipBulkUpdate": {
      "parentProductVariants": [
        {
          "id": "gid://shopify/ProductVariant/799757249",
          "productVariantComponents": {
            "nodes": [
              {
                "id": "gid://shopify/ProductVariantComponent/993184086",
                "productVariant": {
                  "id": "gid://shopify/ProductVariant/149896808",
                  "displayName": "Composite_Sauce_Pack - component_product_variant_classic_hot_sauce"
                }
              },
              {
                "id": "gid://shopify/ProductVariantComponent/993184087",
                "productVariant": {
                  "id": "gid://shopify/ProductVariant/709406719",
                  "displayName": "Composite_Sauce_Pack - component_product_variant_classic_garlic_sauce"
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

* ### Delete a product variant component

  #### Description

  Removes all the product variant relationships associated with a variant.

  #### Query

  ```graphql
  mutation RemoveABundleComponent($input: [ProductVariantRelationshipUpdateInput!]!) {
    productVariantRelationshipBulkUpdate(input: $input) {
      parentProductVariants {
        id
        productVariantComponents(first: 10) {
          nodes {
            id
            productVariant {
              id
              displayName
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
    "input": [
      {
        "parentProductVariantId": "gid://shopify/ProductVariant/799757249",
        "productVariantRelationshipsToRemove": [
          "gid://shopify/ProductVariant/149896808"
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
  "query": "mutation RemoveABundleComponent($input: [ProductVariantRelationshipUpdateInput!]!) { productVariantRelationshipBulkUpdate(input: $input) { parentProductVariants { id productVariantComponents(first: 10) { nodes { id productVariant { id displayName } } } } userErrors { code field message } } }",
   "variables": {
      "input": [
        {
          "parentProductVariantId": "gid://shopify/ProductVariant/799757249",
          "productVariantRelationshipsToRemove": [
            "gid://shopify/ProductVariant/149896808"
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
    mutation RemoveABundleComponent($input: [ProductVariantRelationshipUpdateInput!]!) {
      productVariantRelationshipBulkUpdate(input: $input) {
        parentProductVariants {
          id
          productVariantComponents(first: 10) {
            nodes {
              id
              productVariant {
                id
                displayName
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
          "input": [
              {
                  "parentProductVariantId": "gid://shopify/ProductVariant/799757249",
                  "productVariantRelationshipsToRemove": [
                      "gid://shopify/ProductVariant/149896808"
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
    mutation RemoveABundleComponent($input: [ProductVariantRelationshipUpdateInput!]!) {
      productVariantRelationshipBulkUpdate(input: $input) {
        parentProductVariants {
          id
          productVariantComponents(first: 10) {
            nodes {
              id
              productVariant {
                id
                displayName
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
    "input": [
      {
        "parentProductVariantId": "gid://shopify/ProductVariant/799757249",
        "productVariantRelationshipsToRemove": [
          "gid://shopify/ProductVariant/149896808"
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
      "query": `mutation RemoveABundleComponent($input: [ProductVariantRelationshipUpdateInput!]!) {
        productVariantRelationshipBulkUpdate(input: $input) {
          parentProductVariants {
            id
            productVariantComponents(first: 10) {
              nodes {
                id
                productVariant {
                  id
                  displayName
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
          "input": [
              {
                  "parentProductVariantId": "gid://shopify/ProductVariant/799757249",
                  "productVariantRelationshipsToRemove": [
                      "gid://shopify/ProductVariant/149896808"
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
  'mutation RemoveABundleComponent($input: [ProductVariantRelationshipUpdateInput!]!) {
    productVariantRelationshipBulkUpdate(input: $input) {
      parentProductVariants {
        id
        productVariantComponents(first: 10) {
          nodes {
            id
            productVariant {
              id
              displayName
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
    "input": [
      {
        "parentProductVariantId": "gid://shopify/ProductVariant/799757249",
        "productVariantRelationshipsToRemove": [
          "gid://shopify/ProductVariant/149896808"
        ]
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "productVariantRelationshipBulkUpdate": {
      "parentProductVariants": [
        {
          "id": "gid://shopify/ProductVariant/799757249",
          "productVariantComponents": {
            "nodes": [
              {
                "id": "gid://shopify/ProductVariantComponent/636669297",
                "productVariant": {
                  "id": "gid://shopify/ProductVariant/709406719",
                  "displayName": "Composite_Sauce_Pack - component_product_variant_classic_garlic_sauce"
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

* ### Remove all product variant components of a bundle

  #### Description

  Removes all the product variant relationships associated with a variant.

  #### Query

  ```graphql
  mutation RemoveAllBundleComponents($input: [ProductVariantRelationshipUpdateInput!]!) {
    productVariantRelationshipBulkUpdate(input: $input) {
      parentProductVariants {
        id
        productVariantComponents(first: 10) {
          nodes {
            id
            productVariant {
              id
              displayName
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
    "input": [
      {
        "parentProductVariantId": "gid://shopify/ProductVariant/799757249",
        "removeAllProductVariantRelationships": true
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
  "query": "mutation RemoveAllBundleComponents($input: [ProductVariantRelationshipUpdateInput!]!) { productVariantRelationshipBulkUpdate(input: $input) { parentProductVariants { id productVariantComponents(first: 10) { nodes { id productVariant { id displayName } } } } userErrors { code field message } } }",
   "variables": {
      "input": [
        {
          "parentProductVariantId": "gid://shopify/ProductVariant/799757249",
          "removeAllProductVariantRelationships": true
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
    mutation RemoveAllBundleComponents($input: [ProductVariantRelationshipUpdateInput!]!) {
      productVariantRelationshipBulkUpdate(input: $input) {
        parentProductVariants {
          id
          productVariantComponents(first: 10) {
            nodes {
              id
              productVariant {
                id
                displayName
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
          "input": [
              {
                  "parentProductVariantId": "gid://shopify/ProductVariant/799757249",
                  "removeAllProductVariantRelationships": true
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
    mutation RemoveAllBundleComponents($input: [ProductVariantRelationshipUpdateInput!]!) {
      productVariantRelationshipBulkUpdate(input: $input) {
        parentProductVariants {
          id
          productVariantComponents(first: 10) {
            nodes {
              id
              productVariant {
                id
                displayName
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
    "input": [
      {
        "parentProductVariantId": "gid://shopify/ProductVariant/799757249",
        "removeAllProductVariantRelationships": true
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
      "query": `mutation RemoveAllBundleComponents($input: [ProductVariantRelationshipUpdateInput!]!) {
        productVariantRelationshipBulkUpdate(input: $input) {
          parentProductVariants {
            id
            productVariantComponents(first: 10) {
              nodes {
                id
                productVariant {
                  id
                  displayName
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
          "input": [
              {
                  "parentProductVariantId": "gid://shopify/ProductVariant/799757249",
                  "removeAllProductVariantRelationships": true
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
  'mutation RemoveAllBundleComponents($input: [ProductVariantRelationshipUpdateInput!]!) {
    productVariantRelationshipBulkUpdate(input: $input) {
      parentProductVariants {
        id
        productVariantComponents(first: 10) {
          nodes {
            id
            productVariant {
              id
              displayName
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
    "input": [
      {
        "parentProductVariantId": "gid://shopify/ProductVariant/799757249",
        "removeAllProductVariantRelationships": true
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "productVariantRelationshipBulkUpdate": {
      "parentProductVariants": [
        {
          "id": "gid://shopify/ProductVariant/799757249",
          "productVariantComponents": {
            "nodes": []
          }
        }
      ],
      "userErrors": []
    }
  }
  ```

* ### Update a product variant relationship

  #### Description

  Updates the quantity of a bundle component.

  #### Query

  ```graphql
  mutation UpdateBundleComponent($input: [ProductVariantRelationshipUpdateInput!]!) {
    productVariantRelationshipBulkUpdate(input: $input) {
      parentProductVariants {
        id
        productVariantComponents(first: 10) {
          nodes {
            id
            productVariant {
              id
              displayName
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
    "input": [
      {
        "parentProductVariantId": "gid://shopify/ProductVariant/799757249",
        "productVariantRelationshipsToUpdate": [
          {
            "id": "gid://shopify/ProductVariant/149896808",
            "quantity": 33
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
  "query": "mutation UpdateBundleComponent($input: [ProductVariantRelationshipUpdateInput!]!) { productVariantRelationshipBulkUpdate(input: $input) { parentProductVariants { id productVariantComponents(first: 10) { nodes { id productVariant { id displayName } } } } userErrors { code field message } } }",
   "variables": {
      "input": [
        {
          "parentProductVariantId": "gid://shopify/ProductVariant/799757249",
          "productVariantRelationshipsToUpdate": [
            {
              "id": "gid://shopify/ProductVariant/149896808",
              "quantity": 33
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
    mutation UpdateBundleComponent($input: [ProductVariantRelationshipUpdateInput!]!) {
      productVariantRelationshipBulkUpdate(input: $input) {
        parentProductVariants {
          id
          productVariantComponents(first: 10) {
            nodes {
              id
              productVariant {
                id
                displayName
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
          "input": [
              {
                  "parentProductVariantId": "gid://shopify/ProductVariant/799757249",
                  "productVariantRelationshipsToUpdate": [
                      {
                          "id": "gid://shopify/ProductVariant/149896808",
                          "quantity": 33
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
    mutation UpdateBundleComponent($input: [ProductVariantRelationshipUpdateInput!]!) {
      productVariantRelationshipBulkUpdate(input: $input) {
        parentProductVariants {
          id
          productVariantComponents(first: 10) {
            nodes {
              id
              productVariant {
                id
                displayName
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
    "input": [
      {
        "parentProductVariantId": "gid://shopify/ProductVariant/799757249",
        "productVariantRelationshipsToUpdate": [
          {
            "id": "gid://shopify/ProductVariant/149896808",
            "quantity": 33
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
      "query": `mutation UpdateBundleComponent($input: [ProductVariantRelationshipUpdateInput!]!) {
        productVariantRelationshipBulkUpdate(input: $input) {
          parentProductVariants {
            id
            productVariantComponents(first: 10) {
              nodes {
                id
                productVariant {
                  id
                  displayName
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
          "input": [
              {
                  "parentProductVariantId": "gid://shopify/ProductVariant/799757249",
                  "productVariantRelationshipsToUpdate": [
                      {
                          "id": "gid://shopify/ProductVariant/149896808",
                          "quantity": 33
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
  'mutation UpdateBundleComponent($input: [ProductVariantRelationshipUpdateInput!]!) {
    productVariantRelationshipBulkUpdate(input: $input) {
      parentProductVariants {
        id
        productVariantComponents(first: 10) {
          nodes {
            id
            productVariant {
              id
              displayName
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
    "input": [
      {
        "parentProductVariantId": "gid://shopify/ProductVariant/799757249",
        "productVariantRelationshipsToUpdate": [
          {
            "id": "gid://shopify/ProductVariant/149896808",
            "quantity": 33
          }
        ]
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "productVariantRelationshipBulkUpdate": {
      "parentProductVariants": [
        {
          "id": "gid://shopify/ProductVariant/799757249",
          "productVariantComponents": {
            "nodes": [
              {
                "id": "gid://shopify/ProductVariantComponent/477596995",
                "productVariant": {
                  "id": "gid://shopify/ProductVariant/149896808",
                  "displayName": "Composite_Sauce_Pack - component_product_variant_classic_hot_sauce"
                }
              },
              {
                "id": "gid://shopify/ProductVariantComponent/636669297",
                "productVariant": {
                  "id": "gid://shopify/ProductVariant/709406719",
                  "displayName": "Composite_Sauce_Pack - component_product_variant_classic_garlic_sauce"
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

* ### productVariantRelationshipBulkUpdate reference
