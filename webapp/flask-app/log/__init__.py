# Initialize the log module

from flask import Flask
from flask_restful import Api

# Place where app is defined
app = Flask(__name__)

# read the config file
app.config.from_object('config')

from log import log, artwork, scrobble