from __future__ import annotations

import sys

from .cli import main as cli_main


def main_entrypoint() -> None:
    raise SystemExit(cli_main(sys.argv[1:]))


def main() -> None:  # pragma: no cover - script entry point
    main_entrypoint()


if __name__ == "__main__":
    main_entrypoint()
