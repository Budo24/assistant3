from ast import keyword
from os import stat
from this import s
from threading import active_count
from urllib.parse import non_hierarchical
#from turtle import st
from common import NoAction, UUidNotAssigned, PluginResultType, PluginType, plugin_defined_errors, constants
import datetime
from datetime import date
from numpy import single
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

    def similar_keyword_activated(self, target):
        """ checks if input keyword is similar to any of keywords,
            which can be recognised
            and returns keyword
        """

        if len(self.activation_dict['docs']) == 0:
            # if there is no reference phrases, not activated
            return False 
        activation_similarities = self.get_activation_similarities(target)
        for index, similarity in enumerate(activation_similarities):
            # the logic maybe changed later ! 
            if similarity > self.min_similarity:
                return self.activation_dict['docs'][index]
        return False

    def exact_keyword_activated(self, target):
        """ checks if input keyword is the same like keyword, which can be recognised
        and returns keyword
        """
        if len(self.activation_dict['docs']) == 0:
            # if there is no reference phrases, not activated
            return False 
        activation_similarities = self.get_activation_similarities(target)
        for index, similarity in enumerate(activation_similarities):
            # the logic maybe changed later ! 
            if similarity == self.min_similarity:
                print("To return: ", self.activation_dict['docs'][index])
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
        self.end_result["type"] = PluginResultType.TEXT
        self.end_result["plugin_type"] = PluginType.TRIGGER_PLUGIN
        self.end_result["result_speech_func"] = self.spit
        self.queue.put(self.end_result)
        return


class NetworkPlugin(BasePlugin):
    pass

class SingleDate:
    def __init__(self, date_, day_ordinal_number_):

        self.date = date_
        self.next = None
        self.activities = {}
        self.day_ordinal_number = day_ordinal_number_ 
        


class MonthlyPlanPlugin(BasePlugin):

    def __init__(self):
   
        super().__init__("insert") 
        self.first_date = None
        self.last_date = None
        self.actions_keywords = {"add_date": False, "delete_date": False,
                                 "add_activity": False, "delete_activity": False}

        self.time_range_add = False
        self.activity_add = False
        self.said_day = False
        self.date_exist = False
        self.single_day = False
        self.time_range_ = False

    def spit_text(self):

        self.engine.say(self.end_result["result"])
        self.engine.runAndWait()

    def give_date_from_monthly_plan(self, _date):
        print("Date: ", _date)
        if self.first_date is None: 
            print("Returning false")
            return False
        start = self.first_date
        _date = str(_date)
        print("Start date: ", start.date)
        print(type(_date))
        print(type(start.date))
        print("Start ")
        if start.date == _date:
            print("First given")
            return start
        while start.next is not None:
            print("Start date inside: ", _date)
            print("Start.date: ", start.date)
            if start.date == _date:
                print("Found")
                print("Middle given")
                return start
            start = start.next
        if start.date == _date:
            print("Last given")
            return start
        return False

    def form_time_range(activated_keyword):

        activated_keyword = activated_keyword.split(' ')
        hour_minutes = ""
        time_range = []
        skip_interation = False

        for index, keyword_ in enumerate(activated_keyword):
            if skip_interation:
                skip_interation = False
                continue

            hour_minutes += keyword_
            if ('twenty' or 'thirty') == keyword_ \
                and activated_keyword[index+1] != 'zero' \
                and activated_keyword[index+1] != 'thirty':
                hour_minutes += ' ' + activated_keyword[index+1]
                skip_interation = True

            time_range.append(hour_minutes)
            hour_minutes = ""

        return time_range   

    def convert_time_range_from_words_to_numbers(time_range):

        time_range_numbers = []
        print("In function on begin: ", time_range)

        if len(time_range) != 4:
            print("Returning")
            return time_range_numbers

        for index, word in enumerate(time_range):
            for numbers, words in constants.hour_number_to_word.items():
                if index in (0, 2)  and word == words:

                    print("Index in hours: ", index)
                    time_range_numbers.append(int(numbers))

        for index, word in enumerate(time_range):
            for numbers, words in constants.minute_number_to_word.items():
                if index in (1, 3) and word == words:

                    print("Index in minutes: ", index)
                    time_range_numbers.append(int(numbers))
        

        time_range_numbers[2], time_range_numbers[1] = \
            time_range_numbers[1], time_range_numbers[2]
        print("Time range numbers: ", time_range_numbers)
        return time_range_numbers

    def time_range_validy(time_range_numbers):

        time_range = -1
        all_integers = True
        for element in time_range_numbers:
            if not isinstance(element, int):
                all_integers = False

        if len(time_range_numbers) != 4:
            all_integers = False 

        if all_integers:
            print("Time range validy: ", time_range_numbers)
            time_range = (time_range_numbers[2]*60 + time_range_numbers[3])\
                          - (time_range_numbers[0]*60 + time_range_numbers[1])
            print("time_range: ", time_range)
        
        return time_range

    def activity_exist(self, date_single: SingleDate, time_range_numbers_):
        print("self.single_date.date: ", self.single_day.date)
        print("Time range numbers: ", time_range_numbers_)

        time_range_numbers_ = [int(word) for word in time_range_numbers_]
        print("Works1")
        starting_time_to_insert = \
            int(time_range_numbers_[0])*60 + int(time_range_numbers_[1])
        print("Works2")
        ending_time_to_insert = \
            int(time_range_numbers_[2])*60 + int(time_range_numbers_[3])
        print("Works 3")
        for time_range, act in date_single.activities.items():
            print("Time range: ", time_range)
            
            time_range = time_range.split(' ')
            
            starting_time = int(time_range[0])*60 + int(time_range[1]) 
            ending_time = int(time_range[2])*60 + int(time_range[3])

            if ending_time > starting_time_to_insert > starting_time:
                return True

            if ending_time > ending_time_to_insert > starting_time:
                return True

            if ending_time_to_insert >= ending_time and \
                starting_time_to_insert <= starting_time:
                return True
        print("Successfull")
        return False
    
    def activity_in_time(self, time_range_possible, time_range_numbers, \
                        time_range_words):

        if time_range_possible < 0: 
            print("")
            self.actions_keywords['add_activity'] = False
            self.min_similarity = 0.75
            self.reset_activity()
            return "Time range {} is not valid, try another one,"\
            " adding of activity broken.".format(time_range_words)

        if not self.activity_exist(self.single_day, time_range_numbers):
            print("Here")
            self.activity_add = True
            self.add_time_range(time_range_numbers)

            return "Time range {} available,"\
            " you can try to add an activity".format(time_range_numbers)

        print("Returned false")
        self.actions_keywords['add_activity'] = False
        self.min_similarity = 0.75
        self.reset_activity()
        return "In that time range already exist activity"

    def time_range(self, activated_keyword):

        time_range_words = self.form_time_range(activated_keyword)
        time_range_numbers = \
            self.convert_time_range_from_words_to_numbers(time_range_words)
        time_range_possible = \
            self.time_range_validy(time_range_numbers)
        answer = self.activity_in_time(time_range_possible, time_range_numbers,\
                                       time_range_words)
        return answer
    
    def reset_activity(self):
        self.time_range_add = False
        self.activity_add = False
        self.said_day = False
        self.date_exist = False
        self.single_day = False
    
    def add_time_range(self, time_range_numbers):
        time_range_ = ""
        for number in time_range_numbers:
            time_range_ += str(number) + " "
        self.time_range_ = time_range_.rstrip()
    
    def add_activity_to_time_range(self, activated_keyword):

        start = self.first_date
        if start.date == self.single_day.date:
            start.activities[self.time_range_] = activated_keyword
        while start.next != None:
            if start.date == self.single_day.date:
                start.activities[self.time_range_] = activated_keyword
        if start.date == self.single_day.date:
            start.activities[self.time_range_] = activated_keyword

    def insert_activity(self, activated_keyword):
        print("Inside")
        print("Activated keyword: ", activated_keyword)
        print("Here") 

        if self.date_exist is False:
            print("Dating")
            self.date_exist, date_number_of_days, day_in_past, self.said_day = \
                    self.check_date_before_action(activated_keyword)
            print("Dating done")
            print("self.date_exist: ", self.date_exist)
            print(type(self.date_exist))
            
            if self.date_exist:
                print("Exist")
                self.time_range_add = True
                print("SELF.said_day: ", self.said_day)
                self.single_day = self.give_date_from_monthly_plan(self.said_day)
                print("Self.single_day: ", self.single_day)
                say_date = self.say_date(self.said_day)
                return "Date {} exist in monthly plan,"\
                " you can add time range"\
                    .format(say_date)
            else:
                print("Does not exist")
                self.actions_keywords['add_activity'] = False
                self.min_similarity = 0.75
                say_date = self.say_date(self.said_day)
                self.reset_activity()
                return "Date {} does not exist in monthly plan, "\
                        "adding of activity broken".format(say_date)

        if self.activity_add:
            self.add_activity_to_time_range(activated_keyword)
            self.actions_keywords['add_activity'] = False
            self.min_similarity = 0.75
            self.reset_activity()
            return "Activity {} successfully added".format(activated_keyword)

        if self.time_range_add: 

            print("self.time_range_add: ", self.time_range_add)
            
            answer_to_create_time_range = \
                self.time_range(activated_keyword)
            print("Done")
            return answer_to_create_time_range
        


    def say_result_put_in_queue(self):

        self.end_result["type"] = PluginResultType.TEXT
        self.end_result["result_speech_func"] = self.spit_text
        self.queue.put(self.end_result)

        return

    def show_dates(self):

        if self.first_date == None:

            self.end_result["result"] = "Monthly plan is empty"
            self.say_result_put_in_queue()
            
        else:

            date = self.first_date
            self.end_result["result"] = "" 
            while date != None:
                print("Date activity: ", date.activities)
                date_word = self.say_date(date.date)
                self.end_result["result"] += ', ' + date_word
                date = date.next

            self.end_result["result"] += ", that would be your monthly plan"
            self.say_result_put_in_queue()

    def check_existing_dates(self, day_ordinal_number):

        date = self.first_date

        while date != None:

            if date.day_ordinal_number == day_ordinal_number:
                return True
            date = date.next

        return False

    def check_number_of_days_in_month(self, date):

        date = date.split('-')
        date_days = date[2]
        date_month = date[1]
        date_year = date[0]

        print("Date days: ", date_days)
        print("Date month: ", date_month)
        print("Date year: ", date_year)

        for month, days in constants.month_days.items():
            if date_days > days and date_month == month:

                if date_month == '02' and date_days == '29':
                    date_year = int(date_year)
                    if date_year % 4 == 0: 
                        return True
                    else: 
                        return "This year february has {} days".format(days)
                else:
                    return "This month has {} days".format(days)
        return True

    def create_date(self, ordinal_number_day):
        day = False

        for word, number in constants.ordinal_number_to_number.items():
            if word == ordinal_number_day:
                day = number

        today = date.today()
        create_date = str(today)
        if day:
            created_date = create_date[:-2] + day
        else:
            created_date = False

        return  created_date

    def day_today(self):

        day_today = str(date.today())
        day_today = day_today[len(day_today)-2:]
        return day_today

    def day_past_in_monthly_plan(self, date_to_insert):

        day = date_to_insert[len(date_to_insert)-2:]
        day_today = self.day_today()
        
        if day_today > day:
            return constants.answers[5]
        elif day_today == day:
            return constants.answers[6]
        else:
            return False
    
    def check_date_before_action(self, day_ordinal_number):

        date_already_exist = self.check_existing_dates(day_ordinal_number)
        date = self.create_date(day_ordinal_number)
        day_in_past = self.day_past_in_monthly_plan(date)
        check_number_of_days = self.check_number_of_days_in_month(date)
        return date_already_exist, check_number_of_days, day_in_past, date

    def say_date(self, date):
        
        date = date.split('-')
        day = date[2]
        month = date[1]
        year = date[0]

        for number_, month_ in constants.month_number_to_word.items():
            if number_ == month:
                month = month_
        for word_, number_ in constants.ordinal_number_to_number.items():
            if number_ == day:
                day = word_
        date = day + ' ' +  month + ' ' + year

        return date

    def delete_date_(self, day_ordinal_number):

        print("We are inside of deleting of date")

        date_exist, date_number_of_days, day_in_past, date = \
             self.check_date_before_action(day_ordinal_number)
        print("Date: ", date)

        print("Date to say: ", date)
        if date_exist:
            date = self.say_date(date)
            start = self.first_date
            self.actions_keywords['delete_date'] = False
            self.min_similarity = 0.75  

            if start.day_ordinal_number == day_ordinal_number:
                if self.last_date == self.first_date:
                    self.last_date = None
                self.first_date = self.first_date.next
                
                print("First")
                return "The first date {} is successfully deleted, "\
                "fuction for deleting is deactivated".format(date)

            previous = start 
            start = start.next

            while start.next != None:  

                print("Inside")
                if start.day_ordinal_number == day_ordinal_number:

                    previous.next = start.next
                    print("Second")
                    return "The date {} is successfully deleted, "\
                    "fuction for deleting "\
                    "is deactivated".format(date)

                previous = start
                start = start.next 

            self.last_date = previous
            self.last_date.next = None
            print("Third")
            return "The last date {} in the monthly plan is deleted".format(date)

        else:
            date = self.say_date(date)
            self.actions_keywords['delete_date'] = False
            self.min_similarity = 0.75
            print("Fourth")

            return "The date {}  does not exist in monthly "\
            "plan, so it can not be deleted".format(date)

    def insert_date(self, day_ordinal_number):

        date_exist, date_number_of_days, day_in_past, date = \
             self.check_date_before_action(day_ordinal_number)

        print("Date exist: ", date_exist)
        print("Date number of days: ", date_number_of_days)
        print("Day in past: ", day_in_past)
        print("Date: ", date)

        if date_number_of_days != True:

            self.actions_keywords['add_date'] = False
            self.min_similarity = 0.75
            return date_number_of_days

        if date_exist is False:

            if day_in_past:

                self.actions_keywords['add_date'] = False
                self.min_similarity = 0.75
                return day_in_past
            else:

                Date = SingleDate(date, day_ordinal_number)

                if self.last_date == None and self.first_date == None:
                    self.first_date = Date
                    self.last_date = Date

                else:
                    self.last_date.next = Date
                    self.last_date = Date

                date = self.say_date(date)
                self.actions_keywords['add_date'] = False
                self.min_similarity = 0.75

                return "Date {} is successfully inserted, function "\
                "for inserting of dates is deactivated".format(date)
        else:

            self.actions_keywords['add_date'] = False
            self.min_similarity = 0.75
            date_ = self.say_date(date)
            return "Date {} already exist in monthly plan".format(date_)

    def add_date(self, activated_keyword):

        if activated_keyword in constants.days_ordinal_numbers_keywords:
            self.end_result["result"] = self.insert_date(activated_keyword)
            self.say_result_put_in_queue()
            return
    
    def delete_date(self, activated_keyword):

        if activated_keyword in constants.days_ordinal_numbers_keywords:
            self.end_result["result"] = self.delete_date_(activated_keyword)
            self.say_result_put_in_queue()
            return

    def add_activity(self, activated_keyword):
        print("Activated keyword: ", activated_keyword)
        print("self.single_day: ", self.single_day) 


        if activated_keyword not in constants.days_ordinal_numbers_keywords\
             and self.time_range_add is False:
            self.actions_keywords['add_activity'] = False
            self.min_similarity = 0.75
            self.reset_activity()
            self.end_result["result"] = "Break adding of activity"
            self.say_result_put_in_queue()
            return 
        self.end_result["result"] = self.insert_activity(activated_keyword)
        self.say_result_put_in_queue()
        return 
            
    def action_activated(self):

        for function, activated in self.actions_keywords.items():
            if activated:
                return function
        return False
  
    def deactivate_action(self): 

        self.min_similarity = 0.75

        if self.actions_keywords['add_date']:
            self.actions_keywords['add_date'] = False
            self.end_result["result"] = constants.answers[8]

        if self.actions_keywords['delete_date']:
            self.actions_keywords['delete_date'] = False
            self.end_result["result"] = constants.answers[9]
        
        if self.actions_keywords['add_activity']:
            self.actions_keywords['add_activity'] = False
            self.end_result["result"] = constants.answers[10]

        self.say_result_put_in_queue() 
        return
   

    def activate_action(self, activated_keyword):

        self.min_similarity = 1
        print("Activated_keyword: ", activated_keyword)

        if activated_keyword == constants.actions_keywords[5]:

            self.actions_keywords['add_date'] = True
            self.end_result["result"] = constants.answers[1]
            self.say_result_put_in_queue()
        

        if activated_keyword == constants.actions_keywords[2]:

            self.actions_keywords['delete_date'] = True
            self.end_result["result"] = constants.answers[2]
            self.say_result_put_in_queue()
            
            
        if activated_keyword == constants.actions_keywords[3]:

            self.actions_keywords['add_activity'] = True
            self.end_result["result"] = constants.answers[3]
            self.say_result_put_in_queue()

        return

    def add_keywords(self):

        for keyword in constants.actions_keywords:
            self.add_activation_doc(keyword)

        for day_orindal_number_keyword in constants.days_ordinal_numbers_keywords:
            self.add_activation_doc(day_orindal_number_keyword)
    
    def show_dates(self): 

        if self.first_date == None:

            self.end_result["result"] = "Monthly plan is empty"
            self.say_result_put_in_queue()

        else:

            date = self.first_date
            self.end_result["result"] = "" 

            while date != None:
                print("Activity: ", date.activities)
                date__word = self.say_date(date.date)
                self.end_result["result"] += ', ' + date__word
                date = date.next

            self.end_result["result"] += ", that would be your monthly plan"
            self.say_result_put_in_queue()

        return

    def wrong_inputs(self, activated_keyword, action_activated): 
        if action_activated == 'add_date'\
             and activated_keyword not in constants.days_ordinal_numbers_keywords:
            self.actions_keywords['add_date'] = False
            self.end_result["result"] = "Input is wrong, try again with insert"
            self.say_result_put_in_queue()
            return
        if action_activated == 'delete_date'\
             and activated_keyword not in constants.days_ordinal_numbers_keywords:
            self.actions_keywords['delete_date'] = False
            self.end_result["result"] = "Input is wrong, try again with deleting"
            self.say_result_put_in_queue()
            return

    def check_keyword(self, action_activated, activated_keyword):

        if action_activated == 'add_date'\
             and activated_keyword in constants.days_ordinal_numbers_keywords:

            if self.actions_keywords['add_date']:
                self.add_date(activated_keyword)
                return

        if action_activated == 'delete_date'\
             and activated_keyword in constants.days_ordinal_numbers_keywords:

            if self.actions_keywords['delete_date']:
                self.delete_date(activated_keyword)
                return
        
        self.wrong_inputs(activated_keyword, action_activated)

        if action_activated == 'add_activity':
            if self.actions_keywords['add_activity']:
                print("We are on the right position")
                self.add_activity(activated_keyword)
                return
        return
        
    def run_doc(self, doc, queue):

        self.queue = queue

        if self.min_similarity == 1:
            activated_keyword = str(self.exact_keyword_activated(doc))
        else:
            activated_keyword = str(self.similar_keyword_activated(doc))
        
   
        if activated_keyword == constants.actions_keywords[1]:
            self.show_dates()
            return 

        action_activated = self.action_activated() 

        if not action_activated:  

            self.activate_action(activated_keyword)
            return 
        print("Activated keyword: ", activated_keyword)
        print("Doc: ", doc)
        if activated_keyword == 'False' and self.actions_keywords['add_activity']:
            print("jaaa")
            if str(doc) != "":
                self.check_keyword(action_activated, str(doc))
            return
        self.check_keyword(action_activated, activated_keyword)
 