"""PluginWatcher."""
import contextlib
import queue
import typing

import spacy

import processors
from common.exceptions import UidNotAssignedError
from common.utils import bulk_assign_uuid
from processors.base_processor import BasePlugin


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
                self.plugins = [processors.base_processor.BaseInitializationErrorPlugin(
                    error_details={
                        'plugin_name': error_plugin_name,
                    })]
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

    def run(self, speech_text: str, triggered_now_plugins: bool = False) -> list[typing.Any]:
        """Run."""
        # we transform the text from vosk to doc object (pass it to SpaCy to process it)
        self.doc = self.nlp(speech_text)
        # flag to know if a trigger plugin was triggered before run() was called
        # or not
        self.triggered_now_plugins = triggered_now_plugins
        print(self.doc)
        # if there is a trigger plugin assigned to pw ..
        if self.trigger_plugin:
            # if run() was called and no trigger plugin was triggered before,
            # we should run the Trigger run() function and not the plugins
            if not self.triggered_now_plugins:
                self.trigger_plugin.run_doc(self.doc, self.results_queue)
            # if not, (trigger plugin was already triggered successfuly) we pass to plugins
            else:
                for plugin in self.plugins:
                    print('run_doc')
                    plugin.run_doc(self.doc, self.results_queue)
        # if not trigger plugin present, we pass directly to plugins
        else:
            for plugin in self.plugins:
                print('run_doc')
                plugin.run_doc(self.doc, self.results_queue)
        # in all cases, wether we pass to plugins or to trigger plugin,
        # at this point we go back to initial state (after we say "hey assistant, and then ask
        # what we want") we are back to the start,
        self.triggered_now_plugins = False

        # this is a speedy thing, maybe removed later, just quickly getting
        # all results from the queue into a list
        res_list = []
        while self.results_queue.qsize() != 0:
            res_list.append(self.results_queue.get())
        return res_list

    def list_plugins_by_uid(self) -> None:
        """Show all assigned plugin's uids."""
        try:
            if self.is_trigger_plugin_enabled():
                print('[ PLIGIN UID ]  ' + str(self.trigger_plugin.get_uid()))
            for plugin in self.plugins:
                print('[ PLIGIN UID ]  ' + str(plugin.get_uid()))
            return
        except UidNotAssignedError:
            print('MALFUNCTION')
            return
