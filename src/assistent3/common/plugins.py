from enum import Enum

class PluginResultType(Enum):
    UNDEFINED = 1
    TEXT = 2
    HREF = 3
    HTML = 4

class PluginType(Enum):
    SYSTEM_PLUGIN = 1
    ONLINE_PLUGIN = 2