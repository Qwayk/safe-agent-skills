---
title: collectionRulesConditions - GraphQL Admin
description: Lists all rules that can be used to create smart collections.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/collectionRulesConditions
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/collectionRulesConditions.md
---

# collection​Rules​Conditions

query

Lists all rules that can be used to create smart collections.

## Possible returns

* Collection​Rule​Conditions

  [\[Collection​Rule​Conditions!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CollectionRuleConditions)

  Defines the available columns and relationships that can be used when creating rules for smart collections. This provides the schema for building automated collection logic based on product attributes.

  For example, merchants can create rules like "product type equals 'Shirts'" or "vendor contains 'Nike'" using the conditions defined in this object to automatically populate collections.

  Use `CollectionRuleConditions` to:

  * Discovering valid field options for smart collection rule interfaces
  * Understanding which conditions are available for automated collections
  * Exploring available product attributes for collection automation
  * Learning about proper field relationships for rule implementation

  The conditions define which product fields can be used in smart collection rules and what types of comparisons are allowed for each field.

  Learn more about [smart collections](https://shopify.dev/docs/api/admin-graphql/latest/objects/Collection).

  * allowed​Relations

    [\[Collection​Rule​Relation!\]!](https://shopify.dev/docs/api/admin-graphql/latest/enums/CollectionRuleRelation)

    non-null

    Allowed relations of the rule.

  * default​Relation

    [Collection​Rule​Relation!](https://shopify.dev/docs/api/admin-graphql/latest/enums/CollectionRuleRelation)

    non-null

    Most commonly used relation for this rule.

  * rule​Object

    [Collection​Rule​Conditions​Rule​Object](https://shopify.dev/docs/api/admin-graphql/latest/unions/CollectionRuleConditionsRuleObject)

    Additional attributes defining the rule.

  * rule​Type

    [Collection​Rule​Column!](https://shopify.dev/docs/api/admin-graphql/latest/enums/CollectionRuleColumn)

    non-null

    Type of the rule.

***

## Examples

* ### Retrieve a list of collection rule conditions

  #### Query

  ```graphql
  query {
    collectionRulesConditions {
      ruleType
      allowedRelations
      defaultRelation
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
  "query": "query { collectionRulesConditions { ruleType allowedRelations defaultRelation } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query {
      collectionRulesConditions {
        ruleType
        allowedRelations
        defaultRelation
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
    query {
      collectionRulesConditions {
        ruleType
        allowedRelations
        defaultRelation
      }
    }
  QUERY

  response = client.query(query: query)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: `query {
      collectionRulesConditions {
        ruleType
        allowedRelations
        defaultRelation
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    collectionRulesConditions {
      ruleType
      allowedRelations
      defaultRelation
    }
  }'
  ```

  #### Response

  ```json
  {
    "collectionRulesConditions": [
      {
        "ruleType": "TITLE",
        "allowedRelations": [
          "EQUALS",
          "NOT_EQUALS",
          "STARTS_WITH",
          "ENDS_WITH",
          "CONTAINS",
          "NOT_CONTAINS"
        ],
        "defaultRelation": "CONTAINS"
      },
      {
        "ruleType": "VARIANT_TITLE",
        "allowedRelations": [
          "EQUALS",
          "NOT_EQUALS",
          "STARTS_WITH",
          "ENDS_WITH",
          "CONTAINS",
          "NOT_CONTAINS"
        ],
        "defaultRelation": "CONTAINS"
      },
      {
        "ruleType": "TYPE",
        "allowedRelations": [
          "EQUALS",
          "NOT_EQUALS",
          "STARTS_WITH",
          "ENDS_WITH",
          "CONTAINS",
          "NOT_CONTAINS"
        ],
        "defaultRelation": "EQUALS"
      },
      {
        "ruleType": "PRODUCT_TAXONOMY_NODE_ID",
        "allowedRelations": [
          "EQUALS"
        ],
        "defaultRelation": "EQUALS"
      },
      {
        "ruleType": "VENDOR",
        "allowedRelations": [
          "EQUALS",
          "NOT_EQUALS",
          "STARTS_WITH",
          "ENDS_WITH",
          "CONTAINS",
          "NOT_CONTAINS"
        ],
        "defaultRelation": "EQUALS"
      },
      {
        "ruleType": "IS_PRICE_REDUCED",
        "allowedRelations": [
          "IS_SET",
          "IS_NOT_SET"
        ],
        "defaultRelation": "IS_SET"
      },
      {
        "ruleType": "VARIANT_PRICE",
        "allowedRelations": [
          "EQUALS",
          "NOT_EQUALS",
          "GREATER_THAN",
          "LESS_THAN"
        ],
        "defaultRelation": "GREATER_THAN"
      },
      {
        "ruleType": "VARIANT_COMPARE_AT_PRICE",
        "allowedRelations": [
          "EQUALS",
          "NOT_EQUALS",
          "GREATER_THAN",
          "LESS_THAN"
        ],
        "defaultRelation": "GREATER_THAN"
      },
      {
        "ruleType": "VARIANT_INVENTORY",
        "allowedRelations": [
          "EQUALS",
          "GREATER_THAN",
          "LESS_THAN"
        ],
        "defaultRelation": "GREATER_THAN"
      },
      {
        "ruleType": "VARIANT_WEIGHT",
        "allowedRelations": [
          "EQUALS",
          "NOT_EQUALS",
          "GREATER_THAN",
          "LESS_THAN"
        ],
        "defaultRelation": "GREATER_THAN"
      },
      {
        "ruleType": "TAG",
        "allowedRelations": [
          "EQUALS"
        ],
        "defaultRelation": "EQUALS"
      },
      {
        "ruleType": "PRODUCT_METAFIELD_DEFINITION",
        "allowedRelations": [
          "EQUALS",
          "GREATER_THAN",
          "LESS_THAN"
        ],
        "defaultRelation": "GREATER_THAN"
      },
      {
        "ruleType": "PRODUCT_METAFIELD_DEFINITION",
        "allowedRelations": [
          "EQUALS"
        ],
        "defaultRelation": "EQUALS"
      },
      {
        "ruleType": "PRODUCT_METAFIELD_DEFINITION",
        "allowedRelations": [
          "EQUALS",
          "GREATER_THAN",
          "LESS_THAN"
        ],
        "defaultRelation": "GREATER_THAN"
      },
      {
        "ruleType": "PRODUCT_METAFIELD_DEFINITION",
        "allowedRelations": [
          "EQUALS",
          "GREATER_THAN",
          "LESS_THAN"
        ],
        "defaultRelation": "GREATER_THAN"
      },
      {
        "ruleType": "PRODUCT_METAFIELD_DEFINITION",
        "allowedRelations": [
          "EQUALS"
        ],
        "defaultRelation": "EQUALS"
      },
      {
        "ruleType": "PRODUCT_METAFIELD_DEFINITION",
        "allowedRelations": [
          "EQUALS"
        ],
        "defaultRelation": "EQUALS"
      },
      {
        "ruleType": "PRODUCT_METAFIELD_DEFINITION",
        "allowedRelations": [
          "EQUALS"
        ],
        "defaultRelation": "EQUALS"
      },
      {
        "ruleType": "VARIANT_METAFIELD_DEFINITION",
        "allowedRelations": [
          "EQUALS",
          "GREATER_THAN",
          "LESS_THAN"
        ],
        "defaultRelation": "GREATER_THAN"
      },
      {
        "ruleType": "VARIANT_METAFIELD_DEFINITION",
        "allowedRelations": [
          "EQUALS"
        ],
        "defaultRelation": "EQUALS"
      },
      {
        "ruleType": "VARIANT_METAFIELD_DEFINITION",
        "allowedRelations": [
          "EQUALS",
          "GREATER_THAN",
          "LESS_THAN"
        ],
        "defaultRelation": "GREATER_THAN"
      },
      {
        "ruleType": "VARIANT_METAFIELD_DEFINITION",
        "allowedRelations": [
          "EQUALS"
        ],
        "defaultRelation": "EQUALS"
      },
      {
        "ruleType": "VARIANT_METAFIELD_DEFINITION",
        "allowedRelations": [
          "EQUALS"
        ],
        "defaultRelation": "EQUALS"
      },
      {
        "ruleType": "VARIANT_METAFIELD_DEFINITION",
        "allowedRelations": [
          "EQUALS"
        ],
        "defaultRelation": "EQUALS"
      }
    ]
  }
  ```

* ### Retrieve a list of collection rule conditions along with metafield rule objects

  #### Description

  Retrieves a list of collection rule conditions along with the rule object fields. Each returned rule object is a \`CollectionRuleMetafieldCondition\` that contains the metafield definition it refers to. See an example on how to create an automated collection with metafield definition collection rules on the \`collectionCreate\` mutation.

  #### Query

  ```graphql
  query {
    collectionRulesConditions {
      ruleType
      allowedRelations
      defaultRelation
      ruleObject {
        ... on CollectionRuleMetafieldCondition {
          metafieldDefinition {
            id
            name
            ownerType
            type {
              name
            }
            validations {
              value
            }
          }
        }
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
  "query": "query { collectionRulesConditions { ruleType allowedRelations defaultRelation ruleObject { ... on CollectionRuleMetafieldCondition { metafieldDefinition { id name ownerType type { name } validations { value } } } } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query {
      collectionRulesConditions {
        ruleType
        allowedRelations
        defaultRelation
        ruleObject {
          ... on CollectionRuleMetafieldCondition {
            metafieldDefinition {
              id
              name
              ownerType
              type {
                name
              }
              validations {
                value
              }
            }
          }
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
    query {
      collectionRulesConditions {
        ruleType
        allowedRelations
        defaultRelation
        ruleObject {
          ... on CollectionRuleMetafieldCondition {
            metafieldDefinition {
              id
              name
              ownerType
              type {
                name
              }
              validations {
                value
              }
            }
          }
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
    data: `query {
      collectionRulesConditions {
        ruleType
        allowedRelations
        defaultRelation
        ruleObject {
          ... on CollectionRuleMetafieldCondition {
            metafieldDefinition {
              id
              name
              ownerType
              type {
                name
              }
              validations {
                value
              }
            }
          }
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    collectionRulesConditions {
      ruleType
      allowedRelations
      defaultRelation
      ruleObject {
        ... on CollectionRuleMetafieldCondition {
          metafieldDefinition {
            id
            name
            ownerType
            type {
              name
            }
            validations {
              value
            }
          }
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "collectionRulesConditions": [
      {
        "ruleType": "TITLE",
        "allowedRelations": [
          "EQUALS",
          "NOT_EQUALS",
          "STARTS_WITH",
          "ENDS_WITH",
          "CONTAINS",
          "NOT_CONTAINS"
        ],
        "defaultRelation": "CONTAINS",
        "ruleObject": null
      },
      {
        "ruleType": "VARIANT_TITLE",
        "allowedRelations": [
          "EQUALS",
          "NOT_EQUALS",
          "STARTS_WITH",
          "ENDS_WITH",
          "CONTAINS",
          "NOT_CONTAINS"
        ],
        "defaultRelation": "CONTAINS",
        "ruleObject": null
      },
      {
        "ruleType": "TYPE",
        "allowedRelations": [
          "EQUALS",
          "NOT_EQUALS",
          "STARTS_WITH",
          "ENDS_WITH",
          "CONTAINS",
          "NOT_CONTAINS"
        ],
        "defaultRelation": "EQUALS",
        "ruleObject": null
      },
      {
        "ruleType": "PRODUCT_TAXONOMY_NODE_ID",
        "allowedRelations": [
          "EQUALS"
        ],
        "defaultRelation": "EQUALS",
        "ruleObject": null
      },
      {
        "ruleType": "VENDOR",
        "allowedRelations": [
          "EQUALS",
          "NOT_EQUALS",
          "STARTS_WITH",
          "ENDS_WITH",
          "CONTAINS",
          "NOT_CONTAINS"
        ],
        "defaultRelation": "EQUALS",
        "ruleObject": null
      },
      {
        "ruleType": "IS_PRICE_REDUCED",
        "allowedRelations": [
          "IS_SET",
          "IS_NOT_SET"
        ],
        "defaultRelation": "IS_SET",
        "ruleObject": null
      },
      {
        "ruleType": "VARIANT_PRICE",
        "allowedRelations": [
          "EQUALS",
          "NOT_EQUALS",
          "GREATER_THAN",
          "LESS_THAN"
        ],
        "defaultRelation": "GREATER_THAN",
        "ruleObject": null
      },
      {
        "ruleType": "VARIANT_COMPARE_AT_PRICE",
        "allowedRelations": [
          "EQUALS",
          "NOT_EQUALS",
          "GREATER_THAN",
          "LESS_THAN"
        ],
        "defaultRelation": "GREATER_THAN",
        "ruleObject": null
      },
      {
        "ruleType": "VARIANT_INVENTORY",
        "allowedRelations": [
          "EQUALS",
          "GREATER_THAN",
          "LESS_THAN"
        ],
        "defaultRelation": "GREATER_THAN",
        "ruleObject": null
      },
      {
        "ruleType": "VARIANT_WEIGHT",
        "allowedRelations": [
          "EQUALS",
          "NOT_EQUALS",
          "GREATER_THAN",
          "LESS_THAN"
        ],
        "defaultRelation": "GREATER_THAN",
        "ruleObject": null
      },
      {
        "ruleType": "TAG",
        "allowedRelations": [
          "EQUALS"
        ],
        "defaultRelation": "EQUALS",
        "ruleObject": null
      },
      {
        "ruleType": "PRODUCT_METAFIELD_DEFINITION",
        "allowedRelations": [
          "EQUALS",
          "GREATER_THAN",
          "LESS_THAN"
        ],
        "defaultRelation": "GREATER_THAN",
        "ruleObject": {
          "metafieldDefinition": {
            "id": "gid://shopify/MetafieldDefinition/89321433",
            "name": "Non-standard rating",
            "ownerType": "PRODUCT",
            "type": {
              "name": "rating"
            },
            "validations": [
              {
                "value": "1.0"
              },
              {
                "value": "6.0"
              }
            ]
          }
        }
      },
      {
        "ruleType": "PRODUCT_METAFIELD_DEFINITION",
        "allowedRelations": [
          "EQUALS"
        ],
        "defaultRelation": "EQUALS",
        "ruleObject": {
          "metafieldDefinition": {
            "id": "gid://shopify/MetafieldDefinition/371357715",
            "name": "model",
            "ownerType": "PRODUCT",
            "type": {
              "name": "single_line_text_field"
            },
            "validations": [
              {
                "value": "9"
              }
            ]
          }
        }
      },
      {
        "ruleType": "PRODUCT_METAFIELD_DEFINITION",
        "allowedRelations": [
          "EQUALS",
          "GREATER_THAN",
          "LESS_THAN"
        ],
        "defaultRelation": "GREATER_THAN",
        "ruleObject": {
          "metafieldDefinition": {
            "id": "gid://shopify/MetafieldDefinition/397285273",
            "name": "Competitor cost",
            "ownerType": "PRODUCT",
            "type": {
              "name": "number_decimal"
            },
            "validations": []
          }
        }
      },
      {
        "ruleType": "PRODUCT_METAFIELD_DEFINITION",
        "allowedRelations": [
          "EQUALS",
          "GREATER_THAN",
          "LESS_THAN"
        ],
        "defaultRelation": "GREATER_THAN",
        "ruleObject": {
          "metafieldDefinition": {
            "id": "gid://shopify/MetafieldDefinition/475536288",
            "name": "Year released",
            "ownerType": "PRODUCT",
            "type": {
              "name": "number_integer"
            },
            "validations": []
          }
        }
      },
      {
        "ruleType": "PRODUCT_METAFIELD_DEFINITION",
        "allowedRelations": [
          "EQUALS"
        ],
        "defaultRelation": "EQUALS",
        "ruleObject": {
          "metafieldDefinition": {
            "id": "gid://shopify/MetafieldDefinition/660917123",
            "name": "Materials",
            "ownerType": "PRODUCT",
            "type": {
              "name": "list.single_line_text_field"
            },
            "validations": []
          }
        }
      },
      {
        "ruleType": "PRODUCT_METAFIELD_DEFINITION",
        "allowedRelations": [
          "EQUALS"
        ],
        "defaultRelation": "EQUALS",
        "ruleObject": {
          "metafieldDefinition": {
            "id": "gid://shopify/MetafieldDefinition/804905764",
            "name": "Recyclable",
            "ownerType": "PRODUCT",
            "type": {
              "name": "boolean"
            },
            "validations": []
          }
        }
      },
      {
        "ruleType": "PRODUCT_METAFIELD_DEFINITION",
        "allowedRelations": [
          "EQUALS"
        ],
        "defaultRelation": "EQUALS",
        "ruleObject": {
          "metafieldDefinition": {
            "id": "gid://shopify/MetafieldDefinition/985769189",
            "name": "Exporters",
            "ownerType": "PRODUCT",
            "type": {
              "name": "list.single_line_text_field"
            },
            "validations": []
          }
        }
      },
      {
        "ruleType": "VARIANT_METAFIELD_DEFINITION",
        "allowedRelations": [
          "EQUALS",
          "GREATER_THAN",
          "LESS_THAN"
        ],
        "defaultRelation": "GREATER_THAN",
        "ruleObject": {
          "metafieldDefinition": {
            "id": "gid://shopify/MetafieldDefinition/180578340",
            "name": "competitor cost",
            "ownerType": "PRODUCTVARIANT",
            "type": {
              "name": "number_decimal"
            },
            "validations": []
          }
        }
      },
      {
        "ruleType": "VARIANT_METAFIELD_DEFINITION",
        "allowedRelations": [
          "EQUALS"
        ],
        "defaultRelation": "EQUALS",
        "ruleObject": {
          "metafieldDefinition": {
            "id": "gid://shopify/MetafieldDefinition/406572501",
            "name": "Contents",
            "ownerType": "PRODUCTVARIANT",
            "type": {
              "name": "list.single_line_text_field"
            },
            "validations": []
          }
        }
      },
      {
        "ruleType": "VARIANT_METAFIELD_DEFINITION",
        "allowedRelations": [
          "EQUALS",
          "GREATER_THAN",
          "LESS_THAN"
        ],
        "defaultRelation": "GREATER_THAN",
        "ruleObject": {
          "metafieldDefinition": {
            "id": "gid://shopify/MetafieldDefinition/685760035",
            "name": "size of the item",
            "ownerType": "PRODUCTVARIANT",
            "type": {
              "name": "number_integer"
            },
            "validations": []
          }
        }
      },
      {
        "ruleType": "VARIANT_METAFIELD_DEFINITION",
        "allowedRelations": [
          "EQUALS"
        ],
        "defaultRelation": "EQUALS",
        "ruleObject": {
          "metafieldDefinition": {
            "id": "gid://shopify/MetafieldDefinition/898504968",
            "name": "Recyclable",
            "ownerType": "PRODUCTVARIANT",
            "type": {
              "name": "boolean"
            },
            "validations": []
          }
        }
      },
      {
        "ruleType": "VARIANT_METAFIELD_DEFINITION",
        "allowedRelations": [
          "EQUALS"
        ],
        "defaultRelation": "EQUALS",
        "ruleObject": {
          "metafieldDefinition": {
            "id": "gid://shopify/MetafieldDefinition/1043030858",
            "name": "available",
            "ownerType": "PRODUCTVARIANT",
            "type": {
              "name": "single_line_text_field"
            },
            "validations": []
          }
        }
      },
      {
        "ruleType": "VARIANT_METAFIELD_DEFINITION",
        "allowedRelations": [
          "EQUALS"
        ],
        "defaultRelation": "EQUALS",
        "ruleObject": {
          "metafieldDefinition": {
            "id": "gid://shopify/MetafieldDefinition/1067782171",
            "name": "Exporters",
            "ownerType": "PRODUCTVARIANT",
            "type": {
              "name": "list.single_line_text_field"
            },
            "validations": []
          }
        }
      }
    ]
  }
  ```
