"""Generate pick_id and order_id"""
import spacy
import datetime
import typing


def order_id_generate(day_time_func: typing.Any) -> int:
    """give order_id"""
    nlp = spacy.load('en_core_web_md')
    day_time_text = str(day_time_func)
    day_time_doc = nlp(day_time_text)
    split_day_time = [token.text for token in day_time_doc]
    split_day = split_day_time[2:5]
    del split_day[1]
    split_day = [int(split_day[i]) for i in range(len(split_day))]
    split_day = [split_day[1], split_day[0]]
    split_time = list(split_day_time[5])
    del split_time[8:]
    del split_time[2]
    del split_time[4]
    split_time = [int(split_time[i]) for i in range(len(split_time))]
    day_time = split_day + split_time
    day_time = [str(day_time[i]) for i in range(len(day_time))]
    id_day_time = day_time[0]
    for i in range(1, len(day_time)):
        id_day_time = id_day_time + day_time[i]
    return int(id_day_time)


def pick_time_generate(order_id_generate: int) -> int:
    """give pick_time"""
    time_str = str(order_id_generate)
    time_str = time_str[-6:]
    month_day = month_day_generate()
    if month_day[2] is True:
        return int(str(month_day[0]) + str(month_day[1]) + time_str)
    else:
        month_day[0] = month_day[0] + 1
        return int(str(month_day[0]) + str(month_day[1]) + time_str)


def month_day_generate() -> list:
    """Give list of month and day
    use for pick_time_generate"""
    nlp = spacy.load('en_core_web_md')
    date_time_func = datetime.datetime.now()
    day_time_text = str(date_time_func)
    day_time_doc = nlp(day_time_text)
    split_day_time = [token.text for token in day_time_doc]
    month_day = [int(split_day_time[4]), int(split_day_time[2])]
    month_31_day = bool(month_day[0] in (7, 8, 10, 12, 1, 3, 5))
    month_february = bool(month_day[0] == 2)
    if (month_day[0] + 1 > 30 and
        not month_31_day) or (month_day[0] + 1 > 31) or (month_day[0] + 1 > 28 and month_february):
        if month_day[1] + 1 > 12:
            month_day[1] = 1
        else:
            month_day[1] = month_day[1] + 1
        month_day[0] = 1
        return [month_day[0], month_day[1], True]
    else:
        return [month_day[0], month_day[1], False]


if __name__ == '__main__':
    day_time_func = datetime.datetime.now()
    print("order_id= ", order_id_generate(day_time_func))
    print("pick_time= ", pick_time_generate(order_id_generate(day_time_func)))
