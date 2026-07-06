from __future__ import annotations

import sys

from .cli import main as _main


def main() -> None:
    raise SystemExit(_main(sys.argv[1:]))


if __name__ == "__main__":
    main()

