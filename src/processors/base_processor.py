"""BasePlugin."""
import datetime
import queue
import time
import typing
from datetime import date

import pyttsx3
import spacy

from common import constants
from common.exceptions import UidNotAssignedError
from common.plugins import PluginResultType, PluginType


def spit() -> None:
    """Play response audio."""
    print('SPIT')


def run_doc(doc: object, _queue: queue.Queue[typing.Any]) -> None:
    """Run_doc."""
    ret_str = ''
    ret_str += 'Not implemented, [todo] should raise exception instead\n'
    ret_str += 'doc: '
    ret_str += str(doc.__class__)
    ret_str += '\n'
    ret_str += 'queue: '
    ret_str += str(_queue.__class__)
    ret_str += '\n'
    print(ret_str)


class BasePlugin():
    """Base Class from which all plugins need to inherit."""

    def __init__(self, match: str):
        """Contain the reference initial doc passed later from each plugin."""
        self.init_doc = match
        self.spacy_model = spacy.blank('en')
        # pyttsx3 object for voice response
        self.engine = pyttsx3.init()
        # this will hold the activation/reference sentence or sentences
        self.activation_dict: dict[str, list[typing.Any]] = {
            'docs': [],
        }
        # unique id
        self.uid: object = None
        # this is the result dict with several informations like
        # - uid
        # - type of the response
        # - suggestion-message
        # ...

        # this is the dict that will be pushed to the results queue
        # when a plugin is activated and finished with processing
        self.end_result: dict[str, typing.Any] = {
            'uid': None,
            'type': PluginResultType.UNDEFINED,
            'plugin_type': PluginType.SYSTEM_PLUGIN,
            'result': None,
            'error_message': '',
            'suggestion_message': '',
            'resession_message': '',
            'result_speech_func': None,
        }

        # default minimum similarity, for a plugin to be activated,
        # this is used by SpaCy and can also be changed in each plugin
        self.min_similarity = 0.75

    def similar_keyword_activated(self, target: object) -> str | bool:
        """Search after similar words.

        Check if input keyword is similar to any of keywords
        and return keyword
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

    def spit_text(self) -> None:
        """Say answer.

        This function sends response to command given by speaker
        """
        self.engine.say(self.end_result['result'])
        self.engine.runAndWait()

    def exact_keyword_activated(self, target: object) -> str | bool:
        """Find exact keyword.

        Check if given keyword is the same compared to known known keywords
        """
        if len(self.activation_dict['docs']) == 0:
            # if there is no reference phrases, not activated
            return False
        activation_similarities = self.get_activation_similarities(target)
        for index, similarity in enumerate(activation_similarities):
            # the logic maybe changed later !
            if similarity == self.min_similarity:
                print('To return: ', self.activation_dict['docs'][index])
                return self.activation_dict['docs'][index]
        return False

    def get_activation_similarities(self, target: object) -> list[typing.Any]:
        """Return a similarity between 0 and 1.

        list length is the same as how many reference phrases there is
        """
        return [doc.similarity(target) for doc in self.activation_dict['docs']]

    def is_activated(self, target: object) -> bool:
        """Check if a plugin is activated."""
        if len(self.activation_dict['docs']) == 0:
            # if there is no reference phrases, not activated
            return False
        activation_similarities = self.get_activation_similarities(target)
        print(activation_similarities)
        return bool(similarity > self.min_similarity for similarity in activation_similarities)

    def init_activation_doc(self) -> None:
        """Add a SpaCy Object to the reference phrases.

        but only the initial one, to add another one the next function
        'add_activation_doc is used'
        """
        if self.spacy_model:
            init_doc_obj = self.spacy_model(self.init_doc)
            self.activation_dict['docs'].append(init_doc_obj)

    def add_activation_doc(self, text: str) -> None:
        """Add doc from text."""
        if not self.spacy_model:
            return
        self.activation_dict['docs'].append(self.spacy_model(text))

    def list_activation_docs(self) -> None:
        """Print the activation phrases in a plugin."""
        if len(self.activation_dict['docs']) == 0:
            print('[EMPTY]')
        else:
            for doc in self.activation_dict['docs']:
                print(' [DOC TEXT]  ', end='')
                print(doc.text)

    def set_spacy_model(self, model1: spacy.language.Language) -> None:
        """Set spacy model."""
        self.spacy_model = model1
        self.init_activation_doc()

    def set_uid(self, uid: object) -> None:
        """Set UID."""
        if not self.uid:
            self.uid = uid
            self.end_result['uid'] = uid

    def get_uid(self) -> object:
        """Get UID."""
        if self.uid:
            return self.uid
        raise UidNotAssignedError


class BaseInitializationErrorPlugin(BasePlugin):
    """BaseInitializationErrorPlugin."""

    def __init__(self, error_details: dict[str, typing.Any]):
        """Init."""
        self.error_details = error_details
        super().__init__(match='')


class SpacyDatePlugin(BasePlugin):
    """SpacyDatePlugin."""

    def __init__(self) -> None:
        """Pass the initial reference phrase to the parent Object (BasePlugin).

        and it will take care of adding it as described
        above
        """
        super().__init__('what is the date')
        self.queue: queue.Queue[typing.Any] = queue.Queue(0)

    def spit(self) -> None:
        """Play response audio."""
        print(time.strftime('%c'))
        self.engine.say(time.strftime('%c'))
        self.engine.runAndWait()

    def run_doc(self, doc: object, _queue: queue.Queue[typing.Any]) -> None:
        """Run_doc."""
        self.queue = _queue
        # check if plugin is activted
        activated = self.is_activated(doc)
        if not activated:
            print('***')
            return
        output_result_value = datetime.datetime.now()
        # here we set some informations in the result dict
        self.end_result['type'] = PluginResultType.TEXT
        self.end_result['result'] = output_result_value
        self.end_result['result_speech_func'] = spit
        # here we push it to the results queue passed by pw
        self.queue.put(self.end_result)
        return


class TriggerPlugin(BasePlugin):
    """TriggerPlugin."""

    def __init__(self) -> None:
        """Init."""
        super().__init__('hey assistant')
        self.queue: queue.Queue[typing.Any] = queue.Queue(0)
        self.min_similarity = 0.99

    def spit(self) -> None:
        """Play response audio."""
        self.engine.say('how can i help')
        self.engine.runAndWait()

    def run_doc(self, doc: object, _queue: queue.Queue[typing.Any]) -> None:
        """Run_doc."""
        self.queue = _queue
        activated = self.is_activated(doc)
        if not activated:
            print('***')
            return
        self.end_result['type'] = PluginResultType.TEXT
        self.end_result['result'] = datetime.datetime.now()
        self.end_result['plugin_type'] = PluginType.TRIGGER_PLUGIN
        self.end_result['result_speech_func'] = spit
        self.queue.put(self.end_result)
        return


def form_time_range(activated_keyword: str) -> list[str]:
    """Form time range from said time range."""
    activated_keyword_ = activated_keyword.split(' ')
    hour_minutes = ''
    time_range = []
    skip_interation = False

    for index, keyword in enumerate(activated_keyword_):
        if skip_interation:
            skip_interation = False
            continue

        hour_minutes += keyword
        if ('twenty' or 'thirty') == keyword \
            and activated_keyword_[index + 1] != 'zero' \
                and activated_keyword_[index + 1] != 'thirty':
            hour_minutes += ' ' + activated_keyword_[index + 1]
            skip_interation = True

        time_range.append(hour_minutes)
        hour_minutes = ''

    return time_range


def create_date(ordinal_number_day: str) -> str:
    """Create date in current month.

    Create date in month using just day, given like ordinal number
    """
    day_created = 'not created'

    for word, number in constants.ordinal_number_to_number.items():
        if word == ordinal_number_day:
            day_ = number
            day_created = 'created'

    today = date.today()
    create_date_ = str(today)
    if day_created == 'created':
        return str(create_date_[:-2]) + str(day_)
    return day_created


def convert_time_range_from_words_to_numbers(time_range: list[str]) -> list[int]:
    """Convert time range from words to numbers.

    It is helping function, to enable calculation in time_validy
    """
    time_range_numbers: list[int] = []
    print('In function on begin: ', time_range)

    if len(time_range) != 4:
        print('Returning')
        return time_range_numbers

    for index, _word in enumerate(time_range):
        for numbers, _words in constants.hour_number_to_word.items():
            print('Numbers: ', numbers)
            print('')
            if index in (0, 2) and _word == _words:
                print('Index in hours: ', index)
                time_range_numbers.append(int(numbers))

    for index, _word in enumerate(time_range):
        for numbers, _words in constants.minute_number_to_word.items():
            if index in (1, 3) and _word == _words:
                print('Index in minutes: ', index)
                time_range_numbers.append(int(numbers))

    time_range_numbers[2], time_range_numbers[1] = \
        time_range_numbers[1], time_range_numbers[2]
    print('Time range numbers: ', time_range_numbers)
    return time_range_numbers


def check_number_of_days_in_month(_date: str) -> str | bool:
    """Check if given day like ordinal number exist in month.

    To avoid for example 31-06-2022
    """
    _date_ = _date.split('-')
    date_days = _date_[2]
    date_month = _date_[1]
    date_year = int(_date_[0])

    print('Date days: ', date_days)
    print('Date month: ', date_month)
    print('Date year: ', date_year)

    for month, days in constants.month_days.items():
        if date_days > days and date_month == month:

            if date_month == '02' and date_days == '29':
                if date_year % 4 == 0:
                    return True
                return f'This year february has {days} days'
            return f'This month has {days} days'
    return True


def time_range_validy(time_range_numbers: list[int]) -> int:
    """Chech if time range make sense.

    To avoid activity between 16:00 - 15:00
    """
    time_range = -1
    all_integers = True
    print('Time_range_numbers', time_range_numbers)
    for element in time_range_numbers:
        if not isinstance(element, int):
            all_integers = False

    if len(time_range_numbers) != 4:
        all_integers = False

    if all_integers:
        print('Time range validy: ', time_range_numbers)
        time_range = (time_range_numbers[2] * 60 + time_range_numbers[3])\
            - (time_range_numbers[0] * 60 + time_range_numbers[1])
        print('time_range: ', time_range)

    return time_range


def day_today() -> str:
    """Give day in date from today."""
    day_today_ = str(date.today())
    return day_today_[len(day_today_) - 2:]


def day_past_in_monthly_plan(date_to_insert: str) -> str | bool:
    """Check if day in date is before or after today."""
    day = date_to_insert[len(date_to_insert) - 2:]
    day_today_ = day_today()

    if day_today_ > day:
        return constants.answers[5]
    if day_today_ == day:
        return constants.answers[6]
    return False


def say_date(date_to_say: str) -> str:
    """Convert from form date, to form to say.

    Example 20-06-2022 -> twenty sixth 2022
    """
    date_to_say_ = date_to_say.split('-')
    day = date_to_say_[2]
    month = date_to_say_[1]
    year = date_to_say_[0]

    for number_, month_ in constants.month_number_to_word.items():
        if number_ == month:
            month = month_

    for word_, number_ in constants.ordinal_number_to_number.items():
        if number_ == day:
            day = word_
    return day + ' ' + month + ' ' + year


class SingleDate:
    """One single date in month."""

    def __init__(self, date_in_month: str, day_ordinal_number: str):
        """Initialize one single date values."""
        self.date_in_month = date_in_month
        self.next = None
        self.activities: dict[str, str] = {}
        self.day_ordinal_number = day_ordinal_number

    def get_activities(self, day_ordinal_number: str) -> dict | None:
        """Get activity in one single day."""
        if self.day_ordinal_number == day_ordinal_number:
            return self.activities
        return None

    def set_activity(self, day_ordinal_number: str, time_range: str, activity: str) -> None:
        """Set activity in one single day, in one time range."""
        if self.day_ordinal_number == day_ordinal_number:
            self.activities[time_range] = activity


def activity_exist(one_date: SingleDate, time_range_numbers: list[int]) -> bool:
    """Check if activity overlap another activity."""
    print('Time range numbers: ', time_range_numbers)

    time_range_numbers = [int(word) for word in time_range_numbers]
    print('Works1')
    starting_time_to_insert = \
        int(time_range_numbers[0]) * 60 + int(time_range_numbers[1])
    print('Works2')
    ending_time_to_insert = \
        int(time_range_numbers[2]) * 60 + int(time_range_numbers[3])
    print('Works 3')
    for time_range, act in one_date.activities.items():
        print('Time range: ', time_range)
        print('Act: ', act)
        time_range_ = time_range.split(' ')

        starting_time = int(time_range_[0]) * 60 + int(time_range_[1])
        ending_time = int(time_range_[2]) * 60 + int(time_range_[3])

        if starting_time < starting_time_to_insert < ending_time:
            return True

        if starting_time < ending_time_to_insert < ending_time:
            return True

        if ending_time_to_insert >= ending_time and \
                starting_time_to_insert <= starting_time:
            return True
    print('Successfull')
    return False


class MonthlyPlanPlugin(BasePlugin):
    """Monthly Plan."""

    def __init__(self):
        """Initialize values in monthly plan.

        The second separated part of values, will be used
        by dealing with activities
        """
        super().__init__('insert')
        self.first_date = None
        self.last_date = None
        self.actions_keywords = {
            'add_date': False,
            'delete_date': False,
            'add_activity': False,
            'delete_activity': False,
        }

        self.time_range_add = False
        self.activity_add = False
        self.said_day = 'nothing nothing'
        self.date_exist = False
        self.single_day = False
        self.time_range_ = False
        self.queue = None

    def give_date_from_monthly_plan(self, find_date: str) -> SingleDate:
        """Give date from monthly plan, if it exist."""
        print('Date: ', find_date)
        start = self.first_date
        find_date = str(find_date)
        print('Start date: ', start.date_in_month)
        print(type(find_date))
        print(type(start.date_in_month))
        print('Start ')
        if start.date_in_month == find_date:
            print('First given')
            return start
        while start.next is not None:
            print('Start date inside: ', find_date)
            print('Start.date: ', start.date_in_month)
            if start.date_in_month == find_date:
                print('Found')
                print('Middle given')
                return start
            start = start.next
        if start.date_in_month == find_date:
            print('Last given')
            return start
        return start

    def activity_in_time(
        self,
        time_range_possible: int,
        time_range_numbers: list[int],
        time_range_words: list[str],
    ) -> str:
        """Check finally, if it is possible to add time range."""
        print('Time range possible: ', time_range_possible)
        if time_range_possible < 0:
            print('')
            self.actions_keywords['add_activity'] = False
            self.min_similarity = 0.75
            self.reset_activity()
            return f'Time range {time_range_words} is not valid, try another one, \
                adding of activity broken.'

        if not activity_exist(self.single_day, time_range_numbers):
            print('Here')
            # add time_range
            self.activity_add = True
            time_range_ = ''
            for number in time_range_numbers:
                time_range_ += str(number) + ' '
            self.time_range_ = time_range_.rstrip()

            return f'Time range {time_range_numbers} available, you can try to add an activity'

        self.actions_keywords['add_activity'] = False
        self.min_similarity = 0.75
        self.reset_activity()
        return 'In that time range already exist activity'

    def time_range(self, activated_keyword: str) -> str:
        """Create and check if it is possible to add time range."""
        time_range_words = form_time_range(activated_keyword)
        print('Time range: ', time_range_words)
        time_range_numbers = \
            convert_time_range_from_words_to_numbers(time_range_words)
        print('Time range numbers: ', time_range_numbers)
        time_range_possible = \
            time_range_validy(time_range_numbers)
        print('Time range possible: ', time_range_possible)
        return self.activity_in_time(time_range_possible, time_range_numbers, time_range_words)

    def reset_activity(self) -> None:
        """Reset all values regarding activity."""
        self.time_range_add = False
        self.activity_add = False
        self.said_day = 'nothing nothing'
        self.date_exist = False
        self.single_day = False

    def add_activity_to_time_range(self, activated_keyword: str) -> None:
        """Add activity to created time range."""
        start = self.first_date
        if start.date_in_month == self.single_day.date_in_month:
            start.activities[self.time_range_] = activated_keyword
        while start.next is not None:
            if start.date_in_month == self.single_day.date_in_month:
                start.activities[self.time_range_] = activated_keyword
        if start.date_in_month == self.single_day.date_in_month:
            start.activities[self.time_range_] = activated_keyword

    def insert_activity(self, activated_keyword: str) -> str | bool:
        """Try to insert activity, check also if it is possible."""
        print('Inside')
        print('Activated keyword: ', activated_keyword)
        if self.date_exist is False:
            print('Dating')
            self.date_exist, date_number_of_days, day_in_past, self.said_day = \
                self.check_date_before_action(activated_keyword)
            print('date_number_of_days: ', date_number_of_days)
            print('day_in_past: ', day_in_past)
            print('self.date_exist: ', self.date_exist)
            print(type(self.date_exist))

            if self.date_exist:
                print('Exist')
                self.time_range_add = True
                print('self.said_day: ', self.said_day)
                self.single_day = self.give_date_from_monthly_plan(self.said_day)
                print('Self.single_day: ', self.single_day)
                tell_date = say_date(self.said_day)
                return f'Date {tell_date} exist in monthly plan, \
                    you can add time range'

            print('Does not exist')
            self.actions_keywords['add_activity'] = False
            self.min_similarity = 0.75
            tell_date = say_date(self.said_day)
            self.reset_activity()
            return f'Date {tell_date} does not exist in monthly plan, \
                adding of activity broken'

        if self.activity_add:
            self.add_activity_to_time_range(activated_keyword)
            self.actions_keywords['add_activity'] = False
            self.min_similarity = 0.75
            self.reset_activity()
            return f'Activity {activated_keyword} successfully added'

        if self.time_range_add:
            print('self.time_range_add: ', self.time_range_add)
            return self.time_range(activated_keyword)
        return False

    def say_result_put_in_queue(self) -> None:
        """Send message to queue."""
        self.end_result['type'] = PluginResultType.TEXT
        self.end_result['result_speech_func'] = super().spit_text
        self.queue.put(self.end_result)

    def check_existing_dates(self, day_ordinal_number: str) -> bool:
        """Check if date exist in monthly plan."""
        date_ = self.first_date
        while date_ is not None:
            if date_.day_ordinal_number == day_ordinal_number:
                return True
            date_ = date_.next
        return False

    def check_date_before_action(
        self,
        day_ordinal_number: str,
    ) -> tuple[bool, str | bool, str | bool, str]:
        """Check general informations of input, before doing a action, in monthly plan."""
        date_already_exist = self.check_existing_dates(day_ordinal_number)
        date_ = create_date(day_ordinal_number)
        day_in_past = day_past_in_monthly_plan(date_)
        check_number_of_days = check_number_of_days_in_month(date_)
        return date_already_exist, check_number_of_days, day_in_past, date_

    def delete_date_(self, day_ordinal_number: str) -> str:
        """Try to delete one single date from monthly plan."""
        print('We are inside of deleting of date')

        date_exist, date_number_of_days, day_in_past, date_ = \
            self.check_date_before_action(day_ordinal_number)
        print('Date: ', date_)
        print('date_number_of_days: ', date_number_of_days)
        print('day_in_past: ', day_in_past)
        print('Date to say: ', date_)
        if date_exist:
            date_ = say_date(date_)
            start = self.first_date
            self.actions_keywords['delete_date'] = False
            self.min_similarity = 0.75

            if start.day_ordinal_number == day_ordinal_number:
                if self.last_date == self.first_date:
                    self.last_date = None
                self.first_date = self.first_date.next

                print('First')
                return f'The first date {date_} is successfully deleted, \
                fuction for deleting is deactivated'

            previous = start
            start = start.next

            while start.next is not None:

                print('Inside')
                if start.day_ordinal_number == day_ordinal_number:

                    previous.next = start.next
                    print('Second')
                    return f'The date {date_} is successfully deleted, \
                    fuction for deleting is deactivated'

                previous = start
                start = start.next

            self.last_date = previous
            self.last_date.next = None
            print('Third')
            return f'The last date {date_} in the monthly plan is deleted'

        date_ = say_date(date_)
        self.actions_keywords['delete_date'] = False
        self.min_similarity = 0.75
        print('Fourth')

        return f'The date {date_}  does not exist in monthly \
        plan, so it can not be deleted'

    def insert_date(self, day_ordinal_number: str) -> str | bool:
        """Try to insert one date in monthly plan."""
        date_exist, date_number_of_days, day_in_past, date_ = \
            self.check_date_before_action(day_ordinal_number)

        print('Date exist: ', date_exist)
        print('Date number of days: ', date_number_of_days)
        print('Day in past: ', day_in_past)
        print('Date: ', date_)

        if date_number_of_days is not True:

            self.actions_keywords['add_date'] = False
            self.min_similarity = 0.75
            return date_number_of_days

        if date_exist is False:

            if day_in_past:

                self.actions_keywords['add_date'] = False
                self.min_similarity = 0.75
                return day_in_past

            date_in_month = SingleDate(date_, day_ordinal_number)

            if self.last_date is None and self.first_date is None:
                self.first_date = date_in_month
                self.last_date = date_in_month

            else:
                self.last_date.next = date_in_month
                self.last_date = date_in_month
            print('We are trying to say date')
            date_ = say_date(date_)
            self.actions_keywords['add_date'] = False
            self.min_similarity = 0.75

            return f'Date {date_} is successfully inserted, function \
            for inserting of dates is deactivated'

        self.actions_keywords['add_date'] = False
        self.min_similarity = 0.75
        date_ = say_date(date_)
        return f'Date {date_} already exist in monthly plan'

    def add_date(self, activated_keyword: str) -> None:
        """Start adding of date."""
        if activated_keyword in constants.days_ordinal_numbers_keywords:
            self.end_result['result'] = self.insert_date(activated_keyword)
            self.say_result_put_in_queue()
            return

    def delete_date(self, activated_keyword: str) -> None:
        """Start deleting of date."""
        if activated_keyword in constants.days_ordinal_numbers_keywords:
            self.end_result['result'] = self.delete_date_(activated_keyword)
            self.say_result_put_in_queue()
            return

    def add_activity(self, activated_keyword: str) -> None:
        """Start or break adding of activity."""
        print('Activated keyword: ', activated_keyword)
        print('self.single_day: ', self.single_day)

        if activated_keyword not in constants.days_ordinal_numbers_keywords\
                and self.time_range_add is False:
            self.actions_keywords['add_activity'] = False
            self.min_similarity = 0.75
            self.reset_activity()
            self.end_result['result'] = 'Break adding of activity'
            self.say_result_put_in_queue()
            return
        self.end_result['result'] = self.insert_activity(activated_keyword)
        self.say_result_put_in_queue()
        return

    def deactivate_action(self) -> None:
        """Deactivate activated action."""
        self.min_similarity = 0.75

        if self.actions_keywords['add_date']:
            self.actions_keywords['add_date'] = False
            self.end_result['result'] = constants.answers[8]

        if self.actions_keywords['delete_date']:
            self.actions_keywords['delete_date'] = False
            self.end_result['result'] = constants.answers[9]

        if self.actions_keywords['add_activity']:
            self.actions_keywords['add_activity'] = False
            self.end_result['result'] = constants.answers[10]

        self.say_result_put_in_queue()

    def activate_action(self, activated_keyword: str) -> None:
        """Activate action."""
        self.min_similarity = 1
        print('Activated_keyword: ', activated_keyword)

        if activated_keyword == constants.actions_keywords[5]:

            self.actions_keywords['add_date'] = True
            self.end_result['result'] = constants.answers[1]
            self.say_result_put_in_queue()

        if activated_keyword == constants.actions_keywords[2]:

            self.actions_keywords['delete_date'] = True
            self.end_result['result'] = constants.answers[2]
            self.say_result_put_in_queue()

        if activated_keyword == constants.actions_keywords[3]:

            self.actions_keywords['add_activity'] = True
            self.end_result['result'] = constants.answers[3]
            self.say_result_put_in_queue()

    def show_dates(self) -> None:
        """Say/show dates in monthly plan."""
        if self.first_date is None:

            self.end_result['result'] = 'Monthly plan is empty'
            self.say_result_put_in_queue()

        else:

            date_ = self.first_date
            self.end_result['result'] = ''

            while date_ is not None:
                print('Activity: ', date_.activities)
                print('date_.date_in_month: ', date_.date_in_month)
                date__word = say_date(str(date_.date_in_month))
                self.end_result['result'] += ', ' + date__word
                date_ = date_.next

            self.end_result['result'] += ', that would be your monthly plan'
            self.say_result_put_in_queue()

    def check_keyword(self, action_activated: str | bool, activated_keyword: str) -> None:
        """Start contronling of plugin by given keyword."""
        if action_activated == 'add_date'\
            and activated_keyword in constants.days_ordinal_numbers_keywords\
                and self.actions_keywords['add_date']:
            self.add_date(activated_keyword)
            return

        if action_activated == 'delete_date'\
            and activated_keyword in constants.days_ordinal_numbers_keywords\
                and self.actions_keywords['delete_date']:
            self.delete_date(activated_keyword)
            return

        if action_activated == 'add_date'\
                and activated_keyword not in constants.days_ordinal_numbers_keywords:
            self.actions_keywords['add_date'] = False
            self.end_result['result'] = 'Input is wrong, try again with insert'
            self.say_result_put_in_queue()
            return

        if action_activated == 'delete_date'\
                and activated_keyword not in constants.days_ordinal_numbers_keywords:
            self.actions_keywords['delete_date'] = False
            self.end_result['result'] = 'Input is wrong, try again with deleting'
            self.say_result_put_in_queue()
            return

        if action_activated == 'add_activity'\
                and self.actions_keywords['add_activity']:
            print('We are on the right position')
            self.add_activity(activated_keyword)
            return
        return

    def run_doc(self, doc: object, queue_: queue.Queue[typing.Any]) -> None:
        """Run doc."""
        for keyword in constants.actions_keywords:
            self.add_activation_doc(keyword)

        for day_orindal_number_keyword in constants.days_ordinal_numbers_keywords:
            self.add_activation_doc(day_orindal_number_keyword)

        self.queue = queue_

        if self.min_similarity == 1:
            activated_keyword = str(self.exact_keyword_activated(doc))
        else:
            activated_keyword = str(self.similar_keyword_activated(doc))

        if activated_keyword == constants.actions_keywords[1]:
            self.show_dates()
            return

        action_activated = False

        for function, activated in self.actions_keywords.items():
            if activated:
                action_activated = function

        if not action_activated:
            self.activate_action(activated_keyword)
            return
        print('Activated keyword: ', activated_keyword)
        print('Doc: ', doc)
        if activated_keyword == 'False' and self.actions_keywords['add_activity']:
            if str(doc) != '':
                self.check_keyword(action_activated, str(doc))
            return
        self.check_keyword(action_activated, activated_keyword)
