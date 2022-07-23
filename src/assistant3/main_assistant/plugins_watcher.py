"""PluginWatcher."""
import contextlib
import queue
import typing

import spacy

from .. import processors
from ..common.exceptions import UidNotAssignedError
from ..common.plugins import PluginResultType, PluginType
from ..common.utils import bulk_assign_uuid
from ..processors.base_processor import BasePlugin


class FlowRecord():
    """FlowRecord type."""

    def __init__(self) -> None:
        """Create new FlowRecord object."""
        self.record: list[dict[str, object]] = []

    def add_entry(self, entry: dict[str, object]) -> None:
        """Add entry / result object to record.

        Args:
            entry: Result object to add.

        """
        self.record.append(entry)

    def reset(self) -> None:
        """Reset flow_rocord."""
        self.record.clear()

    def get_last(self) -> dict[str, object] | typing.Any:
        """Get last entry / result object to record.

        Returns:
            Entry / Result object

        """
        if self.is_empty():
            return None
        return self.record[-1]

    def is_empty(self) -> bool:
        """Return true if record is empty.

        Returns:
            True if record is empty

        """
        return len(self.record) == 0


class PluginWatcher():
    """PluginWatcher type."""

    def __init__(self, plugins: list[object]) -> None:
        """Create new PluginWatcher object.

        Args:
            plugins: List of plugins objects.

        """
        self.results_queue: queue.Queue[typing.Any] = queue.Queue()
        self.flow_record = FlowRecord()
        self.plugins: list[BasePlugin] = []
        self.trigger_plugin: BasePlugin = BasePlugin(match='')
        self.triggered_now_plugins = False
        self.nlp = spacy.load('en_core_web_md')
        self.doc: typing.Any = None
        for plugin in plugins:
            if not isinstance(plugin, BasePlugin):
                error_plugin_name = ''
                with contextlib.suppress(Exception):
                    error_plugin_name = plugin.__str__()
                self.plugins = [
                    processors.base_processor.BaseInitializationErrorPlugin(
                    ),
                ]
                print(error_plugin_name)
                break
            plugin.set_spacy_model(self.nlp)
            self.plugins.append(plugin)
        self.init()

    def pop_result(self) -> object:
        """Get last element in results queue.

        Returns:
            Get last element in results queue.

        """
        return self.results_queue.get()

    def init(self) -> None:
        """Initialize plugins."""
        self.plugins = bulk_assign_uuid(self.plugins)
        for plugin in self.plugins:
            plugin.set_spacy_model(self.nlp)

    def init_trigger_plugin(self) -> None:
        """Initialize trigger plugin seperately."""
        if self.trigger_plugin:
            self.trigger_plugin = bulk_assign_uuid([self.trigger_plugin])[0]
            self.trigger_plugin.set_spacy_model(self.nlp)

    def add_trigger_plugin(self, trigger_plugin_obj: BasePlugin) -> None:
        """Add trigger plugin.

        Args:
            trigger_plugin_obj: TriggerPlugin object.

        """
        self.trigger_plugin = trigger_plugin_obj
        if self.trigger_plugin:
            self.init_trigger_plugin()

    def is_trigger_plugin_enabled(self) -> bool:
        """Return true if trigger plugin exists / enabled.

        Returns:
            True if trigger plugin exists

        """
        return self.trigger_plugin is not None

    def add_entry_to_flow_record(self, entry: dict[str, object]) -> None:
        """Add entry / result to plugins flow record.

        Args:
            entry: Entry or result.

        """
        self.flow_record.add_entry(entry)

    def flush_result_queue_in_list(self) -> list[dict[str, object]]:
        """Empty results queue into a list.

        Returns:
            List of results popped from queue.

        """
        res_list = []
        while self.results_queue.qsize() != 0:
            res_list.append(self.results_queue.get())
        return res_list

    def run_by_uid(self, uid: object) -> None:
        """Run specific plugin by uid.

        Args:
            uid: Plugin uid.

        """
        if uid == self.trigger_plugin.get_uid():
            self.run_trigger()
        else:
            self.run_plugins(uid)

    def run_trigger(self) -> None:
        """Run trigger plugin."""
        self.trigger_plugin.run_doc(self.doc, self.results_queue)

    def run_plugins(self, uid: object = None) -> None:
        """Run all plugins or specific plugin by uid.

        Args:
            uid: Plugin uid.

        """
        if uid:
            for plugin in self.plugins:
                if uid == plugin.get_uid():
                    plugin.run_doc(self.doc, self.results_queue, True)
                    return
        for plugin in self.plugins:
            plugin.run_doc(self.doc, self.results_queue)

    def run(self, speech_text: str) -> list[typing.Any]:
        """Run one assistant3 session.

        Args:
            speech_text: Text recognized by speech recognition library.

        Returns:
            List of results from plugins

        """
        self.doc = self.nlp(speech_text)

        if self.flow_record.is_empty():
            self.run_trigger()
            return self.flush_result_queue_in_list()

        last_record = self.flow_record.get_last()

        if last_record['type'] == PluginResultType.ERROR:
            if last_record['plugin_type'] == PluginType.TRIGGER_PLUGIN:
                self.run_by_uid(last_record['uid'])
                return self.flush_result_queue_in_list()
            self.run_plugins()
            return self.flush_result_queue_in_list()

        if last_record['plugin_type'] == PluginType.TRIGGER_PLUGIN:
            self.run_plugins()
            return self.flush_result_queue_in_list()
        if last_record['type'] == PluginResultType.KEEP_ALIVE:
            self.run_trigger()
            trigger_flushed = self.flush_result_queue_in_list()
            if trigger_flushed[0]['type'] != PluginResultType.ERROR:
                plugins = self.plugins
                self.plugins = [plugin.__class__() for plugin in plugins]
                self.init()
                return trigger_flushed
            self.run_by_uid(last_record['uid'])
            return self.flush_result_queue_in_list()
        if last_record['type'] == PluginResultType.TEXT:
            self.flow_record.reset()
            return []
        return []

    def list_plugins_by_uid(self) -> None:
        """List plugins by uid."""
        try:
            if self.is_trigger_plugin_enabled():
                print('[ PLUGIN UID ]  ' + str(self.trigger_plugin.get_uid()))
            for plugin in self.plugins:
                print('[ PLUGIN UID ]  ' + str(plugin.get_uid()))
            return
        except UidNotAssignedError:
            print('MALFUNCTION')
            return
