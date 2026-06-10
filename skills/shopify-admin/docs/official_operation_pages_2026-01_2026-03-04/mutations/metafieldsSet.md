---
title: metafieldsSet - GraphQL Admin
description: >-
  Sets metafield values. Metafield values will be set regardless if they were
  previously created or not.


  Allows a maximum of 25 metafields to be set at a time, with a maximum total
  request payload size of 10MB.


  This operation is atomic, meaning no changes are persisted if an error is
  encountered.


  As of `2024-07`, this operation supports compare-and-set functionality to
  better handle concurrent requests.

  If `compareDigest` is set for any metafield, the mutation will only set that
  metafield if the persisted metafield value matches the digest used on
  `compareDigest`.

  If the metafield doesn't exist yet, but you want to guarantee that the
  operation will run in a safe manner, set `compareDigest` to `null`.

  The `compareDigest` value can be acquired by querying the metafield object and
  selecting `compareDigest` as a field.

  If the `compareDigest` value does not match the digest for the persisted
  value, the mutation will return an error.

  You can opt out of write guarantees by not sending `compareDigest` in the
  request.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/metafieldsSet'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/metafieldsSet.md'
---

# metafields​Set

mutation

Requires the same access level needed to mutate the owner resource. For instance, if you want to set a metafield on a product, you need the same permissions as you would need to mutate a product.

Sets metafield values. Metafield values will be set regardless if they were previously created or not.

Allows a maximum of 25 metafields to be set at a time, with a maximum total request payload size of 10MB.

This operation is atomic, meaning no changes are persisted if an error is encountered.

As of `2024-07`, this operation supports compare-and-set functionality to better handle concurrent requests. If `compareDigest` is set for any metafield, the mutation will only set that metafield if the persisted metafield value matches the digest used on `compareDigest`. If the metafield doesn't exist yet, but you want to guarantee that the operation will run in a safe manner, set `compareDigest` to `null`. The `compareDigest` value can be acquired by querying the metafield object and selecting `compareDigest` as a field. If the `compareDigest` value does not match the digest for the persisted value, the mutation will return an error. You can opt out of write guarantees by not sending `compareDigest` in the request.

## Arguments

* metafields

  [\[Metafields​Set​Input!\]!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/MetafieldsSetInput)

  required

  The list of metafield values to set. Maximum of 25.

***

## Metafields​Set​Payload returns

* metafields

  [\[Metafield!\]](https://shopify.dev/docs/api/admin-graphql/latest/objects/Metafield)

  The list of metafields that were set.

* user​Errors

  [\[Metafields​Set​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetafieldsSetUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create a metafield

  #### Query

  ```graphql
  mutation MetafieldsSet($metafields: [MetafieldsSetInput!]!) {
    metafieldsSet(metafields: $metafields) {
      metafields {
        key
        namespace
        value
        createdAt
        updatedAt
      }
      userErrors {
        field
        message
        code
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "metafields": [
      {
        "key": "example_key",
        "namespace": "example_namespace",
        "ownerId": "gid://shopify/Product/20995642",
        "type": "single_line_text_field",
        "value": "Example Value"
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
  "query": "mutation MetafieldsSet($metafields: [MetafieldsSetInput!]!) { metafieldsSet(metafields: $metafields) { metafields { key namespace value createdAt updatedAt } userErrors { field message code } } }",
   "variables": {
      "metafields": [
        {
          "key": "example_key",
          "namespace": "example_namespace",
          "ownerId": "gid://shopify/Product/20995642",
          "type": "single_line_text_field",
          "value": "Example Value"
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
    mutation MetafieldsSet($metafields: [MetafieldsSetInput!]!) {
      metafieldsSet(metafields: $metafields) {
        metafields {
          key
          namespace
          value
          createdAt
          updatedAt
        }
        userErrors {
          field
          message
          code
        }
      }
    }`,
    {
      variables: {
          "metafields": [
              {
                  "key": "example_key",
                  "namespace": "example_namespace",
                  "ownerId": "gid://shopify/Product/20995642",
                  "type": "single_line_text_field",
                  "value": "Example Value"
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
    mutation MetafieldsSet($metafields: [MetafieldsSetInput!]!) {
      metafieldsSet(metafields: $metafields) {
        metafields {
          key
          namespace
          value
          createdAt
          updatedAt
        }
        userErrors {
          field
          message
          code
        }
      }
    }
  QUERY

  variables = {
    "metafields": [
      {
        "key": "example_key",
        "namespace": "example_namespace",
        "ownerId": "gid://shopify/Product/20995642",
        "type": "single_line_text_field",
        "value": "Example Value"
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
      "query": `mutation MetafieldsSet($metafields: [MetafieldsSetInput!]!) {
        metafieldsSet(metafields: $metafields) {
          metafields {
            key
            namespace
            value
            createdAt
            updatedAt
          }
          userErrors {
            field
            message
            code
          }
        }
      }`,
      "variables": {
          "metafields": [
              {
                  "key": "example_key",
                  "namespace": "example_namespace",
                  "ownerId": "gid://shopify/Product/20995642",
                  "type": "single_line_text_field",
                  "value": "Example Value"
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
  'mutation MetafieldsSet($metafields: [MetafieldsSetInput!]!) {
    metafieldsSet(metafields: $metafields) {
      metafields {
        key
        namespace
        value
        createdAt
        updatedAt
      }
      userErrors {
        field
        message
        code
      }
    }
  }' \
  --variables \
  '{
    "metafields": [
      {
        "key": "example_key",
        "namespace": "example_namespace",
        "ownerId": "gid://shopify/Product/20995642",
        "type": "single_line_text_field",
        "value": "Example Value"
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "metafieldsSet": {
      "metafields": [
        {
          "key": "example_key",
          "namespace": "example_namespace",
          "value": "Example Value",
          "createdAt": "2024-11-18T21:40:28Z",
          "updatedAt": "2024-11-18T21:40:28Z"
        }
      ],
      "userErrors": []
    }
  }
  ```

* ### Creating and updating metafields

  #### Description

  Create and update operations are combined in the \`metafieldSet\` mutation. The following example shows you how to create one new metafield, \`key: "manufactured"\`, and update an existing metafield, \`key: "materials"\` in one mutation.

  #### Query

  ```graphql
  mutation MetafieldsSet($metafields: [MetafieldsSetInput!]!) {
    metafieldsSet(metafields: $metafields) {
      metafields {
        key
        namespace
        value
        createdAt
        updatedAt
      }
      userErrors {
        field
        message
        code
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "metafields": [
      {
        "key": "materials",
        "namespace": "my_fields",
        "ownerId": "gid://shopify/Product/20995642",
        "type": "multi_line_text_field",
        "value": "95% Cotton\n5% Spandex"
      },
      {
        "key": "manufactured",
        "namespace": "my_fields",
        "ownerId": "gid://shopify/Product/20995642",
        "type": "single_line_text_field",
        "value": "Made in Canada"
      },
      {
        "key": "product_description",
        "namespace": "custom",
        "ownerId": "gid://shopify/Product/20995642",
        "type": "rich_text_field",
        "value": "{\"type\":\"root\",\"children\":[{\"type\":\"paragraph\",\"children\":[{\"type\":\"text\",\"value\":\"This is italicized text and \",\"italic\":true},{\"url\":\"https:\\/\\/example.com\",\"title\":\"Link to example.com\",\"type\":\"link\",\"children\":[{\"type\":\"text\",\"value\":\"a bolded hyperlink\",\"bold\":true}]}]}]}"
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
  "query": "mutation MetafieldsSet($metafields: [MetafieldsSetInput!]!) { metafieldsSet(metafields: $metafields) { metafields { key namespace value createdAt updatedAt } userErrors { field message code } } }",
   "variables": {
      "metafields": [
        {
          "key": "materials",
          "namespace": "my_fields",
          "ownerId": "gid://shopify/Product/20995642",
          "type": "multi_line_text_field",
          "value": "95% Cotton\n5% Spandex"
        },
        {
          "key": "manufactured",
          "namespace": "my_fields",
          "ownerId": "gid://shopify/Product/20995642",
          "type": "single_line_text_field",
          "value": "Made in Canada"
        },
        {
          "key": "product_description",
          "namespace": "custom",
          "ownerId": "gid://shopify/Product/20995642",
          "type": "rich_text_field",
          "value": "{\"type\":\"root\",\"children\":[{\"type\":\"paragraph\",\"children\":[{\"type\":\"text\",\"value\":\"This is italicized text and \",\"italic\":true},{\"url\":\"https:\\/\\/example.com\",\"title\":\"Link to example.com\",\"type\":\"link\",\"children\":[{\"type\":\"text\",\"value\":\"a bolded hyperlink\",\"bold\":true}]}]}]}"
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
    mutation MetafieldsSet($metafields: [MetafieldsSetInput!]!) {
      metafieldsSet(metafields: $metafields) {
        metafields {
          key
          namespace
          value
          createdAt
          updatedAt
        }
        userErrors {
          field
          message
          code
        }
      }
    }`,
    {
      variables: {
          "metafields": [
              {
                  "key": "materials",
                  "namespace": "my_fields",
                  "ownerId": "gid://shopify/Product/20995642",
                  "type": "multi_line_text_field",
                  "value": "95% Cotton\n5% Spandex"
              },
              {
                  "key": "manufactured",
                  "namespace": "my_fields",
                  "ownerId": "gid://shopify/Product/20995642",
                  "type": "single_line_text_field",
                  "value": "Made in Canada"
              },
              {
                  "key": "product_description",
                  "namespace": "custom",
                  "ownerId": "gid://shopify/Product/20995642",
                  "type": "rich_text_field",
                  "value": "{\"type\":\"root\",\"children\":[{\"type\":\"paragraph\",\"children\":[{\"type\":\"text\",\"value\":\"This is italicized text and \",\"italic\":true},{\"url\":\"https:\\/\\/example.com\",\"title\":\"Link to example.com\",\"type\":\"link\",\"children\":[{\"type\":\"text\",\"value\":\"a bolded hyperlink\",\"bold\":true}]}]}]}"
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
    mutation MetafieldsSet($metafields: [MetafieldsSetInput!]!) {
      metafieldsSet(metafields: $metafields) {
        metafields {
          key
          namespace
          value
          createdAt
          updatedAt
        }
        userErrors {
          field
          message
          code
        }
      }
    }
  QUERY

  variables = {
    "metafields": [
      {
        "key": "materials",
        "namespace": "my_fields",
        "ownerId": "gid://shopify/Product/20995642",
        "type": "multi_line_text_field",
        "value": "95% Cotton\n5% Spandex"
      },
      {
        "key": "manufactured",
        "namespace": "my_fields",
        "ownerId": "gid://shopify/Product/20995642",
        "type": "single_line_text_field",
        "value": "Made in Canada"
      },
      {
        "key": "product_description",
        "namespace": "custom",
        "ownerId": "gid://shopify/Product/20995642",
        "type": "rich_text_field",
        "value": "{\"type\":\"root\",\"children\":[{\"type\":\"paragraph\",\"children\":[{\"type\":\"text\",\"value\":\"This is italicized text and \",\"italic\":true},{\"url\":\"https:\\/\\/example.com\",\"title\":\"Link to example.com\",\"type\":\"link\",\"children\":[{\"type\":\"text\",\"value\":\"a bolded hyperlink\",\"bold\":true}]}]}]}"
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
      "query": `mutation MetafieldsSet($metafields: [MetafieldsSetInput!]!) {
        metafieldsSet(metafields: $metafields) {
          metafields {
            key
            namespace
            value
            createdAt
            updatedAt
          }
          userErrors {
            field
            message
            code
          }
        }
      }`,
      "variables": {
          "metafields": [
              {
                  "key": "materials",
                  "namespace": "my_fields",
                  "ownerId": "gid://shopify/Product/20995642",
                  "type": "multi_line_text_field",
                  "value": "95% Cotton\n5% Spandex"
              },
              {
                  "key": "manufactured",
                  "namespace": "my_fields",
                  "ownerId": "gid://shopify/Product/20995642",
                  "type": "single_line_text_field",
                  "value": "Made in Canada"
              },
              {
                  "key": "product_description",
                  "namespace": "custom",
                  "ownerId": "gid://shopify/Product/20995642",
                  "type": "rich_text_field",
                  "value": "{\"type\":\"root\",\"children\":[{\"type\":\"paragraph\",\"children\":[{\"type\":\"text\",\"value\":\"This is italicized text and \",\"italic\":true},{\"url\":\"https:\\/\\/example.com\",\"title\":\"Link to example.com\",\"type\":\"link\",\"children\":[{\"type\":\"text\",\"value\":\"a bolded hyperlink\",\"bold\":true}]}]}]}"
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
  'mutation MetafieldsSet($metafields: [MetafieldsSetInput!]!) {
    metafieldsSet(metafields: $metafields) {
      metafields {
        key
        namespace
        value
        createdAt
        updatedAt
      }
      userErrors {
        field
        message
        code
      }
    }
  }' \
  --variables \
  '{
    "metafields": [
      {
        "key": "materials",
        "namespace": "my_fields",
        "ownerId": "gid://shopify/Product/20995642",
        "type": "multi_line_text_field",
        "value": "95% Cotton\n5% Spandex"
      },
      {
        "key": "manufactured",
        "namespace": "my_fields",
        "ownerId": "gid://shopify/Product/20995642",
        "type": "single_line_text_field",
        "value": "Made in Canada"
      },
      {
        "key": "product_description",
        "namespace": "custom",
        "ownerId": "gid://shopify/Product/20995642",
        "type": "rich_text_field",
        "value": "{\"type\":\"root\",\"children\":[{\"type\":\"paragraph\",\"children\":[{\"type\":\"text\",\"value\":\"This is italicized text and \",\"italic\":true},{\"url\":\"https:\\/\\/example.com\",\"title\":\"Link to example.com\",\"type\":\"link\",\"children\":[{\"type\":\"text\",\"value\":\"a bolded hyperlink\",\"bold\":true}]}]}]}"
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "metafieldsSet": {
      "metafields": [
        {
          "key": "materials",
          "namespace": "my_fields",
          "value": "95% Cotton\n5% Spandex",
          "createdAt": "2024-11-13T20:04:12Z",
          "updatedAt": "2024-11-13T20:04:13Z"
        },
        {
          "key": "manufactured",
          "namespace": "my_fields",
          "value": "Made in Canada",
          "createdAt": "2024-11-13T20:04:13Z",
          "updatedAt": "2024-11-13T20:04:13Z"
        },
        {
          "key": "product_description",
          "namespace": "custom",
          "value": "{\"type\":\"root\",\"children\":[{\"type\":\"paragraph\",\"children\":[{\"type\":\"text\",\"value\":\"This is italicized text and \",\"italic\":true},{\"url\":\"https://example.com\",\"title\":\"Link to example.com\",\"type\":\"link\",\"children\":[{\"type\":\"text\",\"value\":\"a bolded hyperlink\",\"bold\":true}]}]}]}",
          "createdAt": "2024-11-13T20:04:13Z",
          "updatedAt": "2024-11-13T20:04:13Z"
        }
      ],
      "userErrors": []
    }
  }
  ```

* ### Creating and updating metafields using compare-and-swap (CAS)

  #### Description

  Create and update operations are combined in the \`metafieldSet\` mutation. The following example shows you how to create one new metafield, \`key: "manufactured"\`, and update an existing metafield, \`key: "materials"\` in one mutation in a safer way with compare-and-swap (CAS) through the \`compareDigest\` field.

  #### Query

  ```graphql
  mutation MetafieldsSet($metafields: [MetafieldsSetInput!]!) {
    metafieldsSet(metafields: $metafields) {
      metafields {
        key
        namespace
        value
        compareDigest
        createdAt
        updatedAt
      }
      userErrors {
        field
        message
        code
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "metafields": [
      {
        "key": "materials",
        "namespace": "my_fields",
        "ownerId": "gid://shopify/Product/20995642",
        "type": "multi_line_text_field",
        "value": "95% Cotton\n5% Spandex",
        "compareDigest": "fd6b73725c9e83da2d2bcfaf90b27305b9058a48a1565639aa00d718d4caf8e8"
      },
      {
        "key": "manufactured",
        "namespace": "my_fields",
        "ownerId": "gid://shopify/Product/20995642",
        "type": "single_line_text_field",
        "value": "Made in Canada",
        "compareDigest": null
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
  "query": "mutation MetafieldsSet($metafields: [MetafieldsSetInput!]!) { metafieldsSet(metafields: $metafields) { metafields { key namespace value compareDigest createdAt updatedAt } userErrors { field message code } } }",
   "variables": {
      "metafields": [
        {
          "key": "materials",
          "namespace": "my_fields",
          "ownerId": "gid://shopify/Product/20995642",
          "type": "multi_line_text_field",
          "value": "95% Cotton\n5% Spandex",
          "compareDigest": "fd6b73725c9e83da2d2bcfaf90b27305b9058a48a1565639aa00d718d4caf8e8"
        },
        {
          "key": "manufactured",
          "namespace": "my_fields",
          "ownerId": "gid://shopify/Product/20995642",
          "type": "single_line_text_field",
          "value": "Made in Canada",
          "compareDigest": null
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
    mutation MetafieldsSet($metafields: [MetafieldsSetInput!]!) {
      metafieldsSet(metafields: $metafields) {
        metafields {
          key
          namespace
          value
          compareDigest
          createdAt
          updatedAt
        }
        userErrors {
          field
          message
          code
        }
      }
    }`,
    {
      variables: {
          "metafields": [
              {
                  "key": "materials",
                  "namespace": "my_fields",
                  "ownerId": "gid://shopify/Product/20995642",
                  "type": "multi_line_text_field",
                  "value": "95% Cotton\n5% Spandex",
                  "compareDigest": "fd6b73725c9e83da2d2bcfaf90b27305b9058a48a1565639aa00d718d4caf8e8"
              },
              {
                  "key": "manufactured",
                  "namespace": "my_fields",
                  "ownerId": "gid://shopify/Product/20995642",
                  "type": "single_line_text_field",
                  "value": "Made in Canada",
                  "compareDigest": null
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
    mutation MetafieldsSet($metafields: [MetafieldsSetInput!]!) {
      metafieldsSet(metafields: $metafields) {
        metafields {
          key
          namespace
          value
          compareDigest
          createdAt
          updatedAt
        }
        userErrors {
          field
          message
          code
        }
      }
    }
  QUERY

  variables = {
    "metafields": [
      {
        "key": "materials",
        "namespace": "my_fields",
        "ownerId": "gid://shopify/Product/20995642",
        "type": "multi_line_text_field",
        "value": "95% Cotton\n5% Spandex",
        "compareDigest": "fd6b73725c9e83da2d2bcfaf90b27305b9058a48a1565639aa00d718d4caf8e8"
      },
      {
        "key": "manufactured",
        "namespace": "my_fields",
        "ownerId": "gid://shopify/Product/20995642",
        "type": "single_line_text_field",
        "value": "Made in Canada",
        "compareDigest": null
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
      "query": `mutation MetafieldsSet($metafields: [MetafieldsSetInput!]!) {
        metafieldsSet(metafields: $metafields) {
          metafields {
            key
            namespace
            value
            compareDigest
            createdAt
            updatedAt
          }
          userErrors {
            field
            message
            code
          }
        }
      }`,
      "variables": {
          "metafields": [
              {
                  "key": "materials",
                  "namespace": "my_fields",
                  "ownerId": "gid://shopify/Product/20995642",
                  "type": "multi_line_text_field",
                  "value": "95% Cotton\n5% Spandex",
                  "compareDigest": "fd6b73725c9e83da2d2bcfaf90b27305b9058a48a1565639aa00d718d4caf8e8"
              },
              {
                  "key": "manufactured",
                  "namespace": "my_fields",
                  "ownerId": "gid://shopify/Product/20995642",
                  "type": "single_line_text_field",
                  "value": "Made in Canada",
                  "compareDigest": null
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
  'mutation MetafieldsSet($metafields: [MetafieldsSetInput!]!) {
    metafieldsSet(metafields: $metafields) {
      metafields {
        key
        namespace
        value
        compareDigest
        createdAt
        updatedAt
      }
      userErrors {
        field
        message
        code
      }
    }
  }' \
  --variables \
  '{
    "metafields": [
      {
        "key": "materials",
        "namespace": "my_fields",
        "ownerId": "gid://shopify/Product/20995642",
        "type": "multi_line_text_field",
        "value": "95% Cotton\n5% Spandex",
        "compareDigest": "fd6b73725c9e83da2d2bcfaf90b27305b9058a48a1565639aa00d718d4caf8e8"
      },
      {
        "key": "manufactured",
        "namespace": "my_fields",
        "ownerId": "gid://shopify/Product/20995642",
        "type": "single_line_text_field",
        "value": "Made in Canada",
        "compareDigest": null
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "metafieldsSet": {
      "metafields": [
        {
          "key": "materials",
          "namespace": "my_fields",
          "value": "95% Cotton\n5% Spandex",
          "compareDigest": "8164fa2a8e66a6bb54181ac0c095375c701ae276e801f43efa16ea7be516f678",
          "createdAt": "2024-11-13T20:03:43Z",
          "updatedAt": "2024-11-13T20:04:12Z"
        },
        {
          "key": "manufactured",
          "namespace": "my_fields",
          "value": "Made in Canada",
          "compareDigest": "f8c307f7c79ec624884e1c71640ee3e6441cf7bb4589b9e3cc551ab3e3b95ff1",
          "createdAt": "2024-11-13T20:04:12Z",
          "updatedAt": "2024-11-13T20:04:12Z"
        }
      ],
      "userErrors": []
    }
  }
  ```

* ### Updates a metafield

  #### Query

  ```graphql
  mutation MetafieldsSet($metafields: [MetafieldsSetInput!]!) {
    metafieldsSet(metafields: $metafields) {
      metafields {
        key
        namespace
        value
        createdAt
        updatedAt
      }
      userErrors {
        field
        message
        code
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "metafields": [
      {
        "key": "materials",
        "namespace": "my_fields",
        "ownerId": "gid://shopify/Product/20995642",
        "type": "multi_line_text_field",
        "value": "95% Cotton\n5% Spandex"
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
  "query": "mutation MetafieldsSet($metafields: [MetafieldsSetInput!]!) { metafieldsSet(metafields: $metafields) { metafields { key namespace value createdAt updatedAt } userErrors { field message code } } }",
   "variables": {
      "metafields": [
        {
          "key": "materials",
          "namespace": "my_fields",
          "ownerId": "gid://shopify/Product/20995642",
          "type": "multi_line_text_field",
          "value": "95% Cotton\n5% Spandex"
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
    mutation MetafieldsSet($metafields: [MetafieldsSetInput!]!) {
      metafieldsSet(metafields: $metafields) {
        metafields {
          key
          namespace
          value
          createdAt
          updatedAt
        }
        userErrors {
          field
          message
          code
        }
      }
    }`,
    {
      variables: {
          "metafields": [
              {
                  "key": "materials",
                  "namespace": "my_fields",
                  "ownerId": "gid://shopify/Product/20995642",
                  "type": "multi_line_text_field",
                  "value": "95% Cotton\n5% Spandex"
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
    mutation MetafieldsSet($metafields: [MetafieldsSetInput!]!) {
      metafieldsSet(metafields: $metafields) {
        metafields {
          key
          namespace
          value
          createdAt
          updatedAt
        }
        userErrors {
          field
          message
          code
        }
      }
    }
  QUERY

  variables = {
    "metafields": [
      {
        "key": "materials",
        "namespace": "my_fields",
        "ownerId": "gid://shopify/Product/20995642",
        "type": "multi_line_text_field",
        "value": "95% Cotton\n5% Spandex"
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
      "query": `mutation MetafieldsSet($metafields: [MetafieldsSetInput!]!) {
        metafieldsSet(metafields: $metafields) {
          metafields {
            key
            namespace
            value
            createdAt
            updatedAt
          }
          userErrors {
            field
            message
            code
          }
        }
      }`,
      "variables": {
          "metafields": [
              {
                  "key": "materials",
                  "namespace": "my_fields",
                  "ownerId": "gid://shopify/Product/20995642",
                  "type": "multi_line_text_field",
                  "value": "95% Cotton\n5% Spandex"
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
  'mutation MetafieldsSet($metafields: [MetafieldsSetInput!]!) {
    metafieldsSet(metafields: $metafields) {
      metafields {
        key
        namespace
        value
        createdAt
        updatedAt
      }
      userErrors {
        field
        message
        code
      }
    }
  }' \
  --variables \
  '{
    "metafields": [
      {
        "key": "materials",
        "namespace": "my_fields",
        "ownerId": "gid://shopify/Product/20995642",
        "type": "multi_line_text_field",
        "value": "95% Cotton\n5% Spandex"
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "metafieldsSet": {
      "metafields": [
        {
          "key": "materials",
          "namespace": "my_fields",
          "value": "95% Cotton\n5% Spandex",
          "createdAt": "2024-11-18T21:40:55Z",
          "updatedAt": "2024-11-18T21:40:55Z"
        }
      ],
      "userErrors": []
    }
  }
  ```

* ### metafieldsSet reference
