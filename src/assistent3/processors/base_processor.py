from common import NoAction, UUidNotAssigned, PluginResultType, PluginType
import datetime
import requests

class BasePlugin():
    def __init__(self):
        self.uid = None
        self.end_result = {
            "type": PluginResultType.UNDEFINED,
            "result": None,
            "should_die": True
        }
    
    def set_uid(self, uid):
        if not self.uid:
            self.uid = uid

    def get_uid(self):
        if self.uid:
            return self.uid
        else: 
            raise UUidNotAssigned

class DatePlugin(BasePlugin):
    activation_dict = {
        'w1': 'date',
    }
    
    def __init__(self):
        super().__init__()
        self.words = []
        self.queue = None


    
    def should_run(self):
        print(self.words)
        print(__class__.activation_dict['w1'])
        if not __class__.activation_dict['w1'] in self.words:

            raise NoAction()
        else:
            print("RUNNING")

    def output(self):
        o = datetime.datetime.now()
        self.end_result["type"] = PluginResultType.TEXT
        self.end_result["result"] = o
        self.queue.put(self.end_result)
        return 
    
    def run(self, l, queue):
        print("***************************")
        self.words = l
        self.queue = queue
        try:
            self.should_run()
            return self.output()
        except Exception as e:
            print("EXCEPTION OCCURED")


class NetworkPlugin(BasePlugin):
    activation_dict = {
        'w1': 'internet',
    }
    
    def __init__(self):
        super().__init__()
        self.words = []
        self.queue = None


    
    def should_run(self):
        print(self.words)
        print(__class__.activation_dict['w1'])
        if not __class__.activation_dict['w1'] in self.words:

            raise NoAction()
        else:
            print("RUNNING")

    def output(self):
        try:
            x = requests.get("https://google.com/")
            self.queue.put(x.text)
            return 
        except Exception as e:
            raise Exception
    
    def run(self, l, queue):
        print("***************************")
        self.words = l
        self.queue = queue
        try:
            self.should_run()
            self.end_result["type"] = PluginResultType.HTML
            self.end_result["result"] = self.output()
            self.queue.put(self.end_result)
            return self.end_result
        except Exception as e:
            print("EXCEPTION OCCURED")