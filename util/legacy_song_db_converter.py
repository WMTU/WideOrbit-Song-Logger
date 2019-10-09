# utility to convert the legacy log db to format to the new log format
# takes a csv argument and does the work on it

''' legacy table
+------------------+------------------+------+-----+-------------------+----------------+
| Field            | Type             | Null | Key | Default           | Extra          |
+------------------+------------------+------+-----+-------------------+----------------+
| id               | int(10) unsigned | NO   | PRI | NULL              | auto_increment |
| cd_number        | varchar(20)      | NO   |     |                   |                |
| song_name        | varchar(255)     | NO   |     | NULL              |                |
| artist           | varchar(255)     | NO   |     | NULL              |                |
| genre            | varchar(64)      | NO   |     | NULL              |                |
| album            | varchar(255)     | NO   |     | NULL              |                |
| score            | int(5)           | NO   |     | 0                 |                |
| location         | varchar(64)      | NO   |     | NULL              |                |
| truncated_artist | varchar(255)     | NO   |     | NULL              |                |
| ts               | timestamp        | NO   |     | CURRENT_TIMESTAMP |                |
+------------------+------------------+------+-----+-------------------+----------------+
'''

#########################################################################################

# Configurations

db_username = "username"
db_password = "password"
db_hostname = "hostname"
db_port     = "5433"
db_database = "song_logs"

#########################################################################################

# system utilities
import sys, getopt
from datetime import datetime, date, time, timedelta

# libraries for working with the table
import pandas as pd
import numpy as np

# psycopg2 for working with postgres
import psycopg2
from psycopg2 import sql

try:
    opts, args = getopt.getopt(sys.argv[1:], "", ["file="])

except getopt.GetoptError:
    print("Specify a file with --file=<file name>")
    sys.exit(1)

if len(opts) < 1:
    print("Specify a file with --file=<file name>")
    sys.exit(1)

csv_file = None

for o, a in opts:
    if o == "--file":
        csv_file = a

# legacy table
legacy = pd.read_csv(csv_file, sep=',', header=None, keep_default_na=False)
legacy.columns = ["id", "cd_number", "song_name", "artist", "genre", "album", "score", "location", "truncated_artist", "ts"]

# convert from legacy to new
new_rows = []
for row in legacy.itertuples():
    tmp_dict = {}

    # strip out the ts and convert to the needed date formats
    ts = datetime.strptime(row.ts, "%Y-%m-%d %H:%M:%S")
    tmp_dict['play_date'] = ts.strftime("%Y-%m-%d")
    tmp_dict['play_time'] = ts.strftime("%H:%M:%S")
    tmp_dict['timestamp'] = row.ts

    # update all of the data for the new row from the legacy
    tmp_dict['song']        = row.song_name
    tmp_dict['artist']      = row.artist
    tmp_dict['album']       = row.album
    tmp_dict['genre']       = row.genre
    tmp_dict['location']    = row.location
    tmp_dict['cd_id']       = row.cd_number

    # add the new row to the rows list
    new_rows.append(tmp_dict)

# new table
new = pd.DataFrame(data=new_rows, columns=["play_date", "play_time", "timestamp", "song", "artist", "album", "genre", "location", "cd_id"])

# add the new rows to the new database
# song log query
log_query = "INSERT INTO play_log(play_date, play_time, timestamp, song, artist, album, genre, location, cd_id) \
    VALUES(%(play_date)s, %(play_time)s, %(timestamp)s, %(song)s, %(artist)s, %(album)s, %(genre)s, %(location)s, %(cd_id)s);"

# stats log query
select_query = "SELECT * FROM play_stats \
    WHERE song = %(song)s AND artist = %(artist)s AND album = %(album)s;"
add_query    = "INSERT INTO play_stats(song, artist, album) \
    VALUES(%(song)s, %(artist)s, %(album)s);"
update_query = "UPDATE play_stats SET play_count = (play_count + 1) \
    WHERE song = %(song)s AND artist = %(artist)s AND album = %(album)s;"

# set up the database connection
try:
    db = psycopg2.connect(
        user        = db_username,
        password    = db_password,
        host        = db_hostname,
        port        = db_port,
        database    = db_database
    )
    db.set_session(autocommit=True)
    cursor = db.cursor()

    if(cursor):
        for row in new_rows:
            # print out song info
            print("\n=== Adding Song ===")
            print("Song     => " + row['song'])
            print("Artist   => " + row['artist'])
            print("Album    => " + row['album'])
            print("Genre    => " + row['genre'])
            print("Location => " + row['location'])
            print("CD ID    => " + row['cd_id'])
            print("TS       => " + row['timestamp'])

            # add to song log
            cursor.execute(log_query, row)

            # add to stats log
            if row['album'] == "":
                album = "--"
            else:
                album = row['album']

            query_args = {'song': row['song'], 'artist': row['artist'], 'album': album}

            # query the database
            cursor.execute(select_query, query_args)

            # based on the query result either add a new entry or update an existing entry
            if len(cursor.fetchall()) == 0:
                cursor.execute(add_query, query_args)
            else:
                cursor.execute(update_query, query_args)

except (Exception, psycopg2.DatabaseError) as error :
    print ("Database Error! => ", error)

