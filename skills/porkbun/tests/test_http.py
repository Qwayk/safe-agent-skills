from __future__ import annotations

from unittest import TestCase
from unittest.mock import Mock, patch

from qwayk_porkbun_safe_agent_cli.http import RequestsTransport


class TestRequestsTransport(TestCase):
    @patch("qwayk_porkbun_safe_agent_cli.http.requests.request")
    def test_redirects_are_disabled_at_transport(self, request: Mock) -> None:
        response = Mock()
        response.status_code = 302
        response.headers = {"Location": "https://evil.example/collect"}
        response.content = b""
        response.url = "https://api.porkbun.com/api/json/v3/ping"
        request.return_value = response

        RequestsTransport().request(
            "GET",
            "https://api.porkbun.com/api/json/v3/ping",
            headers={"X-API-Key": "sentinel"},
        )

        self.assertIs(request.call_args.kwargs["allow_redirects"], False)
