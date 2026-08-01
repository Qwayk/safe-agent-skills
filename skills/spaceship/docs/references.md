# Official sources

The tool boundary and behavior use these official Spaceship sources, checked on 2026-08-01:

- [Spaceship External API documentation](https://docs.spaceship.dev/)
- [Spaceship API Manager](https://www.spaceship.com/application/api-manager/)
- [Spaceship domains product page](https://www.spaceship.com/domains/)

The pinned OpenAPI 3.0 input is `openapi.json`, supplied separately for the source build. Its SHA-256 is `d4025290f62a5d14ad17142e2d75a59c19504f61066dfdaf7fab3d357cb75eeb`. The file defines 40 operations across 29 paths and 10 families.

The official descriptions for `domainDelete` and `getDomainPersonalNameserverHostInfo` say the operations are under development and return HTTP 501. The tool keeps both in the coverage ledger and refuses them locally.

No credentialed Spaceship request was used to confirm provider behavior. The source implementation is therefore live-unverified.
