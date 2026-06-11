import unittest

from callrail_safe_agent_cli.cli import _API_COMMAND_CATALOG, _API_COMMAND_QUERY_PARAMS, _query_flag_name


class TestQueryParamCatalog(unittest.TestCase):
    def test_query_flags_are_unique_per_command(self) -> None:
        duplicates: dict[str, list[str]] = {}

        for command_name, query_params in _API_COMMAND_QUERY_PARAMS.items():
            seen: set[str] = set()
            command_duplicates: set[str] = set()
            for _query_param, attr_name in query_params:
                flag_name = _query_flag_name(attr_name)
                if flag_name in seen:
                    command_duplicates.add(flag_name)
                seen.add(flag_name)
            if command_duplicates:
                duplicates[command_name] = sorted(command_duplicates)

        self.assertEqual(duplicates, {})

    def test_audited_query_capabilities_are_present(self) -> None:
        expected_flags = {
            "accounts get": {"fields"},
            "calls get": {"fields"},
            "companies get": {"fields"},
            "integrations list": {"page", "per-page", "company-id", "fields"},
            "integrations get": {"fields"},
            "page-views list": {"page", "per-page", "time-zone"},
            "sms-threads get": {"page", "per-page", "with-msg-errors", "fields"},
            "text-messages get": {"fields"},
            "message-flows list": {"page", "per-page", "company-id"},
            "trackers get": {"fields"},
        }

        for command_name, required_flags in expected_flags.items():
            with self.subTest(command=command_name):
                actual_flags = {
                    _query_flag_name(attr_name)
                    for _query_key, attr_name in _API_COMMAND_QUERY_PARAMS.get(command_name, ())
                }
                self.assertTrue(required_flags.issubset(actual_flags))

    def test_removed_reference_helpers_are_not_in_command_catalog(self) -> None:
        removed_commands = {
            ("tags", "available-colors"),
            ("integrations", "configure"),
            ("message-flows", "configure"),
            ("trackers", "request-number"),
            ("trackers", "configure-call-flows"),
            ("trackers", "session-call-sources"),
            ("trackers", "source-call-sources"),
            ("users", "roles"),
        }

        shipped_pairs = {
            (family_name, command_name)
            for family_name, commands in _API_COMMAND_CATALOG.items()
            for command_name in commands
        }
        self.assertTrue(removed_commands.isdisjoint(shipped_pairs))
