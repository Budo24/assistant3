from enum import Enum

class PluginResultType(Enum):
    UNDEFINED = 1
    TEXT = 2
    HREF = 3
    HTML = 4
    ERROR = 5
    KEEP_ALIVE = 6
    # budo added
    DATE = 7

class PluginType(Enum):
    SYSTEM_PLUGIN = 1
    ONLINE_PLUGIN = 2
    TRIGGER_PLUGIN = 3

plugin_defined_errors = {
    "initialization_error": "Error at plugins initialization occured"
}