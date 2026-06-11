#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


class _StubHandler(BaseHTTPRequestHandler):
    def _send_json(self, obj: dict) -> None:
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/api/account/v1/accounts":
            self._send_json({"items": []})
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self) -> None:  # noqa: N802
        if self.path == "/api/account/v1/accounts":
            self._send_json({"account": {"id": "00000000-0000-0000-0000-000000000000", "name": "Example"}})
            return
        if "/backups/" in self.path and self.path.endswith("/restore"):
            self._send_json({"restore": "started"})
            return
        self.send_response(404)
        self.end_headers()

    def log_message(self, _fmt: str, *_args) -> None:
        return


def _start_server() -> HTTPServer:
    server = HTTPServer(("127.0.0.1", 0), _StubHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server


def _run_cli(tool_root: Path, argv: list[str], env: dict[str, str]) -> dict:
    proc = subprocess.run(
        [sys.executable, "-m", "qdrant_cloud_api_tool", *argv],
        cwd=str(tool_root),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if proc.returncode not in (0, 1, 130):
        raise RuntimeError(f"CLI failed rc={proc.returncode}: {proc.stderr.strip()}")
    try:
        return json.loads(proc.stdout)
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(f"CLI did not output JSON: {type(e).__name__}: {e}\nstdout={proc.stdout}\nstderr={proc.stderr}") from None


def main() -> int:
    tool_root = Path(__file__).resolve().parents[1]
    examples = tool_root / "docs" / "examples"
    outputs_dir = examples / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    server = _start_server()
    base_url = f"http://127.0.0.1:{server.server_address[1]}"

    env = dict(os.environ)
    env["PYTHONPATH"] = str(tool_root / "src")
    env["QDRANT_CLOUD_API_BASE_URL"] = base_url
    env["QDRANT_CLOUD_API_KEY"] = "EXAMPLE_KEY_SHOULD_NEVER_APPEAR"
    env["QDRANT_CLOUD_TIMEOUT_S"] = "30"

    try:
        version = _run_cli(tool_root, ["--output", "json", "--version"], env)
        (outputs_dir / "version.json").write_text(json.dumps(version, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        read = _run_cli(tool_root, ["--output", "json", "--live", "account-v1", "list-accounts"], env)
        (outputs_dir / "read.example.json").write_text(json.dumps(read, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        req_path = examples / "request.example.json"
        req_path.write_text(json.dumps({"account": {"name": "Example"}}, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        plan = _run_cli(
            tool_root,
            [
                "--output",
                "json",
                "--plan-out",
                str(examples / "plan.example.json"),
                "account-v1",
                "create-account",
                "--request-json",
                str(req_path),
            ],
            env,
        )
        # The tool also writes plan.example.json via --plan-out; we keep stdout too.
        (outputs_dir / "plan_stdout.example.json").write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        apply_out = _run_cli(
            tool_root,
            [
                "--output",
                "json",
                "--live",
                "--apply",
                "--no-artifacts",
                "--plan-in",
                str(examples / "plan.example.json"),
                "--receipt-out",
                str(examples / "receipt.example.json"),
                "account-v1",
                "create-account",
                "--request-json",
                str(req_path),
            ],
            env,
        )
        # Ordinary writes currently refuse before Qdrant Cloud HTTP. Keep the old receipt filename
        # as the committed refusal example so stale successful write receipts cannot linger.
        (examples / "receipt.example.json").write_text(json.dumps(apply_out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (outputs_dir / "receipt_stdout.example.json").write_text(json.dumps(apply_out, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        backup_req_path = examples / "backup_restore.request.example.json"
        backup_req_path.write_text(json.dumps({"snapshot": "example"}, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        _run_cli(
            tool_root,
            [
                "--output",
                "json",
                "--plan-out",
                str(examples / "backup_restore.plan.example.json"),
                "cluster-backup-v1",
                "restore-backup",
                "--account-id",
                "00000000-0000-0000-0000-000000000000",
                "--backup-id",
                "11111111-1111-1111-1111-111111111111",
                "--request-json",
                str(backup_req_path),
            ],
            env,
        )

        _run_cli(
            tool_root,
            [
                "--output",
                "json",
                "--live",
                "--apply",
                "--plan-in",
                str(examples / "backup_restore.plan.example.json"),
                "--receipt-out",
                str(examples / "backup_restore.receipt.example.json"),
                "cluster-backup-v1",
                "restore-backup",
                "--account-id",
                "00000000-0000-0000-0000-000000000000",
                "--backup-id",
                "11111111-1111-1111-1111-111111111111",
                "--request-json",
                str(backup_req_path),
            ],
            env,
        )

    finally:
        server.shutdown()
        server.server_close()

    # Safety check: ensure the example key isn't present in committed outputs.
    haystack = ""
    for p in list(outputs_dir.glob("*.json")) + list(examples.glob("*.json")):
        if p.exists():
            haystack += p.read_text(encoding="utf-8")
    if "EXAMPLE_KEY_SHOULD_NEVER_APPEAR" in haystack:
        raise RuntimeError("Secret leaked into example outputs")

    print("ok: examples generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
