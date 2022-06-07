import sys
import os

def get_root_dir():
    root_name, _, _ = __name__.partition('.')
    root_module = sys.modules[root_name]
    root_dir = os.path.dirname(root_module.__file__)
    return root_dir

#config_path = os.path.join(root_dir, 'configuration.conf')