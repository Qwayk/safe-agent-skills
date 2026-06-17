from __future__ import annotations

import sys
from pathlib import Path

# Allow `python3 -m unittest` without requiring an editable install.
_SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(_SRC))

