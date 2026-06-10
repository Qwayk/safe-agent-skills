---
title: menuCreate - GraphQL Admin
description: >-
  Creates a navigation
  [`Menu`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Menu) for
  the online store. Menus organize links that help customers navigate to
  [collections](https://shopify.dev/docs/api/admin-graphql/latest/objects/Collection),
  [products](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product),
  [pages](https://shopify.dev/docs/api/admin-graphql/latest/objects/Page),
  [blogs](https://shopify.dev/docs/api/admin-graphql/latest/objects/Blog), and
  custom URLs.


  Each menu requires a unique handle for identification and can contain multiple
  [`MenuItem`](https://shopify.dev/docs/api/admin-graphql/latest/objects/MenuItem)
  objects with nested sub-items up to three levels deep.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/menuCreate'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/menuCreate.md'
---

# menu​Create

mutation

Requires `write_online_store_navigation` access scope.

Creates a navigation [`Menu`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Menu) for the online store. Menus organize links that help customers navigate to [collections](https://shopify.dev/docs/api/admin-graphql/latest/objects/Collection), [products](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product), [pages](https://shopify.dev/docs/api/admin-graphql/latest/objects/Page), [blogs](https://shopify.dev/docs/api/admin-graphql/latest/objects/Blog), and custom URLs.

Each menu requires a unique handle for identification and can contain multiple [`MenuItem`](https://shopify.dev/docs/api/admin-graphql/latest/objects/MenuItem) objects with nested sub-items up to three levels deep.

## Arguments

* handle

  [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  required

  The menu's handle.

* items

  [\[Menu​Item​Create​Input!\]!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/MenuItemCreateInput)

  required

  List of the menu's items.

* title

  [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  required

  The menu's title.

***

## Menu​Create​Payload returns

* menu

  [Menu](https://shopify.dev/docs/api/admin-graphql/latest/objects/Menu)

  The created menu.

* user​Errors

  [\[Menu​Create​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MenuCreateUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create a menu

  #### Description

  Create a menu with sub items

  #### Query

  ```graphql
  mutation CreateMenu($title: String!, $handle: String!, $items: [MenuItemCreateInput!]!) {
    menuCreate(title: $title, handle: $handle, items: $items) {
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
    "title": "Sidebar",
    "handle": "sidebar",
    "items": [
      {
        "title": "Collections",
        "type": "COLLECTION",
        "url": "/collection",
        "items": [
          {
            "title": "Bestsellers",
            "type": "COLLECTION",
            "resourceId": "gid://shopify/Collection/1007901140",
            "url": "/collection/bestsellers/new",
            "tags": [
              "new"
            ],
            "items": []
          }
        ]
      },
      {
        "title": "Products",
        "type": "CATALOG",
        "url": "/collections/all",
        "items": []
      },
      {
        "title": "About us",
        "type": "PAGE",
        "resourceId": "gid://shopify/Page/905192165",
        "url": "/pages/about-us",
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
  "query": "mutation CreateMenu($title: String!, $handle: String!, $items: [MenuItemCreateInput!]!) { menuCreate(title: $title, handle: $handle, items: $items) { menu { id handle items { id title items { id title } } } } }",
   "variables": {
      "title": "Sidebar",
      "handle": "sidebar",
      "items": [
        {
          "title": "Collections",
          "type": "COLLECTION",
          "url": "/collection",
          "items": [
            {
              "title": "Bestsellers",
              "type": "COLLECTION",
              "resourceId": "gid://shopify/Collection/1007901140",
              "url": "/collection/bestsellers/new",
              "tags": [
                "new"
              ],
              "items": []
            }
          ]
        },
        {
          "title": "Products",
          "type": "CATALOG",
          "url": "/collections/all",
          "items": []
        },
        {
          "title": "About us",
          "type": "PAGE",
          "resourceId": "gid://shopify/Page/905192165",
          "url": "/pages/about-us",
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
    mutation CreateMenu($title: String!, $handle: String!, $items: [MenuItemCreateInput!]!) {
      menuCreate(title: $title, handle: $handle, items: $items) {
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
          "title": "Sidebar",
          "handle": "sidebar",
          "items": [
              {
                  "title": "Collections",
                  "type": "COLLECTION",
                  "url": "/collection",
                  "items": [
                      {
                          "title": "Bestsellers",
                          "type": "COLLECTION",
                          "resourceId": "gid://shopify/Collection/1007901140",
                          "url": "/collection/bestsellers/new",
                          "tags": [
                              "new"
                          ],
                          "items": []
                      }
                  ]
              },
              {
                  "title": "Products",
                  "type": "CATALOG",
                  "url": "/collections/all",
                  "items": []
              },
              {
                  "title": "About us",
                  "type": "PAGE",
                  "resourceId": "gid://shopify/Page/905192165",
                  "url": "/pages/about-us",
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
    mutation CreateMenu($title: String!, $handle: String!, $items: [MenuItemCreateInput!]!) {
      menuCreate(title: $title, handle: $handle, items: $items) {
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
    "title": "Sidebar",
    "handle": "sidebar",
    "items": [
      {
        "title": "Collections",
        "type": "COLLECTION",
        "url": "/collection",
        "items": [
          {
            "title": "Bestsellers",
            "type": "COLLECTION",
            "resourceId": "gid://shopify/Collection/1007901140",
            "url": "/collection/bestsellers/new",
            "tags": [
              "new"
            ],
            "items": []
          }
        ]
      },
      {
        "title": "Products",
        "type": "CATALOG",
        "url": "/collections/all",
        "items": []
      },
      {
        "title": "About us",
        "type": "PAGE",
        "resourceId": "gid://shopify/Page/905192165",
        "url": "/pages/about-us",
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
      "query": `mutation CreateMenu($title: String!, $handle: String!, $items: [MenuItemCreateInput!]!) {
        menuCreate(title: $title, handle: $handle, items: $items) {
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
          "title": "Sidebar",
          "handle": "sidebar",
          "items": [
              {
                  "title": "Collections",
                  "type": "COLLECTION",
                  "url": "/collection",
                  "items": [
                      {
                          "title": "Bestsellers",
                          "type": "COLLECTION",
                          "resourceId": "gid://shopify/Collection/1007901140",
                          "url": "/collection/bestsellers/new",
                          "tags": [
                              "new"
                          ],
                          "items": []
                      }
                  ]
              },
              {
                  "title": "Products",
                  "type": "CATALOG",
                  "url": "/collections/all",
                  "items": []
              },
              {
                  "title": "About us",
                  "type": "PAGE",
                  "resourceId": "gid://shopify/Page/905192165",
                  "url": "/pages/about-us",
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
  'mutation CreateMenu($title: String!, $handle: String!, $items: [MenuItemCreateInput!]!) {
    menuCreate(title: $title, handle: $handle, items: $items) {
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
    "title": "Sidebar",
    "handle": "sidebar",
    "items": [
      {
        "title": "Collections",
        "type": "COLLECTION",
        "url": "/collection",
        "items": [
          {
            "title": "Bestsellers",
            "type": "COLLECTION",
            "resourceId": "gid://shopify/Collection/1007901140",
            "url": "/collection/bestsellers/new",
            "tags": [
              "new"
            ],
            "items": []
          }
        ]
      },
      {
        "title": "Products",
        "type": "CATALOG",
        "url": "/collections/all",
        "items": []
      },
      {
        "title": "About us",
        "type": "PAGE",
        "resourceId": "gid://shopify/Page/905192165",
        "url": "/pages/about-us",
        "items": []
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "menuCreate": {
      "menu": null
    }
  }
  ```

* ### menuCreate reference
