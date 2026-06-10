import sys
from pathlib import Path

# Allow running `python3 -m unittest` without installing the package.
_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

