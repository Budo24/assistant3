"""Test functions in helpers."""
from datetime import date
from unittest.mock import patch

from common import constants, helpers


def test_form_time_range() -> None:
    """Test form time range."""
    # this case happend oft, with one word infront of

    activated_keyword = 'he ten zero ten thirty'
    time_range = helpers.form_time_range(activated_keyword)
    assert time_range == ['ten', 'zero', 'ten', 'thirty']

    activated_keyword = 'ten zero ten thirty'
    time_range = helpers.form_time_range(activated_keyword)
    assert time_range == ['ten', 'zero', 'ten', 'thirty']

    activated_keyword = 'hello hello'
    time_range = helpers.form_time_range(activated_keyword)
    assert time_range == ['hello', 'hello']

    activated_keyword = 'twenty two zero twenty three thirty'
    time_range = helpers.form_time_range(activated_keyword)
    assert time_range == ['twenty two', 'zero', 'twenty three', 'thirty']

    activated_keyword = 'twenty two zero twenty zero'
    time_range = helpers.form_time_range(activated_keyword)
    assert time_range == ['twenty two', 'zero', 'twenty', 'zero']


def test_create_date() -> None:
    """Test creation of date."""
    ordinal_number_day = 'thirty'

    with patch('common.helpers.date') as mock_date:
        mock_date.today.return_value = date(2010, 10, 8)
        assert helpers.create_date(ordinal_number_day) == '2010-10-30'


def test_convert_time_range_from_words_to_numbers() -> None:
    """Test converting time range words to numbers."""
    time_range = ['twenty two', 'zero', 'twenty three', 'zero']
    time_range_numbers = helpers.convert_time_range_from_words_to_numbers(time_range)
    assert time_range_numbers == [22, 0, 23, 0]

    time_range = ['hello', 'zero', 'twenty three', 'zero']
    time_range_numbers = helpers.convert_time_range_from_words_to_numbers(time_range)
    assert time_range_numbers == [23, 0, 0]

    time_range = ['hello', 'zero', 'twenty hello', 'zero']
    time_range_numbers = helpers.convert_time_range_from_words_to_numbers(time_range)
    assert time_range_numbers == [0, 0]

    time_range = ['word1', 'word2']
    time_range_numbers = helpers.convert_time_range_from_words_to_numbers(time_range)
    assert not time_range_numbers


def test_check_number_of_days_in_month() -> None:
    """Test number of days."""
    date__ = '2021-02-29'
    answer = helpers.check_number_of_days_in_month(date__)
    assert answer == 'This year february has 28 days'

    date__ = '2022-06-31'
    answer = helpers.check_number_of_days_in_month(date__)
    assert answer == 'This month has 30 days'

    date__ = '2022-06-30'
    answer = helpers.check_number_of_days_in_month(date__)
    assert answer is True

    date__ = '2020-02-29'
    answer = helpers.check_number_of_days_in_month(date__)
    assert answer is True

    date__ = '2022-04-31'
    answer = helpers.check_number_of_days_in_month(date__)
    assert answer == 'This month has 30 days'

    date__ = '2022-07-31'
    answer = helpers.check_number_of_days_in_month(date__)
    assert answer is True


def test_time_range_validy() -> None:
    """Test time range validy."""
    time_range_numbers = [22, 0, 23, 0]
    time_range = helpers.time_range_validy(time_range_numbers)
    assert time_range == 60

    time_range_numbers = [20, 0, 19, 0]
    time_range = helpers.time_range_validy(time_range_numbers)
    assert time_range == -60

    time_range_numbers = [23, 0, 0]
    time_range = helpers.time_range_validy(time_range_numbers)
    assert time_range == -1


def test_day_today() -> None:
    """Test day today."""
    with patch('common.helpers.date') as mock_date:
        mock_date.today.return_value = date(2010, 10, 8)

        date_date = helpers.day_today()
        assert date_date == '08'


def test_day_past_in_monthly_plan() -> None:
    """Test of day is in the past or in the future in monthly plan."""
    with patch('common.helpers.date') as mock_date:
        mock_date.today.return_value = date(2010, 10, 8)

        date_to_insert = '2010-10-07'
        date_in_past = helpers.day_past_in_monthly_plan(date_to_insert)
        assert date_in_past == constants.answers[5]

        date_to_insert = '2010-10-08'
        date_in_past = helpers.day_past_in_monthly_plan(date_to_insert)
        assert date_in_past == constants.answers[6]

        date_to_insert = '2010-10-09'
        date_in_past = helpers.day_past_in_monthly_plan(date_to_insert)
        assert date_in_past is False

        date_to_insert = '2010-10-19'
        date_in_past = helpers.day_past_in_monthly_plan(date_to_insert)
        assert date_in_past is False


def test_say_date() -> None:
    """Test saying of date."""
    date_to_say = '2022-06-20'
    date_said = helpers.say_date(date_to_say)
    assert date_said == 'twentieth june 2022'
