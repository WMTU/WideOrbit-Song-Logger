# core log module

# import the app
from log import app
from .db import *
from .artwork import *
from .scrobble import *

# import system libraries
from datetime import datetime, date, time, timedelta

# import Flask libraries
from flask import jsonify, request
from flask_restful import Resource, Api, reqparse

# define the api
api = Api(app)

class SongAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()

        # required arguments
        self.reqparse.add_argument('api_key', type = str, required = True, 
            help = 'An API Key is required!', location = 'args')
        self.reqparse.add_argument('song', type = str, required = True, 
            help = 'Song name is required!', location = 'args')
        self.reqparse.add_argument('artist', type = str, required = True, 
            help = 'Artist name is required!', location = 'args')

        # optional arguments
        self.reqparse.add_argument('album', type = str, required = False, 
            default = "", location = 'args')
        self.reqparse.add_argument('genre', type = str, required = False, 
            default = "", location = 'args')
        self.reqparse.add_argument('location', type = str, required = False, 
            default = "CD Library", location = 'args')
        self.reqparse.add_argument('cd_id', type = str, required = False, 
            default = "", location = 'args')

        super(SongAPI, self).__init__()

    def post(self):
        new_song = Song(
            self.reqparse['song'], 
            self.reqparse['artist'], 
            self.reqparse['album'], 
            self.reqparse['genre'], 
            self.reqparse['location'], 
            self.reqparse['cd_id'], 
            fetchArtwork(self.reqparse['artist'], self.reqparse['album']))

        db = DB(
            app.config['DB_USERNAME'], 
            app.config['DB_PASSWORD'], 
            app.config['DB_HOSTNAME'], 
            app.config['DB_PORT'], 
            app.config['DB_DATABASE'])
        db.connect()
        if db.validateKey(self.reqparse['api_key']) is True:
            post_result = db.addSong(new_song)
        db.close()

        return post_result, 202

class DiscrepancyAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()

        # required arguments
        self.reqparse.add_argument('api_key', type = str, required = True, 
            help = 'An API Key is required!', location = 'args')
        self.reqparse.add_argument('song', type = str, required = True, 
            help = 'Song name is required!', location = 'args')
        self.reqparse.add_argument('artist', type = str, required = True, 
            help = 'Artist name is required!', location = 'args')
        self.reqparse.add_argument('dj_name', type = str, required = True, 
            help = 'DJ name is required!', location = 'args')
        self.reqparse.add_argument('word', type = str, required = True, 
            help = 'Word is required!', location = 'args')
        self.reqparse.add_argument('button_hit', type = bool, required = True, 
            help = 'Button press status is required!', location = 'args')

        super(DiscrepancyAPI, self).__init__()

    def post(self):
        new_discrepancy = Discrepancy(
            self.reqparse['api_key'], 
            self.reqparse['song'], 
            self.reqparse['artist'], 
            self.reqparse['dj_name'], 
            self.reqparse['word'], 
            self.reqparse['button_hit'])

        db = DB(
            app.config['DB_USERNAME'], 
            app.config['DB_PASSWORD'], 
            app.config['DB_HOSTNAME'], 
            app.config['DB_PORT'], 
            app.config['DB_DATABASE'])
        db.connect()
        if db.validateKey(self.reqparse['api_key']) is True:
            post_result = db.addDiscrepancy(new_discrepancy)
        db.close()

        return post_result, 202

class RequestAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()

        # required arguments
        self.reqparse.add_argument('api_key', type = str, required = True, 
            help = 'An API Key is required!', location = 'args')
        self.reqparse.add_argument('song', type = str, required = True, 
            help = 'Song name is required!', location = 'args')
        self.reqparse.add_argument('artist', type = str, required = True, 
            help = 'Artist name is required!', location = 'args')

        # optional arguments
        self.reqparse.add_argument('album', type = str, required = False, 
            default = "Any album", location = 'args')
        self.reqparse.add_argument('rq_name', type = str, required = False, 
            default = "WMTU Listener", location = 'args')
        self.reqparse.add_argument('rq_message', type = str, required = False, 
            default = "No message given", location = 'args')

        super(RequestAPI, self).__init__()

    def post(self):
        new_req = Request(
            self.reqparse['song'], 
            self.reqparse['artist'], 
            self.reqparse['album'], 
            self.reqparse['rq_name'], 
            self.reqparse['rq_message'])

        db = DB(
            app.config['DB_USERNAME'], 
            app.config['DB_PASSWORD'], 
            app.config['DB_HOSTNAME'], 
            app.config['DB_PORT'], 
            app.config['DB_DATABASE'])
        db.connect()
        if db.validateKey(self.reqparse['api_key']) is True:
            post_result = db.addRequest(new_req)
        db.close()

        return post_result, 202

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

        super(LogAPI, self).__init__()

    def get(self):
        db = DB(
            app.config['DB_USERNAME'], 
            app.config['DB_PASSWORD'], 
            app.config['DB_HOSTNAME'], 
            app.config['DB_PORT'], 
            app.config['DB_DATABASE'])
        db.connect()
        log_result = db.getLog(self.reqparse['type'], self.reqparse['n'], self.reqparse['delay'], self.reqparse['date'])
        db.close()

        return log_result, 200

# add endpoints for the api
api.add_resource(SongAPI, 'api/2.0/song', endpoint = 'song')
api.add_resource(DiscrepancyAPI, '/api/2.0/discrepancy', endpoint = 'discrepancy')
api.add_resource(RequestAPI, '/api/2.0/request', endpoint = 'request')
api.add_resource(LogAPI, '/api/2.0/log', endpoint = 'log')