"""Public wire-shape types, grouped by contract.

These are TypedDicts and type aliases, not runtime validators. Nested dictionary
keys retain their contract spelling; resource method keywords use snake_case.
"""

from .generated import types_control_plane as control_plane
from .generated import types_images as images
from .generated import types_inference as inference
from .generated import types_native as native
from .generated import types_runtime as runtime
from .generated import types_tools as tools

__all__ = ["control_plane", "images", "inference", "native", "runtime", "tools"]
