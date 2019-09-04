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

## Nginx

We use Nginx as our webserver of choice. We have an example vhost configuration included.

## PostgreSQL Table

We are using PostgreSQL as our database of choice for logging our songs. There's no big advantage for us, but PostgreSQL is a more modern database package versus MySQL.

Here is our table structure for logging our songs:

play_date       => date the song was played
play_time       => time the song was played
unix_date*      => unix-style date string
song            => song name
artist          => artist name
album           => album name
genre           => genre of song
play_count      => number of times played
artwork_url     => url to an image of the album art

'*' = key
