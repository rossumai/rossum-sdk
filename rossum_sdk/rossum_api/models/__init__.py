"""Model classes used to deserialize API payloads.

The classes can be provided by 3rd party packages as plugins in the rossum_sdk.models namespace.
* If no 3rd party plugin is discovered, the implementation in rossum_models is used by default.
* If more than one 3rd party plugin is discovered, rossum_api refuses to operate.
"""
from __future__ import annotations

import sys

if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points

# Discover plugins providing models and import one
model_libs = entry_points(group="rossum_sdk.models")  # type: ignore
models_module = model_libs["default"].load()  # type: ignore
symbols = dict(models_module.__dict__.items())
locals().update(symbols)
