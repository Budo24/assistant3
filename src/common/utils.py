"""Utils."""
import os
import sys
import uuid

import processors


def get_root_dir() -> str:
    """Get root directory."""
    root_name, _, _ = __name__.partition('.')
    root_module = sys.modules[root_name]
    return os.path.dirname(str(root_module.__file__))


def bulk_assign_uuid(
        plugins: list[processors.base_processor.BasePlugin],
) -> list[processors.base_processor.BasePlugin]:
    """Assign uuids in bulk."""
    for plugin in plugins:
        plugin.set_uid(uuid.uuid4())
    return plugins
