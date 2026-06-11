from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

from .config import Config
from .http import HttpClient, HttpResponse


@dataclass(frozen=True)
class PlausibleClient:
    cfg: Config
    http: HttpClient

    def _cf_access_headers(self) -> dict[str, str]:
        if not (self.cfg.cf_access_client_id and self.cfg.cf_access_client_secret):
            return {}
        return {
            "CF-Access-Client-Id": self.cfg.cf_access_client_id,
            "CF-Access-Client-Secret": self.cfg.cf_access_client_secret,
        }

    def _auth_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.cfg.api_key}",
            "Accept": "application/json",
            **self._cf_access_headers(),
        }

    @staticmethod
    def _path_escape(value: str) -> str:
        return quote(str(value), safe="")

    def _url(self, path: str) -> str:
        return f"{self.cfg.base_url}{path}"

    def health(self) -> HttpResponse:
        return self.http.request("GET", self._url("/api/health"))

    def stats_query(self, query: dict[str, Any]) -> dict[str, Any]:
        headers = {**self._auth_headers(), "Content-Type": "application/json"}
        resp = self.http.request("POST", self._url("/api/v2/query"), headers=headers, json_body=query)
        return resp.json()

    def send_event(self, payload: dict[str, Any], *, user_agent: str | None = None) -> dict[str, Any]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            **self._cf_access_headers(),
        }
        if user_agent:
            headers["User-Agent"] = user_agent
        resp = self.http.request("POST", self._url("/api/event"), headers=headers, json_body=payload)
        # Plausible commonly returns 202 Accepted with an empty body; tolerate both.
        if not resp.body:
            return {"status": resp.status}
        try:
            return resp.json()
        except Exception:
            return {"status": resp.status, "body": resp.text()}

    def sites_list(
        self,
        *,
        after: str | None = None,
        before: str | None = None,
        limit: int | None = None,
        team_id: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if after:
            params["after"] = str(after)
        if before:
            params["before"] = str(before)
        if limit is not None:
            params["limit"] = int(limit)
        if team_id:
            params["team_id"] = str(team_id)
        resp = self.http.request("GET", self._url("/api/v1/sites"), headers=self._auth_headers(), params=params or None)
        return resp.json()

    def sites_teams_list(self) -> dict[str, Any]:
        resp = self.http.request("GET", self._url("/api/v1/sites/teams"), headers=self._auth_headers())
        return resp.json()

    def site_get(self, site_id: str) -> dict[str, Any]:
        site_id_esc = self._path_escape(site_id)
        resp = self.http.request("GET", self._url(f"/api/v1/sites/{site_id_esc}"), headers=self._auth_headers())
        return resp.json()

    def site_goals_list(
        self,
        *,
        site_id: str,
        after: str | None = None,
        before: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"site_id": site_id}
        if after:
            params["after"] = str(after)
        if before:
            params["before"] = str(before)
        if limit is not None:
            params["limit"] = int(limit)
        resp = self.http.request("GET", self._url("/api/v1/sites/goals"), headers=self._auth_headers(), params=params)
        return resp.json()

    def site_custom_props_list(self, *, site_id: str) -> dict[str, Any]:
        params: dict[str, Any] = {"site_id": site_id}
        resp = self.http.request("GET", self._url("/api/v1/sites/custom-props"), headers=self._auth_headers(), params=params)
        return resp.json()

    def site_guests_list(
        self,
        *,
        site_id: str,
        after: str | None = None,
        before: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"site_id": site_id}
        if after:
            params["after"] = str(after)
        if before:
            params["before"] = str(before)
        if limit is not None:
            params["limit"] = int(limit)
        resp = self.http.request("GET", self._url("/api/v1/sites/guests"), headers=self._auth_headers(), params=params)
        return resp.json()

    def site_create(self, payload: dict[str, Any]) -> dict[str, Any]:
        headers = {**self._auth_headers(), "Content-Type": "application/json"}
        resp = self.http.request("POST", self._url("/api/v1/sites"), headers=headers, json_body=payload)
        return resp.json()

    def site_update(self, site_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        site_id_esc = self._path_escape(site_id)
        headers = {**self._auth_headers(), "Content-Type": "application/json"}
        resp = self.http.request("PUT", self._url(f"/api/v1/sites/{site_id_esc}"), headers=headers, json_body=payload)
        return resp.json()

    def site_delete(self, site_id: str) -> dict[str, Any]:
        site_id_esc = self._path_escape(site_id)
        resp = self.http.request("DELETE", self._url(f"/api/v1/sites/{site_id_esc}"), headers=self._auth_headers())
        return resp.json()

    def site_shared_links_ensure(self, *, site_id: str, name: str) -> dict[str, Any]:
        headers = {**self._auth_headers(), "Content-Type": "application/json"}
        payload = {"site_id": site_id, "name": name}
        resp = self.http.request("PUT", self._url("/api/v1/sites/shared-links"), headers=headers, json_body=payload)
        return resp.json()

    def site_goal_ensure(
        self,
        *,
        site_id: str,
        goal_type: str,
        event_name: str | None = None,
        page_path: str | None = None,
        display_name: str | None = None,
    ) -> dict[str, Any]:
        headers = {**self._auth_headers(), "Content-Type": "application/json"}
        payload: dict[str, Any] = {"site_id": site_id, "goal_type": goal_type}
        if display_name is not None:
            payload["display_name"] = display_name
        if event_name is not None:
            payload["event_name"] = event_name
        if page_path is not None:
            payload["page_path"] = page_path
        resp = self.http.request("PUT", self._url("/api/v1/sites/goals"), headers=headers, json_body=payload)
        return resp.json()

    def site_goal_delete(self, *, goal_id: str, site_id: str) -> dict[str, Any]:
        goal_id_esc = self._path_escape(goal_id)
        headers = {**self._auth_headers(), "Content-Type": "application/json"}
        payload = {"site_id": site_id}
        resp = self.http.request("DELETE", self._url(f"/api/v1/sites/goals/{goal_id_esc}"), headers=headers, json_body=payload)
        return resp.json()

    def site_custom_prop_ensure(self, *, site_id: str, prop_key: str) -> dict[str, Any]:
        files = {"site_id": (None, site_id), "property": (None, prop_key)}
        resp = self.http.request("PUT", self._url("/api/v1/sites/custom-props"), headers=self._auth_headers(), files=files)
        return resp.json()

    def site_custom_prop_delete(self, *, site_id: str, prop_key: str) -> dict[str, Any]:
        prop_key_esc = self._path_escape(prop_key)
        files = {"site_id": (None, site_id)}
        resp = self.http.request(
            "DELETE", self._url(f"/api/v1/sites/custom-props/{prop_key_esc}"), headers=self._auth_headers(), files=files
        )
        return resp.json()

    def site_guest_ensure(self, *, site_id: str, email: str, role: str) -> dict[str, Any]:
        headers = {**self._auth_headers(), "Content-Type": "application/json"}
        payload = {"site_id": site_id, "email": email, "role": role}
        resp = self.http.request("PUT", self._url("/api/v1/sites/guests"), headers=headers, json_body=payload)
        return resp.json()

    def site_guest_delete(self, *, email: str) -> dict[str, Any]:
        email_esc = self._path_escape(email)
        resp = self.http.request("DELETE", self._url(f"/api/v1/sites/guests/{email_esc}"), headers=self._auth_headers())
        return resp.json()
