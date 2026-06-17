from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from fortnox_api_tool.cli import main


class TestAccountingReads(unittest.TestCase):
    def test_customers_list_wires_documented_query_params(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            buf = io.StringIO()
            with patch("fortnox_api_tool.commands.accounting_reads.request_json") as request_json:
                request_json.return_value = {
                    "status": 200,
                    "url": "https://api.fortnox.se/3/customers",
                    "token_source": "env",
                    "token_expired": None,
                    "body": {"Customers": []},
                }
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_path),
                            "customers",
                            "list",
                            "--filter",
                            "active",
                            "--sort-by",
                            "name",
                            "--customer-number",
                            "C-100",
                            "--name",
                            "Acme",
                            "--zip-code",
                            "11122",
                            "--city",
                            "Stockholm",
                            "--email",
                            "billing@example.com",
                            "--phone",
                            "08-100200",
                            "--organisation-number",
                            "556677-8899",
                            "--gln",
                            "7300000000012",
                            "--gln-delivery",
                            "7300000000013",
                            "--last-modified",
                            "2026-06-16",
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(request_json.call_args.kwargs["path"], "/customers")
            self.assertEqual(
                request_json.call_args.kwargs["query_params"],
                {
                    "filter": "active",
                    "sortby": "name",
                    "customernumber": "C-100",
                    "name": "Acme",
                    "zipcode": "11122",
                    "city": "Stockholm",
                    "email": "billing@example.com",
                    "phone": "08-100200",
                    "organisationnumber": "556677-8899",
                    "gln": "7300000000012",
                    "glndelivery": "7300000000013",
                    "lastmodified": "2026-06-16",
                },
            )

    def test_company_information_get_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\n", encoding="utf-8")
            buf = io.StringIO()
            with patch(
                "fortnox_api_tool.commands.accounting_reads.get_json",
                return_value={
                    "status": 200,
                    "url": "https://api.fortnox.se/3/companyinformation",
                    "token_source": "env",
                    "token_expired": None,
                    "body": {"CompanyInformation": {"Name": "Demo Co"}},
                },
            ):
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_path),
                            "company-information",
                            "get",
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["path"], "/companyinformation")

    def test_customers_get_requires_customer_number(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\n", encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", str(env_path), "customers", "get"])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")

    def test_suppliers_list_wires_documented_query_params(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            buf = io.StringIO()
            with patch("fortnox_api_tool.commands.accounting_reads.request_json") as request_json:
                request_json.return_value = {
                    "status": 200,
                    "url": "https://api.fortnox.se/3/suppliers",
                    "token_source": "env",
                    "token_expired": None,
                    "body": {"Suppliers": []},
                }
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_path),
                            "suppliers",
                            "list",
                            "--supplier-number",
                            "S-100",
                            "--name",
                            "Nordic Parts",
                            "--organisation-number",
                            "556677-0000",
                            "--phone",
                            "08-555444",
                            "--zip-code",
                            "11455",
                            "--city",
                            "Stockholm",
                            "--email",
                            "ap@example.com",
                            "--last-modified",
                            "2026-06-16",
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(request_json.call_args.kwargs["path"], "/suppliers")
            self.assertEqual(
                request_json.call_args.kwargs["query_params"],
                {
                    "suppliernumber": "S-100",
                    "name": "Nordic Parts",
                    "organisationnumber": "556677-0000",
                    "phone": "08-555444",
                    "zipcode": "11455",
                    "city": "Stockholm",
                    "email": "ap@example.com",
                    "lastmodified": "2026-06-16",
                },
            )

    def test_prices_get_by_from_quantity_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\n", encoding="utf-8")
            buf = io.StringIO()
            with patch(
                "fortnox_api_tool.commands.accounting_reads.get_json",
                return_value={
                    "status": 200,
                    "url": "https://api.fortnox.se/3/prices/PL1/ART1/10",
                    "token_source": "env",
                    "token_expired": None,
                    "body": {"Price": {"PriceList": "PL1", "ArticleNumber": "ART1", "FromQuantity": 10}},
                },
            ):
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_path),
                            "prices",
                            "get-by-from-quantity",
                            "--price-list",
                            "PL1",
                            "--article-number",
                            "ART1",
                            "--from-quantity",
                            "10",
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["path"], "/prices/PL1/ART1/10")

    def test_currencies_get_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\n", encoding="utf-8")
            buf = io.StringIO()
            with patch(
                "fortnox_api_tool.commands.accounting_reads.get_json",
                return_value={
                    "status": 200,
                    "url": "https://api.fortnox.se/3/currencies/SEK",
                    "token_source": "env",
                    "token_expired": None,
                    "body": {"Currency": {"Code": "SEK"}},
                },
            ):
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_path),
                            "currencies",
                            "get",
                            "--code",
                            "SEK",
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["path"], "/currencies/SEK")

    def test_terms_of_payments_get_requires_code(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\n", encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", str(env_path), "terms-of-payments", "get"])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")

    def test_accounts_get_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\n", encoding="utf-8")
            buf = io.StringIO()
            with patch(
                "fortnox_api_tool.commands.accounting_reads.get_json",
                return_value={
                    "status": 200,
                    "url": "https://api.fortnox.se/3/accounts/1510",
                    "token_source": "env",
                    "token_expired": None,
                    "body": {"Account": {"Number": 1510}},
                },
            ):
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_path),
                            "accounts",
                            "get",
                            "--number",
                            "1510",
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["path"], "/accounts/1510")

    def test_vouchers_list_current_financial_year_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\n", encoding="utf-8")
            buf = io.StringIO()
            with patch(
                "fortnox_api_tool.commands.accounting_reads.get_json",
                return_value={
                    "status": 200,
                    "url": "https://api.fortnox.se/3/vouchers/sublist",
                    "token_source": "env",
                    "token_expired": None,
                    "body": {"Vouchers": []},
                },
            ):
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_path),
                            "vouchers",
                            "list-current-financial-year",
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["path"], "/vouchers/sublist")

    def test_predefined_accounts_get_requires_name(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\n", encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", str(env_path), "predefined-accounts", "get"])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")

    def test_invoice_payments_list_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\n", encoding="utf-8")
            buf = io.StringIO()
            with patch(
                "fortnox_api_tool.commands.accounting_reads.get_json",
                return_value={
                    "status": 200,
                    "url": "https://api.fortnox.se/3/invoicepayments",
                    "token_source": "env",
                    "token_expired": None,
                    "body": {"InvoicePayments": []},
                },
            ):
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", str(env_path), "invoice-payments", "list"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["path"], "/invoicepayments")

    def test_locked_period_get_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\n", encoding="utf-8")
            buf = io.StringIO()
            with patch(
                "fortnox_api_tool.commands.accounting_reads.get_json",
                return_value={
                    "status": 200,
                    "url": "https://api.fortnox.se/3/settings/lockedperiod",
                    "token_source": "env",
                    "token_expired": None,
                    "body": {"LockedPeriod": {"EndDate": "2026-06-01"}},
                },
            ):
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", str(env_path), "locked-period", "get"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["path"], "/settings/lockedperiod")

    def test_print_templates_list_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\n", encoding="utf-8")
            buf = io.StringIO()
            with patch(
                "fortnox_api_tool.commands.accounting_reads.get_json",
                return_value={
                    "status": 200,
                    "url": "https://api.fortnox.se/3/printtemplates",
                    "token_source": "env",
                    "token_expired": None,
                    "body": {"PrintTemplates": []},
                },
            ):
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", str(env_path), "print-templates", "list"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["path"], "/printtemplates")

    def test_articles_list_wires_documented_query_params(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            buf = io.StringIO()
            with patch("fortnox_api_tool.commands.accounting_reads.request_json") as request_json:
                request_json.return_value = {
                    "status": 200,
                    "url": "https://api.fortnox.se/3/articles",
                    "token_source": "env",
                    "token_expired": None,
                    "body": {"Articles": []},
                }
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_path),
                            "articles",
                            "list",
                            "--filter",
                            "inactive",
                            "--sort-by",
                            "stockvalue",
                            "--article-number",
                            "ART-100",
                            "--description",
                            "Widget",
                            "--ean",
                            "1234567890123",
                            "--supplier-number",
                            "S-100",
                            "--manufacturer",
                            "Acme Works",
                            "--manufacturer-article-number",
                            "MFG-7788",
                            "--webshop",
                            "true",
                            "--last-modified",
                            "2026-06-16",
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(request_json.call_args.kwargs["path"], "/articles")
            self.assertEqual(
                request_json.call_args.kwargs["query_params"],
                {
                    "filter": "inactive",
                    "sortby": "stockvalue",
                    "articlenumber": "ART-100",
                    "description": "Widget",
                    "ean": "1234567890123",
                    "suppliernumber": "S-100",
                    "manufacturer": "Acme Works",
                    "manufacturerarticlenumber": "MFG-7788",
                    "webshop": "true",
                    "lastmodified": "2026-06-16",
                },
            )

    def test_invoices_get_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\n", encoding="utf-8")
            buf = io.StringIO()
            with patch(
                "fortnox_api_tool.commands.accounting_reads.get_json",
                return_value={
                    "status": 200,
                    "url": "https://api.fortnox.se/3/invoices/1001",
                    "token_source": "env",
                    "token_expired": None,
                    "body": {"Invoice": {"DocumentNumber": "1001"}},
                },
            ):
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_path),
                            "invoices",
                            "get",
                            "--document-number",
                            "1001",
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["path"], "/invoices/1001")

    def test_registrations_get_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\n", encoding="utf-8")
            buf = io.StringIO()
            with patch(
                "fortnox_api_tool.commands.accounting_reads.get_json",
                return_value={
                    "status": 200,
                    "url": "https://api.fortnox.se/api/time/registrations-v2",
                    "token_source": "env",
                    "token_expired": None,
                    "body": {"Registrations": []},
                },
            ):
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", str(env_path), "registrations", "get"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["path"], "/api/time/registrations-v2")

    def test_vacation_debt_basis_get_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\n", encoding="utf-8")
            buf = io.StringIO()
            with patch(
                "fortnox_api_tool.commands.accounting_reads.get_json",
                return_value={
                    "status": 200,
                    "url": "https://api.fortnox.se/3/vacationdebtbasis/2026/6",
                    "token_source": "env",
                    "token_expired": None,
                    "body": {"VacationDebtBasis": {"Year": 2026, "Month": 6}},
                },
            ):
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_path),
                            "vacation-debt-basis",
                            "get",
                            "--year",
                            "2026",
                            "--month",
                            "6",
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["path"], "/vacationdebtbasis/2026/6")

    def test_offers_get_requires_document_number(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\n", encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", str(env_path), "offers", "get"])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")
