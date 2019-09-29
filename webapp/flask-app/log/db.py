# module for working with the database
# all the functions to query the database are in here

# import app
from log import app

# import system libraries
from datetime import datetime, date, time, timedelta
from json import dumps
import secrets

# postgres library
import psycopg2
from psycopg2 import sql
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
            #self.cursor = self.conn.cursor(cursor_factory = RealDictCursor)
            self.cursor = self.conn.cursor()

        except (Exception, psycopg2.DatabaseError) as error :
            print ("Error connecting to database! => ", error)

    # close the db connection
    def close(self):
        if(self.cursor):
            self.cursor.close()
            self.conn.close()

    # JSON serializer for datetime objects
    def __clean_datetime(self, obj):
        if isinstance(obj, (datetime, date)):
            return str(obj)
        raise TypeError ("Type %s not serializable" % type(obj))

    # function to generate a valid key
    def genKey(self):
        key = secrets.token_urlsafe(30)

        if(self.cursor):
            while self.validateKey(key) is True:
                key = secrets.token_urlsafe(30)

            return {'key': key}
        else:
            return False

    # function to validate a supplied key
    def validateKey(self, key):
        query = "SELECT api_key FROM users WHERE api_key = %(key)s;"
        query_args = {'key': key}

        if(self.cursor):
            try:
                # query the database
                self.cursor.execute(query, query_args)
                query_result = self.cursor.fetchall()

                # if the key is found (1 result) then it's valid
                # note that the api_key column has a unique constraint on it
                if len(query_result) is 1:
                    return True
                else:
                    return False
            
            except (Exception, psycopg2.DatabaseError) as error :
                print ("Error executing validateKey query! => ", error)
                return False

    def addSong(self, song):
        now = datetime.now()

        # build the query for the database
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
                # query the database
                self.cursor.execute(query, query_args)
                # also add the song to the songs stats table
                self.addStat(song)
                
                # return the added song
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
        # use -- for entries without an album
        # since a unique entry consists of the song, artist, AND album
        if song.album is "":
            album = "--"
        else:
            album = song.album

        # build the query
        select_query = "SELECT * FROM play_stats \
            WHERE song = %s AND artist = %s AND album = %s;"
        add_query    = "INSERT INTO play_stats(song, artist, album) \
            VALUES(%s, %s, %s);"
        update_query = "UPDATE play_stats SET play_count = (play_count + 1) \
            WHERE song = %s AND artist = %s AND album = %s;"
        query_args = (song.song, song.artist, album)

        try:
            if(self.cursor):
                # query the database
                self.cursor.execute(select_query, query_args)

                # based on the query result either add a new entry or update an existing entry
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

        # build a query
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
                # query the database
                self.cursor.execute(query, query_args)
                
                # return the added discrepancy
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

        # build a query
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
                # query the database
                self.cursor.execute(query)
                
                # return the added request
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

    def getLog(self, type, n, date, delay, desc):

        # current time
        now = datetime.now()

        # start building the query
        query = ""
        end_query_desc = "ORDER BY {} DESC LIMIT %(n)s;"
        end_query_asc = "ORDER BY {} ASC LIMIT %(n)s;"
        query_args = {'n': n}

        # process a request for song logs
        if type is "song":
            order_by = "play_id"
            base_query = "SELECT play_id, timestamp, song, artist, album, genre, location, cd_id, artwork FROM play_log "

            if date is not None:
                date_query = "WHERE play_date = %(date)s "
                query_args['date'] = date

                query = base_query + date_query

            if delay is True:
                delay_query = "WHERE play_time < %(delay_time)s "
                query_args['delay_time'] = (now - timedelta(seconds = 40).strftime('%H:%M:%S'))

                if date is not None:
                    query = query + "AND " + delay_query
                else:
                    query = base_query + delay_query

            # final query
            if date is None or delay is False:
                query = base_query

        # process a request for discrepancy logs
        elif type is "discrepancy":
            order_by = "dis_id"
            base_query = "SELECT dis_id, timestamp, song, artist, dj_name, word, button_hit FROM discrepancy_log "

            if date is not None:
                date_query = "WHERE play_date = %(date)s"
                query_args['date'] = date

                query = base_query + date_query
            else:
                query = base_query

        # process a request for song request logs
        elif type is "request":
            order_by = "rq_id"
            base_query = "SELECT rq_id, timestamp, song, artist, album, rq_name, rq_message FROM song_requests "

            if date is not None:
                date_query = "WHERE rq_date = %(date)s"
                query_args['date'] = date

                query = base_query + date_query
            else:
                query = base_query

        else:
            return False

        # apply the correct ending based on order choice
        if desc is True:
            query = query + end_query_desc
        else:
            query = query + end_query_asc

        if(self.cursor):
            try:
                # execute the query
                self.cursor.execute(
                    sql.SQL(query).format(sql.Identifier(order_by)), 
                    query_args)

                # return the query results
                query_result = self.cursor.fetchall()
                return dumps(query_result, default=self.__clean_datetime)
            
            except (Exception, psycopg2.DatabaseError) as error :
                print ("Error executing log query! => ", error)
                return False

    def getStats(self, song, artist, album, order_by, desc):
        # process a request for song stats
        query = ""
        base_query = "SELECT song_id, song, artist, album, play_count FROM play_stats "
        end_query_desc = "ORDER BY {} DESC;"
        end_query_asc = "ORDER BY {} ASC;"
        query_args = {'order_by': order_by}

        if song is not None:
            song_query = "WHERE song = %(song)s "
            query_args['song'] = song

            query = base_query + song_query
        else:
            query = base_query

        if artist is not None:
            artist_query = "WHERE artist = %(artist)s "
            query_args['artist'] = artist

            if song is not None:
                query = query + "AND " + artist_query
            else:
                query = base_query + artist_query

        if album is not None:
            album_query = "WHERE album = %(album)s "
            query_args['album'] = album

            if song is not None or artist is not None:
                query = query + "AND " + album_query
            else:
                query = base_query + album_query

        # final assembled query
        if song is None and artist is None and album is None:
            query = base_query

        # apply the correct ending based on order choice
        if desc is True:
            query = query + end_query_desc
        else:
            query = query + end_query_asc

        if(self.cursor):
            try:
                # execute the query
                self.cursor.execute(
                    sql.SQL(query).format(sql.Identifier(order_by)), 
                    query_args)

                # return the query results
                query_result = self.cursor.fetchall()
                return dumps(query_result, default=self.__clean_datetime)
            
            except (Exception, psycopg2.DatabaseError) as error :
                print ("Error executing stats query! => ", error)
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
