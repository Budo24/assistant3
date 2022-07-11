"""All helping functions for MothlyPlanPlugin."""

from datetime import date

from common import constants


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

    if len(time_range) == 5:
        del time_range[0]

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

    if len(time_range) != 4:
        return time_range_numbers

    for index, _word in enumerate(time_range):
        for numbers, _words in constants.hour_number_to_word.items():
            if index in (0, 2) and _word == _words:
                time_range_numbers.append(int(numbers))

    for index, _word in enumerate(time_range):
        for numbers, _words in constants.minute_number_to_word.items():
            if index in (1, 3) and _word == _words:
                time_range_numbers.append(int(numbers))

    if len(time_range_numbers) > 2:
        time_range_numbers[2], time_range_numbers[1] = \
            time_range_numbers[1], time_range_numbers[2]

    return time_range_numbers


def check_number_of_days_in_month(_date: str) -> str | bool:
    """Check if given day like ordinal number exist in month.

    To avoid for example 31-06-2022
    """
    _date_ = _date.split('-')
    date_days = _date_[2]
    date_month = _date_[1]
    date_year = int(_date_[0])

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
    for element in time_range_numbers:
        if not isinstance(element, int):
            all_integers = False

    if len(time_range_numbers) != 4:
        all_integers = False

    if all_integers:
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
