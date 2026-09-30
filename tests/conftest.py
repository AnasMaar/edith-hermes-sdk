from __future__ import annotations

import sys
from pathlib import Path

MOCK_SERVICE = Path(__file__).resolve().parents[1] / "services" / "mock_server"
sys.path.insert(0, str(MOCK_SERVICE))
RUNTIME_BRIDGE = Path(__file__).resolve().parents[1] / "services" / "runtime_bridge"
sys.path.insert(0, str(RUNTIME_BRIDGE))
