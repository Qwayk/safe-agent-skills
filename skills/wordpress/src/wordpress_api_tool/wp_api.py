from __future__ import annotations

import base64
import dataclasses
from typing import Any
from urllib.parse import urlparse

from .config import Config
from .http import HttpClient


def _basic_auth_header(username: str, app_password: str) -> str:
    token = base64.b64encode(f"{username}:{app_password}".encode()).decode("ascii")
    return f"Basic {token}"


@dataclasses.dataclass(frozen=True)
class WordPressApi:
    base_url: str
    http: HttpClient
    auth_header: str

    @classmethod
    def from_config(cls, cfg: Config, http: HttpClient) -> WordPressApi:
        return cls(
            base_url=cfg.base_url.rstrip("/") + "/wp-json/wp/v2",
            http=http,
            auth_header=_basic_auth_header(cfg.username, cfg.app_password),
        )

    def _headers(self) -> dict[str, str]:
        return {"Authorization": self.auth_header, "Accept": "application/json"}

    def get(self, path: str, *, params: dict[str, Any] | None = None, retries: int = 1) -> Any:
        return self.http.request(
            "GET", self.base_url + path, headers=self._headers(), params=params, retries=retries
        ).json()

    def post(self, path: str, *, payload: dict[str, Any]) -> Any:
        return self.http.request(
            "POST",
            self.base_url + path,
            headers=self._headers(),
            json_body=payload,
            retries=0,
        ).json()

    def list_collection(
        self,
        path: str,
        *,
        params: dict[str, Any] | None,
        context: str | None,
        limit: int,
        per_page: int | None,
        max_pages: int,
        retries: int = 1,
    ) -> dict[str, Any]:
        limit = max(int(limit), 1)
        if per_page is None:
            per_page = min(limit, 100)
        per_page = max(int(per_page), 1)
        if per_page > 100:
            raise RuntimeError("Refused: per_page must be <= 100")
        max_pages = max(int(max_pages), 1)
        if max_pages > 100:
            raise RuntimeError("Refused: max_pages must be <= 100")

        base_params: dict[str, Any] = {}
        if params:
            base_params.update(params)
        if context is not None and str(context).strip():
            base_params["context"] = str(context)
        base_params["per_page"] = str(per_page)

        out: list[Any] = []
        total: int | None = None
        total_pages: int | None = None

        def _parse_total(headers: dict[str, str]) -> None:
            nonlocal total, total_pages
            t = headers.get("x-wp-total")
            tp = headers.get("x-wp-totalpages")
            try:
                total = None if t is None else max(int(t), 0)
            except Exception:
                total = None
            try:
                total_pages = None if tp is None else max(int(tp), 1)
            except Exception:
                total_pages = None

        page_num = 1
        pages_fetched = 0
        stopped_due_to_limit = False
        last_page_num_fetched: int | None = None
        truncated = False
        truncated_reason: str | None = None

        while True:
            if pages_fetched >= max_pages:
                break
            if total_pages is not None and page_num > total_pages:
                break

            req = self.http.request(
                "GET",
                self.base_url + path,
                headers=self._headers(),
                params={**base_params, "page": str(page_num)},
                retries=retries,
            )
            last_page_num_fetched = page_num
            if pages_fetched == 0:
                _parse_total(req.headers)
            pages_fetched += 1

            batch = req.json()
            if not isinstance(batch, list):
                raise RuntimeError(f"Unexpected WordPress response for {path} (expected a list).")
            if not batch:
                break
            out.extend(batch)
            if len(out) >= limit:
                stopped_due_to_limit = True
                break
            page_num += 1

        items = out[:limit]
        if len(out) > limit:
            truncated = True
            truncated_reason = "limit"
        elif stopped_due_to_limit:
            can_prove_end = False
            if total is not None:
                can_prove_end = total <= len(items)
            elif total_pages is not None and last_page_num_fetched is not None:
                can_prove_end = last_page_num_fetched >= total_pages
            if not can_prove_end:
                truncated = True
                truncated_reason = "limit"

        if not truncated and pages_fetched >= max_pages:
            if total_pages is None or pages_fetched < total_pages:
                truncated = True
                truncated_reason = "max_pages"

        return {
            "items": items,
            "limit": limit,
            "truncated": truncated,
            "truncated_reason": truncated_reason,
            "total": total,
            "total_pages": total_pages,
            "pages_fetched": pages_fetched,
            "per_page": per_page,
        }

    # Auth
    def users_me(self) -> dict[str, Any]:
        return self.get("/users/me")

    # Settings (read-only)
    def settings(self, *, context: str = "view") -> dict[str, Any]:
        # Some WordPress versions only support `context=edit` for settings; omit for `view`.
        params = None
        if str(context).strip() and str(context) != "view":
            params = {"context": str(context)}
        res = self.get("/settings", params=params, retries=1)
        if not isinstance(res, dict):
            raise RuntimeError("Unexpected WordPress response for /settings (expected an object).")
        return res

    # Discovery (read-only)
    def types(self, *, context: str = "view") -> dict[str, Any]:
        res = self.get("/types", params={"context": str(context)}, retries=1)
        if not isinstance(res, dict):
            raise RuntimeError("Unexpected WordPress response for /types (expected an object).")
        return res

    def statuses(self, *, context: str = "view") -> dict[str, Any]:
        res = self.get("/statuses", params={"context": str(context)}, retries=1)
        if not isinstance(res, dict):
            raise RuntimeError("Unexpected WordPress response for /statuses (expected an object).")
        return res

    def taxonomies(self, *, context: str = "view") -> dict[str, Any]:
        res = self.get("/taxonomies", params={"context": str(context)}, retries=1)
        if not isinstance(res, dict):
            raise RuntimeError("Unexpected WordPress response for /taxonomies (expected an object).")
        return res

    # Posts
    def search_posts(self, *, post_type: str, query: str, limit: int) -> list[dict[str, Any]]:
        limit = max(int(limit), 1)
        per_page = min(limit, 100)
        out: list[dict[str, Any]] = []

        first = self.http.request(
            "GET",
            self.base_url + f"/{post_type}",
            headers=self._headers(),
            # WordPress defaults `status` to `publish` for collections; for migration work we need drafts too.
            params={
                "search": query,
                "context": "edit",
                "status": "any",
                "per_page": str(per_page),
                "page": "1",
            },
            retries=1,
        )
        batch = first.json()
        if not isinstance(batch, list):
            raise RuntimeError("Unexpected WordPress response for post search (expected a list).")
        out.extend(batch)

        total_pages_raw = first.headers.get("x-wp-totalpages", "1")
        try:
            total_pages = max(int(total_pages_raw), 1)
        except Exception:
            total_pages = 1

        page = 2
        while len(out) < limit and page <= total_pages:
            more = self.get(
                f"/{post_type}",
                params={
                    "search": query,
                    "context": "edit",
                    "status": "any",
                    "per_page": str(per_page),
                    "page": str(page),
                },
                retries=1,
            )
            if not more:
                break
            out.extend(more)
            page += 1

        return out[:limit]

    def post_by_slug(self, *, post_type: str, slug: str) -> dict[str, Any]:
        res = self.get(
            f"/{post_type}",
            params={"slug": slug, "context": "edit", "status": "any", "per_page": "100"},
        )
        if not res:
            raise RuntimeError(f"No {post_type} found for slug={slug!r}")
        if len(res) > 1:
            raise RuntimeError(f"Multiple {post_type} found for slug={slug!r}")
        return res[0]

    def post_by_id(self, *, post_type: str, post_id: int) -> dict[str, Any]:
        return self.get(f"/{post_type}/{post_id}", params={"context": "edit"})

    def update_post_content(self, *, post_type: str, post_id: int, content_raw: str) -> dict[str, Any]:
        return self.post(f"/{post_type}/{post_id}", payload={"content": content_raw})

    def update_post_status(self, *, post_type: str, post_id: int, status: str) -> dict[str, Any]:
        return self.post(f"/{post_type}/{post_id}", payload={"status": status})

    def update_post_terms(
        self,
        *,
        post_type: str,
        post_id: int,
        categories: list[int] | None,
        tags: list[int] | None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if categories is not None:
            payload["categories"] = [int(x) for x in categories]
        if tags is not None:
            payload["tags"] = [int(x) for x in tags]
        if not payload:
            raise RuntimeError("Refused: no terms provided to update")
        return self.post(f"/{post_type}/{post_id}", payload=payload)

    # Media
    def media_by_id(self, media_id: int) -> dict[str, Any]:
        return self.get(f"/media/{media_id}", params={"context": "edit"})

    def media_by_include(self, ids: list[int]) -> list[dict[str, Any]]:
        if not ids:
            return []

        # De-dupe while preserving order.
        seen = set()
        uniq: list[int] = []
        for i in ids:
            i = int(i)
            if i in seen:
                continue
            seen.add(i)
            uniq.append(i)

        out: list[dict[str, Any]] = []
        for start in range(0, len(uniq), 100):
            chunk = uniq[start : start + 100]
            include = ",".join(str(i) for i in chunk)
            out.extend(
                self.get(
                    "/media",
                    params={
                        "include": include,
                        "context": "edit",
                        "per_page": str(min(len(chunk), 100)),
                    },
                    retries=1,
                )
            )
        return out

    def media_search(self, *, query: str, limit: int = 25) -> list[dict[str, Any]]:
        limit = max(int(limit), 1)
        per_page = min(limit, 100)
        return self.get(
            "/media",
            params={"search": query, "context": "edit", "per_page": str(per_page), "page": "1"},
            retries=1,
        )

    def media_resolve_by_url(self, *, url: str) -> dict[str, Any]:
        """
        Best-effort resolver for a media item by its source_url.

        Strategy:
        - search media by filename (basename)
        - pick exact source_url match
        - refuse on ambiguity
        """
        parsed = urlparse(url)
        basename = (parsed.path or "").split("/")[-1]
        if not basename:
            raise RuntimeError("Refused: URL has no basename")
        candidates = self.media_search(query=basename, limit=100)
        exact = [m for m in candidates if isinstance(m, dict) and m.get("source_url") == url]
        if not exact:
            raise RuntimeError("No media item matched this URL")
        if len(exact) > 1:
            raise RuntimeError("Multiple media items matched this URL")
        return exact[0]

    # Users
    def user_by_id(self, user_id: int) -> dict[str, Any]:
        return self.get(f"/users/{int(user_id)}", params={"context": "edit"})

    # Terms
    def terms_by_include(self, *, taxonomy: str, ids: list[int]) -> list[dict[str, Any]]:
        if not ids:
            return []
        seen = set()
        uniq: list[int] = []
        for i in ids:
            i = int(i)
            if i in seen:
                continue
            seen.add(i)
            uniq.append(i)
        out: list[dict[str, Any]] = []
        for start in range(0, len(uniq), 100):
            chunk = uniq[start : start + 100]
            include = ",".join(str(i) for i in chunk)
            out.extend(
                self.get(
                    f"/{taxonomy}",
                    params={"include": include, "context": "edit", "per_page": str(min(len(chunk), 100))},
                    retries=1,
                )
            )
        return out

    def term_by_slug(self, *, taxonomy: str, slug: str, context: str = "view") -> dict[str, Any]:
        """
        Resolve a term by its slug within a taxonomy.

        Refuses on missing or ambiguous results.
        """
        taxonomy = str(taxonomy)
        slug = str(slug)
        res = self.get(
            f"/{taxonomy}",
            params={"slug": slug, "context": context, "per_page": "100"},
            retries=1,
        )
        if not isinstance(res, list):
            raise RuntimeError("Unexpected WordPress response for term slug lookup (expected a list).")
        if not res:
            raise RuntimeError(f"No term found for taxonomy={taxonomy!r} slug={slug!r}")
        if len(res) > 1:
            raise RuntimeError(f"Multiple terms found for taxonomy={taxonomy!r} slug={slug!r}")
        term = res[0]
        if not isinstance(term, dict):
            raise RuntimeError("Unexpected WordPress response for term slug lookup (expected an object).")
        return term

    def update_media(
        self,
        *,
        media_id: int,
        caption: str | None,
        alt_text: str | None,
        title: str | None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if caption is not None:
            payload["caption"] = caption
        if alt_text is not None:
            payload["alt_text"] = alt_text
        if title is not None:
            payload["title"] = title
        if not payload:
            raise RuntimeError("No fields provided to update.")
        return self.post(f"/media/{media_id}", payload=payload)
