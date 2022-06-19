from common import NoAction, UUidNotAssigned, PluginResultType, PluginType, plugin_defined_errors, constants
import datetime
from datetime import date
import requests
import spacy
import time,pyttsx3
import re



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
        print("init_activation_doc")
        self.activation_dict['docs'].append(self.spacy_model(self.init_doc))
    
    def add_activation_doc(self, text):
        if not self.spacy_model:
            return
        self.activation_dict['docs'].append(self.spacy_model(text))

    def similar_word(self, target):
        """ checks if a plugin is activated """
        if len(self.activation_dict['docs']) == 0:
            # if there is no reference phrases, not activated
            return False 
        activation_similarities = self.get_activation_similarities(target)
        for index, similarity in enumerate(activation_similarities):
            # the logic maybe changed later ! 
            if similarity > self.min_similarity:
                return self.activation_dict['docs'][index]
        return False

    def exact_keyword_activated_(self, target):
        """ checks if a plugin is activated """
        if len(self.activation_dict['docs']) == 0:
            # if there is no reference phrases, not activated
            return False 
        activation_similarities = self.get_activation_similarities(target)
        for index, similarity in enumerate(activation_similarities):
            # the logic maybe changed later ! 
            print("Similarity: ", similarity)
            print("Self.min_similarity: ", self.min_similarity)
            if similarity == self.min_similarity:
                return self.activation_dict['docs'][index]
        return False

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
    def add_keywords(self):
        keywords = ['how are you']
        for keyword in keywords:
            print("Keyword: ", keyword)
            self.add_activation_doc(keyword)

    def spit(self):
        """this is the function/callback that a plugin needs to add in end result 
            in "result_speech_func" key, and in pw we call it to let the user 
            hear the answer of the plugin
        """
        print(time.strftime("%c"))
        self.engine.say(time.strftime("%c"))
        self.engine.runAndWait()
    def spit_text(self):
        self.engine.say(self.end_result["result"])
        self.engine.runAndWait()
    
    def run_doc(self, doc, queue):
        """run function that we call in pw for each plugin
            * we pass the queue result defined in pw to each plugin, so the plugin can 
            push the final result to it if it's activated
            * and the doc representing a Spacy Object where the received voice input is
        """
        print("Queue: ", queue)
        self.queue = queue
        #check if plugin is activted
        activated = self.is_activated(doc)

        if not activated:
            print("***")
            return
        print("Here")
        activated_keyword = str(self.similar_word(doc))
        print("Activated_keyword: ", activated_keyword)

        if activated_keyword == "what is the date":
            o = datetime.datetime.now() 
            # here we set some informations in the result dict
            self.end_result["type"] = PluginResultType.TEXT
            self.end_result["result"] = o
            self.end_result["result_speech_func"] = self.spit
            # here we push it to the results queue passed by pw

        elif activated_keyword == "how are you":
            print("Found")
            self.end_result["type"] = PluginResultType.TEXT
            self.end_result["result"] = 'why do you ask me how am I'
            self.end_result["result_speech_func"] = self.spit_text
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

class Single_Date:
    def __init__(self, date, date_date):
        self.date = date
        self.next = None
        self.activities = {}
        self.date_date = date_date

    def set_date(self, date):
        self.date = date

    def get_date(self, date):
        if self.date == date:
            return self.date
        else:
            print("Date do not exist")
            return False

class MonthlyPlanPlugin(BasePlugin):

    def __init__(self):
        super().__init__("insert date in monthly plan") 
        self.head = None
        self.tail = None

        self.add_date = False
        self.delete_date = False
        self.add_activity = False
        self.delete_activity = False
        self.update_activitiy = False

        self.dates = constants.dates
        self.conv_date = constants.conv_date
        self.months = constants.months

        """ here we pass the initial reference phrase to the parent
            Object (BasePlugin) and it will take care of adding it as described
            above
        """
    def add_keywords(self):
        keywords = ['insert date in monthly plan', 'break', 'show dates'] 
        for keyword in keywords:
            self.add_activation_doc(keyword)
        for date in self.dates:
            self.add_activation_doc(date)
        print("Self.activation_dict: ", self.activation_dict)
        print("Keywords added")

    def show_dates(self):
        if self.head == None:
            self.end_result["type"] = PluginResultType.TEXT
            self.end_result["result"] = "Monthly plan is empty"
            self.end_result["result_speech_func"] = self.spit_text
            self.queue.put(self.end_result)
            return
        else:
            date__ = self.head
            self.end_result["result"] = "" 
            while date__!= None:
                date__word = self.say_date(date__.date)
                self.end_result["result"] += ', ' + date__word
                date__ = date__.next
            self.end_result["result"] += ", that would be your monthly plan"
            self.end_result["type"] = PluginResultType.TEXT
            self.end_result["result_speech_func"] = self.spit_text
            self.queue.put(self.end_result)

    def say_date(self, date):
        date = date.split('-')
        if date[2][0] == '0':
            date[2] = date[2].replace('0', '')
        print("date[2]: ", date[2])
        for number, month in self.months.items():
            if number == date[1]:
                month_ = month
        for word, number in self.conv_date.items():
            if str(number) == date[2]:
                day_ = word
        date = day_ + ' ' +  month_ + ' ' + date[0]
        return date

    def date_exist_in_monthly_plan(self, date_day):
        start = self.head
        while start != None:
            if start.date_date == date_day:
                print("Date found: ", start.date_date)
                return True
            start = start.next
        return False

    def make_date(self, date_day):
            for word, number in self.conv_date.items():
                if word == date_day:
                    day = number
            print("Day: ", day) 
            day = str(day)
            if len(day) == 1:
                day = '0' + day
            date_ = date.today()
            date_ = str(date_)
            date_ = date_[:-2] + day
            return date_

    def day_today(self):
        day_today = date.today()
        day_today = str(day_today)
        day_today = day_today[len(day_today)-2:]
        return day_today

    def check_number_of_days_in_month(self, date_):
        print("\n\n")
        print("Checking of number of days in month")
        date_ = date_.split('-')
        print("Date_: ", date_)
        for month, days in constants.days_per_month.items():
            print("\n\n")
            print("month: ", month)
            print("date_[1]: ", date_[1]) 
            print("days: ", days)
            print("date_[2]: ", date_[2])
            print("\n\n")
            if date_[2] > days and date_[1] == month:
                if date_[1] == '02' and date_[2] == '29':
                    date_[0] = int(date_[0])
                    print("Type: ", type(date_[0]))
                    if date_[0] % 4 == 0: 
                        print("Possible")
                        return True
                    else: 
                        return("This year february has {} days".format(days))
                else:
                    return("This month has {} days".format(days))
        return True
 
    def insert_date(self, date_day):

        date_already_exist = self.date_exist_in_monthly_plan(date_day)
        date_ = self.make_date(date_day)
        print("Date_: ", date_)
        check_number_of_days = self.check_number_of_days_in_month(date_)

        if check_number_of_days != True:
            return check_number_of_days

        if not date_already_exist:

            day = date_[len(date_)-2:]
            day_today = self.day_today()
           

            if day_today > day:
                return ("That date is in the past for this month, mothly plan provides just future")
            elif day_today == day:
                print("Today")
                return("if you want to plan, than plan for tomorrow, monthly plan does not provides plannig in the same day for now")
            else:
                Date = Single_Date(date_, date_day)
                if self.tail == None and self.head == None:
                    self.head = Date
                    self.tail = Date
                else:
                    self.tail.next = Date
                    self.tail = Date
                date_ = self.say_date(date_)
                self.add_date = False
                self.min_similarity = 0.75
                return ("Date {} is successfully inserted, function for inserting of dates is deactivated".format(date_))
        else:
            date_ = self.say_date(date_)
            return ("Date {} already exist in monthly plan".format(date_))

    def spit_text(self):
        self.engine.say(self.end_result["result"])
        self.engine.runAndWait()
    
    def run_doc(self, doc, queue):
        """run function that we call in pw for each plugin
            * we pass the queue result defined in pw to each plugin, so the plugin can 
            push the final result to it if it's activated
            * and the doc representing a Spacy Object where the received voice input is
        """
        print("Queue: ", queue)
        self.queue = queue
        #check if plugin is activted
        # activated = self.is_activated(doc)

        print("Here")
        if self.min_similarity == 1:
            activated_keyword = str(self.exact_keyword_activated_(doc))
        else:
            activated_keyword = str(self.similar_word(doc))
       
        if activated_keyword == "show dates":
            self.show_dates()

        if activated_keyword == "insert date in monthly plan" and not self.add_date:
            # here we set some informations in the result dict
            self.min_similarity = 1
            self.add_date = True
            self.end_result["type"] = PluginResultType.TEXT
            self.end_result["result"] = "Can you please say the date"
            self.end_result["result_speech_func"] = self.spit_text
            self.queue.put(self.end_result)
            return
            # here we push it to the results queue passed by pw
        print("Self.add_date: ", self.add_date)
        
        if activated_keyword == 'break' and self.add_date == True:
            self.add_date = False
            self.min_similarity = 0.75
            self.end_result["type"] = PluginResultType.TEXT
            self.end_result["result"] = "Ok insert of date is broken"
            self.end_result["result_speech_func"] = self.spit_text
            self.queue.put(self.end_result) 
            return
        
        print("Self.add_date: ", self.add_date)
        if activated_keyword in self.dates and self.add_date:
            print("We are on the right position")
            self.end_result["type"] = PluginResultType.TEXT
            self.end_result["result"] = self.insert_date(activated_keyword)
            self.end_result["result_speech_func"] = self.spit_text
            self.queue.put(self.end_result)
            return
        if self.add_date and activated_keyword != 'show dates':
            print("Right activation")
            self.end_result["type"] = PluginResultType.TEXT
            self.end_result["result"] = "I did not understand the date, can you please repeat, or say break, if you do not want to insert"
            self.end_result["result_speech_func"] = self.spit_text
            self.queue.put(self.end_result)
            return
        

