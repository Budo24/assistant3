"""Generate pick_id and order_id."""
import datetime

import spacy


def order_id_generate(day_time_func: datetime.datetime) -> int:
    """Give order_id.

    Args:
        day_time_func: day and time that we become with datetime modul.

    Returns:
        Return order_id.

    """
    nlp = spacy.load('en_core_web_md')
    day_time_text = str(day_time_func)
    day_time_doc = nlp(day_time_text)
    split_day_time = [token.text for token in day_time_doc]
    split_day = split_day_time[2:5]
    del split_day[1]
    iter_1 = iter(split_day)
    _f2 = next(iter_1)
    _f1 = next(iter_1)
    split_time = list(split_day_time[5])
    del split_time[8:]
    del split_time[2]
    del split_time[4]
    _m1 = int(_f1)
    _m2 = int(_f2)
    day_time = [str(_m1), str(_m2)] + split_time
    id_day_time = _f1
    for i in range(1, len(day_time)):
        id_day_time = id_day_time + day_time[i]
    return int(id_day_time)


def pick_time_generate(order_id: int) -> int:
    """Give pick_time.

    Args:
        order_id: Use order id to generate pick time.

    Returns:
        Return pick time. It is one day after store order.

    """
    time_str = str(order_id)
    time_str = time_str[-6:]
    month_day = month_day_generate()
    if month_day[2] is True:
        return int(str(month_day[0]) + str(month_day[1]) + time_str)
    month_day[0] = month_day[0] + 1
    return int(str(month_day[0]) + str(month_day[1]) + time_str)


def month_day_generate() -> list[bool | int]:
    """Give list of month and day. use for pick_time_generate.

    Add one day to the actually day to determine pick_time.
    That why its make sence to check the actually day.

    Returns:
        Return month and day.

    """
    nlp = spacy.load('en_core_web_md')
    date_time_func = datetime.datetime.now()
    day_time_text = str(date_time_func)
    day_time_doc = nlp(day_time_text)
    split_day_time = [token.text for token in day_time_doc]
    month_day = [int(split_day_time[4]), int(split_day_time[2])]
    month_31_day = month_day[0] in (7, 8, 10, 12, 1, 3, 5)
    month_february = month_day[0] == 2
    _m = (month_day[0] + 1 > 28 and month_february)
    _n = (month_day[0] + 1 > 30 and not month_31_day)
    if _n or (month_day[0] + 1 > 31) or _m:
        if month_day[1] + 1 > 12:
            month_day[1] = 1
        else:
            month_day[1] = month_day[1] + 1
        month_day[0] = 1
        return [month_day[0], month_day[1], True]
    return [month_day[0], month_day[1], False]

