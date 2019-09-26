# song module to fetch songs from the database

from log import app
from flask import Flask, jsonify, request
import flask_marshmallow as Marshmallow
from datetime import datetime, date, time, timedelta

@log.route('/api/2.0/song', methods=['GET'])
def get_log():

    try:
        # get the number of requested songs from the log
        num = request.args.get('n')
        
        if
        else if num is 'latest' or num is 1:
            # return only the latest song
            return
        else:
            # return the requested number of songs
            return