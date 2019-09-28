# module to publish the logged song to services

# import the app
from log import app

# import system libraries
import base64
import urllib, urllib.parse, urllib.request

# import pylast for lastfm api calls
import pylast

# Icecast Info
ic_url = app.config['ICECAST_SERVER_URL'] + "/admin/metadata"
ic_auth = base64.encodestring('%s:%s' % (app.config['ICECAST_USERNAME'], app.config['ICECAST_PASSWORD'])).replace('\n', '')

# LastFM API Info
lastfm = pylast.LastFMNetwork(
        api_key       = app.config['LASTFM_API_KEY'],
        api_secret    = app.config['LASTFM_API_SECRET'],
        username      = app.config['LASTFM_USERNAME'],
        password_hash = pylast.md5(app.config['LASTFM_PASSWORD']))

# TuneIn API Info
ti_query = {
        'partnerId':  app.config['TUNEIN_PARTNER_ID'],
        'partnerKey': app.config['TUNEIN_PARTNER_KEY'],
        'id':         app.config['TUNEIN_STATION_ID']}

# takes the played song and publishes it to various places
def scrobbleSong(song, artist, album, timestamp):
    
    # push song to Icecast
    ic_query = {'mode': 'updinfo', 'song': artist + " | " + song}
    for m in app.config['ICECAST_MOUNTPOINTS']:
        ic_query['mount'] = m
        ic_url_m = ic_url + '?' + urllib.parse.urlencode(ic_query)
        ic_request = urllib.request.Request(ic_url_m)

        # add the basic auth header for the request
        ic_request.add_header("Authorization", "Basic %s" % ic_auth)

        urllib.request.urlopen(ic_request)

    # scrobble to last.fm
    lastfm.scrobble(artist = artist, title = song, timestamp = timestamp, album = album)

    # scrobble to TuneIn
    ti_query['title']   = song
    ti_query['artist']  = artist
    if (album):
        ti_query['album'] = album
    
    ti_url = app.config['TUNEIN_API_URL'] + '?' + urllib.parse.urlencode(ti_query)
    ti_request = urllib.request.Request(ti_url)
    urllib.request.urlopen(ti_request)

    return True
