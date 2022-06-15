from common import NoAction, UUidNotAssigned, PluginResultType, PluginType, plugin_defined_errors
import datetime
import requests
import spacy
import time,pyttsx3



class BasePlugin():
    """Base Class from which all plugins need to inherit"""
    def __init__(self, match):
        # this will contain the reference initial doc
        # passed later from each plugin
        self.init_doc = match
        # pyttsx3 object for voice response
        self.engine=pyttsx3.init()
        # this will hold the activation/reference sentence or sentences
        self.activation_dict = {
            'docs': []
        }
        # unique id
        self.uid = None
        # this is the result dict with several informations like 
        # - uid
        # - type of the response 
        # - suggestion-message
        # ...

        # this is the dict that will be pushed to the results queue
        # when a plugin is activated and finished with processing
        self.end_result = {
            "uid": None,
            "type": PluginResultType.UNDEFINED,
            "plugin_type": PluginType.SYSTEM_PLUGIN,
            "result": None,
            "error_message": "",
            "suggestion_message": "",
            "resession_message": "",
            "result_speech_func": None
        }
        self.spacy_model = None

        # default minimum similarity, for a plugin to be activated, 
        # this is used by SpaCy and can also be changed in each plugin
        self.min_similarity = 0.75

    def spit(self):
        print("SPIT")
    
    def get_activation_similarities(self, target):
        """ return a number between 0 and 1 of how similar the input phrase 
            to the reference phrase/phrases
            list length is the same as how many reference phrases there is
        """
        return [doc.similarity(target) for doc in self.activation_dict['docs']]

    def is_activated(self, target):
        """ checks if a plugin is activated """
        if len(self.activation_dict['docs']) == 0:
            # if there is no reference phrases, not activated
            return False 
        activation_similarities = self.get_activation_similarities(target)
        print(activation_similarities)
        for similarity in activation_similarities:
            # the logic mybe changed later ! 
            if similarity > self.min_similarity:
                return True
        return False

    def init_activation_doc(self):
        """ this will add a SpaCy Object to the reference phrases, 
            but only the initial one, to add another one the next function 
            'add_activation_doc is used'
        """
        self.activation_dict['docs'].append(self.spacy_model(self.init_doc))
    
    def add_activation_doc(self, text):
        if not self.spacy_model:
            return
        self.activation_dict['docs'].append(self.spacy_model(text))

    def list_activation_docs(self):
        """ this prints the activation phrases in a plugin"""
        if len(self.activation_dict['docs']) == 0:
            print(" [EMPTY]")
        else:
            for doc in self.activation_dict['docs']:
                print(" [DOC TEXT]  ", end="")
                print(doc.text)
    
    def set_spacy_model(self, model):
        self.spacy_model = model
        self.init_activation_doc()
    
    def set_uid(self, uid):
        """Obvious"""
        if not self.uid:
            self.uid = uid
            self.end_result["uid"] = uid

    def get_uid(self):
        """Obvious"""
        if self.uid:
            return self.uid
        else: 
            raise UUidNotAssigned

class BaseInitializationErrorPlugin(BasePlugin):
    def __init__(self, error_details = {}):
        self.error_details = error_details
        super().__init__()

    def run_doc(self, doc, queue):
        pass


class SpacyDatePlugin(BasePlugin):
    def __init__(self):
        """ here we pass the initial reference phrase to the parent
            Object (BasePlugin) and it will take care of adding it as described
            above
        """
        super().__init__("what is the date")
        self.queue = None
       
    def spit(self):
        """this is the function/callback that a plugin needs to add in end result 
            in "result_speech_func" key, and in pw we call it to let the user 
            hear the answer of the plugin
        """
        print(time.strftime("%c"))
        self.engine.say(time.strftime("%c"))
        self.engine.runAndWait()
    
    def run_doc(self, doc, queue):
        """run function that we call in pw for each plugin
            * we pass the queue result defined in pw to each plugin, so the plugin can 
            push the final result to it if it's activated
            * and the doc representing a Spacy Object where the received voice input is
        """
        self.queue = queue
        #check if plugin is activted
        activated = self.is_activated(doc)
        if not activated:
            print("***")
            return
        o = datetime.datetime.now()
        # here we set some informations in the result dict
        self.end_result["type"] = PluginResultType.TEXT
        self.end_result["result"] = o
        self.end_result["result_speech_func"] = self.spit
        # here we push it to the results queue passed by pw
        self.queue.put(self.end_result)
        return

class TriggerPlugin(BasePlugin):
    def __init__(self):
        super().__init__("hey assistant")
        self.queue = None
        self.min_similarity = 0.99

    def spit(self):
        self.engine.say("how can i help")
        self.engine.runAndWait()
    
    def run_doc(self, doc, queue):
        self.queue = queue
        activated = self.is_activated(doc)
        if not activated:
            print("***")
            return
        o = datetime.datetime.now()
        self.end_result["type"] = PluginResultType.TEXT
        self.end_result["plugin_type"] = PluginType.TRIGGER_PLUGIN
        self.end_result["result_speech_func"] = self.spit
        self.queue.put(self.end_result)
        return

class DatePlugin(BasePlugin):
    pass


class NetworkPlugin(BasePlugin):
    pass