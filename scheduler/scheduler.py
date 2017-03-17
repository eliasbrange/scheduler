from datetime import datetime, timedelta


class Scheduler():
    """Scheduler class that parses entries and finds available times. """
    def add_entries(self, entries):
        """Add entries to the schedulers memory.

        Entries should be on the forms:
            - User: 'id;name'
            - BusyEntry: 'user_id;start_time;end_time;checksum'

        Args:
            entries: A list of entries

        Returns:
            Tuple with users and busy_entries.
        """
        users = set()
        busy_entries = set()

        for entry in entries:
            user = self._add_user_entry(entry)
            if user:
                users.add(user)

            busy_entry = self._add_busy_entry(entry)
            if busy_entry:
                busy_entries.add(busy_entry)

        return (list(users), list(busy_entries))

    @staticmethod
    def _add_user_entry(entry):
        parts = entry.strip().split(';')
        if len(parts) != 2:
            return None

        try:
            user_id = int(parts[0])
        except ValueError:
            return None

        return User(id=user_id, name=parts[1])

    @staticmethod
    def _add_busy_entry(entry):
        parts = entry.strip().split(';')
        if len(parts) != 4:
            return None

        try:
            user_id = int(parts[0])
        except ValueError:
            return None

        try:
            start_time = datetime.strptime(parts[1], '%m/%d/%Y %I:%M:%S %p')
            start_time = datetime.strftime(start_time, '%Y-%m-%d %H:%M')
            end_time = datetime.strptime(parts[2], '%m/%d/%Y %I:%M:%S %p')
            end_time = datetime.strftime(end_time, '%Y-%m-%d %H:%M')
        except ValueError:
            # print('BusyEntry has badly formatted date, skipping entry...')
            return None

        return BusyEntry(id=user_id, start_time=start_time, end_time=end_time)

    def find_available_meeting_times(self, busy_entries, start_date,
                                     end_date, start_hour, end_hour,
                                     duration):
        meeting_times = self._generate_meeting_times(start_date=start_date,
                                                     end_date=end_date,
                                                     start_hour=start_hour,
                                                     end_hour=end_hour,
                                                     duration=duration)

        meeting_times = [time for time in meeting_times
                         if not any(time.overlaps(busy_entry.get_time_tuple())
                                    for busy_entry in busy_entries)]

        return meeting_times

    @staticmethod
    def _generate_meeting_times(start_date, end_date, start_hour, end_hour,
                                duration):
        if start_hour > end_hour:
            raise ValueError('Start hour must be before end hour.')

        if start_date > end_date:
            raise ValueError('Start date must be before end date.')

        if duration < 1:
            raise ValueError('Duration must be a positive integer.')

        # Number of possible starting points.
        # If hours are 8-10 there are four possible starting points:
        # 8:00, 8:30, 9:00, 9:30
        starting_points = 2 * (end_hour - start_hour)

        # Remove late starting points to not go past end_hour.
        starting_points -= duration // 30

        # Allow meetings to end exactly at end_hour.
        if (duration % 30 == 0):
            starting_points += 1

        days = (end_date-start_date).days

        for i in range(days + 1):
            for j in range(starting_points):
                start = start_date + timedelta(days=i,
                                               hours=start_hour,
                                               minutes=30*j)
                end = start_date + timedelta(days=i,
                                             hours=start_hour,
                                             minutes=30*j+duration)
                yield TimeTuple(start, end)


class TimeTuple():
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __str__(self):
        return ('TimeTuple(start={}, end={})'
                .format(datetime.strftime(self.start, '%Y-%m-%d %H:%M'),
                        datetime.strftime(self.end, '%Y-%m-%d %H:%M')))

    def overlaps(self, timetuple):
        """Check whether this TimeTuple overlaps the given TimeTuple.

        Args:
            timetuple: The TimeTuple to check.

        Returns:
            Booelan indicating whether the two TimeTuples overlaps.
        """
        return self.start < timetuple.end and self.end > timetuple.start


class User():
    """Class representing a user in the scheduler.

    Attributes:
        id: the id of the user.
        name: the name of the user.
    """
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __str__(self):
        return 'User(name={}, id={})'.format(self.name, self.id)


class BusyEntry():
    """Class representing a busy entry in the scheduler.

    Attributes:
        id: the user id the entry references to.
        start_time: the start of the busy entry.
        end_time: the end of the busy entry.
    """
    def __init__(self, id, start_time, end_time):
        self.id = id
        self.start_time = start_time
        self.end_time = end_time

    def get_time_tuple(self):
        return TimeTuple(start=datetime.strptime(self.start_time,
                                                 '%Y-%m-%d %H:%M'),
                         end=datetime.strptime(self.end_time,
                                                 '%Y-%m-%d %H:%M'))

    def __str__(self):
        return ('BusyEntry(id={}, start_time={}, end_time={})'
                .format(self.id, self.start_time, self.end_time))
