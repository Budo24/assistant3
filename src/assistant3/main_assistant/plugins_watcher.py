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
    """Plugins invoking flow container."""

    def __init__(self) -> None:
        """Create FlowRecord object."""
        self.record: list[dict[str, object]] = []

    def add_entry(self, entry: dict[str, object]) -> None:
        """Add entry / result object to record.

        Args:
            entry: Result object to add.
        """
        self.record.append(entry)

    def get_last(self) -> dict[str, object] | typing.Any:
        """Get last entry / result object to record.

        Args:
            entry: Result object to add.

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

    def printify(self) -> None:
        """Empty."""
        if self.is_empty():
            print()
            print(str('EMPTY RECORD'))
            print()
        print()
        print(str(self.record))
        print()


class PluginWatcher():
    """PluginWatcher type"""

    def __init__(self, plugins: list[object]):
        """Create new PluginWatcher object.

        Args:
            plugins: List of plugins objects.

        Returns:
            New PluginWatcher instance
        """
        # reslts_queue : the queue where all plugins push their result dicts
        self.results_queue: queue.Queue[typing.Any] = queue.Queue()
        self.flow_record = FlowRecord()
        self.plugins: list[BasePlugin] = []
        self.trigger_plugin: BasePlugin = BasePlugin(match='')
        # flag to tell pw if a trigger plugin was already triggered ("hey assistant")
        self.triggered_now_plugins = False
        # spacy object with a trained AI model initialized
        self.nlp = spacy.load('en_core_web_md')
        # data type related to SpaCy (nlp library)
        self.doc: typing.Any = None
        # checks if any plugin was passed that doesn't inherit from BasePlugin
        # if it's the case, it will drop them all, and change it with a
        # special plugin for this case 'processors.base_processor.BaseInitializationErrorPlugin'
        # we will see what to add in it later..
        for plugin in plugins:
            if not isinstance(plugin, BasePlugin):
                error_plugin_name = ''
                with contextlib.suppress(Exception):
                    error_plugin_name = plugin.__str__()
                self.plugins = [
                    processors.base_processor.BaseInitializationErrorPlugin(
                    ),
                ]
                break
            # if all good, we pass an instance of the nlp object to each plugin,
            # so it can be used to check similarity of what the user said compared
            # to the reference sentence
            plugin.set_spacy_model(self.nlp)
            self.plugins.append(plugin)
        # here we add an empty trigger plugin, and later we can add one.
        # we can also remove it at any time
        # self.add_trigger_plugin(None)
        self.init()

    def pop_result(self) -> object:
        """Get last element in results queue.

        Returns:
            Get last element in results queue.
        """
        # CHECK how a queue works (python queue module)
        return self.results_queue.get()

    def init(self) -> None:
        """Initialize plugins."""
        # here we assign a unique id to each plugin, so later we can distinguish
        # between them, just from the result they send (which contains this uid)
        # witout bothering of accessing them with the names and all that head ache
        self.plugins = bulk_assign_uuid(self.plugins)

        # this is maybe a duplication, i'll check it later
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
            entre: Entry / result.

        """
        self.flow_record.add_entry(entry)

    def flush_result_queue_in_list(self) -> list[dict[str, object]]:
        """Empty results queue into a list.

        Returns:
            List of results popped from queue.
        """
        res_list = []
        print('Size: ', self.results_queue.qsize())
        while self.results_queue.qsize() != 0:
            res_list.append(self.results_queue.get())
        print('res_list: ', res_list)
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
        print('----------------------------Budo')
        print('self.doc, self.results_queue: ', self.doc, self.results_queue)
        print('----------------------------Budo')
        self.trigger_plugin.run_doc(self.doc, self.results_queue)

    def run_plugins(self, uid: object = None) -> None:
        """Run all plugins or specific plugin by uid.

        Args:
            uid: Plugin uid.

        """
        print('run_plugins function')
        if uid:
            print('uid', uid)
            for plugin in self.plugins:
                print('plugin', plugin)
                if uid == plugin.get_uid():
                    plugin.run_doc(self.doc, self.results_queue)
                    return
        print('not uid')
        print('\n\n\t', self.plugins)
        for plugin in self.plugins:
            print('run_doc')
            plugin.run_doc(self.doc, self.results_queue)
    
    def run(self, speech_text: str) -> list[typing.Any]:
        """Run one assistant3 session.

        Args:
            speech_text: Text recognized by speech recognition library.

        Returns:
            List of results from plugins
        """
        # we transform the text from vosk to doc object (pass it to SpaCy to process it)
        self.doc = self.nlp(speech_text)
        # self.flow_record.printify()

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
            print('LAST RECORD', last_record)
            self.run_plugins()
            return self.flush_result_queue_in_list()
        if last_record['type'] == PluginResultType.KEEP_ALIVE:
            print('Last record recognised')
            self.run_trigger()
            trigger_flushed = self.flush_result_queue_in_list()
            if trigger_flushed[0]['type'] != PluginResultType.ERROR:
                print('---------------------------_>>>>')
                plugins = self.plugins
                for plugin in plugins:
                    print(plugin)
                print('\n\n')
                self.plugins = [plugin.__class__() for plugin in plugins]
                # IHEB LINE DONE YERY IMPORTANT, UID IS IN PLUGIN WATCHER!!!
                self.init()
                for plugin in self.plugins:
                    print(plugin)
                print('<<<<<<<<------------------------')
                return trigger_flushed
            self.run_by_uid(last_record['uid'])
            return self.flush_result_queue_in_list()
        if speech_text == 'hey assistant':
            print('Hey assistant said')
            self.run_trigger()
        else:
            print('Hey assistant not said')
            self.run_plugins()
        return self.flush_result_queue_in_list()

    def run2(self, speech_text: str) -> list[typing.Any]:
        self.doc = self.nlp(speech_text)
        

        last_record = self.flow_record.get_last()
        if not last_record:
            self.run_trigger()
            return self.flush_result_queue_in_list()
        elif last_record['plugin_type'] == PluginType.TRIGGER_PLUGIN:
            self.run_plugins()
            return self.flush_result_queue_in_list()
        else:
            self.run_trigger()
            return self.flush_result_queue_in_list()




    def list_plugins_by_uid(self) -> None:
        """List plugins by uid."""
        try:
            if self.is_trigger_plugin_enabled():
                print('[ PLIGIN UID ]  ' + str(self.trigger_plugin.get_uid()))
            for plugin in self.plugins:
                print('[ PLIGIN UID ]  ' + str(plugin.get_uid()))
            return
        except UidNotAssignedError:
            print('MALFUNCTION')
            return
