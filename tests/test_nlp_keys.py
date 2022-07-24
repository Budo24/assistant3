"""Test generated Keys for order_id and pick_time."""
import datetime

from assistant3.processors.bestellung_management.npl_keys import (
    month_day_generate,
    order_id_generate,
    pick_time_generate,
)


def test_id_time_value() -> None:
    """Test that generation of order_id from datetime.

    the pick time comes from order_id. that means you add to this day one day
    and we will become the pick time.

    """
    _lml = '%Y-%m-%d %H:%M:%S.%f'
    _m = datetime.datetime.strptime('2022-07-24 23:03:30.002221', _lml)
    order_id = order_id_generate(_m)
    assert order_id_generate(_m) == 247230330
    assert pick_time_generate(order_id) == 257230330


def test_month_day_value() -> None:
    """Test that generation of pick_time from order_id.

    When we find True like [1, 3, True] that means that it was one
    day already added cause in this case when we add one day we will have
    the next month.Otherwise will one day in pick_time_generate function
    be added and in month_day_generate will the month stay like ho he is.

    """
    _format = '%Y-%m-%d %H:%M:%S.%f'
    _month_1 = [[str('1'.zfill(2)), 30], [str('1'.zfill(2)), 31]]
    _month_2 = [[str('2'.zfill(2)), 27], [str('2'.zfill(2)), 28]]
    _month_4 = [[str('4'.zfill(2)), 29], [str('4'.zfill(2)), 30]]
    _month_12 = [[str('12'.zfill(0)), 30], [str('12'.zfill(0)), 31]]
    _time_now = ' 23:03:30.002221'
    _klist = _month_1 + _month_2 + _month_4 + _month_12
    for _list in _klist:
        _c = '2022-' + f'{_list[0]}' + '-' + f'{_list[1]}' + _time_now
        _month_day = datetime.datetime.strptime(_c, _format)
        if _list == _month_1[0]:
            assert month_day_generate(_month_day) == [30, 1, False]
        if _list == _month_1[1]:
            assert month_day_generate(_month_day) == [1, 2, True]
        if _list == _month_2[0]:
            assert month_day_generate(_month_day) == [27, 2, False]
        if _list == _month_2[1]:
            assert month_day_generate(_month_day) == [1, 3, True]
        if _list == _month_4[0]:
            assert month_day_generate(_month_day) == [29, 4, False]
        if _list == _month_4[1]:
            assert month_day_generate(_month_day) == [1, 5, True]
        if _list == _month_12[0]:
            assert month_day_generate(_month_day) == [30, 12, False]
        if _list == _month_12[1]:
            assert month_day_generate(_month_day) == [1, 1, True]
