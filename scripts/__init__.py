"""Scripts package -- adds src/ to sys.path so `uv run python -m scripts.X`
can resolve `import const`, `from simulate import simulate`, etc.
"""

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
