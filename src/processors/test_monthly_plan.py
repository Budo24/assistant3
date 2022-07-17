"""Test monthly plan."""
import queue
from datetime import date
from unittest.mock import patch

import pyttsx3

from common import constants
from plugins_watcher import PluginWatcher
from processors import base_processor
from processors.base_processor import MonthlyPlanPlugin

engine_ = pyttsx3.init('dummy')


def test_activity_exist() -> None:
    """Test if time range is empty."""
    single_date = base_processor.SingleDate('2022-07-30', 'thirty')
    single_date.activities = {'15 0 18 0': 'playing football'}
    time_range_numbers = [15, 0, 16, 0]
    activity_exist = base_processor.activity_exist(single_date, time_range_numbers)
    assert activity_exist is True

    time_range_numbers = [16, 0, 18, 0]
    activity_exist = base_processor.activity_exist(single_date, time_range_numbers)
    assert activity_exist is True

    time_range_numbers = [16, 0, 17, 0]
    activity_exist = base_processor.activity_exist(single_date, time_range_numbers)
    assert activity_exist is True

    time_range_numbers = [14, 0, 19, 0]
    activity_exist = base_processor.activity_exist(single_date, time_range_numbers)
    assert activity_exist is True

    time_range_numbers = [14, 0, 15, 0]
    activity_exist = base_processor.activity_exist(single_date, time_range_numbers)
    assert activity_exist is False

    time_range_numbers = [18, 0, 19, 0]
    activity_exist = base_processor.activity_exist(single_date, time_range_numbers)
    assert activity_exist is False
    print('Everything successful')


def test_write_xls() -> None:
    """Test writing into xls."""

    with patch('common.helpers.date') as mock_date:
        mock_date.today.return_value = date(2010, 10, 8)

        with patch('processors.base_processor.BasePlugin') as plugin:
            plugin.engine.return_value = engine_

            monthly_plan = MonthlyPlanPlugin()

            monthly_plan.insert_date('ninth')

            monthly_plan.insert_activity('ninth')
            monthly_plan.insert_activity('twenty zero twenty three zero')
            monthly_plan.insert_activity('playing football')

            monthly_plan.insert_date('eleventh')

            monthly_plan.insert_activity('eleventh')
            monthly_plan.insert_activity('eighteen zero twenty three zero')
            monthly_plan.insert_activity('playing football')

            monthly_plan.insert_activity('eleventh')
            monthly_plan.insert_activity('sixteen zero eighteen zero')
            monthly_plan.insert_activity('watching tv')
            # enable line down if you want to see how it looks
            # monthly_plan.write_xls()

        # look if monthly_plan.xlsx exist and if feeling of sheets makes logical sence


def test_add_to_xls() -> None:
    """Test adding to xls."""
    time_range_activity = ''
    date_to_xls = base_processor.SingleDate('2022-01-01', 'thirty')
    date_to_xls.activities = {'15 0 18 0': 'playing football', '14 0 15 0': 'watching tv'}

    for counter, (range_time, activity) in enumerate(date_to_xls.activities.items()):
        range_time_standard = range_time.replace(' ', '-')
        time_range_activity = range_time_standard + '->' + activity
        row_day = date_to_xls.date_in_month.split('-')[-1]

        if row_day[0] == '0':
            row_day = row_day[-1]

        assert row_day == '1'

        if counter == 0:
            assert time_range_activity == '15-0-18-0->playing football'
        else:
            assert time_range_activity == '14-0-15-0->watching tv'


def test_give_date_from_monthly_plan() -> None:
    """Test give date from monthly plan.

    This function will NOT be executed, if date does not exist in monthly plan !
    """
    monthly_plan = MonthlyPlanPlugin()
    with patch('common.helpers.date') as mock_date:
        mock_date.today.return_value = date(2010, 10, 8)
        with patch('processors.base_processor.BasePlugin') as plugin:
            plugin.engine.return_value = engine_

            monthly_plan = MonthlyPlanPlugin()

            monthly_plan.insert_date('ninth')
            monthly_plan.insert_date('eleventh')
            monthly_plan.insert_date('fifteenth')

            assert monthly_plan.give_date_from_monthly_plan('2010-10-09').date_in_month\
                == '2010-10-09'

            assert monthly_plan.give_date_from_monthly_plan('2010-10-11').date_in_month\
                == '2010-10-11'

            assert monthly_plan.give_date_from_monthly_plan('2010-10-15').date_in_month\
                == '2010-10-15'


def test_activity_in_time() -> None:
    """Test activity in time."""
    print('Start')
    with patch('common.helpers.date') as mock_date:
        mock_date.today.return_value = date(2010, 10, 8)
        with patch('processors.base_processor.BasePlugin') as plugin:
            plugin.engine.return_value = engine_
        
            monthly_plan = MonthlyPlanPlugin()

            monthly_plan.insert_date('ninth')

            time_range_possible = 60
            time_range_numbers = [16, 0, 17, 0]
            time_range_words = ['sixteen', 'zero', 'seventeen', 'zero']

            assert monthly_plan.activity_in_time(time_range_possible,
                                                time_range_numbers, time_range_words)\
                == 'Time range [16, 0, 17, 0] available, you can try to add an activity'

            # because of previous line
            monthly_plan.reset_activity()

            monthly_plan.insert_activity('ninth')
            monthly_plan.insert_activity('sixteen zero seventeen zero')
            monthly_plan.insert_activity('playing football')

            monthly_plan.single_day = monthly_plan.give_date_from_monthly_plan('2010-10-09')

            time_range_possible = 60
            time_range_numbers = [16, 0, 17, 0]
            time_range_words = ['sixteen', 'zero', 'sixteen', 'thirty']

            assert monthly_plan.activity_in_time(time_range_possible,
                                                time_range_numbers, time_range_words)\
                == 'In that time range already exist activity'

            monthly_plan.reset_activity()

            time_range_possible = -60
            time_range_numbers = [17, 0, 16, 0]
            time_range_words = ['seventeen', 'zero', 'sixteen', 'zero']

            assert monthly_plan.activity_in_time(time_range_possible,
                                                time_range_numbers, time_range_words)\
                == "Time range ['seventeen', 'zero', 'sixteen', 'zero'] is not valid,"\
                ' try another one, adding of activity broken.'


def test_add_activity_to_time_range() -> None:
    """Test adding of activity to time range."""
    activity = 'playing football'

    with patch('common.helpers.date') as mock_date:
        mock_date.today.return_value = date(2010, 10, 8)
        with patch('processors.base_processor.BasePlugin') as plugin:
            plugin.engine.return_value = engine_
        
            monthly_plan = MonthlyPlanPlugin()
            monthly_plan.insert_date('ninth')
            monthly_plan.insert_date('eleventh')
            monthly_plan.insert_date('fifteenth')

            monthly_plan.time_range_ = '20 0 20 30'
            monthly_plan.single_day = monthly_plan.give_date_from_monthly_plan('2010-10-09')
            monthly_plan.add_activity_to_time_range(activity)

            assert monthly_plan.single_day.activities == {'20 0 20 30': 'playing football'}

            monthly_plan.single_day = monthly_plan.give_date_from_monthly_plan('2010-10-11')
            monthly_plan.add_activity_to_time_range(activity)

            assert monthly_plan.single_day.activities == {'20 0 20 30': 'playing football'}

            monthly_plan.single_day = monthly_plan.give_date_from_monthly_plan('2010-10-15')
            monthly_plan.add_activity_to_time_range(activity)

            assert monthly_plan.single_day.activities == {'20 0 20 30': 'playing football'}


def test_insert_activity() -> None:
    """Test inserting of activity."""
    with patch('common.helpers.date') as mock_date:
        mock_date.today.return_value = date(2010, 10, 8)
        with patch('processors.base_processor.BasePlugin') as plugin:
            plugin.engine.return_value = engine_
        
            monthly_plan = MonthlyPlanPlugin()
            monthly_plan.insert_date('ninth')
            monthly_plan.insert_date('eleventh')
            monthly_plan.insert_date('fifteenth')

            assert monthly_plan.insert_activity('ninth') == 'Date ninth october 2010 exist'\
                ' in monthly plan, you can add time range'

            monthly_plan.reset_activity()

            assert monthly_plan.insert_activity('seventeenth') == 'Date seventeenth october 2010'\
                ' does not exist in monthly plan,adding of activity broken'

            monthly_plan.reset_activity()

            monthly_plan.insert_activity('ninth')
            monthly_plan.insert_activity('six zero six thirty')
            assert monthly_plan.insert_activity('playing football') ==\
                'Activity playing football successfully added'


def test_check_existing_date() -> None:
    """Check existing dates."""
    with patch('common.helpers.date') as mock_date:
        mock_date.today.return_value = date(2010, 10, 8)
        with patch('processors.base_processor.BasePlugin') as plugin:
            plugin.engine.return_value = engine_
        
            monthly_plan = MonthlyPlanPlugin()
            monthly_plan.insert_date('ninth')
            monthly_plan.insert_date('eleventh')
            monthly_plan.insert_date('fifteenth')

            assert monthly_plan.check_existing_dates('ninth') is True

            assert monthly_plan.check_existing_dates('eleventh') is True

            assert monthly_plan.check_existing_dates('fifteenth') is True

            assert monthly_plan.check_existing_dates('seventeenth') is False


def test_delete_date_() -> None:
    """Test deleting of dates."""
    with patch('common.helpers.date') as mock_date:
        mock_date.today.return_value = date(2010, 10, 8)
        with patch('processors.base_processor.BasePlugin') as plugin:
            plugin.engine.return_value = engine_
        
            monthly_plan = MonthlyPlanPlugin()
            
            monthly_plan.insert_date('ninth')

            assert monthly_plan.delete_date_('ninth') == 'The first date ninth october'\
                ' 2010 is successfully deleted, fuction for deleting is deactivated'

            monthly_plan.insert_date('ninth')
            monthly_plan.insert_date('eleventh')
            monthly_plan.insert_date('fifteenth')

            assert monthly_plan.delete_date_('ninth') == 'The first date ninth october'\
                ' 2010 is successfully deleted, fuction for deleting is deactivated'

            monthly_plan.insert_date('ninth')

            assert monthly_plan.delete_date_('fifteenth') == 'The date fifteenth october'\
                ' 2010 is successfully deleted, fuction for deleting is deactivated'

            monthly_plan.insert_date('fifteenth')

            assert monthly_plan.delete_date_('fifteenth') == 'The last date'\
                ' fifteenth october 2010 in the monthly plan is deleted'

            print(monthly_plan.delete_date_('fifteenth'))
            assert monthly_plan.delete_date_('fifteenth') == 'The date fifteenth'\
                ' october 2010  does not exist in monthlyplan, so it can not be deleted'


def test_insert_date() -> None:
    """Check existing dates."""
    with patch('common.helpers.date') as mock_date:
        mock_date.today.return_value = date(2010, 10, 8)
        with patch('processors.base_processor.BasePlugin') as plugin:
            plugin.engine.return_value = engine_
        
            monthly_plan = MonthlyPlanPlugin()

            assert monthly_plan.insert_date('ninth') == 'Date ninth'\
                ' october 2010 is successfully inserted, function for'\
                ' inserting of dates is deactivated'

            assert monthly_plan.insert_date('ninth') == 'Date ninth october'\
                ' 2010 already exist in monthly plan'


def test_add_date() -> None:
    """Test control function for switching to add date."""
    with patch('common.helpers.date') as mock_date:
        mock_date.today.return_value = date(2010, 10, 8)
        with patch('processors.base_processor.BasePlugin') as plugin:
            plugin.engine.return_value = engine_
        
            monthly_plan = MonthlyPlanPlugin()

            monthly_plan.add_date('thirty')

            assert monthly_plan.end_result['result'] == 'Date thirty october'\
                ' 2010 is successfully inserted, function for inserting of dates is deactivated'

            monthly_plan.end_result['result'] = None

            monthly_plan.add_date('hello')

            assert monthly_plan.end_result['result'] is None


def test_delete_date() -> None:
    """Test deleting of date."""
    with patch('common.helpers.date') as mock_date:
        mock_date.today.return_value = date(2010, 10, 8)
        with patch('processors.base_processor.BasePlugin') as plugin:
            plugin.engine.return_value = engine_
        
            monthly_plan = MonthlyPlanPlugin()

            monthly_plan.insert_date('ninth')

            monthly_plan.delete_date('ninth')

            print(monthly_plan.end_result['result'])
            assert monthly_plan.end_result['result'] == 'The first date'\
                ' ninth october 2010 is successfully deleted,'\
                ' fuction for deleting is deactivated'

            monthly_plan.end_result['result'] = None

            monthly_plan.delete_date('ninth')

            assert monthly_plan.end_result['result'] == 'The date ninth'\
                ' october 2010  does not exist in monthlyplan, so it can not be deleted'


def test_add_activity() -> None:
    """Test control function to add activity."""
    with patch('common.helpers.date') as mock_date:
        mock_date.today.return_value = date(2010, 10, 8)
        with patch('processors.base_processor.BasePlugin') as plugin:
            plugin.engine.return_value = engine_
        
            monthly_plan = MonthlyPlanPlugin()

            monthly_plan.insert_date('ninth')

            monthly_plan.add_activity('ninth')

            assert monthly_plan.end_result['result'] == 'Date ninth'\
                ' october 2010 exist in monthly plan, you can add time range'

            monthly_plan.add_activity('twenty zero twenty thirty')

            assert monthly_plan.end_result['result'] == 'Time range'\
                ' [20, 0, 20, 30] available, you can try to add an activity'

            monthly_plan.add_activity('playing football')

            assert monthly_plan.end_result['result'] == \
                'Activity playing football successfully added'

            monthly_plan.reset_activity()

            monthly_plan.end_result['result'] = None

            monthly_plan.add_activity('ninth')

            monthly_plan.add_activity('hello')

            assert monthly_plan.end_result['result'] == "Time range ['hello'] is not valid,"\
                ' try another one, adding of activity broken.'


def test_deactivate_action() -> None:
    """Test deactivate action."""
    with patch('common.helpers.date') as mock_date:
        mock_date.today.return_value = date(2010, 10, 8)
        with patch('processors.base_processor.BasePlugin') as plugin:
            plugin.engine.return_value = engine_
        
            monthly_plan = MonthlyPlanPlugin()
            monthly_plan.actions_keywords['add_date'] = True

            monthly_plan.deactivate_action()

            assert monthly_plan.actions_keywords['add_date'] is False

            assert monthly_plan.end_result['result'] == 'Insert of date is broken'


def test_activate_action() -> None:
    """Test activate action."""
    with patch('common.helpers.date') as mock_date:
        mock_date.today.return_value = date(2010, 10, 8)
        with patch('processors.base_processor.BasePlugin') as plugin:
            plugin.engine.return_value = engine_
        
            monthly_plan = MonthlyPlanPlugin()

            monthly_plan.activate_action('insert')

            assert monthly_plan.end_result['result'] == 'Which date do'\
                ' you want to insert, say me just ordinal number of day in date'


def test_show_dates() -> None:
    """Test showing of dates."""
    with patch('common.helpers.date') as mock_date:
        mock_date.today.return_value = date(2010, 10, 8)
        with patch('processors.base_processor.BasePlugin') as plugin:
            plugin.engine.return_value = engine_
            monthly_plan = MonthlyPlanPlugin()
            monthly_plan.show_dates()
            print(monthly_plan.end_result['result'])
            assert monthly_plan.end_result['result'] == 'Monthly plan is empty'
            monthly_plan.insert_date('ninth')
            monthly_plan.insert_date('eleventh')
            monthly_plan.insert_date('fifteenth')

            monthly_plan.show_dates()
            print(monthly_plan.end_result['result'])
            assert monthly_plan.end_result['result'] == ', ninth october 2010, eleventh'\
                ' october 2010, fifteenth october 2010, that would be your monthly plan'


def test_check_keyword() -> None:
    """Test checking from keywords."""
    with patch('common.helpers.date') as mock_date:
        mock_date.today.return_value = date(2010, 10, 8)
        with patch('processors.base_processor.BasePlugin') as plugin:
            plugin.engine.return_value = engine_
            monthly_plan = MonthlyPlanPlugin()
            monthly_plan.actions_keywords['add_date'] = True


            monthly_plan.check_keyword('add_date', 'hello')

            assert monthly_plan.end_result['result'] == 'Input'\
                ' is wrong, try again with insert'
            
            monthly_plan.actions_keywords['add_date'] = True

            print('Here is good')
            monthly_plan.check_keyword('add_date', 'thirty')

            assert monthly_plan.end_result['result'] == 'Date thirty'\
                ' october 2010 is successfully inserted,'\
                ' function for inserting of dates is deactivated'


def test_run_doc_without_activity() -> None:
    """Test run_doc."""
    with patch('common.helpers.date') as mock_date:
        mock_date.today.return_value = date(2010, 10, 8)
        with patch('processors.base_processor.BasePlugin') as plugin:
            plugin.engine.return_value = engine_
            monthly_plan = MonthlyPlanPlugin()

            plugins_watcher = PluginWatcher([monthly_plan])

            plugins_watcher.run('insert')
            monthly_plan.run_doc(plugins_watcher.doc, queue.Queue())

            assert monthly_plan.end_result['result'] == \
                'Which date do you want to insert, say me'\
                ' just ordinal number of day in date'

            plugins_watcher.run('thirty')
            monthly_plan.run_doc(plugins_watcher.doc, queue.Queue())
            assert monthly_plan.end_result['result'] == \
                'Date thirty october 2010 is successfully inserted,'\
                ' function for inserting of dates is deactivated'

            plugins_watcher.run('insert')
            monthly_plan.run_doc(plugins_watcher.doc, queue.Queue())
            plugins_watcher.run('hello')
            monthly_plan.run_doc(plugins_watcher.doc, queue.Queue())

            assert monthly_plan.end_result['result'] == \
                'Input is wrong, try again with insert'

            plugins_watcher.run('insert')
            monthly_plan.run_doc(plugins_watcher.doc, queue.Queue())
            plugins_watcher.run('twenty first')
            monthly_plan.run_doc(plugins_watcher.doc, queue.Queue())

            plugins_watcher.run('delete')
            monthly_plan.run_doc(plugins_watcher.doc, queue.Queue())

            assert monthly_plan.end_result['result'] ==\
                'Which date do you want to delete'

            plugins_watcher.run('fifteenth')
            monthly_plan.run_doc(plugins_watcher.doc, queue.Queue())

            print(monthly_plan.end_result['result'])

            assert monthly_plan.end_result['result'] == \
                'The date fifteenth october 2010  does'\
                ' not exist in monthlyplan, so it can not be deleted'

            plugins_watcher.run('delete')
            monthly_plan.run_doc(plugins_watcher.doc, queue.Queue())
            plugins_watcher.run('hello')
            monthly_plan.run_doc(plugins_watcher.doc, queue.Queue())

            assert monthly_plan.end_result['result'] == \
                'Input is wrong, try again with deleting'

            plugins_watcher.run('delete')
            monthly_plan.run_doc(plugins_watcher.doc, queue.Queue())
            plugins_watcher.run('twenty first')
            monthly_plan.run_doc(plugins_watcher.doc, queue.Queue())

            assert monthly_plan.end_result['result'] == 'The last date'\
                ' twenty first october 2010 in the monthly plan is deleted'


def test_run_doc_activity() -> None:
    """Test run_doc."""
    with patch('common.helpers.date') as mock_date:
        mock_date.today.return_value = date(2010, 10, 8)
        with patch('processors.base_processor.BasePlugin') as plugin:
            plugin.engine.return_value = engine_
            monthly_plan = MonthlyPlanPlugin()

            plugins_watcher = PluginWatcher([monthly_plan])

            plugins_watcher.run('insert')
            monthly_plan.run_doc(plugins_watcher.doc, queue.Queue())
            plugins_watcher.run('thirty')
            monthly_plan.run_doc(plugins_watcher.doc, queue.Queue())

            plugins_watcher.run('activity')
            monthly_plan.run_doc(plugins_watcher.doc, queue.Queue())

            assert monthly_plan.end_result['result'] == \
                'On which date you want to add activity'
            plugins_watcher.run('hello')
            monthly_plan.run_doc(plugins_watcher.doc, queue.Queue())

            assert monthly_plan.end_result['result'] == \
                'Break adding of activity'
            plugins_watcher.run('activity')
            monthly_plan.run_doc(plugins_watcher.doc, queue.Queue())
            plugins_watcher.run('thirty')
            monthly_plan.run_doc(plugins_watcher.doc, queue.Queue())

            assert monthly_plan.end_result['result'] == \
                'Date thirty october 2010 exist in monthly plan, you can add time range'

            plugins_watcher.run('hello')
            monthly_plan.run_doc(plugins_watcher.doc, queue.Queue())

            assert monthly_plan.end_result['result'] == \
                "Time range ['hello'] is not valid,"\
                ' try another one, adding of activity broken.'

            plugins_watcher.run('activity')
            monthly_plan.run_doc(plugins_watcher.doc, queue.Queue())
            plugins_watcher.run('thirty')
            monthly_plan.run_doc(plugins_watcher.doc, queue.Queue())
            plugins_watcher.run('six zero seven zero')
            monthly_plan.run_doc(plugins_watcher.doc, queue.Queue())

            assert monthly_plan.end_result['result'] == \
                'Time range [6, 0, 7, 0] available, you can try to add an activity'

            plugins_watcher.run('watching tv')
            monthly_plan.run_doc(plugins_watcher.doc, queue.Queue())

            assert monthly_plan.end_result['result'] == 'Activity'\
                ' watching tv successfully added'


def test_exact_keyword__similar_keyword_activated() -> None:
    """Test exact keyword activated."""
    with patch('common.helpers.date') as mock_date:
        mock_date.today.return_value = date(2010, 10, 8)
        with patch('processors.base_processor.BasePlugin') as plugin:
            plugin.engine.return_value = engine_
            monthly_plan = MonthlyPlanPlugin()

            plugins_watcher = PluginWatcher([monthly_plan])
            monthly_plan.min_similarity = 1

            for keyword in constants.actions_keywords:
                monthly_plan.add_activation_doc(keyword)

            for day_orindal_number_keyword in constants.days_ordinal_numbers_keywords:
                monthly_plan.add_activation_doc(day_orindal_number_keyword)

            plugins_watcher.doc = plugins_watcher.nlp('insert')
            assert monthly_plan.exact_keyword_activated(plugins_watcher.doc) ==\
                'insert'

            monthly_plan.min_similarity = 0.5
            plugins_watcher.doc = plugins_watcher.nlp('hu insert')
            assert monthly_plan.similar_keyword_activated(plugins_watcher.doc) ==\
                'insert'
