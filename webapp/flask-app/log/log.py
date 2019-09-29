# core log module
# this module defines the API endpoints and arguments

# import the app
from log import app
from .db import *
from .artwork import *
from .scrobble import *

# import system libraries
from datetime import datetime, date, time
from json import loads

# import Flask libraries
from flask import jsonify, request
from flask_restful import Resource, Api, reqparse

# define the api
api = Api(app)

# API for logging songs
class SongAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()

        # required arguments
        self.reqparse.add_argument('api_key', type = str, required = True, 
            help = 'An API Key is required!', location = 'json')
        self.reqparse.add_argument('song', type = str, required = True, 
            help = 'Song name is required!', location = 'json')
        self.reqparse.add_argument('artist', type = str, required = True, 
            help = 'Artist name is required!', location = 'json')

        # optional arguments
        self.reqparse.add_argument('album', type = str, required = False, 
            default = "", location = 'json')
        self.reqparse.add_argument('genre', type = str, required = False, 
            default = "", location = 'json')
        self.reqparse.add_argument('location', type = str, required = False, 
            default = "CD Library", location = 'json')
        self.reqparse.add_argument('cd_id', type = str, required = False, 
            default = "", location = 'json')

        self.args = self.reqparse.parse_args()

        super(SongAPI, self).__init__()

    # API takes a POST request
    def post(self):
        post_result = None

        # build a new Song object
        new_song = Song(
            self.args['song'], 
            self.args['artist'], 
            self.args['album'], 
            self.args['genre'], 
            self.args['location'], 
            self.args['cd_id'], 
            fetchArtwork(self.args['artist'], self.args['album']))

        # build a new DB object and connect to the database
        db = DB(
            app.config['DB_USERNAME'], 
            app.config['DB_PASSWORD'], 
            app.config['DB_HOSTNAME'], 
            app.config['DB_PORT'], 
            app.config['DB_DATABASE'])
        db.connect()

        # validate the API key and add the song log
        if db.validateKey(self.args['api_key']) is True:
            # add song log to the db
            post_result = db.addSong(new_song)

            # publish the song to scrobble sources
            if app.config['SCROBBLE'] is "True":
                scrobbleSong(datetime.datetime.utcnow().strftime("%s"), new_song)
        else:
            return "Invalid API Key!", 400
        
        # close the database connection
        db.close()

        # return the logged song
        if post_result is not False:
            return post_result, 202
        else:
            return "Error submitting Song!", 500

class DiscrepancyAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()

        # required arguments
        self.reqparse.add_argument('api_key', type = str, required = True, 
            help = 'An API Key is required!', location = 'json')
        self.reqparse.add_argument('song', type = str, required = True, 
            help = 'Song name is required!', location = 'json')
        self.reqparse.add_argument('artist', type = str, required = True, 
            help = 'Artist name is required!', location = 'json')
        self.reqparse.add_argument('dj_name', type = str, required = True, 
            help = 'DJ name is required!', location = 'json')
        self.reqparse.add_argument('word', type = str, required = True, 
            help = 'Word is required!', location = 'json')
        self.reqparse.add_argument('button_hit', type = bool, required = True, 
            help = 'Button press status is required!', location = 'json')

        self.args = self.reqparse.parse_args()

        super(DiscrepancyAPI, self).__init__()

    def post(self):
        post_result = None

        # build a new Discrepancy object
        new_discrepancy = Discrepancy(
            self.args['api_key'], 
            self.args['song'], 
            self.args['artist'], 
            self.args['dj_name'], 
            self.args['word'], 
            self.args['button_hit'])

        # build a DB object and connect to the database
        db = DB(
            app.config['DB_USERNAME'], 
            app.config['DB_PASSWORD'], 
            app.config['DB_HOSTNAME'], 
            app.config['DB_PORT'], 
            app.config['DB_DATABASE'])
        db.connect()

        # validate the API key and log the discrepancy
        if db.validateKey(self.args['api_key']) is True:
            post_result = db.addDiscrepancy(new_discrepancy)
        else:
            return "Invalid API Key!", 400
        
        # close the database connection
        db.close()

        # return the logged discrepancy
        if post_result is not False:
            return post_result, 202
        else:
            return "Error submitting Discrepancy!", 500

class RequestAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()

        # required arguments
        self.reqparse.add_argument('api_key', type = str, required = True, 
            help = 'An API Key is required!', location = 'json')
        self.reqparse.add_argument('song', type = str, required = True, 
            help = 'Song name is required!', location = 'json')
        self.reqparse.add_argument('artist', type = str, required = True, 
            help = 'Artist name is required!', location = 'json')

        # optional arguments
        self.reqparse.add_argument('album', type = str, required = False, 
            default = "Any album", location = 'json')
        self.reqparse.add_argument('rq_name', type = str, required = False, 
            default = "WMTU Listener", location = 'json')
        self.reqparse.add_argument('rq_message', type = str, required = False, 
            default = "No message given", location = 'json')

        self.args = self.reqparse.parse_args()

        super(RequestAPI, self).__init__()

    def post(self):
        post_result = None

        # build a new Request object
        new_req = Request(
            self.args['song'], 
            self.args['artist'], 
            self.args['album'], 
            self.args['rq_name'], 
            self.args['rq_message'])

        # build a new DB object and connect to the database
        db = DB(
            app.config['DB_USERNAME'], 
            app.config['DB_PASSWORD'], 
            app.config['DB_HOSTNAME'], 
            app.config['DB_PORT'], 
            app.config['DB_DATABASE'])
        db.connect()

        # validate the API key and log the request
        if db.validateKey(self.args['api_key']) is True:
            post_result = db.addRequest(new_req)
        else:
            return "Invalid API Key!", 400
        
        # close the connection to the database
        db.close()

        # return the logged request
        if post_result is not False:
            return post_result, 202
        else:
            return "Error submitting Request!", 500

class LogAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()

        # optional arguments
        self.reqparse.add_argument('type', type = str, required = False, 
            default = "song", location = 'args')
        self.reqparse.add_argument('n', type = int, required = False, 
            default = 1, location = 'args')
        self.reqparse.add_argument('delay', type = bool, required = False, 
            default = False, location = 'args')
        self.reqparse.add_argument('date', type = str, required = False, 
            default = None, location = 'args')
        self.reqparse.add_argument('desc', type = bool, required = False, 
            default = True, location = 'args')

        self.args = self.reqparse.parse_args()

        super(LogAPI, self).__init__()

    def get(self):
        log_result = None

        # build a new DB object and connect to the database
        db = DB(
            app.config['DB_USERNAME'], 
            app.config['DB_PASSWORD'], 
            app.config['DB_HOSTNAME'], 
            app.config['DB_PORT'], 
            app.config['DB_DATABASE'])
        db.connect()

        # get the requested log(s) from the database
        log_result = db.getLog(self.args['type'], self.args['n'], self.args['date'], self.args['delay'], self.args['desc'])
        
        # close the connection to the database
        db.close()

        # return the requested log(s)
        if log_result is not False:
            return loads(log_result), 200
        else:
            return "Error fetching log!", 500

class StatsAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()

        # optional arguments
        self.reqparse.add_argument('song', type = str, required = False, 
            default = None, location = 'args')
        self.reqparse.add_argument('artist', type = str, required = False, 
            default = None, location = 'args')
        self.reqparse.add_argument('album', type = str, required = False, 
            default = None, location = 'args')
        self.reqparse.add_argument('order_by', type = str, required = False, 
            default = "play_count", location = 'args')
        self.reqparse.add_argument('desc', type = bool, required = False, 
            default = True, location = 'args')

        self.args = self.reqparse.parse_args()

        super(StatsAPI, self).__init__()

    def get(self):
        stats_result = None

        # build a new DB object and connect to the database
        db = DB(
            app.config['DB_USERNAME'], 
            app.config['DB_PASSWORD'], 
            app.config['DB_HOSTNAME'], 
            app.config['DB_PORT'], 
            app.config['DB_DATABASE'])
        db.connect()

        # get the requested log(s) from the database
        stats_result = db.getStats(self.args['song'], self.args['artist'], self.args['album'], self.args['order_by'], self.args['desc'])
        
        # close the connection to the database
        db.close()

        # return the requested log(s)
        if stats_result is not False:
            return loads(stats_result), 200
        else:
            return "Error fetching stats!", 500

class KeyAPI(Resource):
    def get(self):
        key_result = None

        # build a new DB object and connect to the database
        db = DB(
            app.config['DB_USERNAME'], 
            app.config['DB_PASSWORD'], 
            app.config['DB_HOSTNAME'], 
            app.config['DB_PORT'], 
            app.config['DB_DATABASE'])
        db.connect()

        # generate a new key
        key_result = db.genKey()

        # close the connection to the database
        db.close()

        # return the generated key
        if key_result is not False:
            return key_result, 200
        else:
            return "Error generating key!", 500

# add endpoints for the api
api.add_resource(SongAPI,           '/api/2.0/song',        endpoint = 'song')
api.add_resource(DiscrepancyAPI,    '/api/2.0/discrepancy', endpoint = 'discrepancy')
api.add_resource(RequestAPI,        '/api/2.0/request',     endpoint = 'request')
api.add_resource(LogAPI,            '/api/2.0/log',         endpoint = 'log')
api.add_resource(StatsAPI,          '/api/2.0/stats',       endpoint = 'stats')

if app.config['KEY_API'] is "True":
    api.add_resource(KeyAPI, '/api/2.0/key', endpoint = 'key')