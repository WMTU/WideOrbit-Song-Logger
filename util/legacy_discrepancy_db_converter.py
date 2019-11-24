# utility to convert the legacy log db to format to the new log format
# takes a csv argument and does the work on it

''' legacy table
+------------+------------------+------+-----+-------------------+----------------+
| Field      | Type             | Null | Key | Default           | Extra          |
+------------+------------------+------+-----+-------------------+----------------+
| id         | int(10) unsigned | NO   | PRI | NULL              | auto_increment |
| dj_name    | varchar(64)      | NO   |     | NULL              |                |
| song_name  | varchar(255)     | NO   |     | NULL              |                |
| artist     | varchar(255)     | NO   |     | NULL              |                |
| word       | varchar(64)      | NO   |     | NULL              |                |
| cd_number  | varchar(16)      | NO   |     |                   |                |
| hit_button | varchar(10)      | NO   |     | NULL              |                |
| timestamp  | timestamp        | NO   |     | CURRENT_TIMESTAMP |                |
+------------+------------------+------+-----+-------------------+----------------+
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
legacy.columns = ["id", "dj_name", "song_name", "artist", "word", "cd_number", "hit_button", "timestamp"]

# convert from legacy to new
new_rows = []
for row in legacy.itertuples():
    tmp_dict = {}

    # strip out the ts and convert to the needed date formats
    ts = datetime.strptime(row.timestamp, "%m/%d/%Y %h:%M")
    tmp_dict['dis_date'] = ts.strftime("%Y-%m-%d")
    tmp_dict['dis_time'] = ts.strftime("%H:%M:%S")
    tmp_dict['timestamp'] = ts.strftime("%Y-%m-%d %H:%M:%S")

    # update all of the data for the new row from the legacy
    tmp_dict['song']        = row.song_name
    tmp_dict['artist']      = row.artist
    tmp_dict['dj_name']     = row.dj_name
    tmp_dict['word']        = row.word
    tmp_dict['button_hit']  = row.hit_button

    # add the new row to the rows list
    new_rows.append(tmp_dict)

# new table
new = pd.DataFrame(data=new_rows, columns=["dis_date", "dis_time", "timestamp", "song", "artist", "dj_name", "word", "button_hit"])

# add the new rows to the new database
query = "INSERT INTO discrepancy_log(dis_date, dis_time, timestamp, song, artist, dj_name, word, button_hit, logged_by) \
    VALUES(%(dis_date)s, %(dis_time)s, %(timestamp)s, %(song)s, %(artist)s, %(dj_name)s, %(word)s, %(button_hit)s, 'nobody');"

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
            # print out discrepancy info
            print("\n=== Adding Discrepancy ===")
            print("Song     => " + row['song'])
            print("Artist   => " + row['artist'])
            print("DJ Name  => " + row['dj_name'])
            print("Word     => " + row['word'])
            print("But Hit  => " + row['button_hit'])
            print("TS       => " + row['timestamp'])

            # add discrepancy to db
            cursor.execute(query, row)

except (Exception, psycopg2.DatabaseError) as error :
    print ("Database Error! => ", error)

