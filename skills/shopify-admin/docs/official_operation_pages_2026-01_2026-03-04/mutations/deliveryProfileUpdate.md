---
title: deliveryProfileUpdate - GraphQL Admin
description: >-
  Updates a
  [`DeliveryProfile`](https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliveryProfile)'s
  configuration, including its shipping zones, rates, and associated products.


  Modify location groups to control which fulfillment
  [`Location`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Location)
  objects serve specific geographic areas. Add or remove shipping zones with
  custom countries and provinces. Create or update shipping methods with rate
  definitions and delivery conditions. Associate or dissociate
  [`ProductVariant`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant)
  objects and
  [`SellingPlanGroup`](https://shopify.dev/docs/api/admin-graphql/latest/objects/SellingPlanGroup)
  objects to determine which products use this profile's shipping rules.


  The mutation supports partial updates through dedicated input fields for
  creating, updating, and deleting specific components without affecting the
  entire profile structure.


  Learn more about [building delivery
  profiles](https://shopify.dev/docs/apps/build/purchase-options/deferred/delivery-and-deferment/build-delivery-profiles).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/deliveryProfileUpdate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/deliveryProfileUpdate.md
---

# delivery​Profile​Update

mutation

Requires Any of `shipping` access scopes or `manage_delivery_settings` user permission.

Updates a [`DeliveryProfile`](https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliveryProfile)'s configuration, including its shipping zones, rates, and associated products.

Modify location groups to control which fulfillment [`Location`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Location) objects serve specific geographic areas. Add or remove shipping zones with custom countries and provinces. Create or update shipping methods with rate definitions and delivery conditions. Associate or dissociate [`ProductVariant`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant) objects and [`SellingPlanGroup`](https://shopify.dev/docs/api/admin-graphql/latest/objects/SellingPlanGroup) objects to determine which products use this profile's shipping rules.

The mutation supports partial updates through dedicated input fields for creating, updating, and deleting specific components without affecting the entire profile structure.

Learn more about [building delivery profiles](https://shopify.dev/docs/apps/build/purchase-options/deferred/delivery-and-deferment/build-delivery-profiles).

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the delivery profile to update.

* profile

  [Delivery​Profile​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/DeliveryProfileInput)

  required

  Specifies the input fields for a delivery profile.

* leave​Legacy​Mode​Profiles

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Deprecated (removal date set)

***

## Delivery​Profile​Update​Payload returns

* profile

  [Delivery​Profile](https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliveryProfile)

  The delivery profile that was updated.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Update delivery profile to add a location and a zone to an existing group

  #### Description

  Given a delivery profile with a location group for shipping from locations in Canada, group is updated to include shipping from a warehouse in Ottawa. The group is also updated to allow shipping to a United States zone. \*\*Note:\*\* due to the potential complexity of the nested data, it is recommended to update no more than 5 groups per each request.

  #### Query

  ```graphql
  mutation deliveryProfileUpdate($id: ID!, $profile: DeliveryProfileInput!) {
    deliveryProfileUpdate(id: $id, profile: $profile) {
      profile {
        id
        name
        profileLocationGroups {
          locationGroup {
            id
            locations(first: 5) {
              nodes {
                name
                address {
                  country
                }
              }
            }
          }
          locationGroupZones(first: 2) {
            edges {
              node {
                zone {
                  id
                  name
                  countries {
                    code {
                      countryCode
                    }
                    provinces {
                      code
                    }
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
    "id": "gid://shopify/DeliveryProfile/593363170",
    "profile": {
      "name": "Sample Updated Delivery Profile",
      "locationGroupsToUpdate": [
        {
          "id": "gid://shopify/DeliveryLocationGroup/955592432",
          "locationsToAdd": [
            "gid://shopify/Location/884687543"
          ],
          "zonesToCreate": [
            {
              "name": "USA Zone",
              "countries": {
                "code": "US",
                "provinces": [
                  {
                    "code": "CO"
                  }
                ]
              },
              "methodDefinitionsToCreate": [
                {
                  "name": "Standard",
                  "rateDefinition": {
                    "price": {
                      "amount": 1,
                      "currencyCode": "USD"
                    }
                  }
                }
              ]
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
  "query": "mutation deliveryProfileUpdate($id: ID!, $profile: DeliveryProfileInput!) { deliveryProfileUpdate(id: $id, profile: $profile) { profile { id name profileLocationGroups { locationGroup { id locations(first: 5) { nodes { name address { country } } } } locationGroupZones(first: 2) { edges { node { zone { id name countries { code { countryCode } provinces { code } } } } } } } } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/DeliveryProfile/593363170",
      "profile": {
        "name": "Sample Updated Delivery Profile",
        "locationGroupsToUpdate": [
          {
            "id": "gid://shopify/DeliveryLocationGroup/955592432",
            "locationsToAdd": [
              "gid://shopify/Location/884687543"
            ],
            "zonesToCreate": [
              {
                "name": "USA Zone",
                "countries": {
                  "code": "US",
                  "provinces": [
                    {
                      "code": "CO"
                    }
                  ]
                },
                "methodDefinitionsToCreate": [
                  {
                    "name": "Standard",
                    "rateDefinition": {
                      "price": {
                        "amount": 1,
                        "currencyCode": "USD"
                      }
                    }
                  }
                ]
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
    mutation deliveryProfileUpdate($id: ID!, $profile: DeliveryProfileInput!) {
      deliveryProfileUpdate(id: $id, profile: $profile) {
        profile {
          id
          name
          profileLocationGroups {
            locationGroup {
              id
              locations(first: 5) {
                nodes {
                  name
                  address {
                    country
                  }
                }
              }
            }
            locationGroupZones(first: 2) {
              edges {
                node {
                  zone {
                    id
                    name
                    countries {
                      code {
                        countryCode
                      }
                      provinces {
                        code
                      }
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
          "id": "gid://shopify/DeliveryProfile/593363170",
          "profile": {
              "name": "Sample Updated Delivery Profile",
              "locationGroupsToUpdate": [
                  {
                      "id": "gid://shopify/DeliveryLocationGroup/955592432",
                      "locationsToAdd": [
                          "gid://shopify/Location/884687543"
                      ],
                      "zonesToCreate": [
                          {
                              "name": "USA Zone",
                              "countries": {
                                  "code": "US",
                                  "provinces": [
                                      {
                                          "code": "CO"
                                      }
                                  ]
                              },
                              "methodDefinitionsToCreate": [
                                  {
                                      "name": "Standard",
                                      "rateDefinition": {
                                          "price": {
                                              "amount": 1,
                                              "currencyCode": "USD"
                                          }
                                      }
                                  }
                              ]
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
    mutation deliveryProfileUpdate($id: ID!, $profile: DeliveryProfileInput!) {
      deliveryProfileUpdate(id: $id, profile: $profile) {
        profile {
          id
          name
          profileLocationGroups {
            locationGroup {
              id
              locations(first: 5) {
                nodes {
                  name
                  address {
                    country
                  }
                }
              }
            }
            locationGroupZones(first: 2) {
              edges {
                node {
                  zone {
                    id
                    name
                    countries {
                      code {
                        countryCode
                      }
                      provinces {
                        code
                      }
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
    "id": "gid://shopify/DeliveryProfile/593363170",
    "profile": {
      "name": "Sample Updated Delivery Profile",
      "locationGroupsToUpdate": [
        {
          "id": "gid://shopify/DeliveryLocationGroup/955592432",
          "locationsToAdd": [
            "gid://shopify/Location/884687543"
          ],
          "zonesToCreate": [
            {
              "name": "USA Zone",
              "countries": {
                "code": "US",
                "provinces": [
                  {
                    "code": "CO"
                  }
                ]
              },
              "methodDefinitionsToCreate": [
                {
                  "name": "Standard",
                  "rateDefinition": {
                    "price": {
                      "amount": 1,
                      "currencyCode": "USD"
                    }
                  }
                }
              ]
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
      "query": `mutation deliveryProfileUpdate($id: ID!, $profile: DeliveryProfileInput!) {
        deliveryProfileUpdate(id: $id, profile: $profile) {
          profile {
            id
            name
            profileLocationGroups {
              locationGroup {
                id
                locations(first: 5) {
                  nodes {
                    name
                    address {
                      country
                    }
                  }
                }
              }
              locationGroupZones(first: 2) {
                edges {
                  node {
                    zone {
                      id
                      name
                      countries {
                        code {
                          countryCode
                        }
                        provinces {
                          code
                        }
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
          "id": "gid://shopify/DeliveryProfile/593363170",
          "profile": {
              "name": "Sample Updated Delivery Profile",
              "locationGroupsToUpdate": [
                  {
                      "id": "gid://shopify/DeliveryLocationGroup/955592432",
                      "locationsToAdd": [
                          "gid://shopify/Location/884687543"
                      ],
                      "zonesToCreate": [
                          {
                              "name": "USA Zone",
                              "countries": {
                                  "code": "US",
                                  "provinces": [
                                      {
                                          "code": "CO"
                                      }
                                  ]
                              },
                              "methodDefinitionsToCreate": [
                                  {
                                      "name": "Standard",
                                      "rateDefinition": {
                                          "price": {
                                              "amount": 1,
                                              "currencyCode": "USD"
                                          }
                                      }
                                  }
                              ]
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
  'mutation deliveryProfileUpdate($id: ID!, $profile: DeliveryProfileInput!) {
    deliveryProfileUpdate(id: $id, profile: $profile) {
      profile {
        id
        name
        profileLocationGroups {
          locationGroup {
            id
            locations(first: 5) {
              nodes {
                name
                address {
                  country
                }
              }
            }
          }
          locationGroupZones(first: 2) {
            edges {
              node {
                zone {
                  id
                  name
                  countries {
                    code {
                      countryCode
                    }
                    provinces {
                      code
                    }
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
    "id": "gid://shopify/DeliveryProfile/593363170",
    "profile": {
      "name": "Sample Updated Delivery Profile",
      "locationGroupsToUpdate": [
        {
          "id": "gid://shopify/DeliveryLocationGroup/955592432",
          "locationsToAdd": [
            "gid://shopify/Location/884687543"
          ],
          "zonesToCreate": [
            {
              "name": "USA Zone",
              "countries": {
                "code": "US",
                "provinces": [
                  {
                    "code": "CO"
                  }
                ]
              },
              "methodDefinitionsToCreate": [
                {
                  "name": "Standard",
                  "rateDefinition": {
                    "price": {
                      "amount": 1,
                      "currencyCode": "USD"
                    }
                  }
                }
              ]
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
    "deliveryProfileUpdate": {
      "profile": {
        "id": "gid://shopify/DeliveryProfile/593363170",
        "name": "Sample Updated Delivery Profile",
        "profileLocationGroups": [
          {
            "locationGroup": {
              "id": "gid://shopify/DeliveryLocationGroup/955592432",
              "locations": {
                "nodes": [
                  {
                    "name": "Ottawa Store",
                    "address": {
                      "country": "Canada"
                    }
                  },
                  {
                    "name": "Ottawa Warehouse",
                    "address": {
                      "country": "Canada"
                    }
                  },
                  {
                    "name": "Shipping Origin",
                    "address": {
                      "country": "Canada"
                    }
                  }
                ]
              }
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
                            "countryCode": "CA"
                          },
                          "provinces": [
                            {
                              "code": "ON"
                            }
                          ]
                        }
                      ]
                    }
                  }
                },
                {
                  "node": {
                    "zone": {
                      "id": "gid://shopify/DeliveryZone/1066475777",
                      "name": "USA Zone",
                      "countries": [
                        {
                          "code": {
                            "countryCode": "US"
                          },
                          "provinces": [
                            {
                              "code": "CO"
                            }
                          ]
                        }
                      ]
                    }
                  }
                }
              ]
            }
          }
        ]
      },
      "userErrors": []
    }
  }
  ```

* ### Update delivery profile to add a location group

  #### Description

  Given a delivery profile with a location group for shipping from Canada, profile is updated to add a location group for shipping from the United States. \*\*Note:\*\* due to the potential complexity of the nested data, it is recommended to create no more than 5 groups per each request.

  #### Query

  ```graphql
  mutation deliveryProfileUpdate($id: ID!, $profile: DeliveryProfileInput!) {
    deliveryProfileUpdate(id: $id, profile: $profile) {
      profile {
        id
        name
        profileLocationGroups {
          locationGroup {
            id
            locations(first: 5) {
              nodes {
                name
                address {
                  country
                }
              }
            }
          }
          locationGroupZones(first: 2) {
            edges {
              node {
                zone {
                  id
                  name
                  countries {
                    code {
                      countryCode
                    }
                    provinces {
                      code
                    }
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
    "id": "gid://shopify/DeliveryProfile/593363170",
    "profile": {
      "name": "Sample Updated Delivery Profile",
      "locationGroupsToCreate": [
        {
          "locationsToAdd": [
            "gid://shopify/Location/415211365"
          ],
          "zonesToCreate": [
            {
              "name": "USA Zone",
              "countries": {
                "code": "US",
                "provinces": [
                  {
                    "code": "CO"
                  }
                ]
              },
              "methodDefinitionsToCreate": [
                {
                  "name": "Standard",
                  "rateDefinition": {
                    "price": {
                      "amount": 1,
                      "currencyCode": "USD"
                    }
                  }
                }
              ]
            },
            {
              "name": "Mexico Zone",
              "countries": {
                "code": "MX",
                "provinces": [
                  {
                    "code": "MOR"
                  }
                ]
              },
              "methodDefinitionsToCreate": [
                {
                  "name": "Standard",
                  "rateDefinition": {
                    "price": {
                      "amount": 1,
                      "currencyCode": "USD"
                    }
                  }
                }
              ]
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
  "query": "mutation deliveryProfileUpdate($id: ID!, $profile: DeliveryProfileInput!) { deliveryProfileUpdate(id: $id, profile: $profile) { profile { id name profileLocationGroups { locationGroup { id locations(first: 5) { nodes { name address { country } } } } locationGroupZones(first: 2) { edges { node { zone { id name countries { code { countryCode } provinces { code } } } } } } } } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/DeliveryProfile/593363170",
      "profile": {
        "name": "Sample Updated Delivery Profile",
        "locationGroupsToCreate": [
          {
            "locationsToAdd": [
              "gid://shopify/Location/415211365"
            ],
            "zonesToCreate": [
              {
                "name": "USA Zone",
                "countries": {
                  "code": "US",
                  "provinces": [
                    {
                      "code": "CO"
                    }
                  ]
                },
                "methodDefinitionsToCreate": [
                  {
                    "name": "Standard",
                    "rateDefinition": {
                      "price": {
                        "amount": 1,
                        "currencyCode": "USD"
                      }
                    }
                  }
                ]
              },
              {
                "name": "Mexico Zone",
                "countries": {
                  "code": "MX",
                  "provinces": [
                    {
                      "code": "MOR"
                    }
                  ]
                },
                "methodDefinitionsToCreate": [
                  {
                    "name": "Standard",
                    "rateDefinition": {
                      "price": {
                        "amount": 1,
                        "currencyCode": "USD"
                      }
                    }
                  }
                ]
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
    mutation deliveryProfileUpdate($id: ID!, $profile: DeliveryProfileInput!) {
      deliveryProfileUpdate(id: $id, profile: $profile) {
        profile {
          id
          name
          profileLocationGroups {
            locationGroup {
              id
              locations(first: 5) {
                nodes {
                  name
                  address {
                    country
                  }
                }
              }
            }
            locationGroupZones(first: 2) {
              edges {
                node {
                  zone {
                    id
                    name
                    countries {
                      code {
                        countryCode
                      }
                      provinces {
                        code
                      }
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
          "id": "gid://shopify/DeliveryProfile/593363170",
          "profile": {
              "name": "Sample Updated Delivery Profile",
              "locationGroupsToCreate": [
                  {
                      "locationsToAdd": [
                          "gid://shopify/Location/415211365"
                      ],
                      "zonesToCreate": [
                          {
                              "name": "USA Zone",
                              "countries": {
                                  "code": "US",
                                  "provinces": [
                                      {
                                          "code": "CO"
                                      }
                                  ]
                              },
                              "methodDefinitionsToCreate": [
                                  {
                                      "name": "Standard",
                                      "rateDefinition": {
                                          "price": {
                                              "amount": 1,
                                              "currencyCode": "USD"
                                          }
                                      }
                                  }
                              ]
                          },
                          {
                              "name": "Mexico Zone",
                              "countries": {
                                  "code": "MX",
                                  "provinces": [
                                      {
                                          "code": "MOR"
                                      }
                                  ]
                              },
                              "methodDefinitionsToCreate": [
                                  {
                                      "name": "Standard",
                                      "rateDefinition": {
                                          "price": {
                                              "amount": 1,
                                              "currencyCode": "USD"
                                          }
                                      }
                                  }
                              ]
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
    mutation deliveryProfileUpdate($id: ID!, $profile: DeliveryProfileInput!) {
      deliveryProfileUpdate(id: $id, profile: $profile) {
        profile {
          id
          name
          profileLocationGroups {
            locationGroup {
              id
              locations(first: 5) {
                nodes {
                  name
                  address {
                    country
                  }
                }
              }
            }
            locationGroupZones(first: 2) {
              edges {
                node {
                  zone {
                    id
                    name
                    countries {
                      code {
                        countryCode
                      }
                      provinces {
                        code
                      }
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
    "id": "gid://shopify/DeliveryProfile/593363170",
    "profile": {
      "name": "Sample Updated Delivery Profile",
      "locationGroupsToCreate": [
        {
          "locationsToAdd": [
            "gid://shopify/Location/415211365"
          ],
          "zonesToCreate": [
            {
              "name": "USA Zone",
              "countries": {
                "code": "US",
                "provinces": [
                  {
                    "code": "CO"
                  }
                ]
              },
              "methodDefinitionsToCreate": [
                {
                  "name": "Standard",
                  "rateDefinition": {
                    "price": {
                      "amount": 1,
                      "currencyCode": "USD"
                    }
                  }
                }
              ]
            },
            {
              "name": "Mexico Zone",
              "countries": {
                "code": "MX",
                "provinces": [
                  {
                    "code": "MOR"
                  }
                ]
              },
              "methodDefinitionsToCreate": [
                {
                  "name": "Standard",
                  "rateDefinition": {
                    "price": {
                      "amount": 1,
                      "currencyCode": "USD"
                    }
                  }
                }
              ]
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
      "query": `mutation deliveryProfileUpdate($id: ID!, $profile: DeliveryProfileInput!) {
        deliveryProfileUpdate(id: $id, profile: $profile) {
          profile {
            id
            name
            profileLocationGroups {
              locationGroup {
                id
                locations(first: 5) {
                  nodes {
                    name
                    address {
                      country
                    }
                  }
                }
              }
              locationGroupZones(first: 2) {
                edges {
                  node {
                    zone {
                      id
                      name
                      countries {
                        code {
                          countryCode
                        }
                        provinces {
                          code
                        }
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
          "id": "gid://shopify/DeliveryProfile/593363170",
          "profile": {
              "name": "Sample Updated Delivery Profile",
              "locationGroupsToCreate": [
                  {
                      "locationsToAdd": [
                          "gid://shopify/Location/415211365"
                      ],
                      "zonesToCreate": [
                          {
                              "name": "USA Zone",
                              "countries": {
                                  "code": "US",
                                  "provinces": [
                                      {
                                          "code": "CO"
                                      }
                                  ]
                              },
                              "methodDefinitionsToCreate": [
                                  {
                                      "name": "Standard",
                                      "rateDefinition": {
                                          "price": {
                                              "amount": 1,
                                              "currencyCode": "USD"
                                          }
                                      }
                                  }
                              ]
                          },
                          {
                              "name": "Mexico Zone",
                              "countries": {
                                  "code": "MX",
                                  "provinces": [
                                      {
                                          "code": "MOR"
                                      }
                                  ]
                              },
                              "methodDefinitionsToCreate": [
                                  {
                                      "name": "Standard",
                                      "rateDefinition": {
                                          "price": {
                                              "amount": 1,
                                              "currencyCode": "USD"
                                          }
                                      }
                                  }
                              ]
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
  'mutation deliveryProfileUpdate($id: ID!, $profile: DeliveryProfileInput!) {
    deliveryProfileUpdate(id: $id, profile: $profile) {
      profile {
        id
        name
        profileLocationGroups {
          locationGroup {
            id
            locations(first: 5) {
              nodes {
                name
                address {
                  country
                }
              }
            }
          }
          locationGroupZones(first: 2) {
            edges {
              node {
                zone {
                  id
                  name
                  countries {
                    code {
                      countryCode
                    }
                    provinces {
                      code
                    }
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
    "id": "gid://shopify/DeliveryProfile/593363170",
    "profile": {
      "name": "Sample Updated Delivery Profile",
      "locationGroupsToCreate": [
        {
          "locationsToAdd": [
            "gid://shopify/Location/415211365"
          ],
          "zonesToCreate": [
            {
              "name": "USA Zone",
              "countries": {
                "code": "US",
                "provinces": [
                  {
                    "code": "CO"
                  }
                ]
              },
              "methodDefinitionsToCreate": [
                {
                  "name": "Standard",
                  "rateDefinition": {
                    "price": {
                      "amount": 1,
                      "currencyCode": "USD"
                    }
                  }
                }
              ]
            },
            {
              "name": "Mexico Zone",
              "countries": {
                "code": "MX",
                "provinces": [
                  {
                    "code": "MOR"
                  }
                ]
              },
              "methodDefinitionsToCreate": [
                {
                  "name": "Standard",
                  "rateDefinition": {
                    "price": {
                      "amount": 1,
                      "currencyCode": "USD"
                    }
                  }
                }
              ]
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
    "deliveryProfileUpdate": {
      "profile": {
        "id": "gid://shopify/DeliveryProfile/593363170",
        "name": "Sample Updated Delivery Profile",
        "profileLocationGroups": [
          {
            "locationGroup": {
              "id": "gid://shopify/DeliveryLocationGroup/955592432",
              "locations": {
                "nodes": [
                  {
                    "name": "Ottawa Store",
                    "address": {
                      "country": "Canada"
                    }
                  },
                  {
                    "name": "Shipping Origin",
                    "address": {
                      "country": "Canada"
                    }
                  }
                ]
              }
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
                            "countryCode": "CA"
                          },
                          "provinces": [
                            {
                              "code": "ON"
                            }
                          ]
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
              "id": "gid://shopify/DeliveryLocationGroup/982182450",
              "locations": {
                "nodes": [
                  {
                    "name": "US Store",
                    "address": {
                      "country": "United States"
                    }
                  }
                ]
              }
            },
            "locationGroupZones": {
              "edges": [
                {
                  "node": {
                    "zone": {
                      "id": "gid://shopify/DeliveryZone/1066475776",
                      "name": "Mexico Zone",
                      "countries": [
                        {
                          "code": {
                            "countryCode": "MX"
                          },
                          "provinces": [
                            {
                              "code": "MOR"
                            }
                          ]
                        }
                      ]
                    }
                  }
                },
                {
                  "node": {
                    "zone": {
                      "id": "gid://shopify/DeliveryZone/1066475775",
                      "name": "USA Zone",
                      "countries": [
                        {
                          "code": {
                            "countryCode": "US"
                          },
                          "provinces": [
                            {
                              "code": "CO"
                            }
                          ]
                        }
                      ]
                    }
                  }
                }
              ]
            }
          }
        ]
      },
      "userErrors": []
    }
  }
  ```

* ### deliveryProfileUpdate reference
