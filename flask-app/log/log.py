# core log module
# this module defines the API endpoints and arguments

# import the app
from log import app
from .db import *
from .artwork import *
from .scrobble import *

# import system libraries
from datetime import datetime, date, time
from json import loads, dumps, dump
import io, os, sys

# import Flask libraries
from flask import jsonify, request, make_response, abort
from flask import send_file, send_from_directory, safe_join
from flask_restful import Resource, Api, reqparse

# import webargs argument handling for flask-restful
from webargs import fields, validate
from webargs.flaskparser import use_args, use_kwargs, parser, abort

# import pandas (lol) to convert json to csv
import pandas as pd

# define the api
api = Api(app)

# API for logging songs
class SongAPI(Resource):
    
    def __init__(self):

        self.api_args = {
            "api_key":  fields.Str(required=True),
            "song":     fields.Str(required=True),
            "artist":   fields.Str(required=True),
            "album":    fields.Str(required=False, missing=""),
            "genre":    fields.Str(required=False, missing=""),
            "location": fields.Str(required=False, missing="CD Library"),
            "cd_id":    fields.Str(required=False, missing="")
        }

        self.args = parser.parse(self.api_args, request, location="json")

        super(SongAPI, self).__init__()

    # API takes a POST request
    def post(self):

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
            "api_key":      fields.Str(required=True),
            "song":         fields.Str(required=True),
            "artist":       fields.Str(required=True),
            "dj_name":      fields.Str(required=True),
            "word":         fields.Str(required=True),
            "button_hit":   fields.Bool(required=True)
        }

        self.args = parser.parse(self.api_args, request, location="json")

        super(DiscrepancyAPI, self).__init__()

    def post(self):

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
            "api_key":      fields.Str(required=False, missing=app.config['PUB_KEY']),
            "song":         fields.Str(required=True),
            "artist":       fields.Str(required=True),
            "album":        fields.Str(required=False, missing="-"),
            "rq_name":      fields.Str(required=False, missing="Anonymous"),
            "rq_message":   fields.Str(required=False, missing="None"),
        }

        self.args = parser.parse(self.api_args, request, location="json")

        super(RequestAPI, self).__init__()

    def post(self):

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

    # helper function to validate a timestamp
    # note that this is basically the same as the date validator
    # except timestamps can also include date AND time
    def __ts_validator(self, date):
        try:
            datetime.strptime(date, "%Y-%m-%d")
            return True
        
        except (Exception, ValueError) as error:
            try:
                datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                return True
            
            except (Exception, ValueError) as error:
                return False

            return False

    def __init__(self):

        self.api_args = {
            "type":     fields.Str(required=False, 
                validate=validate.OneOf(choices=["song", "discrepancy", "request"],
                error="Invalid Type Provided!"),
                missing="song"),
            "n":        fields.Int(required=False, missing=1),
            "delay":    fields.Bool(required=False, missing=False),
            "date":     fields.Str(required=False, validate=self.__date_validator, missing=""),
            "ts_start": fields.Str(required=False, validate=self.__ts_validator, missing=""),
            "ts_end":   fields.Str(required=False, validate=self.__ts_validator, missing=""),
            "desc":     fields.Bool(required=False, missing=True),
            "format":   fields.Str(required=False, 
                validate=validate.OneOf(choices=["json", "csv"], 
                error="Invalid return format!"),
                missing="json")
        }

        self.args = parser.parse(self.api_args, request, location="query")

        super(LogAPI, self).__init__()

    def get(self):

        # validate date and timestamp selections
        # only allow a date OR a timestamp selection
        # if valid then check provided values and reformat as needed
        # note that we have already done some initial validation as part of the request
        if self.args['date'] != "" and (self.args['ts_start'] != "" or self.args['ts_end'] != ""):
            return {"message": {"error": "Please provide either a date OR a timestamp!"}}, 500
        elif self.args['ts_start'] != "" and self.args['ts_end'] == "":
            return {"message": {"error": "Please provide an ending timestamp!"}}, 500
        elif self.args['ts_start'] == "" and self.args['ts_end'] != "":
            return {"message": {"error": "Please provide a starting timestamp!"}}, 500
        elif self.args['date'] != "" or self.args['ts_start'] != "":
            # turn a date into a timestamp
            if self.args['date'] != "":
                self.args['ts_start'] = self.args['date']
                self.args['ts_end'] = self.args['date']

            # reformat timestamps as needed
            # timestamps will either be dates or date & time
            # ultimately we need a date & time
            try:
                datetime.strptime(self.args['ts_start'], "%Y-%m-%d %H:%M:%S")
            except (Exception, ValueError) as error:
                self.args['ts_start'] = self.args['ts_start'] + " 00:00:00"

            try:
                datetime.strptime(self.args['ts_end'], "%Y-%m-%d %H:%M:%S")
            except (Exception, ValueError) as error:
                self.args['ts_end'] = self.args['ts_end'] + " 23:59:59"

            # validate start ts comes before the end ts
            # the timestamps should already be validated (lol like 3 times)
            try:
                ts_start = datetime.strptime(self.args['ts_start'], "%Y-%m-%d %H:%M:%S").timestamp()
                ts_end   = datetime.strptime(self.args['ts_end'], "%Y-%m-%d %H:%M:%S").timestamp()
            except (Exception, ValueError) as error:
                return {"message": {"error": "Error processing your timestamps!"}}, 500
            if ts_start >= ts_end:
                return {"message": {"error": "Starting timestamp must be BEFORE the ending timestamp!"}}, 500

        # build a new DB object and connect to the database
        db = DB(
            app.config['DB_USERNAME'], 
            app.config['DB_PASSWORD'], 
            app.config['DB_HOSTNAME'], 
            app.config['DB_PORT'], 
            app.config['DB_DATABASE'])
        db.connect()

        # get the requested log(s) from the database
        log_result = db.getLog(
            self.args['type'], 
            self.args['n'], 
            self.args['ts_start'], 
            self.args['ts_end'], 
            self.args['delay'], 
            int(app.config['DELAY_TIME']), 
            self.args['desc'])

        # close the connection to the database
        db.close()

        # return the requested log(s)
        if log_result == False:
            return {"message": {"error": "Error fetching log!"}}, 500
        else:
            if self.args['format'] == "json":
                return loads(log_result), 200
            else:
                # create a new file for the csv formatted data
                filename = "log_" + str(datetime.now().timestamp()).replace('.', '') + ".csv"
                csv_path = app.config['TMP_STOR'] + filename
                try:
                    csv_file = open(csv_path, 'w')
                except FileNotFoundError:
                    #print("Unable to create file: " + csv_path)
                    return {"message": {"error": "Error creating CSV file!"}}, 500

                # format data from the db as csv
                # put the csv data into the csv file
                df = pd.read_json(log_result, orient="records")
                df.to_csv(csv_file, index=False)
                csv_file.close()
                
                # send the generated file to the user
                try:
                    return send_file(csv_path, mimetype='text/csv', as_attachment=True)
                except FileNotFoundError:
                    message, code = {"message": {"error": "File not found!"}}, 404
                finally:
                    # remove the file
                    os.unlink(csv_path)

class StatsAPI(Resource):
    
    def __init__(self):

        self.api_args = {
            "n":        fields.Int(required=False, missing=1),
            "song":     fields.Str(required=False, missing=""),
            "artist":   fields.Str(required=False, missing=""),
            "album":    fields.Str(required=False, missing=""),
            "order_by": fields.Str(required=False, missing="play_count",
                validate=validate.OneOf(choices=["song", "artist", "album", "play_count"],
                error="Invalid Value for Argument 'order_by'")),
            "desc":     fields.Bool(required=False, missing=True),
        }

        self.args = parser.parse(self.api_args, request, location="query")

        super(StatsAPI, self).__init__()

    def get(self):

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