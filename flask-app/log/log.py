# core log module
# this module defines the API endpoints and arguments

# import the app
from log import app
from .db import *
from .artwork import *
from .scrobble import *

# import system libraries
from datetime import datetime, date, time
from json import loads, dumps

# import Flask libraries
from flask import jsonify, request
from flask_restful import Resource, Api, reqparse

# import webargs argument handling for flask-restful
from webargs import fields, validate
from webargs.flaskparser import use_args, use_kwargs, parser, abort

# define the api
api = Api(app)

# API for logging songs
class SongAPI(Resource):
    def __init__(self):

        self.api_args = {
            "api_key":  fields.Str(required=True, location="json"),
            "song":     fields.Str(required=True, location="json"),
            "artist":   fields.Str(required=True, location="json"),
            "album":    fields.Str(required=False, location="json", missing=""),
            "genre":    fields.Str(required=False, location="json", missing=""),
            "location": fields.Str(required=False, location="json", missing="CD Library"),
            "cd_id":    fields.Str(required=False, location="json", missing="")
        }

        self.args = parser.parse(self.api_args, request)

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
        api_user = loads(db.validateKey(self.args['api_key']))
        if api_user != False:
            if new_song.artist != "WMTU":
                # add song log to the db
                post_result = db.addSong(new_song, api_user[0]['username'])
                message, code = post_result, 202

                # publish the song to scrobble sources
                if app.config['SCROBBLE'] == "True":
                    scrobbleSong(datetime.now().strftime("%s"), new_song)
            else:
                message, code = {"message": {"WMTU": "Not logging song tagged with WMTU artist!"}}, 202
        else:
            message, code = {"message": {"api_key": "Invalid API Key!"}}, 400
        
        # close the database connection
        db.close()

        # return the logged song
        if post_result == False:
            message, code = {"message": {"error": "Error submitting Song!"}}, 500

        return message, code

class DiscrepancyAPI(Resource):
    def __init__(self):

        self.api_args = {
            "api_key":      fields.Str(required=True, location="json"),
            "song":         fields.Str(required=True, location="json"),
            "artist":       fields.Str(required=True, location="json"),
            "dj_name":      fields.Str(required=True, location="json"),
            "word":         fields.Str(required=True, location="json"),
            "button_hit":   fields.Bool(required=True, location="json")
        }

        self.args = parser.parse(self.api_args, request)

        super(DiscrepancyAPI, self).__init__()

    def post(self):
        post_result = None

        # build a new Discrepancy object
        new_discrepancy = Discrepancy(
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
        api_user = loads(db.validateKey(self.args['api_key']))
        if api_user != False:
            post_result = db.addDiscrepancy(new_discrepancy, api_user[0]['username'])
            message, code = post_result, 202
        else:
            message, code = {"message": {"api_key": "Invalid API Key!"}}, 400
        
        # close the database connection
        db.close()

        # return the logged discrepancy
        if post_result == False:
            message, code = {"message": {"error": "Error submitting Discrepancy!"}}, 500

        return message, code

class RequestAPI(Resource):
    def __init__(self):

        self.api_args = {
            "api_key":      fields.Str(required=True, location="json"),
            "song":         fields.Str(required=False, location="json", missing="-"),
            "artist":       fields.Str(required=False, location="json", missing="-"),
            "album":        fields.Str(required=False, location="json", missing="-"),
            "rq_name":      fields.Str(required=False, location="json", missing="WMTU Listener"),
            "rq_message":   fields.Str(required=False, location="json", missing="No Message Given"),
        }

        self.args = parser.parse(self.api_args, request)

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
        api_user = loads(db.validateKey(self.args['api_key']))
        if api_user != False:
            post_result = db.addRequest(new_req, api_user[0]['username'])
            message, code = post_result, 202
        else:
            message, code = {"message": {"api_key": "Invalid API Key!"}}, 400
        
        # close the connection to the database
        db.close()

        # return the logged request
        if post_result == False:
            message, code = {"message": {"error": "Error submitting Request!"}}, 500

        return message, code

class LogAPI(Resource):
    # helper function to validate a date
    def __date_validator(self, date):
        try:
            datetime.strptime(date, "%Y-%m-%d")
            return True
        except (Exception, ValueError) as error:
            return False

    def __init__(self):

        self.api_args = {
            "type":     fields.Str(required=False, location="query", 
                validate=validate.OneOf(choices=["song", "discrepancy", "request"],
                error="Invalid Type Provided!"),
                missing="song"),
            "n":        fields.Int(required=False, location="query", missing=1),
            "delay":    fields.Bool(required=False, location="query", missing=False),
            "date":     fields.Str(required=False, location="query", 
                validate=self.__date_validator, missing=""),
            "desc":     fields.Bool(required=False, location="query", missing=True)
        }

        self.args = parser.parse(self.api_args, request)

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
        log_result = db.getLog(self.args['type'], self.args['n'], self.args['date'], self.args['delay'], int(app.config['DELAY_TIME']), self.args['desc'])
        message, code = loads(log_result), 200
        
        # close the connection to the database
        db.close()

        # return the requested log(s)
        if log_result == False:
            message, code = {"message": {"error": "Error fetching log!"}}, 500

        return message, code

class StatsAPI(Resource):
    def __init__(self):

        self.api_args = {
            "n":        fields.Int(required=False, location="query", missing=0),
            "song":     fields.Str(required=False, location="query", missing=""),
            "artist":   fields.Str(required=False, location="query", missing=""),
            "album":    fields.Str(required=False, location="query", missing=""),
            "order_by": fields.Str(required=False, location="query", missing="play_count",
                validate=validate.OneOf(choices=["song", "artist", "album", "play_count"],
                error="Invalid Value for Argument 'order_by'")),
            "desc":     fields.Bool(required=False, location="query", missing=True),
        }

        self.args = parser.parse(self.api_args, request)

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
        stats_result = db.getStats(self.args['n'], self.args['song'], self.args['artist'], self.args['album'], self.args['order_by'], self.args['desc'])
        message, code = loads(stats_result), 200
        
        # close the connection to the database
        db.close()

        # return the requested log(s)
        if stats_result == False:
            message, code = {"message": {"error": "Error fetching stats!"}}, 500

        return message, code

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
        message, code = key_result, 200

        # close the connection to the database
        db.close()

        # return the generated key
        if key_result == False:
            message, code = {"message": {"error": "Error generating key!"}}, 500

        return message, code

# This error handler is necessary for usage with Flask-RESTful
@parser.error_handler
def handle_request_parsing_error(err, req, schema, error_status_code, error_headers):
    """webargs error handler that uses Flask-RESTful's abort function to return
    a JSON error response to the client.
    """
    abort(error_status_code, errors=err.messages)

# add endpoints for the api
api.add_resource(SongAPI,           '/api/2.0/song',        endpoint = 'song')
api.add_resource(DiscrepancyAPI,    '/api/2.0/discrepancy', endpoint = 'discrepancy')
api.add_resource(RequestAPI,        '/api/2.0/request',     endpoint = 'request')
api.add_resource(LogAPI,            '/api/2.0/log',         endpoint = 'log')
api.add_resource(StatsAPI,          '/api/2.0/stats',       endpoint = 'stats')

if app.config['KEY_API'] == "True":
    api.add_resource(KeyAPI, '/api/2.0/key', endpoint = 'key')