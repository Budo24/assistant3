from multiprocessing.dummy import active_children
from common import NoAction, UUidNotAssigned, PluginResultType, PluginType
import datetime
from numpy import datetime_as_string
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


class MonthlyPlanPlugin(BasePlugin):

    activation_dict = { 'w1': ['access', 'monthly', 'plan'],
                        'w2': ['insert', 'date'],
                        'w3': ['insert', 'activity'],
                        'w4': ['update', 'activity'],
                        'w5': ['delete', 'activity'],
                        'w6': ['tell', 'day'],
                        'w7': ['tell', 'me', 'actions']
    }
    
    def __init__(self):
        super().__init__()
        self.words = []
        self.queue = None
        self.access = False
        self.head = None
        self.tail = None

    def access_monthly_plan_(self):
        print("Inside access_monthly_plan")
        self.access = True
        self.end_result["type"] = PluginResultType.TEXT
        return ('Monthly plan is now accessable, if you want to see options, give me next command: tell me actions'
        .format(self.access))
    
    def say_me_actions(self):
        self.end_result["type"] = PluginResultType.TEXT
        if self.access == False:
            return ('Monthly plan is not accessable for everybody, if you are a real user you will know keywords')
        else:
            menu = ""
            count = 0
            for key, value in __class__.activation_dict.items():
                count += 1
                menu = menu + "{}th command is: {}".format(count, value)
            return menu

    def should_run(self):
        for activation in __class__.activation_dict.values():
            if all(word in self.words for word in activation):
                print("Word is catched")
                print("Switch between activities")
                if activation == ['access', 'monthly', 'plan']: 
                    print("Activation: ", activation)
                    self.end_result["result"] = self.access_monthly_plan_()
                    print("End_result: ", self.end_result)
                    return 
                if activation == ['tell', 'me', 'actions']:
                    print("Activation: ", activation)
                    self.end_result["result"] = self.say_me_actions()
                    return
        raise NoAction()
        
    def run(self, l, queue):
        print("***************************")
        self.words = l.split(' ')
        print("Words inserted: ", self.words)
        print("Type self.words: ", self.words)
        self.queue = queue
        self.end_result = {}
        print("End_result: ", self.end_result)
        try:
            self.should_run()
            print("Before")
            self.queue.put(self.end_result)
            print("After")
            return self.end_result
        except Exception as e:
            print("EXCEPTION OCCURED")

class DayPlanPlugin:
    def __init__(self, date):
        self.date = date
        self.next = None
