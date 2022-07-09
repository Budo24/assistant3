"""PluginWatcher."""
import contextlib
import queue
import typing

import spacy

import processors
from common.exceptions import UidNotAssignedError
from common.plugins import PluginResultType, PluginType
from common.utils import bulk_assign_uuid
from processors.base_processor import BasePlugin


class FlowRecord():
    """The class where we record plugins invoking flow."""

    def __init__(self) -> None:
        """Create FlowRecord object."""
        self.record: list[dict[str, object]] = []

    def add_entry(self, entry: dict[str, object]) -> None:
        """Empty."""
        self.record.append(entry)

    def get_last(self) -> dict[str, object] | typing.Any:
        """Empty."""
        if self.is_empty():
            return None
        return self.record[-1]

    def is_empty(self) -> bool:
        """Empty."""
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


class FeedbackIgnore():
    """The class to ignore feedback noise."""

    def __init__(self) -> None:
        """Init."""
        self.feedback_ignore = False

    def toggle_feedback_ignore(self) -> None:
        """Empty."""
        self.feedback_ignore = not self.feedback_ignore

    def get_feedback_ignore(self) -> bool:
        """Empty."""
        return self.feedback_ignore


class PluginWatcher():
    """The class where we maintain Plugins initialization and running.

    it does accept a list of plugins objects (not just class names) ex:
    plugin1 = DatePlugin()
    plugin2 = EtwasPlugin()
    pw = PluginWatcher([plugin1, plugin2, ...])
    """

    def __init__(self, plugins: list[object]):
        """Init."""
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
                        error_details={
                            'plugin_name': error_plugin_name,
                        },
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
        """Return last Result dict."""
        # CHECK how a queue works (python queue module)
        return self.results_queue.get()

    def init(self) -> None:
        """Init uid and spacy model."""
        print('INIT')
        # here we assign a unique id to each plugin, so later we can distinguish
        # between them, just from the result they send (which contains this uid)
        # witout bothering of accessing them with the names and all that head ache
        self.plugins = bulk_assign_uuid(self.plugins)

        # this is maybe a duplication, i'll check it later
        for plugin in self.plugins:
            plugin.set_spacy_model(self.nlp)

    def init_trigger_plugin(self) -> None:
        """If we add a trigger plugin to pw, this will initialize it like all plugins before.

        - set uid
        - set SpaCy model
        """
        print('INIT TRIGGER PLUGIN')
        self.trigger_plugin = bulk_assign_uuid([self.trigger_plugin])[0]
        self.trigger_plugin.set_spacy_model(self.nlp)

    def add_trigger_plugin(self, trigger_plugin_obj: BasePlugin) -> None:
        """Add trigger plugin, otherwise plugins will act on received voice directly."""
        self.trigger_plugin = trigger_plugin_obj
        if self.trigger_plugin:
            self.init_trigger_plugin()

    def is_trigger_plugin_enabled(self) -> bool:
        """Check if pw has a trigger plugin."""
        return self.trigger_plugin is not None

    def add_entry_to_flow_record(self, entry: dict[str, object]) -> None:
        """Empty."""
        self.flow_record.add_entry(entry)

    def run(self, speech_text: str) -> list[typing.Any]:
        """Run."""
        # we transform the text from vosk to doc object (pass it to SpaCy to process it)
        self.doc = self.nlp(speech_text)

        def run_by_uid(uid: object) -> None:
            if uid == self.trigger_plugin.get_uid():
                run_trigger()
            else:
                run_plugins(uid)

        def run_trigger() -> None:
            self.trigger_plugin.run_doc(self.doc, self.results_queue)

        def run_plugins(uid: object = None) -> None:
            if uid:
                for plugin in self.plugins:
                    if uid == plugin.get_uid():
                        plugin.run_doc(self.doc, self.results_queue)
                        return
            for plugin in self.plugins:
                print('run_doc')
                plugin.run_doc(self.doc, self.results_queue)

        def flush_result_queue_in_list() -> list[dict[str, object]]:
            res_list = []
            while self.results_queue.qsize() != 0:
                res_list.append(self.results_queue.get())
            return res_list

        self.flow_record.printify()

        if self.flow_record.is_empty():
            run_trigger()
            return flush_result_queue_in_list()

        last_record = self.flow_record.get_last()
        if last_record['type'] == PluginResultType.ERROR:
            run_by_uid(last_record['uid'])
            return flush_result_queue_in_list()

        if last_record['plugin_type'] == PluginType.TRIGGER_PLUGIN:
            print('LAST RECORD', last_record)
            run_plugins()
            return flush_result_queue_in_list()

        str_msg = ''
        if last_record['type'] == PluginResultType.KEEP_ALIVE:
            str_msg += '__KEEP_ALIVE'
        else:
            str_msg += '__NORMAL'

        print(str_msg)

        return []

    def list_plugins_by_uid(self) -> None:
        """Show all assigned plugin's uids."""
        try:
            if self.is_trigger_plugin_enabled():
                print('[ PLUGIN UID ]  ' + str(self.trigger_plugin.get_uid()))
            for plugin in self.plugins:
                print('[ PLUGIN UID ]  ' + str(plugin.get_uid()))
            return
        except UidNotAssignedError:
            print('MALFUNCTION')
            return
