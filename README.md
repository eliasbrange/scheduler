# Scheduler

## Install
`$ pip install -r requirements`

## Run tests
`$ py.test`

## Run
```
$ scheduler count_entries
> # Users: 0
> # Busy entries: 0

$ scheduler add-entries -f test.txt
> 2 users added.
> 2 busy entries added.

$ scheduler count_entries
> # Users: 2
> # Busy entries: 2

$ scheduler meeting -i "1,2" -sd "2015-03-13" -ed "2015-03-13" -sh 7 -eh 11 -d 30
> Participants:
> user1
> user2
> Times:
> 2015-03-13 07:00:00 - 2015-03-13 07:30:00
> 2015-03-13 07:30:00 - 2015-03-13 08:00:00
> 2015-03-13 08:30:00 - 2015-03-13 09:00:00
> 2015-03-13 09:00:00 - 2015-03-13 09:30:00
> 2015-03-13 10:30:00 - 2015-03-13 11:00:00

$ scheduler purge_db
> Database was purged.

$ scheduler count_entries
> # Users: 0
> # Busy entries: 0
```
