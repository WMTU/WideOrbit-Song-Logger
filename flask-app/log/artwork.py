# module to fetch the album artwork url for a logged song

# import app
from log import app

# imports pylast for lastfm api calls
import pylast

def fetchArtwork(artist, album):

    lastfm = pylast.LastFMNetwork(
        api_key       = app.config['LASTFM_API_KEY'],
        api_secret    = app.config['LASTFM_API_SECRET'],
        username      = app.config['LASTFM_USERNAME'],
        password_hash = pylast.md5(app.config['LASTFM_PASSWORD']))

    image = ""

    if album != "":
        try:
            lfm_album = lastfm.get_album(artist, album)
            image = str(lfm_album.get_cover_image())
        
        except (Exception, pylast.WSError) as error :
            print ("Error fetching album artwork! => ", error)
    
    if image == "None":
        image = ""

    return image
    