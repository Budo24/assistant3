"""Utils."""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from assistant3.processors.base_processor import BasePlugin


def bulk_assign_uuid(plugins: list[BasePlugin]) -> list[BasePlugin]:
    """Assign uuids in bulk.

    Args:
        plugins: List of plugins.

    Returns:
        List of plugins with uuid assigned.

    """
    for plugin in plugins:
        plugin.set_uid(uuid.uuid4())
    return plugins
