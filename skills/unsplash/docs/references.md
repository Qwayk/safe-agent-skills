# References (sources)

Purpose:
- Record the sources this tool relies on (so behavior is auditable and reproducible).
- Prefer official docs; only use other sources when required for a specific detail.

## Official docs

- Unsplash API documentation: https://unsplash.com/documentation
- Authorization (Client-ID / Bearer): https://unsplash.com/documentation#authorization
- Rate limiting: https://unsplash.com/documentation#rate-limiting
- Pagination (includes `per_page` max 30): https://unsplash.com/documentation#pagination
- Photos: https://unsplash.com/documentation#photos
  - List photos (`GET /photos`): https://unsplash.com/documentation#list-photos
  - Get a photo (`GET /photos/:id`): https://unsplash.com/documentation#get-a-photo
  - Get random photos (`GET /photos/random`): https://unsplash.com/documentation#get-a-random-photo
  - Photo stats (`GET /photos/:id/statistics`): https://unsplash.com/documentation#get-a-photos-statistics
- Track a photo download (`GET /photos/:id/download`): https://unsplash.com/documentation#track-a-photo-download
- Collections: https://unsplash.com/documentation#collections
  - List collections (`GET /collections`): https://unsplash.com/documentation#list-collections
  - Get a collection (`GET /collections/:id`): https://unsplash.com/documentation#get-a-collection
  - Collection photos (`GET /collections/:id/photos`): https://unsplash.com/documentation#get-a-collections-photos
  - Related collections (`GET /collections/:id/related`): https://unsplash.com/documentation#get-a-collections-related-collections
- Topics: https://unsplash.com/documentation#topics
  - List topics (`GET /topics`): https://unsplash.com/documentation#list-topics
  - Get a topic (`GET /topics/:id`): https://unsplash.com/documentation#get-a-topic
  - Topic photos (`GET /topics/:id/photos`): https://unsplash.com/documentation#get-a-topics-photos
- Search: https://unsplash.com/documentation#search
  - Search photos (`GET /search/photos`): https://unsplash.com/documentation#search-photos
  - Search collections (`GET /search/collections`): https://unsplash.com/documentation#search-collections
  - Search users (`GET /search/users`): https://unsplash.com/documentation#search-users
- Users: list collections + user statistics endpoints: https://unsplash.com/documentation#users
  - List a user’s photos (`GET /users/:username/photos`): https://unsplash.com/documentation#list-a-users-photos
  - List a user’s likes (`GET /users/:username/likes`): https://unsplash.com/documentation#list-a-users-liked-photos
  - List a user’s collections (`GET /users/:username/collections`): https://unsplash.com/documentation#list-a-users-collections
  - Get a user’s statistics (`GET /users/:username/statistics`): https://unsplash.com/documentation#get-a-users-statistics
- Global stats: https://unsplash.com/documentation#stats
  - Totals (`GET /stats/total`): https://unsplash.com/documentation#totals
  - Month (`GET /stats/month`): https://unsplash.com/documentation#month
- Download guideline (“Triggering a download”): https://help.unsplash.com/api-guidelines/guideline-triggering-a-download

Last verified (UTC): 2026-02-03
