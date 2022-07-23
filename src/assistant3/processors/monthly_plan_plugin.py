"""MonthlyPlan plugin."""
import queue
import typing

import xlsxwriter

from ..common import constants, helpers
from ..common.plugins import PluginResultType
from .base_processor import BasePlugin


class SingleDate:
    """One single date in month."""

    def __init__(self, date_in_month: str, day_ordinal_number: str):
        """Initialize one single date values."""
        self.date_in_month = date_in_month
        self.next: typing.Any = None
        self.activities: dict[str, str] = {}
        self.day_ordinal_number = day_ordinal_number

    def get_activities(self, day_ordinal_number: str) -> dict[str, str]:
        """Get activity in one single day."""
        if self.day_ordinal_number == day_ordinal_number:
            return self.activities
        return {}

    def set_activity(self, day_ordinal_number: str, time_range: str, activity: str) -> None:
        """Set activity in one single day, in one time range."""
        if self.day_ordinal_number == day_ordinal_number:
            self.activities[time_range] = activity


def activity_exist(one_date: SingleDate, time_range_numbers: list[int]) -> bool:
    """Check if activity overlap another activity."""
    if isinstance(one_date, SingleDate):

        time_range_numbers = [int(word) for word in time_range_numbers]
        print('Time range numbers', time_range_numbers)

        starting_time_to_insert = \
            int(time_range_numbers[0]) * 60 + int(time_range_numbers[1])

        ending_time_to_insert = \
            int(time_range_numbers[2]) * 60 + int(time_range_numbers[3])

        for time_range, _act in one_date.activities.items():

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
    return False


def add_to_xls(monthly_plan_to_write: xlsxwriter, date_to_xls_: SingleDate) -> None:
    """Get time range and activity from dictionary and write in excel file."""
    time_range_activity = ''

    for counter, (range_time, activity) in enumerate(date_to_xls_.activities.items()):

        range_time_standard = range_time.replace(' ', '-')
        time_range_activity = range_time_standard + '->' + activity
        row_day = date_to_xls_.date_in_month.split('-')[-1]

        if row_day[0] == '0':
            row_day = row_day[-1]

        monthly_plan_to_write.write(constants.xls_sheets[counter] + row_day, time_range_activity)


class MonthlyPlanPlugin(BasePlugin):
    """Monthly Plan."""

    def __init__(self) -> None:
        """Initialize values in monthly plan.

        The second separated part of values, will be used
        by dealing with activities
        """
        super().__init__('insert')
        self.first_date = SingleDate('', '')
        self.last_date = SingleDate('', '')
        self.actions_keywords = {
            'add_date': False,
            'delete_date': False,
            'add_activity': False,
            'delete_activity': False,
        }
        self.activation_dict['general_tts_error_message'] = 'Budo error'
        self.activity_values = {
            'time_range_add': False,
            'activity_add': False,
            'said_day': '',
            'date_exist': False,
            'time_range_': '',
        }
        self.single_day = SingleDate('', '')
        self.queue: queue.Queue[typing.Any] = queue.Queue(0)

    def give_date_from_monthly_plan(self, find_date: str) -> SingleDate:
        """Give date from monthly plan, date exist defenetely."""
        start = self.first_date
        find_date = str(find_date)

        if start.date_in_month == find_date:
            return start

        while start.next is not None:
            if start.date_in_month == find_date:
                return start

            if isinstance(start.next, SingleDate):
                start = start.next

        if start.date_in_month == find_date:
            return start

        return start

    def activity_in_time(
        self,
        time_range_possible: int,
        time_range_numbers: list[int],
        time_range_words: list[str],
    ) -> str:
        """Check finally, if it is possible to add time range."""
        if time_range_possible < 0:
            self.actions_keywords['add_activity'] = False
            self.min_similarity = 1
            self.reset_activity()

            return f'Time range {time_range_words} is not valid, try another one, '\
                'adding of activity broken.'

        if not activity_exist(self.single_day, time_range_numbers):
            # add time_range
            self.activity_values['activity_add'] = True
            time_range_ = ''
            for number in time_range_numbers:
                time_range_ += str(number) + ' '
            self.activity_values['time_range_'] = time_range_.rstrip()

            return f'Time range {time_range_numbers} available, you can try to add an activity'

        self.actions_keywords['add_activity'] = False
        self.min_similarity = 1
        self.reset_activity()

        return 'In that time range already exist activity'

    def time_range(self, activated_keyword: str) -> str:
        """Create and check if it is possible to add time range."""
        time_range_words = helpers.form_time_range(activated_keyword)

        time_range_numbers = \
            helpers.convert_time_range_from_words_to_numbers(time_range_words)

        time_range_possible = \
            helpers.time_range_validy(time_range_numbers)

        return self.activity_in_time(time_range_possible, time_range_numbers, time_range_words)

    def reset_activity(self) -> None:
        """Reset all values regarding activity."""
        self.activity_values['time_range_add'] = False
        self.activity_values['activity_add'] = False
        self.activity_values['said_day'] = ''
        self.activity_values['date_exist'] = False
        self.single_day = SingleDate('', '')
        self.activity_values['time_range_'] = ''

    def add_activity_to_time_range(self, activated_keyword: str) -> None:
        """Add activity to created time range."""
        start = self.first_date

        while start.date_in_month != '':

            if start.date_in_month == self.single_day.date_in_month:
                time_range_ = str(self.activity_values['time_range_'])
                start.activities[time_range_] = activated_keyword
                break
            if isinstance(start.next, SingleDate):
                print('Here')
                start = start.next
            else:
                break

    def insert_activity(self, activated_keyword: str) -> str:
        """Try to insert activity, check also if it is possible."""
        if self.activity_values['date_exist'] is False:
            self.activity_values['date_exist'], date_number_of_days,\
                day_in_past, self.activity_values['said_day'] = \
                self.check_date_before_action(activated_keyword)

            print('date_number_of_days: ', date_number_of_days)
            print('day_in_past: ', day_in_past)
            print("self.activity_values['date_exist']: ", self.activity_values['date_exist'])

            if self.activity_values['date_exist']:
                self.activity_values['time_range_add'] = True
                self.single_day = self.give_date_from_monthly_plan(self.activity_values['said_day'])
                tell_date = helpers.say_date(self.activity_values['said_day'])

                return f'Date {tell_date} exist in monthly plan, ' \
                    'you can add time range'

            self.actions_keywords['add_activity'] = False
            self.min_similarity = 1
            said_day = str(self.activity_values['said_day'])
            tell_date = helpers.say_date(said_day)
            self.reset_activity()
            return f'Date {tell_date} does not exist in monthly plan,'\
                'adding of activity broken'

        if self.activity_values['activity_add']:
            self.add_activity_to_time_range(activated_keyword)
            self.actions_keywords['add_activity'] = False
            self.min_similarity = 1
            self.reset_activity()
            print('Here')
            return f'Activity {activated_keyword} successfully added'

        if self.activity_values['time_range_add']:
            return self.time_range(activated_keyword)

        return 'Error'

    def say_result_put_in_queue(self) -> None:
        """Send message to queue."""
        trigger_again = False
        for _action, activated in self.actions_keywords.items():
            if activated is True:
                trigger_again = True
                break
        self.end_result['type'] = PluginResultType.KEEP_ALIVE
        if trigger_again is False:
            self.end_result['type'] = PluginResultType.TEXT
        self.end_result['result_speech_func'] = super().spit_text
        self.queue.put(self.end_result)

    def check_existing_dates(self, day_ordinal_number: str) -> bool:
        """Check if date exist in monthly plan."""
        date_ = self.first_date
        while date_.date_in_month != '':

            if date_.day_ordinal_number == day_ordinal_number:
                return True
            if isinstance(date_.next, SingleDate):
                date_ = date_.next
            else:
                break

        return False

    def check_date_before_action(
        self,
        day_ordinal_number: str,
    ) -> tuple[bool, str | bool, str | bool, str]:
        """Check general informations of input, before doing a action, in monthly plan."""
        date_already_exist = self.check_existing_dates(day_ordinal_number)
        date_ = helpers.create_date(day_ordinal_number)
        day_in_past = helpers.day_past_in_monthly_plan(date_)
        check_number_of_days = helpers.check_number_of_days_in_month(date_)

        return date_already_exist, check_number_of_days, day_in_past, date_

    def delete_date_(self, day_ordinal_number: str) -> str:
        """Try to delete one single date from monthly plan."""
        date_exist, date_number_of_days, day_in_past, date_ = \
            self.check_date_before_action(day_ordinal_number)

        print('Date: ', date_)
        print('Date exist: ', date_exist)
        print('date_number_of_days: ', date_number_of_days)
        print('day_in_past: ', day_in_past)
        print('Date to say: ', date_)

        if date_exist:
            date_ = helpers.say_date(date_)
            start = self.first_date
            self.actions_keywords['delete_date'] = False
            self.min_similarity = 1

            if start.day_ordinal_number == day_ordinal_number:

                if self.last_date == self.first_date:
                    self.last_date = SingleDate('', '')
                    self.first_date = SingleDate('', '')

                if isinstance(self.first_date.next, SingleDate):
                    self.first_date = self.first_date.next
                print('DATE_: ', date_)
                return f'The first date {date_} is successfully deleted,'\
                    ' fuction for deleting is deactivated'

            previous = start
            if isinstance(start.next, SingleDate):
                start = start.next

            while start.next is not None:
                if start.day_ordinal_number == day_ordinal_number:

                    previous.next = start.next
                    return f'The date {date_} is successfully deleted, '\
                        'fuction for deleting is deactivated'

                previous = start
                if isinstance(start.next, SingleDate):
                    start = start.next

            self.last_date = previous
            self.last_date.next = None
            return f'The last date {date_} in the monthly plan is deleted'

        date_ = helpers.say_date(date_)
        self.actions_keywords['delete_date'] = False
        self.min_similarity = 1

        return f'The date {date_}  does not exist in monthly' \
            'plan, so it can not be deleted'

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
            self.min_similarity = 1
            return date_number_of_days

        if date_exist is False:

            if day_in_past:

                self.actions_keywords['add_date'] = False
                self.min_similarity = 1
                return day_in_past

            date_in_month = SingleDate(date_, day_ordinal_number)

            if self.last_date.date_in_month == '' and self.first_date.date_in_month == '':

                self.first_date = date_in_month
                self.last_date = date_in_month

            else:
                self.last_date.next = date_in_month
                self.last_date = date_in_month

            date_ = helpers.say_date(date_)
            self.actions_keywords['add_date'] = False
            self.min_similarity = 1

            return f'Date {date_} is successfully inserted, function'\
                ' for inserting of dates is deactivated'

        self.actions_keywords['add_date'] = False
        self.min_similarity = 1
        date_ = helpers.say_date(date_)
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
        if activated_keyword not in constants.days_ordinal_numbers_keywords\
                and self.activity_values['time_range_add'] is False:

            self.actions_keywords['add_activity'] = False
            self.min_similarity = 1
            self.reset_activity()
            self.end_result['result'] = 'Break adding of activity'
            self.say_result_put_in_queue()
            return

        self.end_result['result'] = self.insert_activity(activated_keyword)
        self.say_result_put_in_queue()
        return

    def deactivate_action(self) -> None:
        """Deactivate activated action."""
        self.min_similarity = 1

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
            return

        if activated_keyword == constants.actions_keywords[2]:

            self.actions_keywords['delete_date'] = True
            self.end_result['result'] = constants.answers[2]
            self.say_result_put_in_queue()
            return

        if activated_keyword == constants.actions_keywords[3]:

            self.actions_keywords['add_activity'] = True
            self.end_result['result'] = constants.answers[3]
            self.say_result_put_in_queue()
            return
        return

    def show_dates(self) -> None:
        """Say/show dates in monthly plan."""
        if self.first_date.date_in_month == '':

            self.end_result['result'] = 'Monthly plan is empty'
            self.say_result_put_in_queue()

        else:

            date_ = self.first_date
            self.end_result['result'] = ''

            while date_.date_in_month != '':

                date__word = helpers.say_date(str(date_.date_in_month))
                self.end_result['result'] += ', ' + date__word

                if isinstance(date_.next, SingleDate):
                    date_ = date_.next
                else:
                    break

            self.end_result['result'] += ', that would be your monthly plan'
            self.say_result_put_in_queue()

    def write_xls(self) -> None:
        """Write activities and time ranges from date in monthly plan."""
        date_to_xls = self.first_date
        monthly_plan = xlsxwriter.Workbook('monthly_plan.xlsx')
        monthly_plan_to_write = monthly_plan.add_worksheet()
        while date_to_xls is not None:

            add_to_xls(monthly_plan_to_write, date_to_xls)
            if isinstance(date_to_xls, SingleDate):
                date_to_xls = date_to_xls.next
            else:
                break
        monthly_plan.close()
        self.end_result['result'] = 'All time ranges and activies are written'
        self.say_result_put_in_queue()

    def check_keyword(self, action_activated: str | bool, activated_keyword: str) -> None:
        """Start contronling of plugin by given keyword."""
        if action_activated == 'add_date'\
            and activated_keyword in constants.days_ordinal_numbers_keywords\
                and self.actions_keywords['add_date']:
            print('Add_date')
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
            self.add_activity(activated_keyword)
            return
        return

    def run_doc(self, doc: object, queue_: queue.Queue[typing.Any], by_uid: bool = False) -> None:
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

        if activated_keyword == constants.actions_keywords[6]:
            self.write_xls()
            return

        action_activated = False
        action_activated_ = str(action_activated)

        for function, activated in self.actions_keywords.items():
            if activated:
                action_activated_ = function

        if action_activated_ == 'False':
            self.activate_action(activated_keyword)
            return

        print('Activated keyword: ', activated_keyword)
        print('Doc: ', doc)

        if activated_keyword == 'False' and self.actions_keywords['add_activity']:
            if str(doc) != '':
                self.check_keyword(action_activated_, str(doc))
            return
        self.check_keyword(action_activated_, activated_keyword)
