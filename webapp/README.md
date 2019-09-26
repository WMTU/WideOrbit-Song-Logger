# WideOrbit Song Logger -- Webapp

Current Version: 2.0

Webapp interface and backend API for logging and querying the song log PostgreSQL database.

Technologies used:

- [BootStrap](https://getbootstrap.com/)
- [Python 3](https://www.python.org/)
- [virtualenv](https://virtualenv.pypa.io/en/latest/)
- [Flask](https://palletsprojects.com/p/flask/)
- [Nginx](https://nginx.org/en/)

## Web Interface

The interface is built using bootstrap and common web development practices.

## Flask API backend

The backend API is built as a Flask app using Python 3.

### Using the API

**Logging a Song**

Required Parameters:

- api_key   : api key
- song      : name of the song
- artist    : name of the artist

Optional Parameters:

- album     : name of the album
- genre     : genre of the song
- location  : library location for the song
- cd_id     : WMTU library CD ID

Example:

```text
https://log.wmtu.fm/api/2.0/log?api_key=<api key here>?song=<song name>?artist=<artist name>
```

**Logging a Discrepancy**

Required Parameters:

- api_key       : API key
- song          : song name
- artist        : artist name
- dj_name       : DJ name
- word          : swear word
- button_hit    : True/False if the swear button was hit

```text
https://log.wmtu.fm/api/2.0/discrepancy?api_key=<api key>?song=<song name>?artist=<artist name>...
```

**Submitting a Song Request**

Required Parameters:

- api_key       : API key
- song          : song name
- artist        : artist name

Optional Parameters:

- album         : album name
- rq_name       : requester name
- rq_message    : request message

```text
https://log.wmtu.fm/api/2.0/request?api_key=<api key>?song=<song name>?artist=<artist name>...
```

**Requesting a Log**

Optional Paramters:

- type  : the type of record to request (song, discrepancy, request)
- n     : number of items to list
- date  : list items for a specific date (yyyy-mm-dd)
- delay : (only for song records) apply a 40 second delay to the logged songs list

Default Action:

If no arguments are supplied the default is to return the last song logged.

Example:

```text
https://log.wmtu.fm/api/2.0/log?type=<song, discrepancy, request>?n=<#>
```

## PostgreSQL Database

We are using PostgreSQL as our database of choice for logging our songs. There's no big advantage for us, but PostgreSQL is a more modern database package versus MySQL.

### Song Log Table

Here is our table structure for logging our songs:

**play_log**

```text
play_id*        => incrementing count of played songs
play_date       => date the song was played (yyyy-mm-dd)
play_time       => time the song was played (hh:mm:ss)
timestamp       => timestamp with date and time
song            => song name
artist          => artist name
album           => album name
genre           => genre of song
location        => library the song came from
cd_id           => WMTU library CD ID
artwork         => url for artwork

'*' = key
```

### Play Statistics Table

Here is our table for keeping track of play statistics:

**play_stats**

```text
song_id         => incrementing count of played songs
song*           => song name
artist*         => artist name
album*          => album name
play_count      => number of times played

'*' = key
```

### Discrepancy Table

This table is for keeping track of songs that swear on air:

**discrepancy_log**

```text
dis_count*      => incrementing count of discrepancies
play_date       => date the song was played (yyyy-mm-dd)
play_time       => time the song was played (hh:mm:ss)
timestamp       => timestamp with date and time
song            => song name
artist          => artist name
dj_name         => name of the current dj
word            => swear word played
button_hit      => boolean for if the swear button was pressed

'*' = key
```

### Song Request Table

**song_requests**

```text
rq_id*          => incrementing request id number
rq_date         => date the song was played (yyyy-mm-dd)
rq_time         => time the song was played (hh:mm:ss)
timestamp       => timestamp with date and time
song            => song name
artist          => artist name
album           => album name
rq_name         => name of the requester
rq_message      => request message

'*' = key
```

## Nginx

We use Nginx as our webserver of choice. We have an example vhost configuration included.
