from tinydb import TinyDB, where
import click
import sys
from scheduler.scheduler import Scheduler, BusyEntry
from datetime import datetime

db = TinyDB('db.json')
table_users = db.table('users')
table_busy = db.table('busy')

scheduler = Scheduler()


@click.group(context_settings={
    'help_option_names': ['--help', '-h'],
})
def cli():
    pass


@cli.command()
@click.option('--file', '-f', prompt=True, required=True,
              help='The file to add entries from.')
def add_entries(file):
    """Add entries to the scheduler from the specified file."""
    with open(file, 'r') as f:
        # Get users and busy entries from file
        users, busy_entries = scheduler.add_entries(f.readlines())

        # Add entries to database
        table_users.insert_multiple([entry.__dict__ for entry in users])
        table_busy.insert_multiple([entry.__dict__ for entry in busy_entries])

        print('{} users added.'.format(len(users)))
        print('{} busy entries added.'.format(len(busy_entries)))


@cli.command()
@click.option('--ids', '-i', required=True,
              help='Comma-separated string with user ids to schedule meeting '
                   'for.')
@click.option('--start-date', '-sd', required=True,
              help='Earliest wanted meeting date.')
@click.option('--end-date', '-ed', required=True,
              help='Latest wanted meeting date.')
@click.option('--start-hour', '-sh', required=True,
              help='Earliest wanted meeting hour.')
@click.option('--end-hour', '-eh', required=True,
              help='Latest wanted meeting hour.')
@click.option('--duration', '-d', required=True,
              help='Meeting duration in minutes.')
def meeting(ids, start_date, end_date, start_hour, end_hour, duration):
    """Find possible meeting times."""
    try:
        ids = ids.split(',')
        ids = list(map(int, ids))
    except ValueError:
        print('Ids have to be numeric.')
        sys.exit(1)

    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        print('Dates must be on format YYYY-MM-DD')
        sys.exit(1)

    try:
        start_hour = int(start_hour)
        end_hour = int(end_hour)
    except ValueError:
        print('Hours must be integers between 0 and 24.')
        sys.exit(1)

    try:
        start_hour = int(start_hour)
        end_hour = int(end_hour)
    except ValueError:
        print('Hours must be integers between 0 and 24.')
        sys.exit(1)

    try:
        duration = int(duration)
    except ValueError:
        print('Duration mus be an integer.')
        sys.exit(1)

    users = _get_user_names(ids)
    busy_entries = list(_get_busy_entries(ids))

    res = scheduler.find_available_meeting_times(busy_entries=busy_entries,
                                                 start_date=start_date,
                                                 end_date=end_date,
                                                 start_hour=start_hour,
                                                 end_hour=end_hour,
                                                 duration=duration)

    if not res:
        print('No possible times found.')
        sys.exit(0)

    print('Participants: ')
    print('\n'.join(users))
    print('Times:')
    for time in res:
        print('{} - {}'.format(time.start, time.end))


@cli.command()
def purge_db():
    """Purge database"""
    db.purge_tables()
    print('Database was purged.')


@cli.command()
def count_entries():
    """Purge database"""
    print('# Users: {}'.format(len(table_users)))
    print('# Busy entries: {}'.format(len(table_busy)))


def _get_user_names(ids):
    for id in ids:
        for res in table_users.search(where('id') == id):
            yield res['name']


def _get_busy_entries(ids):
    for id in ids:
        for res in table_busy.search(where('id') == id):
            yield BusyEntry(id=res['id'],
                            start_time=res['start_time'],
                            end_time=res['end_time'])


if __name__ == '__main__':
    sys.exit(cli())
