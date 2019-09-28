# module to fetch the album artwork url for a logged song

# import app
from log import app

# import system libraries
import json

# imports pylast for lastfm api calls
import pylast

def fetchArtwork(artist, album):

    lastfm = pylast.LastFMNetwork(
        api_key       = app.config['LASTFM_API_KEY'],
        api_secret    = app.config['LASTFM_API_SECRET'],
        username      = app.config['LASTFM_USERNAME'],
        password_hash = pylast.md5(app.config['LASTFM_PASSWORD']))

    if album is not "":
        lfm_album = lastfm.get_album(artist, album)
        image = album.get_cover_image()
    else:
        image = "-"
    
    return image
    