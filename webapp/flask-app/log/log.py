# core log module

# import the app
from log import app

# import system libraries
from datetime import datetime, date, time, timedelta

# import Flask libraries
from flask import Flask, jsonify, request
from flask_restful import Resource, Api, reqparse

# import other libraries
import psycopg2

# define the api
api = Api(app)

class LoggingAPI(Resource):


class PlaylistAPI(Resource):


class DiscrepancyAPI(Resource):


# add endpoints for the api
api.add_resource(LoggingAPI, 'api/2.0/log', endpoint = 'log')
api.add_resource(PlaylistAPI, '/api/2.0/playlist', endpoint = 'playlist')
api.add_resource(DiscrepancyAPI, '/api/2.0/discrepancies', endpoint = 'discrepancies')