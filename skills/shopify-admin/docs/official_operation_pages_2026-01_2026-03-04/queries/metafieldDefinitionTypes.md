---
title: metafieldDefinitionTypes - GraphQL Admin
description: >-
  The available metafield types that you can use when creating
  [`MetafieldDefinition`](/docs/api/admin-graphql/2026-01/objects/MetafieldDefinition)
  objects. Each type specifies what kind of data it stores (such as boolean,
  color, date, or references), its category, and which validations it supports.


  For a list of supported types and their capabilities, refer to the [metafield
  types documentation](https://shopify.dev/docs/apps/metafields/types).
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/metafieldDefinitionTypes
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/metafieldDefinitionTypes.md
---

# metafield​Definition​Types

query

The available metafield types that you can use when creating [`MetafieldDefinition`](https://shopify.dev/docs/api/admin-graphql/2026-01/objects/MetafieldDefinition) objects. Each type specifies what kind of data it stores (such as boolean, color, date, or references), its category, and which validations it supports.

For a list of supported types and their capabilities, refer to the [metafield types documentation](https://shopify.dev/docs/apps/metafields/types).

## Possible returns

* Metafield​Definition​Type

  [\[Metafield​Definition​Type!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetafieldDefinitionType)

  A metafield definition type provides basic foundation and validation for a metafield.

  * category

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The category associated with the metafield definition type.

  * name

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The name of the type for the metafield definition. See the list of [supported types](https://shopify.dev/apps/metafields/types).

  * supported​Validations

    [\[Metafield​Definition​Supported​Validation!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetafieldDefinitionSupportedValidation)

    non-null

    The supported validations for a metafield definition type.

  * supports​Definition​Migrations

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether metafields without a definition can be migrated to a definition of this type.

  * value​Type

    [Metafield​Value​Type!](https://shopify.dev/docs/api/admin-graphql/latest/enums/MetafieldValueType)

    non-nullDeprecated

***

## Examples

* ### Fetch all metafield definition types

  #### Description

  Fetch the full list of metafield definition types along with their supported validations.

  #### Query

  ```graphql
  query MetafieldDefinitionTypes {
    metafieldDefinitionTypes {
      category
      name
      supportsDefinitionMigrations
      supportedValidations {
        name
        type
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
  "query": "query MetafieldDefinitionTypes { metafieldDefinitionTypes { category name supportsDefinitionMigrations supportedValidations { name type } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query MetafieldDefinitionTypes {
      metafieldDefinitionTypes {
        category
        name
        supportsDefinitionMigrations
        supportedValidations {
          name
          type
        }
      }
    }`,
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
    query MetafieldDefinitionTypes {
      metafieldDefinitionTypes {
        category
        name
        supportsDefinitionMigrations
        supportedValidations {
          name
          type
        }
      }
    }
  QUERY

  response = client.query(query: query)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: `query MetafieldDefinitionTypes {
      metafieldDefinitionTypes {
        category
        name
        supportsDefinitionMigrations
        supportedValidations {
          name
          type
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query MetafieldDefinitionTypes {
    metafieldDefinitionTypes {
      category
      name
      supportsDefinitionMigrations
      supportedValidations {
        name
        type
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "metafieldDefinitionTypes": [
      {
        "category": "TRUE_FALSE",
        "name": "boolean",
        "supportsDefinitionMigrations": true,
        "supportedValidations": []
      },
      {
        "category": "COLOR",
        "name": "color",
        "supportsDefinitionMigrations": true,
        "supportedValidations": []
      },
      {
        "category": "DATE_TIME",
        "name": "date_time",
        "supportsDefinitionMigrations": true,
        "supportedValidations": [
          {
            "name": "min",
            "type": "date_time"
          },
          {
            "name": "max",
            "type": "date_time"
          }
        ]
      },
      {
        "category": "DATE_TIME",
        "name": "date",
        "supportsDefinitionMigrations": true,
        "supportedValidations": [
          {
            "name": "min",
            "type": "date"
          },
          {
            "name": "max",
            "type": "date"
          }
        ]
      },
      {
        "category": "MEASUREMENT",
        "name": "dimension",
        "supportsDefinitionMigrations": true,
        "supportedValidations": [
          {
            "name": "min",
            "type": "dimension"
          },
          {
            "name": "max",
            "type": "dimension"
          }
        ]
      },
      {
        "category": "JSON",
        "name": "json",
        "supportsDefinitionMigrations": true,
        "supportedValidations": [
          {
            "name": "schema",
            "type": "json"
          }
        ]
      },
      {
        "category": "LANGUAGE",
        "name": "language",
        "supportsDefinitionMigrations": false,
        "supportedValidations": []
      },
      {
        "category": "COLOR",
        "name": "list.color",
        "supportsDefinitionMigrations": false,
        "supportedValidations": [
          {
            "name": "list.min",
            "type": "number_integer"
          },
          {
            "name": "list.max",
            "type": "number_integer"
          }
        ]
      },
      {
        "category": "DATE_TIME",
        "name": "list.date_time",
        "supportsDefinitionMigrations": false,
        "supportedValidations": [
          {
            "name": "min",
            "type": "date_time"
          },
          {
            "name": "max",
            "type": "date_time"
          },
          {
            "name": "list.min",
            "type": "number_integer"
          },
          {
            "name": "list.max",
            "type": "number_integer"
          }
        ]
      },
      {
        "category": "DATE_TIME",
        "name": "list.date",
        "supportsDefinitionMigrations": false,
        "supportedValidations": [
          {
            "name": "min",
            "type": "date"
          },
          {
            "name": "max",
            "type": "date"
          },
          {
            "name": "list.min",
            "type": "number_integer"
          },
          {
            "name": "list.max",
            "type": "number_integer"
          }
        ]
      },
      {
        "category": "MEASUREMENT",
        "name": "list.dimension",
        "supportsDefinitionMigrations": false,
        "supportedValidations": [
          {
            "name": "min",
            "type": "dimension"
          },
          {
            "name": "max",
            "type": "dimension"
          },
          {
            "name": "list.min",
            "type": "number_integer"
          },
          {
            "name": "list.max",
            "type": "number_integer"
          }
        ]
      },
      {
        "category": "NUMBER",
        "name": "list.number_decimal",
        "supportsDefinitionMigrations": false,
        "supportedValidations": [
          {
            "name": "min",
            "type": "number_decimal"
          },
          {
            "name": "max",
            "type": "number_decimal"
          },
          {
            "name": "max_precision",
            "type": "number_integer"
          },
          {
            "name": "list.min",
            "type": "number_integer"
          },
          {
            "name": "list.max",
            "type": "number_integer"
          }
        ]
      },
      {
        "category": "NUMBER",
        "name": "list.number_integer",
        "supportsDefinitionMigrations": false,
        "supportedValidations": [
          {
            "name": "min",
            "type": "number_integer"
          },
          {
            "name": "max",
            "type": "number_integer"
          },
          {
            "name": "list.min",
            "type": "number_integer"
          },
          {
            "name": "list.max",
            "type": "number_integer"
          }
        ]
      },
      {
        "category": "RATING",
        "name": "list.rating",
        "supportsDefinitionMigrations": false,
        "supportedValidations": [
          {
            "name": "scale_min",
            "type": "number_decimal"
          },
          {
            "name": "scale_max",
            "type": "number_decimal"
          },
          {
            "name": "list.min",
            "type": "number_integer"
          },
          {
            "name": "list.max",
            "type": "number_integer"
          }
        ]
      },
      {
        "category": "TEXT",
        "name": "list.single_line_text_field",
        "supportsDefinitionMigrations": false,
        "supportedValidations": [
          {
            "name": "min",
            "type": "number_integer"
          },
          {
            "name": "max",
            "type": "number_integer"
          },
          {
            "name": "regex",
            "type": "single_line_text_field"
          },
          {
            "name": "choices",
            "type": "list.single_line_text_field"
          },
          {
            "name": "list.min",
            "type": "number_integer"
          },
          {
            "name": "list.max",
            "type": "number_integer"
          }
        ]
      },
      {
        "category": "URL",
        "name": "list.url",
        "supportsDefinitionMigrations": false,
        "supportedValidations": [
          {
            "name": "allowed_domains",
            "type": "list.single_line_text_field"
          },
          {
            "name": "list.min",
            "type": "number_integer"
          },
          {
            "name": "list.max",
            "type": "number_integer"
          }
        ]
      },
      {
        "category": "MEASUREMENT",
        "name": "list.volume",
        "supportsDefinitionMigrations": false,
        "supportedValidations": [
          {
            "name": "min",
            "type": "volume"
          },
          {
            "name": "max",
            "type": "volume"
          },
          {
            "name": "list.min",
            "type": "number_integer"
          },
          {
            "name": "list.max",
            "type": "number_integer"
          }
        ]
      },
      {
        "category": "MEASUREMENT",
        "name": "list.weight",
        "supportsDefinitionMigrations": false,
        "supportedValidations": [
          {
            "name": "min",
            "type": "weight"
          },
          {
            "name": "max",
            "type": "weight"
          },
          {
            "name": "list.min",
            "type": "number_integer"
          },
          {
            "name": "list.max",
            "type": "number_integer"
          }
        ]
      },
      {
        "category": "MONEY",
        "name": "money",
        "supportsDefinitionMigrations": false,
        "supportedValidations": []
      },
      {
        "category": "TEXT",
        "name": "multi_line_text_field",
        "supportsDefinitionMigrations": true,
        "supportedValidations": [
          {
            "name": "min",
            "type": "number_integer"
          },
          {
            "name": "max",
            "type": "number_integer"
          },
          {
            "name": "regex",
            "type": "single_line_text_field"
          }
        ]
      },
      {
        "category": "NUMBER",
        "name": "number_decimal",
        "supportsDefinitionMigrations": true,
        "supportedValidations": [
          {
            "name": "min",
            "type": "number_decimal"
          },
          {
            "name": "max",
            "type": "number_decimal"
          },
          {
            "name": "max_precision",
            "type": "number_integer"
          }
        ]
      },
      {
        "category": "NUMBER",
        "name": "number_integer",
        "supportsDefinitionMigrations": true,
        "supportedValidations": [
          {
            "name": "min",
            "type": "number_integer"
          },
          {
            "name": "max",
            "type": "number_integer"
          }
        ]
      },
      {
        "category": "RATING",
        "name": "rating",
        "supportsDefinitionMigrations": true,
        "supportedValidations": [
          {
            "name": "scale_min",
            "type": "number_decimal"
          },
          {
            "name": "scale_max",
            "type": "number_decimal"
          }
        ]
      },
      {
        "category": "TEXT",
        "name": "rich_text_field",
        "supportsDefinitionMigrations": false,
        "supportedValidations": []
      },
      {
        "category": "TEXT",
        "name": "single_line_text_field",
        "supportsDefinitionMigrations": true,
        "supportedValidations": [
          {
            "name": "min",
            "type": "number_integer"
          },
          {
            "name": "max",
            "type": "number_integer"
          },
          {
            "name": "regex",
            "type": "single_line_text_field"
          },
          {
            "name": "choices",
            "type": "list.single_line_text_field"
          }
        ]
      },
      {
        "category": "URL",
        "name": "url",
        "supportsDefinitionMigrations": true,
        "supportedValidations": [
          {
            "name": "allowed_domains",
            "type": "list.single_line_text_field"
          }
        ]
      },
      {
        "category": "LINK",
        "name": "link",
        "supportsDefinitionMigrations": true,
        "supportedValidations": [
          {
            "name": "allowed_domains",
            "type": "list.single_line_text_field"
          }
        ]
      },
      {
        "category": "LINK",
        "name": "list.link",
        "supportsDefinitionMigrations": false,
        "supportedValidations": [
          {
            "name": "allowed_domains",
            "type": "list.single_line_text_field"
          },
          {
            "name": "list.min",
            "type": "number_integer"
          },
          {
            "name": "list.max",
            "type": "number_integer"
          }
        ]
      },
      {
        "category": "MEASUREMENT",
        "name": "volume",
        "supportsDefinitionMigrations": true,
        "supportedValidations": [
          {
            "name": "min",
            "type": "volume"
          },
          {
            "name": "max",
            "type": "volume"
          }
        ]
      },
      {
        "category": "MEASUREMENT",
        "name": "weight",
        "supportsDefinitionMigrations": true,
        "supportedValidations": [
          {
            "name": "min",
            "type": "weight"
          },
          {
            "name": "max",
            "type": "weight"
          }
        ]
      },
      {
        "category": "REFERENCE",
        "name": "company_reference",
        "supportsDefinitionMigrations": false,
        "supportedValidations": []
      },
      {
        "category": "REFERENCE",
        "name": "list.company_reference",
        "supportsDefinitionMigrations": false,
        "supportedValidations": [
          {
            "name": "list.min",
            "type": "number_integer"
          },
          {
            "name": "list.max",
            "type": "number_integer"
          }
        ]
      },
      {
        "category": "REFERENCE",
        "name": "customer_reference",
        "supportsDefinitionMigrations": false,
        "supportedValidations": []
      },
      {
        "category": "REFERENCE",
        "name": "list.customer_reference",
        "supportsDefinitionMigrations": false,
        "supportedValidations": [
          {
            "name": "list.min",
            "type": "number_integer"
          },
          {
            "name": "list.max",
            "type": "number_integer"
          }
        ]
      },
      {
        "category": "REFERENCE",
        "name": "product_reference",
        "supportsDefinitionMigrations": false,
        "supportedValidations": []
      },
      {
        "category": "REFERENCE",
        "name": "list.product_reference",
        "supportsDefinitionMigrations": false,
        "supportedValidations": [
          {
            "name": "list.min",
            "type": "number_integer"
          },
          {
            "name": "list.max",
            "type": "number_integer"
          }
        ]
      },
      {
        "category": "REFERENCE",
        "name": "collection_reference",
        "supportsDefinitionMigrations": false,
        "supportedValidations": []
      },
      {
        "category": "REFERENCE",
        "name": "list.collection_reference",
        "supportsDefinitionMigrations": false,
        "supportedValidations": [
          {
            "name": "list.min",
            "type": "number_integer"
          },
          {
            "name": "list.max",
            "type": "number_integer"
          }
        ]
      },
      {
        "category": "REFERENCE",
        "name": "variant_reference",
        "supportsDefinitionMigrations": false,
        "supportedValidations": []
      },
      {
        "category": "REFERENCE",
        "name": "list.variant_reference",
        "supportsDefinitionMigrations": false,
        "supportedValidations": [
          {
            "name": "list.min",
            "type": "number_integer"
          },
          {
            "name": "list.max",
            "type": "number_integer"
          }
        ]
      },
      {
        "category": "REFERENCE",
        "name": "file_reference",
        "supportsDefinitionMigrations": false,
        "supportedValidations": [
          {
            "name": "file_type_options",
            "type": "list.single_line_text_field"
          }
        ]
      },
      {
        "category": "REFERENCE",
        "name": "list.file_reference",
        "supportsDefinitionMigrations": false,
        "supportedValidations": [
          {
            "name": "file_type_options",
            "type": "list.single_line_text_field"
          },
          {
            "name": "list.min",
            "type": "number_integer"
          },
          {
            "name": "list.max",
            "type": "number_integer"
          }
        ]
      },
      {
        "category": "REFERENCE",
        "name": "product_taxonomy_value_reference",
        "supportsDefinitionMigrations": false,
        "supportedValidations": [
          {
            "name": "product_taxonomy_attribute_handle",
            "type": "single_line_text_field"
          }
        ]
      },
      {
        "category": "REFERENCE",
        "name": "list.product_taxonomy_value_reference",
        "supportsDefinitionMigrations": false,
        "supportedValidations": [
          {
            "name": "product_taxonomy_attribute_handle",
            "type": "single_line_text_field"
          },
          {
            "name": "list.min",
            "type": "number_integer"
          },
          {
            "name": "list.max",
            "type": "number_integer"
          }
        ]
      },
      {
        "category": "REFERENCE",
        "name": "metaobject_reference",
        "supportsDefinitionMigrations": false,
        "supportedValidations": [
          {
            "name": "metaobject_definition_id",
            "type": "single_line_text_field"
          }
        ]
      },
      {
        "category": "REFERENCE",
        "name": "list.metaobject_reference",
        "supportsDefinitionMigrations": false,
        "supportedValidations": [
          {
            "name": "metaobject_definition_id",
            "type": "single_line_text_field"
          },
          {
            "name": "list.min",
            "type": "number_integer"
          },
          {
            "name": "list.max",
            "type": "number_integer"
          }
        ]
      },
      {
        "category": "REFERENCE",
        "name": "mixed_reference",
        "supportsDefinitionMigrations": false,
        "supportedValidations": [
          {
            "name": "metaobject_definition_ids",
            "type": "list.single_line_text_field"
          }
        ]
      },
      {
        "category": "REFERENCE",
        "name": "list.mixed_reference",
        "supportsDefinitionMigrations": false,
        "supportedValidations": [
          {
            "name": "metaobject_definition_ids",
            "type": "list.single_line_text_field"
          },
          {
            "name": "list.min",
            "type": "number_integer"
          },
          {
            "name": "list.max",
            "type": "number_integer"
          }
        ]
      },
      {
        "category": "REFERENCE",
        "name": "page_reference",
        "supportsDefinitionMigrations": false,
        "supportedValidations": []
      },
      {
        "category": "REFERENCE",
        "name": "list.page_reference",
        "supportsDefinitionMigrations": false,
        "supportedValidations": [
          {
            "name": "list.min",
            "type": "number_integer"
          },
          {
            "name": "list.max",
            "type": "number_integer"
          }
        ]
      },
      {
        "category": "REFERENCE",
        "name": "order_reference",
        "supportsDefinitionMigrations": false,
        "supportedValidations": []
      }
    ]
  }
  ```
