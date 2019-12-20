# Initialize the log module

from flask import Flask

# Place where app is defined
app = Flask(__name__)

# read the config file
app.config.from_object('config')

from log import log, db, artwork, scrobble