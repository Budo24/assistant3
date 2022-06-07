from common import NoAction
import datetime
import requests

class Plugin():
    activation_dict = {
        'w1': 'start'
    }
    
    def __init__(self):
        self.words = []
    
    def should_run(self):
        print("self")
        print(self.words)
        print(Plugin.activation_dict['w1'] in self.words)
        if not Plugin.activation_dict['w1'] in self.words:

            raise NoAction()
        else:
            print("RUNNING")
    
    def run(self, l):
        print("***************************")
        self.words = l
        try:
            self.should_run()
        except Exception as e:
            print("EXCEPTION OCCURED")


class DatePlugin():
    activation_dict = {
        'w1': 'date',
    }
    
    def __init__(self):
        self.words = []


    
    def should_run(self):
        print(self.words)
        print(Plugin.activation_dict['w1'])
        if not __class__.activation_dict['w1'] in self.words:

            raise NoAction()
        else:
            print("RUNNING")

    def output(self):
        o = datetime.datetime.now()
        return o
    
    def run(self, l):
        print("***************************")
        self.words = l
        try:
            self.should_run()
            return self.output()
        except Exception as e:
            print("EXCEPTION OCCURED")

class DatePlugin():
    activation_dict = {
        'w1': 'date',
    }
    
    def __init__(self):
        self.words = []


    
    def should_run(self):
        print(self.words)
        print(Plugin.activation_dict['w1'])
        if not __class__.activation_dict['w1'] in self.words:

            raise NoAction()
        else:
            print("RUNNING")

    def output(self):
        o = datetime.datetime.now()
        return o
    
    def run(self, l):
        print("***************************")
        self.words = l
        try:
            self.should_run()
            return self.output()
        except Exception as e:
            print("EXCEPTION OCCURED")


class NetworkPlugin():
    activation_dict = {
        'w1': 'internet',
    }
    
    def __init__(self):
        self.words = []


    
    def should_run(self):
        print(self.words)
        print(Plugin.activation_dict['w1'])
        if not __class__.activation_dict['w1'] in self.words:

            raise NoAction()
        else:
            print("RUNNING")

    def output(self):
        try:
            x = requests.get("https://google.com/")
            return(x.text)
        except Exception as e:
            return("NO INTERNET CONNEXION")
    
    def run(self, l):
        print("***************************")
        self.words = l
        try:
            self.should_run()
            return self.output()
        except Exception as e:
            print("EXCEPTION OCCURED")