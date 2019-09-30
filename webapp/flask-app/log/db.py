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
            self.cursor = self.conn.cursor(cursor_factory = RealDictCursor)

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
            while self.validateKey(key) == True:
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
                if len(query_result) == 1:
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
        if song.album == "":
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
                if len(self.cursor.fetchall()) == 0:
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

    def getLog(self, log_type, n, date, delay, desc):

        # current time
        now = datetime.now()

        # start building the query
        query = ""
        query_args = {'n': n}

        # process a log request for a given log_type
        if log_type == "song":
            order_by = "play_id"
            base_query = "SELECT play_id, timestamp, song, artist, album, genre, location, cd_id, artwork FROM play_log "

            if date != "":
                date_query = "WHERE play_date = %(date)s "
                query_args['date'] = date

                query = base_query + date_query

            if delay == True:
                delay_query = "WHERE play_time < %(delay_time)s "
                query_args['delay_time'] = (now - timedelta(seconds = 40).strftime('%H:%M:%S'))

                if date != "":
                    query = query + "AND " + delay_query
                else:
                    query = base_query + delay_query

            if date == "" and delay == False:
                query = base_query
        elif log_type == "discrepancy":
            order_by = "dis_id"
            base_query = "SELECT dis_id, timestamp, song, artist, dj_name, word, button_hit FROM discrepancy_log "

            if date != "":
                date_query = "WHERE play_date = %(date)s"
                query_args['date'] = date

                query = base_query + date_query
            else:
                query = base_query
        elif log_type == "request":
            order_by = "rq_id"
            base_query = "SELECT rq_id, timestamp, song, artist, album, rq_name, rq_message FROM song_requests "

            if date != "":
                date_query = "WHERE rq_date = %(date)s"
                query_args['date'] = date

                query = base_query + date_query
            else:
                query = base_query
        else:
            return False

        # apply the row order
        if desc == True:
            query = query + "ORDER BY {} DESC "
        else:
            query = query + "ORDER BY {} ASC "

        # apply the correct limit
        if date != "":
            query = query + "LIMIT ALL;"
        else:
            query = query + "LIMIT %(n)s;"

        if(self.cursor):
            try:
                # execute the query
                self.cursor.execute(
                    sql.SQL(query).format(sql.Identifier(order_by)), query_args)

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
        query_args = {'order_by': order_by}

        if song != "":
            song_query = "WHERE %(song)s %% ANY(STRING_TO_ARRAY(song,' ')) "
            query_args['song'] = song

            query = base_query + song_query
        else:
            query = base_query

        if artist != "":
            artist_query = "WHERE %(artist)s %% ANY(STRING_TO_ARRAY(artist,' ')) "
            query_args['artist'] = artist

            if song != "":
                query = query + "AND " + artist_query
            else:
                query = base_query + artist_query

        if album != "":
            album_query = "WHERE %(album)s %% ANY(STRING_TO_ARRAY(album,' ')) "
            query_args['album'] = album

            if song != "" or artist != "":
                query = query + "AND " + album_query
            else:
                query = base_query + album_query

        if song == "" and artist == "" and album == "":
            query = base_query

        # apply the row order
        if desc == True:
            query = query + "ORDER BY {} DESC;"
        else:
            query = query + "ORDER BY {} ASC;"

        if(self.cursor):
            try:
                # execute the query
                self.cursor.execute(
                    sql.SQL(query).format(sql.Identifier(order_by)), query_args)

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
