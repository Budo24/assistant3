import queue
from processors import BaseInitializationErrorPlugin, BasePlugin
import common
import spacy

class PluginWatcher():
    """ The class where we maintain Plugins initialization and running 
        it does accept a list of plugins objects (not just class names) ex:
        plugin1 = DatePlugin()
        plugin2 = EtwasPlugin()
        pw = PluginWatcher([plugin1, plugin2, ...])
    """
    def __init__(self, plugins):
        
        # reslts_queue : the queue where all plugins push their result dicts
        self.results_queue = queue.Queue()
        # 
        self.plugins = []
        # flag to tell pw if a trigger plugin was already triggered ("hey assistant")
        self.triggered_now_plugins = False
        # data type related to SpaCy (nlp library)
        self.doc = None
        # spacy object with a trained AI model initialized
        self.nlp=spacy.load("en_core_web_md")
        # checks if any plugin was passed that doesn't inherit from BasePlugin
        # if it's the case, it will drop them all, and change it with a 
        # special plugin for this case 'BaseInitializationErrorPlugin'
        # we will see what to add in it later..
        for plugin in plugins:
            if not isinstance(plugin, BasePlugin):
                error_plugin_name = ''
                try:
                    error_plugin_name = plugin.__str__()
                except Exception as e:
                    pass
                self.plugins = [BaseInitializationErrorPlugin(
                    error_details = {
                        'plugin_name' :error_plugin_name
                    }
                )]
                break
            else:
                # if all good, we pass an instance of the nlp object to each plugin,
                # so it can be used to check similarity of what the user said compared
                # to the reference sentence
                print("Self.nlp: ", self.nlp)
                plugin.set_spacy_model(self.nlp)
                self.plugins.append(plugin)
        # here we add an empty trigger plugin, and later we can add one.
        # we can also remove it at any time
        self.add_trigger_plugin(None)

        self.init()
        
    def pop_result(self):
        # CHECK how a queue works (python queue module)
        return self.results_queue.get()

    def init(self):
        print("INIT")
        # here we assign a unique id to each plugin, so later we can distinguish
        # between them, just from the result they send (which contains this uid)
        # witout bothering of accessing them with the names and all that head ache
        self.plugins = common.bulk_assign_uuid(self.plugins)

        # [TODO] this is maybe a duplication, i'll check it later
        for plugin in self.plugins:
            plugin.set_spacy_model(self.nlp)
    
    def init_trigger_plugin(self):
        """
        if we add a trigger plugin to pw, this will initialize it like all plugins before,
        - set uid
        - set SpaCy model         
        """
        print("INIT TRIGGER PLUGIN")
        self.trigger_plugin = common.bulk_assign_uuid([self.trigger_plugin])[0]
        self.trigger_plugin.set_spacy_model(self.nlp)

    def add_trigger_plugin(self, trigger_plugin_obj):
        """ Adds trigger plugin, otherwise plugins will act on received voice 
            directly
        """
        self.trigger_plugin = trigger_plugin_obj
        if self.trigger_plugin:
            self.init_trigger_plugin()

    def is_trigger_plugin_enabled(self):
        """ checks if pw has a trigger plugin """
        return not self.trigger_plugin == None
    
    def run(self, speech_text, triggered_now_plugins=False):
        """
        This runs
        """
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
                self.trigger_plugin.run_doc( self.doc, self.results_queue)
            # if not, (trigger plugin was already triggered successfuly) we pass to plugins
            else:
                for plugin in self.plugins:
                    print('run_doc')
                    print("Run plugin but not trigger plugin: ", self.doc)
                    plugin.run_doc( self.doc, self.results_queue )
        # if not trigger plugin present, we pass directly to plugins
        else:
            for plugin in self.plugins:

                plugin.run_doc( self.doc, self.results_queue )
        
        # in all cases, wether we pass to plugins or to trigger plugin,
        # at this point we go back to initial state (after we say "hey assistant, and then ask 
        # what we want") we are back to the start, 
        self.triggered_now_plugins = False

        # this is a speedy thing, maybe removed later, just quickly getting 
        # all results from the queue into a list 
        res_list = []
        while not self.results_queue.qsize() == 0:
            res_list.append(self.results_queue.get())
        return res_list


    def standby(self, last_result=None):
        pass

    def list_plugins_by_uid(self):
        """
        shows all assigned plugin's uids
        """
        try:
            if self.is_trigger_plugin_enabled():
                print('[ PLIGIN UID ]  ' + str(self.trigger_plugin.get_uid()))
            for plugin in self.plugins:
                print('[ PLIGIN UID ]  ' + str(plugin.get_uid()))
        except common.UUidNotAssigned as e:
            print('MALFUNCTION')
