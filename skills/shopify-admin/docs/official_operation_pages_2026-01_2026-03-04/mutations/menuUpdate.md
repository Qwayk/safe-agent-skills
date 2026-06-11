---
title: menuUpdate - GraphQL Admin
description: >-
  Updates a
  [`Menu`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Menu) for
  display on the storefront. Modifies the menu's title and navigation structure,
  including nested
  [`MenuItem`](https://shopify.dev/docs/api/admin-graphql/latest/objects/MenuItem)
  objects. You can update the handle for non-default menus.


  The items argument accepts a list of menu items with their nested structure.
  Each item can include nested items to create multi-level navigation
  hierarchies. Default menus have restricted updates—you can't change their
  handles.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/menuUpdate'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/menuUpdate.md'
---

# menu​Update

mutation

Requires `write_online_store_navigation` access scope.

Updates a [`Menu`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Menu) for display on the storefront. Modifies the menu's title and navigation structure, including nested [`MenuItem`](https://shopify.dev/docs/api/admin-graphql/latest/objects/MenuItem) objects. You can update the handle for non-default menus.

The items argument accepts a list of menu items with their nested structure. Each item can include nested items to create multi-level navigation hierarchies. Default menus have restricted updates—you can't change their handles.

## Arguments

* handle

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The menu's handle.

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  ID of the menu to be updated.

* items

  [\[Menu​Item​Update​Input!\]!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/MenuItemUpdateInput)

  required

  List of the menu's items.

* title

  [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  required

  The menu's title.

***

## Menu​Update​Payload returns

* menu

  [Menu](https://shopify.dev/docs/api/admin-graphql/latest/objects/Menu)

  The updated menu.

* user​Errors

  [\[Menu​Update​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MenuUpdateUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Update a menu

  #### Description

  Update a menu

  #### Query

  ```graphql
  mutation UpdateMenu($id: ID!, $title: String!, $handle: String!, $items: [MenuItemUpdateInput!]!) {
    menuUpdate(id: $id, title: $title, handle: $handle, items: $items) {
      menu {
        id
        handle
        items {
          id
          title
          items {
            id
            title
          }
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/Menu/442047006",
    "title": "updated menu",
    "handle": "danielstuff-main-menu",
    "items": [
      {
        "id": "gid://shopify/MenuItem/398712010",
        "title": "Electronics",
        "url": "collection/tables",
        "resourceId": "gid://shopify/Collection/71762467",
        "type": "COLLECTION",
        "items": []
      },
      {
        "id": "gid://shopify/MenuItem/643685044",
        "title": "Furniture",
        "url": "/collections/furniture",
        "resourceId": "gid://shopify/Collection/643685044",
        "type": "COLLECTION",
        "items": [
          {
            "id": "gid://shopify/MenuItem/927352226",
            "title": "Updated Living Room",
            "url": "/collections/living-room",
            "resourceId": "gid://shopify/Collection/927352226",
            "type": "COLLECTION",
            "items": [
              {
                "id": "gid://shopify/MenuItem/307741084",
                "title": "Sofa",
                "url": "/collections/sofa",
                "resourceId": "gid://shopify/Collection/307741084",
                "type": "COLLECTION",
                "items": []
              },
              {
                "id": "gid://shopify/MenuItem/375350346",
                "title": "Sound System",
                "url": "/collections/sound-system",
                "resourceId": "gid://shopify/Collection/375350346",
                "type": "COLLECTION",
                "items": []
              },
              {
                "id": "gid://shopify/MenuItem/837241978",
                "title": "Massage Chairs",
                "url": "/collections/massage%20chairs",
                "resourceId": "gid://shopify/Collection/837241978",
                "type": "COLLECTION",
                "items": []
              },
              {
                "id": "gid://shopify/MenuItem/960081962",
                "title": "Living Room Rugs",
                "url": "/collections/living%20room%20rugs",
                "resourceId": "gid://shopify/Collection/960081962",
                "type": "COLLECTION",
                "items": []
              }
            ]
          },
          {
            "id": "gid://shopify/MenuItem/715378231",
            "title": "Kitchen",
            "url": "/collections/kitchen",
            "resourceId": "gid://shopify/Collection/715378231",
            "type": "COLLECTION",
            "items": [
              {
                "id": "gid://shopify/MenuItem/108641250",
                "title": "Chairs",
                "url": "/collections/chairs",
                "resourceId": "gid://shopify/Collection/108641250",
                "type": "COLLECTION",
                "items": []
              },
              {
                "id": "gid://shopify/MenuItem/71762467",
                "title": "Tables",
                "url": "/collections/tables",
                "resourceId": "gid://shopify/Collection/71762467",
                "type": "COLLECTION",
                "items": []
              },
              {
                "id": "gid://shopify/MenuItem/826396515",
                "title": "Kitchen Rugs",
                "url": "/collections/kitchen%20rugs",
                "resourceId": "gid://shopify/Collection/826396515",
                "type": "COLLECTION",
                "items": []
              }
            ]
          }
        ]
      },
      {
        "id": "gid://shopify/MenuItem/698896745",
        "title": "Mega Sofa Sale",
        "url": "/collections/mega%20sale",
        "resourceId": "gid://shopify/Collection/307741084",
        "type": "COLLECTION",
        "items": []
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
  "query": "mutation UpdateMenu($id: ID!, $title: String!, $handle: String!, $items: [MenuItemUpdateInput!]!) { menuUpdate(id: $id, title: $title, handle: $handle, items: $items) { menu { id handle items { id title items { id title } } } } }",
   "variables": {
      "id": "gid://shopify/Menu/442047006",
      "title": "updated menu",
      "handle": "danielstuff-main-menu",
      "items": [
        {
          "id": "gid://shopify/MenuItem/398712010",
          "title": "Electronics",
          "url": "collection/tables",
          "resourceId": "gid://shopify/Collection/71762467",
          "type": "COLLECTION",
          "items": []
        },
        {
          "id": "gid://shopify/MenuItem/643685044",
          "title": "Furniture",
          "url": "/collections/furniture",
          "resourceId": "gid://shopify/Collection/643685044",
          "type": "COLLECTION",
          "items": [
            {
              "id": "gid://shopify/MenuItem/927352226",
              "title": "Updated Living Room",
              "url": "/collections/living-room",
              "resourceId": "gid://shopify/Collection/927352226",
              "type": "COLLECTION",
              "items": [
                {
                  "id": "gid://shopify/MenuItem/307741084",
                  "title": "Sofa",
                  "url": "/collections/sofa",
                  "resourceId": "gid://shopify/Collection/307741084",
                  "type": "COLLECTION",
                  "items": []
                },
                {
                  "id": "gid://shopify/MenuItem/375350346",
                  "title": "Sound System",
                  "url": "/collections/sound-system",
                  "resourceId": "gid://shopify/Collection/375350346",
                  "type": "COLLECTION",
                  "items": []
                },
                {
                  "id": "gid://shopify/MenuItem/837241978",
                  "title": "Massage Chairs",
                  "url": "/collections/massage%20chairs",
                  "resourceId": "gid://shopify/Collection/837241978",
                  "type": "COLLECTION",
                  "items": []
                },
                {
                  "id": "gid://shopify/MenuItem/960081962",
                  "title": "Living Room Rugs",
                  "url": "/collections/living%20room%20rugs",
                  "resourceId": "gid://shopify/Collection/960081962",
                  "type": "COLLECTION",
                  "items": []
                }
              ]
            },
            {
              "id": "gid://shopify/MenuItem/715378231",
              "title": "Kitchen",
              "url": "/collections/kitchen",
              "resourceId": "gid://shopify/Collection/715378231",
              "type": "COLLECTION",
              "items": [
                {
                  "id": "gid://shopify/MenuItem/108641250",
                  "title": "Chairs",
                  "url": "/collections/chairs",
                  "resourceId": "gid://shopify/Collection/108641250",
                  "type": "COLLECTION",
                  "items": []
                },
                {
                  "id": "gid://shopify/MenuItem/71762467",
                  "title": "Tables",
                  "url": "/collections/tables",
                  "resourceId": "gid://shopify/Collection/71762467",
                  "type": "COLLECTION",
                  "items": []
                },
                {
                  "id": "gid://shopify/MenuItem/826396515",
                  "title": "Kitchen Rugs",
                  "url": "/collections/kitchen%20rugs",
                  "resourceId": "gid://shopify/Collection/826396515",
                  "type": "COLLECTION",
                  "items": []
                }
              ]
            }
          ]
        },
        {
          "id": "gid://shopify/MenuItem/698896745",
          "title": "Mega Sofa Sale",
          "url": "/collections/mega%20sale",
          "resourceId": "gid://shopify/Collection/307741084",
          "type": "COLLECTION",
          "items": []
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
    mutation UpdateMenu($id: ID!, $title: String!, $handle: String!, $items: [MenuItemUpdateInput!]!) {
      menuUpdate(id: $id, title: $title, handle: $handle, items: $items) {
        menu {
          id
          handle
          items {
            id
            title
            items {
              id
              title
            }
          }
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/Menu/442047006",
          "title": "updated menu",
          "handle": "danielstuff-main-menu",
          "items": [
              {
                  "id": "gid://shopify/MenuItem/398712010",
                  "title": "Electronics",
                  "url": "collection/tables",
                  "resourceId": "gid://shopify/Collection/71762467",
                  "type": "COLLECTION",
                  "items": []
              },
              {
                  "id": "gid://shopify/MenuItem/643685044",
                  "title": "Furniture",
                  "url": "/collections/furniture",
                  "resourceId": "gid://shopify/Collection/643685044",
                  "type": "COLLECTION",
                  "items": [
                      {
                          "id": "gid://shopify/MenuItem/927352226",
                          "title": "Updated Living Room",
                          "url": "/collections/living-room",
                          "resourceId": "gid://shopify/Collection/927352226",
                          "type": "COLLECTION",
                          "items": [
                              {
                                  "id": "gid://shopify/MenuItem/307741084",
                                  "title": "Sofa",
                                  "url": "/collections/sofa",
                                  "resourceId": "gid://shopify/Collection/307741084",
                                  "type": "COLLECTION",
                                  "items": []
                              },
                              {
                                  "id": "gid://shopify/MenuItem/375350346",
                                  "title": "Sound System",
                                  "url": "/collections/sound-system",
                                  "resourceId": "gid://shopify/Collection/375350346",
                                  "type": "COLLECTION",
                                  "items": []
                              },
                              {
                                  "id": "gid://shopify/MenuItem/837241978",
                                  "title": "Massage Chairs",
                                  "url": "/collections/massage%20chairs",
                                  "resourceId": "gid://shopify/Collection/837241978",
                                  "type": "COLLECTION",
                                  "items": []
                              },
                              {
                                  "id": "gid://shopify/MenuItem/960081962",
                                  "title": "Living Room Rugs",
                                  "url": "/collections/living%20room%20rugs",
                                  "resourceId": "gid://shopify/Collection/960081962",
                                  "type": "COLLECTION",
                                  "items": []
                              }
                          ]
                      },
                      {
                          "id": "gid://shopify/MenuItem/715378231",
                          "title": "Kitchen",
                          "url": "/collections/kitchen",
                          "resourceId": "gid://shopify/Collection/715378231",
                          "type": "COLLECTION",
                          "items": [
                              {
                                  "id": "gid://shopify/MenuItem/108641250",
                                  "title": "Chairs",
                                  "url": "/collections/chairs",
                                  "resourceId": "gid://shopify/Collection/108641250",
                                  "type": "COLLECTION",
                                  "items": []
                              },
                              {
                                  "id": "gid://shopify/MenuItem/71762467",
                                  "title": "Tables",
                                  "url": "/collections/tables",
                                  "resourceId": "gid://shopify/Collection/71762467",
                                  "type": "COLLECTION",
                                  "items": []
                              },
                              {
                                  "id": "gid://shopify/MenuItem/826396515",
                                  "title": "Kitchen Rugs",
                                  "url": "/collections/kitchen%20rugs",
                                  "resourceId": "gid://shopify/Collection/826396515",
                                  "type": "COLLECTION",
                                  "items": []
                              }
                          ]
                      }
                  ]
              },
              {
                  "id": "gid://shopify/MenuItem/698896745",
                  "title": "Mega Sofa Sale",
                  "url": "/collections/mega%20sale",
                  "resourceId": "gid://shopify/Collection/307741084",
                  "type": "COLLECTION",
                  "items": []
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
    mutation UpdateMenu($id: ID!, $title: String!, $handle: String!, $items: [MenuItemUpdateInput!]!) {
      menuUpdate(id: $id, title: $title, handle: $handle, items: $items) {
        menu {
          id
          handle
          items {
            id
            title
            items {
              id
              title
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/Menu/442047006",
    "title": "updated menu",
    "handle": "danielstuff-main-menu",
    "items": [
      {
        "id": "gid://shopify/MenuItem/398712010",
        "title": "Electronics",
        "url": "collection/tables",
        "resourceId": "gid://shopify/Collection/71762467",
        "type": "COLLECTION",
        "items": []
      },
      {
        "id": "gid://shopify/MenuItem/643685044",
        "title": "Furniture",
        "url": "/collections/furniture",
        "resourceId": "gid://shopify/Collection/643685044",
        "type": "COLLECTION",
        "items": [
          {
            "id": "gid://shopify/MenuItem/927352226",
            "title": "Updated Living Room",
            "url": "/collections/living-room",
            "resourceId": "gid://shopify/Collection/927352226",
            "type": "COLLECTION",
            "items": [
              {
                "id": "gid://shopify/MenuItem/307741084",
                "title": "Sofa",
                "url": "/collections/sofa",
                "resourceId": "gid://shopify/Collection/307741084",
                "type": "COLLECTION",
                "items": []
              },
              {
                "id": "gid://shopify/MenuItem/375350346",
                "title": "Sound System",
                "url": "/collections/sound-system",
                "resourceId": "gid://shopify/Collection/375350346",
                "type": "COLLECTION",
                "items": []
              },
              {
                "id": "gid://shopify/MenuItem/837241978",
                "title": "Massage Chairs",
                "url": "/collections/massage%20chairs",
                "resourceId": "gid://shopify/Collection/837241978",
                "type": "COLLECTION",
                "items": []
              },
              {
                "id": "gid://shopify/MenuItem/960081962",
                "title": "Living Room Rugs",
                "url": "/collections/living%20room%20rugs",
                "resourceId": "gid://shopify/Collection/960081962",
                "type": "COLLECTION",
                "items": []
              }
            ]
          },
          {
            "id": "gid://shopify/MenuItem/715378231",
            "title": "Kitchen",
            "url": "/collections/kitchen",
            "resourceId": "gid://shopify/Collection/715378231",
            "type": "COLLECTION",
            "items": [
              {
                "id": "gid://shopify/MenuItem/108641250",
                "title": "Chairs",
                "url": "/collections/chairs",
                "resourceId": "gid://shopify/Collection/108641250",
                "type": "COLLECTION",
                "items": []
              },
              {
                "id": "gid://shopify/MenuItem/71762467",
                "title": "Tables",
                "url": "/collections/tables",
                "resourceId": "gid://shopify/Collection/71762467",
                "type": "COLLECTION",
                "items": []
              },
              {
                "id": "gid://shopify/MenuItem/826396515",
                "title": "Kitchen Rugs",
                "url": "/collections/kitchen%20rugs",
                "resourceId": "gid://shopify/Collection/826396515",
                "type": "COLLECTION",
                "items": []
              }
            ]
          }
        ]
      },
      {
        "id": "gid://shopify/MenuItem/698896745",
        "title": "Mega Sofa Sale",
        "url": "/collections/mega%20sale",
        "resourceId": "gid://shopify/Collection/307741084",
        "type": "COLLECTION",
        "items": []
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
      "query": `mutation UpdateMenu($id: ID!, $title: String!, $handle: String!, $items: [MenuItemUpdateInput!]!) {
        menuUpdate(id: $id, title: $title, handle: $handle, items: $items) {
          menu {
            id
            handle
            items {
              id
              title
              items {
                id
                title
              }
            }
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/Menu/442047006",
          "title": "updated menu",
          "handle": "danielstuff-main-menu",
          "items": [
              {
                  "id": "gid://shopify/MenuItem/398712010",
                  "title": "Electronics",
                  "url": "collection/tables",
                  "resourceId": "gid://shopify/Collection/71762467",
                  "type": "COLLECTION",
                  "items": []
              },
              {
                  "id": "gid://shopify/MenuItem/643685044",
                  "title": "Furniture",
                  "url": "/collections/furniture",
                  "resourceId": "gid://shopify/Collection/643685044",
                  "type": "COLLECTION",
                  "items": [
                      {
                          "id": "gid://shopify/MenuItem/927352226",
                          "title": "Updated Living Room",
                          "url": "/collections/living-room",
                          "resourceId": "gid://shopify/Collection/927352226",
                          "type": "COLLECTION",
                          "items": [
                              {
                                  "id": "gid://shopify/MenuItem/307741084",
                                  "title": "Sofa",
                                  "url": "/collections/sofa",
                                  "resourceId": "gid://shopify/Collection/307741084",
                                  "type": "COLLECTION",
                                  "items": []
                              },
                              {
                                  "id": "gid://shopify/MenuItem/375350346",
                                  "title": "Sound System",
                                  "url": "/collections/sound-system",
                                  "resourceId": "gid://shopify/Collection/375350346",
                                  "type": "COLLECTION",
                                  "items": []
                              },
                              {
                                  "id": "gid://shopify/MenuItem/837241978",
                                  "title": "Massage Chairs",
                                  "url": "/collections/massage%20chairs",
                                  "resourceId": "gid://shopify/Collection/837241978",
                                  "type": "COLLECTION",
                                  "items": []
                              },
                              {
                                  "id": "gid://shopify/MenuItem/960081962",
                                  "title": "Living Room Rugs",
                                  "url": "/collections/living%20room%20rugs",
                                  "resourceId": "gid://shopify/Collection/960081962",
                                  "type": "COLLECTION",
                                  "items": []
                              }
                          ]
                      },
                      {
                          "id": "gid://shopify/MenuItem/715378231",
                          "title": "Kitchen",
                          "url": "/collections/kitchen",
                          "resourceId": "gid://shopify/Collection/715378231",
                          "type": "COLLECTION",
                          "items": [
                              {
                                  "id": "gid://shopify/MenuItem/108641250",
                                  "title": "Chairs",
                                  "url": "/collections/chairs",
                                  "resourceId": "gid://shopify/Collection/108641250",
                                  "type": "COLLECTION",
                                  "items": []
                              },
                              {
                                  "id": "gid://shopify/MenuItem/71762467",
                                  "title": "Tables",
                                  "url": "/collections/tables",
                                  "resourceId": "gid://shopify/Collection/71762467",
                                  "type": "COLLECTION",
                                  "items": []
                              },
                              {
                                  "id": "gid://shopify/MenuItem/826396515",
                                  "title": "Kitchen Rugs",
                                  "url": "/collections/kitchen%20rugs",
                                  "resourceId": "gid://shopify/Collection/826396515",
                                  "type": "COLLECTION",
                                  "items": []
                              }
                          ]
                      }
                  ]
              },
              {
                  "id": "gid://shopify/MenuItem/698896745",
                  "title": "Mega Sofa Sale",
                  "url": "/collections/mega%20sale",
                  "resourceId": "gid://shopify/Collection/307741084",
                  "type": "COLLECTION",
                  "items": []
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
  'mutation UpdateMenu($id: ID!, $title: String!, $handle: String!, $items: [MenuItemUpdateInput!]!) {
    menuUpdate(id: $id, title: $title, handle: $handle, items: $items) {
      menu {
        id
        handle
        items {
          id
          title
          items {
            id
            title
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/Menu/442047006",
    "title": "updated menu",
    "handle": "danielstuff-main-menu",
    "items": [
      {
        "id": "gid://shopify/MenuItem/398712010",
        "title": "Electronics",
        "url": "collection/tables",
        "resourceId": "gid://shopify/Collection/71762467",
        "type": "COLLECTION",
        "items": []
      },
      {
        "id": "gid://shopify/MenuItem/643685044",
        "title": "Furniture",
        "url": "/collections/furniture",
        "resourceId": "gid://shopify/Collection/643685044",
        "type": "COLLECTION",
        "items": [
          {
            "id": "gid://shopify/MenuItem/927352226",
            "title": "Updated Living Room",
            "url": "/collections/living-room",
            "resourceId": "gid://shopify/Collection/927352226",
            "type": "COLLECTION",
            "items": [
              {
                "id": "gid://shopify/MenuItem/307741084",
                "title": "Sofa",
                "url": "/collections/sofa",
                "resourceId": "gid://shopify/Collection/307741084",
                "type": "COLLECTION",
                "items": []
              },
              {
                "id": "gid://shopify/MenuItem/375350346",
                "title": "Sound System",
                "url": "/collections/sound-system",
                "resourceId": "gid://shopify/Collection/375350346",
                "type": "COLLECTION",
                "items": []
              },
              {
                "id": "gid://shopify/MenuItem/837241978",
                "title": "Massage Chairs",
                "url": "/collections/massage%20chairs",
                "resourceId": "gid://shopify/Collection/837241978",
                "type": "COLLECTION",
                "items": []
              },
              {
                "id": "gid://shopify/MenuItem/960081962",
                "title": "Living Room Rugs",
                "url": "/collections/living%20room%20rugs",
                "resourceId": "gid://shopify/Collection/960081962",
                "type": "COLLECTION",
                "items": []
              }
            ]
          },
          {
            "id": "gid://shopify/MenuItem/715378231",
            "title": "Kitchen",
            "url": "/collections/kitchen",
            "resourceId": "gid://shopify/Collection/715378231",
            "type": "COLLECTION",
            "items": [
              {
                "id": "gid://shopify/MenuItem/108641250",
                "title": "Chairs",
                "url": "/collections/chairs",
                "resourceId": "gid://shopify/Collection/108641250",
                "type": "COLLECTION",
                "items": []
              },
              {
                "id": "gid://shopify/MenuItem/71762467",
                "title": "Tables",
                "url": "/collections/tables",
                "resourceId": "gid://shopify/Collection/71762467",
                "type": "COLLECTION",
                "items": []
              },
              {
                "id": "gid://shopify/MenuItem/826396515",
                "title": "Kitchen Rugs",
                "url": "/collections/kitchen%20rugs",
                "resourceId": "gid://shopify/Collection/826396515",
                "type": "COLLECTION",
                "items": []
              }
            ]
          }
        ]
      },
      {
        "id": "gid://shopify/MenuItem/698896745",
        "title": "Mega Sofa Sale",
        "url": "/collections/mega%20sale",
        "resourceId": "gid://shopify/Collection/307741084",
        "type": "COLLECTION",
        "items": []
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "menuUpdate": {
      "menu": {
        "id": "gid://shopify/Menu/442047006",
        "handle": "danielstuff-main-menu",
        "items": [
          {
            "id": "gid://shopify/MenuItem/398712010",
            "title": "Electronics",
            "items": []
          },
          {
            "id": "gid://shopify/MenuItem/643685044",
            "title": "Furniture",
            "items": [
              {
                "id": "gid://shopify/MenuItem/927352226",
                "title": "Updated Living Room"
              },
              {
                "id": "gid://shopify/MenuItem/715378231",
                "title": "Kitchen"
              }
            ]
          },
          {
            "id": "gid://shopify/MenuItem/698896745",
            "title": "Mega Sofa Sale",
            "items": []
          }
        ]
      }
    }
  }
  ```

* ### menuUpdate reference
