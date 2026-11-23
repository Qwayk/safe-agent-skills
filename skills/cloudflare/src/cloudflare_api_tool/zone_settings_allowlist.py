# Zone setting paths from the pinned Cloudflare API snapshot.
from __future__ import annotations

ALLOWED_ZONE_SETTING_PATHS: frozenset[str] = frozenset(
    [
        'aegis',
        'fonts',
        'origin_h2_max_streams',
        'origin_max_http_version',
        'rum',
        'speed_brain',
        'ssl_automatic_mode',
    ]
)
