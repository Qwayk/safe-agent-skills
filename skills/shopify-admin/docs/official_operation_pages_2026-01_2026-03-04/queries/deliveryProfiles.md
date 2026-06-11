---
title: deliveryProfiles - GraphQL Admin
description: >-
  Returns a paginated list of
  [`DeliveryProfile`](https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliveryProfile)
  objects for the shop. Delivery profiles group
  [`Product`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product)
  and
  [`ProductVariant`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant)
  objects that share shipping rates and zones.


  Each profile contains
  [`DeliveryLocationGroup`](https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliveryLocationGroup)
  objects that organize fulfillment
  [`Location`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Location)
  objects and their associated delivery zones.
  [`DeliveryZone`](https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliveryZone)
  objects define geographic regions with specific shipping methods and rates.
  Use the
  [`merchantOwnedOnly`](https://shopify.dev/docs/api/admin-graphql/latest/queries/deliveryProfiles#arguments-merchantOwnedOnly)
  filter to exclude profiles that third-party apps manage.


  Learn more about [delivery
  profiles](https://shopify.dev/docs/apps/build/purchase-options/deferred/delivery-and-deferment#whats-a-delivery-profile).
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/deliveryProfiles'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/deliveryProfiles.md
---

# delivery​Profiles

query

Returns a paginated list of [`DeliveryProfile`](https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliveryProfile) objects for the shop. Delivery profiles group [`Product`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product) and [`ProductVariant`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant) objects that share shipping rates and zones.

Each profile contains [`DeliveryLocationGroup`](https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliveryLocationGroup) objects that organize fulfillment [`Location`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Location) objects and their associated delivery zones. [`DeliveryZone`](https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliveryZone) objects define geographic regions with specific shipping methods and rates. Use the [`merchantOwnedOnly`](https://shopify.dev/docs/api/admin-graphql/latest/queries/deliveryProfiles#arguments-merchantOwnedOnly) filter to exclude profiles that third-party apps manage.

Learn more about [delivery profiles](https://shopify.dev/docs/apps/build/purchase-options/deferred/delivery-and-deferment#whats-a-delivery-profile).

## DeliveryProfileConnection arguments

[DeliveryProfileConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/DeliveryProfileConnection)

* after

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* before

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* first

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* last

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* merchant​Owned​Only

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  If `true`, returns only delivery profiles that were created by the merchant.

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

***

## Possible returns

* edges

  [\[Delivery​Profile​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliveryProfileEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Delivery​Profile!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliveryProfile)

  non-null

  A list of nodes that are contained in DeliveryProfileEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### Receive a list of all ShippingZones

  #### Query

  ```graphql
  query DeliveryZoneList {
    deliveryProfiles(first: 10) {
      edges {
        node {
          id
          profileLocationGroups {
            locationGroup {
              id
            }
            locationGroupZones(first: 10) {
              edges {
                node {
                  zone {
                    id
                    name
                    countries {
                      code {
                        countryCode
                        restOfWorld
                      }
                      provinces {
                        name
                        code
                      }
                    }
                  }
                  methodDefinitions(first: 10) {
                    edges {
                      node {
                        id
                        active
                        description
                        methodConditions {
                          field
                          operator
                          conditionCriteria {
                            __typename
                            ... on MoneyV2 {
                              amount
                              currencyCode
                            }
                            ... on Weight {
                              unit
                              value
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }
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
  "query": "query DeliveryZoneList { deliveryProfiles(first: 10) { edges { node { id profileLocationGroups { locationGroup { id } locationGroupZones(first: 10) { edges { node { zone { id name countries { code { countryCode restOfWorld } provinces { name code } } } methodDefinitions(first: 10) { edges { node { id active description methodConditions { field operator conditionCriteria { __typename ... on MoneyV2 { amount currencyCode } ... on Weight { unit value } } } } } } } } } } } } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query DeliveryZoneList {
      deliveryProfiles(first: 10) {
        edges {
          node {
            id
            profileLocationGroups {
              locationGroup {
                id
              }
              locationGroupZones(first: 10) {
                edges {
                  node {
                    zone {
                      id
                      name
                      countries {
                        code {
                          countryCode
                          restOfWorld
                        }
                        provinces {
                          name
                          code
                        }
                      }
                    }
                    methodDefinitions(first: 10) {
                      edges {
                        node {
                          id
                          active
                          description
                          methodConditions {
                            field
                            operator
                            conditionCriteria {
                              __typename
                              ... on MoneyV2 {
                                amount
                                currencyCode
                              }
                              ... on Weight {
                                unit
                                value
                              }
                            }
                          }
                        }
                      }
                    }
                  }
                }
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
    query DeliveryZoneList {
      deliveryProfiles(first: 10) {
        edges {
          node {
            id
            profileLocationGroups {
              locationGroup {
                id
              }
              locationGroupZones(first: 10) {
                edges {
                  node {
                    zone {
                      id
                      name
                      countries {
                        code {
                          countryCode
                          restOfWorld
                        }
                        provinces {
                          name
                          code
                        }
                      }
                    }
                    methodDefinitions(first: 10) {
                      edges {
                        node {
                          id
                          active
                          description
                          methodConditions {
                            field
                            operator
                            conditionCriteria {
                              __typename
                              ... on MoneyV2 {
                                amount
                                currencyCode
                              }
                              ... on Weight {
                                unit
                                value
                              }
                            }
                          }
                        }
                      }
                    }
                  }
                }
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
    data: `query DeliveryZoneList {
      deliveryProfiles(first: 10) {
        edges {
          node {
            id
            profileLocationGroups {
              locationGroup {
                id
              }
              locationGroupZones(first: 10) {
                edges {
                  node {
                    zone {
                      id
                      name
                      countries {
                        code {
                          countryCode
                          restOfWorld
                        }
                        provinces {
                          name
                          code
                        }
                      }
                    }
                    methodDefinitions(first: 10) {
                      edges {
                        node {
                          id
                          active
                          description
                          methodConditions {
                            field
                            operator
                            conditionCriteria {
                              __typename
                              ... on MoneyV2 {
                                amount
                                currencyCode
                              }
                              ... on Weight {
                                unit
                                value
                              }
                            }
                          }
                        }
                      }
                    }
                  }
                }
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
  'query DeliveryZoneList {
    deliveryProfiles(first: 10) {
      edges {
        node {
          id
          profileLocationGroups {
            locationGroup {
              id
            }
            locationGroupZones(first: 10) {
              edges {
                node {
                  zone {
                    id
                    name
                    countries {
                      code {
                        countryCode
                        restOfWorld
                      }
                      provinces {
                        name
                        code
                      }
                    }
                  }
                  methodDefinitions(first: 10) {
                    edges {
                      node {
                        id
                        active
                        description
                        methodConditions {
                          field
                          operator
                          conditionCriteria {
                            __typename
                            ... on MoneyV2 {
                              amount
                              currencyCode
                            }
                            ... on Weight {
                              unit
                              value
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }
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
    "deliveryProfiles": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/DeliveryProfile/28404419",
            "profileLocationGroups": [
              {
                "locationGroup": {
                  "id": "gid://shopify/DeliveryLocationGroup/42565096"
                },
                "locationGroupZones": {
                  "edges": [
                    {
                      "node": {
                        "zone": {
                          "id": "gid://shopify/DeliveryZone/600655460",
                          "name": "Ottawa South",
                          "countries": [
                            {
                              "code": {
                                "countryCode": "CA",
                                "restOfWorld": false
                              },
                              "provinces": [
                                {
                                  "name": "Ontario",
                                  "code": "ON"
                                }
                              ]
                            }
                          ]
                        },
                        "methodDefinitions": {
                          "edges": []
                        }
                      }
                    },
                    {
                      "node": {
                        "zone": {
                          "id": "gid://shopify/DeliveryZone/765028017",
                          "name": "Rest of World",
                          "countries": [
                            {
                              "code": {
                                "countryCode": null,
                                "restOfWorld": true
                              },
                              "provinces": []
                            }
                          ]
                        },
                        "methodDefinitions": {
                          "edges": [
                            {
                              "node": {
                                "id": "gid://shopify/DeliveryMethodDefinition/341096212",
                                "active": true,
                                "description": "Use this when shipping a footwear",
                                "methodConditions": []
                              }
                            }
                          ]
                        }
                      }
                    }
                  ]
                }
              },
              {
                "locationGroup": {
                  "id": "gid://shopify/DeliveryLocationGroup/311517628"
                },
                "locationGroupZones": {
                  "edges": []
                }
              }
            ]
          }
        },
        {
          "node": {
            "id": "gid://shopify/DeliveryProfile/142458073",
            "profileLocationGroups": [
              {
                "locationGroup": {
                  "id": "gid://shopify/DeliveryLocationGroup/955592432"
                },
                "locationGroupZones": {
                  "edges": [
                    {
                      "node": {
                        "zone": {
                          "id": "gid://shopify/DeliveryZone/472354800",
                          "name": "Downtown Montreal",
                          "countries": [
                            {
                              "code": {
                                "countryCode": "CA",
                                "restOfWorld": false
                              },
                              "provinces": [
                                {
                                  "name": "Quebec",
                                  "code": "QC"
                                }
                              ]
                            }
                          ]
                        },
                        "methodDefinitions": {
                          "edges": []
                        }
                      }
                    },
                    {
                      "node": {
                        "zone": {
                          "id": "gid://shopify/DeliveryZone/132414656",
                          "name": "Downtown Ottawa",
                          "countries": [
                            {
                              "code": {
                                "countryCode": "CA",
                                "restOfWorld": false
                              },
                              "provinces": [
                                {
                                  "name": "Ontario",
                                  "code": "ON"
                                }
                              ]
                            }
                          ]
                        },
                        "methodDefinitions": {
                          "edges": [
                            {
                              "node": {
                                "id": "gid://shopify/DeliveryMethodDefinition/2482324",
                                "active": true,
                                "description": "Use this when shipping a snowboard",
                                "methodConditions": [
                                  {
                                    "field": "TOTAL_WEIGHT",
                                    "operator": "LESS_THAN_OR_EQUAL_TO",
                                    "conditionCriteria": {
                                      "__typename": "Weight",
                                      "unit": "POUNDS",
                                      "value": 19.9
                                    }
                                  }
                                ]
                              }
                            },
                            {
                              "node": {
                                "id": "gid://shopify/DeliveryMethodDefinition/7712587",
                                "active": false,
                                "description": "Use this when shipping a snowboard",
                                "methodConditions": []
                              }
                            },
                            {
                              "node": {
                                "id": "gid://shopify/DeliveryMethodDefinition/164614040",
                                "active": true,
                                "description": "Use this when shipping a snowboard",
                                "methodConditions": [
                                  {
                                    "field": "TOTAL_WEIGHT",
                                    "operator": "LESS_THAN_OR_EQUAL_TO",
                                    "conditionCriteria": {
                                      "__typename": "Weight",
                                      "unit": "POUNDS",
                                      "value": 10
                                    }
                                  }
                                ]
                              }
                            },
                            {
                              "node": {
                                "id": "gid://shopify/DeliveryMethodDefinition/183895045",
                                "active": true,
                                "description": "Use this when shipping a snowboard",
                                "methodConditions": [
                                  {
                                    "field": "TOTAL_WEIGHT",
                                    "operator": "GREATER_THAN_OR_EQUAL_TO",
                                    "conditionCriteria": {
                                      "__typename": "Weight",
                                      "unit": "POUNDS",
                                      "value": 20
                                    }
                                  },
                                  {
                                    "field": "TOTAL_WEIGHT",
                                    "operator": "LESS_THAN_OR_EQUAL_TO",
                                    "conditionCriteria": {
                                      "__typename": "Weight",
                                      "unit": "POUNDS",
                                      "value": 40
                                    }
                                  }
                                ]
                              }
                            },
                            {
                              "node": {
                                "id": "gid://shopify/DeliveryMethodDefinition/213030275",
                                "active": false,
                                "description": "Use this when shipping a snowboard",
                                "methodConditions": [
                                  {
                                    "field": "TOTAL_WEIGHT",
                                    "operator": "GREATER_THAN_OR_EQUAL_TO",
                                    "conditionCriteria": {
                                      "__typename": "Weight",
                                      "unit": "POUNDS",
                                      "value": 40.01
                                    }
                                  },
                                  {
                                    "field": "TOTAL_WEIGHT",
                                    "operator": "LESS_THAN_OR_EQUAL_TO",
                                    "conditionCriteria": {
                                      "__typename": "Weight",
                                      "unit": "POUNDS",
                                      "value": 60
                                    }
                                  }
                                ]
                              }
                            },
                            {
                              "node": {
                                "id": "gid://shopify/DeliveryMethodDefinition/573089753",
                                "active": false,
                                "description": "Carrier service api rates",
                                "methodConditions": []
                              }
                            }
                          ]
                        }
                      }
                    },
                    {
                      "node": {
                        "zone": {
                          "id": "gid://shopify/DeliveryZone/881877111",
                          "name": "Germany",
                          "countries": [
                            {
                              "code": {
                                "countryCode": "DE",
                                "restOfWorld": false
                              },
                              "provinces": []
                            }
                          ]
                        },
                        "methodDefinitions": {
                          "edges": []
                        }
                      }
                    },
                    {
                      "node": {
                        "zone": {
                          "id": "gid://shopify/DeliveryZone/813997144",
                          "name": "Rest of World",
                          "countries": [
                            {
                              "code": {
                                "countryCode": null,
                                "restOfWorld": true
                              },
                              "provinces": []
                            }
                          ]
                        },
                        "methodDefinitions": {
                          "edges": []
                        }
                      }
                    }
                  ]
                }
              },
              {
                "locationGroup": {
                  "id": "gid://shopify/DeliveryLocationGroup/397370199"
                },
                "locationGroupZones": {
                  "edges": [
                    {
                      "node": {
                        "zone": {
                          "id": "gid://shopify/DeliveryZone/283164273",
                          "name": "Argentina",
                          "countries": [
                            {
                              "code": {
                                "countryCode": "AR",
                                "restOfWorld": false
                              },
                              "provinces": [
                                {
                                  "name": "Buenos Aires",
                                  "code": "B"
                                }
                              ]
                            }
                          ]
                        },
                        "methodDefinitions": {
                          "edges": []
                        }
                      }
                    },
                    {
                      "node": {
                        "zone": {
                          "id": "gid://shopify/DeliveryZone/599563131",
                          "name": "US zone 1",
                          "countries": [
                            {
                              "code": {
                                "countryCode": "US",
                                "restOfWorld": false
                              },
                              "provinces": []
                            }
                          ]
                        },
                        "methodDefinitions": {
                          "edges": [
                            {
                              "node": {
                                "id": "gid://shopify/DeliveryMethodDefinition/159353577",
                                "active": true,
                                "description": "Use this when shipping a snowboard",
                                "methodConditions": [
                                  {
                                    "field": "TOTAL_PRICE",
                                    "operator": "GREATER_THAN_OR_EQUAL_TO",
                                    "conditionCriteria": {
                                      "__typename": "MoneyV2",
                                      "amount": "50.0",
                                      "currencyCode": "USD"
                                    }
                                  }
                                ]
                              }
                            },
                            {
                              "node": {
                                "id": "gid://shopify/DeliveryMethodDefinition/206705707",
                                "active": false,
                                "description": "Use this when shipping a snowboard",
                                "methodConditions": [
                                  {
                                    "field": "TOTAL_PRICE",
                                    "operator": "GREATER_THAN_OR_EQUAL_TO",
                                    "conditionCriteria": {
                                      "__typename": "MoneyV2",
                                      "amount": "100.0",
                                      "currencyCode": "USD"
                                    }
                                  }
                                ]
                              }
                            }
                          ]
                        }
                      }
                    }
                  ]
                }
              },
              {
                "locationGroup": {
                  "id": "gid://shopify/DeliveryLocationGroup/311517628"
                },
                "locationGroupZones": {
                  "edges": []
                }
              }
            ]
          }
        },
        {
          "node": {
            "id": "gid://shopify/DeliveryProfile/426406120",
            "profileLocationGroups": [
              {
                "locationGroup": {
                  "id": "gid://shopify/DeliveryLocationGroup/865330255"
                },
                "locationGroupZones": {
                  "edges": [
                    {
                      "node": {
                        "zone": {
                          "id": "gid://shopify/DeliveryZone/846446649",
                          "name": "Rest of World",
                          "countries": []
                        },
                        "methodDefinitions": {
                          "edges": []
                        }
                      }
                    }
                  ]
                }
              }
            ]
          }
        },
        {
          "node": {
            "id": "gid://shopify/DeliveryProfile/593363170",
            "profileLocationGroups": [
              {
                "locationGroup": {
                  "id": "gid://shopify/DeliveryLocationGroup/311517628"
                },
                "locationGroupZones": {
                  "edges": []
                }
              },
              {
                "locationGroup": {
                  "id": "gid://shopify/DeliveryLocationGroup/955592432"
                },
                "locationGroupZones": {
                  "edges": [
                    {
                      "node": {
                        "zone": {
                          "id": "gid://shopify/DeliveryZone/161697132",
                          "name": "Canada",
                          "countries": [
                            {
                              "code": {
                                "countryCode": "CA",
                                "restOfWorld": false
                              },
                              "provinces": [
                                {
                                  "name": "Ontario",
                                  "code": "ON"
                                }
                              ]
                            }
                          ]
                        },
                        "methodDefinitions": {
                          "edges": [
                            {
                              "node": {
                                "id": "gid://shopify/DeliveryMethodDefinition/718143985",
                                "active": true,
                                "description": "Standard method for shipping a snowboard",
                                "methodConditions": []
                              }
                            }
                          ]
                        }
                      }
                    }
                  ]
                }
              }
            ]
          }
        },
        {
          "node": {
            "id": "gid://shopify/DeliveryProfile/933922677",
            "profileLocationGroups": [
              {
                "locationGroup": {
                  "id": "gid://shopify/DeliveryLocationGroup/562374560"
                },
                "locationGroupZones": {
                  "edges": [
                    {
                      "node": {
                        "zone": {
                          "id": "gid://shopify/DeliveryZone/1066475769",
                          "name": "Rest of World",
                          "countries": []
                        },
                        "methodDefinitions": {
                          "edges": []
                        }
                      }
                    }
                  ]
                }
              }
            ]
          }
        }
      ]
    }
  }
  ```
