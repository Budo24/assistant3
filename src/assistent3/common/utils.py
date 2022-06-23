"""utils"""
import sys
import os
import uuid


def get_root_dir():
    """Get Root"""
    root_name, _, _ = __name__.partition('.')
    root_module = sys.modules[root_name]
    root_dir = os.path.dirname(root_module.__file__)
    return root_dir


def bulk_assign_uuid(plugins):
    """Bulk Assign"""
    for plugin in plugins:
        plugin.set_uid(uuid.uuid4())
    return plugins
