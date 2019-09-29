# module for working with the database

# import app
from log import app

# import system libraries
from datetime import datetime, date, time, timedelta
import secrets

# postgres library
import psycopg2
from psycopg2.extras import RealDictCursor

class DB:

    # initialize the class with the database connection info
    def __init__(self, username, password, hostname, port, database):
        self.username = username
        self.password = password
        self.hostname = hostname
        self.port     = port
        self.database = database

    # connect to the database
    # this must be done first before doing anything else
    def connect(self):
        try:
            self.conn = psycopg2.connect(
                user        = self.username,
                password    = self.password,
                host        = self.hostname,
                port        = self.port,
                database    = self.database
            )
            self.conn.set_session(autocommit = True)
            self.cursor = self.conn.cursor(cursor_factory = RealDictCursor)

        except (Exception, psycopg2.DatabaseError) as error :
            print ("Error connecting to database! => ", error)

    # close the db connection
    def close(self):
        if(self.cursor):
            self.cursor.close()
            self.conn.close()

    def genKey(self):
        key = secrets.token_urlsafe(30)

        if(self.cursor):
            while self.validateKey(key) is True:
                key = secrets.token_urlsafe(30)

            return {'key': key}
        else:
            return False

    def validateKey(self, key):
        query = "SELECT api_key FROM users WHERE api_key = %s;"

        if(self.cursor):
            try:
                self.cursor.execute(query, key)
                query_result = self.cursor.fetchall()
                if len(query_result) is 1:
                    return True
                else:
                    return False
            
            except (Exception, psycopg2.DatabaseError) as error :
                print ("Error executing validateKey query! => ", error)
                return False

    def addSong(self, song):
        now = datetime.now()

        query = "INSERT INTO play_log(play_date, play_time, timestamp, song, artist, album, genre, location, cd_id, artwork) \
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"

        query_args = (
            now.strftime('%Y-%m-%d'), 
            now.strftime('%H:%M:%S'), 
            now.strftime('%Y-%m-%d %H:%M:%S'), 
            song.song, 
            song.artist, 
            song.album, 
            song.genre, 
            song.location, 
            song.cd_id, 
            song.artwork)

        if(self.cursor):
            try:
                self.cursor.execute(query, query_args)
                self.addStat(song)
                return {
                    'timestamp': now.strftime('%Y-%m-%d %H:%M:%S'),
                    'song': song.song, 
                    'artist': song.artist, 
                    'album': song.album, 
                    'genre': song.genre, 
                    'location': song.location,
                    'cd_id': song.cd_id,
                    'artwork': song.artwork}

            except (Exception, psycopg2.DatabaseError) as error :
                print ("Error executing addSong query! => ", error)
                return False
        else:
            return False

    def addStat(self, song):
        if song.album is "":
            album = "--"
        else:
            album = song.album

        select_query = "SELECT * FROM play_stats \
            WHERE song = %s AND artist = %s AND album = %s;"
        add_query    = "INSERT INTO play_stats(song, artist, album) \
            VALUES(%s, %s, %s);"
        update_query = "UPDATE play_stats SET play_count = (play_count + 1) \
            WHERE song = %s AND artist = %s AND album = %s;"
        query_args = (song.song, song.artist, album)

        try:
            if(self.cursor):
                self.cursor.execute(select_query, query_args)
                if len(self.cursor.fetchall()) is 0:
                    self.cursor.execute(add_query, query_args)
                else:
                    self.cursor.execute(update_query, query_args)
                
                return True
            else:
                return False

        except (Exception, psycopg2.DatabaseError) as error :
            print ("Error executing addStat query! => ", error)
            return False

    def addDiscrepancy(self, discrepancy):
        now = datetime.now()

        query = "INSERT INTO discrepancy_log(play_date, play_time, timestamp, song, artist, dj_name, word, button_hit) \
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s);"

        query_args = (
            now.strftime('%Y-%m-%d'), 
            now.strftime('%H:%M:%S'), 
            now.strftime('%Y-%m-%d %H:%M:%S'), 
            discrepancy.song, 
            discrepancy.artist, 
            discrepancy.dj_name, 
            discrepancy.word, 
            discrepancy.button_hit)

        try:
            if(self.cursor):
                self.cursor.execute(query, query_args)
                return {
                    'timestamp': now.strftime('%Y-%m-%d %H:%M:%S'),
                    'song': discrepancy.song, 
                    'artist': discrepancy.artist, 
                    'dj_name': discrepancy.dj_name,
                    'word': discrepancy.word,
                    'button_hit': discrepancy.button_hit}
            else:
                return False

        except (Exception, psycopg2.DatabaseError) as error :
            print ("Error executing addDiscrepancy query! => ", error)
            return False

    def addRequest(self, request):
        now = datetime.now()

        query = "INSERT INTO song_requests(rq_date, rq_time, timestamp, song, artist, album, rq_name, rq_message) \
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s);"

        query_args = (
            now.strftime('%Y-%m-%d'), 
            now.strftime('%H:%M:%S'), 
            now.strftime('%Y-%m-%d %H:%M:%S'), 
            request.song, 
            request.artist, 
            request.album, 
            request.rq_name, 
            request.rq_message)

        try:
            if(self.cursor):
                self.cursor.execute(query)
                return {
                    'timestamp': now.strftime('%Y-%m-%d %H:%M:%S'),
                    'song': request.song,
                    'artist': request.artist,
                    'album': request.album,
                    'rq_name': request.rq_name,
                    'rq_message': request.rq_message}
            else:
                return False

        except (Exception, psycopg2.DatabaseError) as error :
            print ("Error executing addRequest query! => ", error)
            return False

    def getLog(self, type, n, date, delay):

        # current time
        now = datetime.now()

        end_query = " ORDER BY play_id DESC LIMIT %(n)s;"
        query_args = {'n': n}

        if type is "song":
            base_query = "SELECT play_id, timestamp, song, artist, album, genre, location, cd_id, artwork FROM play_log "
            date_query = None
            delay_query = None

            if date is not None:
                date_query = "WHERE play_date = %(date)s"
                query_args['date'] = date

            if delay is True:
                delay_query = "WHERE play_time < %(delay_time)s"
                query_args['delay_time'] = now - timedelta(seconds = 40).strftime('%H:%M:%S')

            if date_query is not None and delay_query is not None:
                query = base_query + date_query + " AND " + delay_query + end_query
            elif date_query is not None and not delay_query is None:
                query = base_query + date_query + end_query
            elif delay_query is not None and not date_query is None:
                query = base_query + delay_query + end_query
            else:
                query = base_query + end_query

        elif type is "discrepancy":
            base_query = "SELECT dis_count, timestamp, song, artist, dj_name, word, button_hit FROM discrepancy_log "

            if date is not None:
                date_query = "WHERE play_date = %(date)s"
                query_args['date'] = date

            if date_query is not None:
                query = base_query + date_query + end_query
            else:
                query = base_query + end_query

        elif type is "request":
            base_query = "SELECT rq_id, timestamp, song, artist, album, rq_name, rq_message FROM song_requests "

            if date is not None:
                date_query = "WHERE play_date = %(date)s"
                query_args['date'] = date

            if date_query is not None:
                query = base_query + date_query + end_query
            else:
                query = base_query + end_query
        else:
            return False

        if(self.cursor):
            try:
                self.cursor.execute(query, query_args)
                query_result = self.cursor.fetchall()
                return query_result
            
            except (Exception, psycopg2.DatabaseError) as error :
                print ("Error executing query! => ", error)
                return False


############################################
# Object classes for passing to DB functions
############################################

class Song:
    def __init__(self, song, artist, album, genre, location, cd_id, artwork):
        self.song       = song
        self.artist     = artist
        self.album      = album
        self.genre      = genre
        self.location   = location
        self.cd_id      = cd_id
        self.artwork    = artwork

class Discrepancy:
    def __init__(self, song, artist, dj_name, word, button_hit):
        self.song       = song
        self.artist     = artist
        self.dj_name    = dj_name
        self.word       = word
        self.button_hit = button_hit

class Request:
    def __init__(self, song, artist, album, rq_name, rq_message):
        self.song       = song
        self.artist     = artist
        self.album      = album
        self.rq_name    = rq_name
        self.rq_message = rq_message
