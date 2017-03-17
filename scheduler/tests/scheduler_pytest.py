import pytest
from scheduler.scheduler import Scheduler, User, BusyEntry, TimeTuple
from datetime import datetime


@pytest.fixture
def scheduler():
    return Scheduler()


def test_add_entries(scheduler):
    entries = ['1;name', '1;3/13/2015 8:00:00 AM;3/13/2015 1:00:00 PM;1234']
    users, busy_entries = scheduler.add_entries(entries)
    assert len(users) == 1
    assert len(busy_entries) == 1


def test_add_user_entry(scheduler):
    entry = '1;name'
    user = scheduler._add_user_entry(entry)

    assert isinstance(user, User)

    assert user.id == 1
    assert user.name == 'name'


@pytest.mark.parametrize('entry', [
    ('1'),
    ('1;name;start_time'),
    ('1;name;start_time;end_time'),
    ('badid;name'),
])
def test_add_user_entry_returns_none_if_bad_format(entry, scheduler):
    user = scheduler._add_user_entry(entry)
    assert user is None


def test_add_busy_entry(scheduler):
    entry = '1;3/13/2015 8:00:00 AM;3/13/2015 1:00:00 PM;1234'
    busy_entry = scheduler._add_busy_entry(entry)

    assert isinstance(busy_entry, BusyEntry)

    assert busy_entry.id == 1
    assert busy_entry.start_time == '2015-03-13 08:00'
    assert busy_entry.end_time == '2015-03-13 13:00'


@pytest.mark.parametrize('entry', [
    ('1'),
    ('1;start_time;end_time;101010'),
    ('badid;3/13/2015 8:00:00 AM;3/13/2015 1:00:00 PM;1234'),
])
def test_add_busy_entry_returns_none_if_bad_format(entry, scheduler):
    busy_entry = scheduler._add_busy_entry(entry)
    assert busy_entry is None


def test_get_busy_entry_time_tuple():
    busy_entry = BusyEntry(1, '2015-03-13 08:00', '2015-03-13 13:00')

    timetuple = busy_entry.get_time_tuple()

    assert isinstance(timetuple, TimeTuple)

    assert timetuple.start == datetime(2015, 3, 13, 8)
    assert timetuple.end == datetime(2015, 3, 13, 13)


def test_user_str():
    user = User(1, 'user')
    assert user.__str__() == 'User(name=user, id=1)'


def test_busy_entry_str():
    busy_entry = BusyEntry(1, '2015-03-13 08:00', '2015-03-13 13:00')
    expected = ('BusyEntry(id=1, start_time=2015-03-13 08:00, '
                'end_time=2015-03-13 13:00)')
    assert busy_entry.__str__() == expected


def test_time_tuple_str():
    timetuple = TimeTuple(datetime(2015, 3, 13, 8), datetime(2015, 3, 13, 13))
    expected = ('TimeTuple(start=2015-03-13 08:00, end=2015-03-13 13:00)')
    assert timetuple.__str__() == expected


def test_time_tuples_overlap():
    timetuple1 = TimeTuple(datetime(2015, 3, 13, 7), datetime(2015, 3, 13, 9))
    timetuple2 = TimeTuple(datetime(2015, 3, 13, 8), datetime(2015, 3, 13, 10))
    timetuple3 = TimeTuple(datetime(2015, 3, 13, 6), datetime(2015, 3, 13, 7))
    assert timetuple1.overlaps(timetuple2)
    assert not timetuple1.overlaps(timetuple3)


def test_generate_meeting_times(scheduler):
    start_date = datetime(2015, 1, 2)
    end_date = datetime(2015, 1, 3)
    start_hour = 8
    end_hour = 9

    res = list(scheduler._generate_meeting_times(start_date, end_date,
                                                 start_hour, end_hour, 30))

    assert len(res) == 4
    assert res[0].start == datetime(2015, 1, 2, 8)
    assert res[0].end == datetime(2015, 1, 2, 8, 30)

    assert res[1].start == datetime(2015, 1, 2, 8, 30)
    assert res[1].end == datetime(2015, 1, 2, 9)

    assert res[2].start == datetime(2015, 1, 3, 8)
    assert res[2].end == datetime(2015, 1, 3, 8, 30)

    assert res[3].start == datetime(2015, 1, 3, 8, 30)
    assert res[3].end == datetime(2015, 1, 3, 9)

    res = list(scheduler._generate_meeting_times(start_date, end_date,
                                                 start_hour, end_hour, 40))

    assert len(res) == 2
    assert res[0].start == datetime(2015, 1, 2, 8)
    assert res[0].end == datetime(2015, 1, 2, 8, 40)

    assert res[1].start == datetime(2015, 1, 3, 8)
    assert res[1].end == datetime(2015, 1, 3, 8, 40)

    res = list(scheduler._generate_meeting_times(start_date, end_date,
                                                 start_hour, end_hour, 60))

    assert len(res) == 2
    assert res[0].start == datetime(2015, 1, 2, 8)
    assert res[0].end == datetime(2015, 1, 2, 9)

    assert res[1].start == datetime(2015, 1, 3, 8)
    assert res[1].end == datetime(2015, 1, 3, 9)


@pytest.mark.parametrize('start_date, end_date, start_hour, end_hour, dur', [
    (datetime(2015, 1, 2), datetime(2015, 1, 1), 8, 9, 30),
    (datetime(2015, 1, 1), datetime(2015, 1, 2), 9, 8, 30),
    (datetime(2015, 1, 1), datetime(2015, 1, 2), 8, 9, 0),
    (datetime(2015, 1, 1), datetime(2015, 1, 2), 8, 9, -30),
])
def test_generate_meeting_times_raises_error(start_date, end_date, start_hour,
                                             end_hour, dur, scheduler):
    with pytest.raises(ValueError):
        list(scheduler._generate_meeting_times(start_date=start_date,
                                               end_date=end_date,
                                               start_hour=start_hour,
                                               end_hour=end_hour,
                                               duration=dur))


def test_find_available_meeting_times(scheduler):
    busy_entry = BusyEntry(1, '2015-03-13 08:30', '2015-03-13 09:30')
    start_date = datetime(2015, 3, 13)
    end_date = datetime(2015, 3, 13)
    start_hour = 8
    end_hour = 10
    duration = 30

    res = scheduler.find_available_meeting_times(busy_entries=[busy_entry],
                                                 start_date=start_date,
                                                 end_date=end_date,
                                                 start_hour=start_hour,
                                                 end_hour=end_hour,
                                                 duration=duration)

    assert len(res) == 2
    assert res[0].start == datetime(2015, 3, 13, 8)
    assert res[0].end == datetime(2015, 3, 13, 8, 30)

    assert res[1].start == datetime(2015, 3, 13, 9, 30)
    assert res[1].end == datetime(2015, 3, 13, 10)
