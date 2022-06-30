"""Utils."""
from __future__ import annotations

import os
import sys
import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from processors.base_processor import BasePlugin


def get_root_dir() -> str:
    """Get root directory."""
    root_name, _, _ = __name__.partition('.')
    root_module = sys.modules[root_name]
    return os.path.dirname(str(root_module.__file__))


def bulk_assign_uuid(plugins: list[BasePlugin]) -> list[BasePlugin]:
    """Assign uuids in bulk."""
    for plugin in plugins:
        plugin.set_uid(uuid.uuid4())
    return plugins
