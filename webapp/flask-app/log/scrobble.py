# module to publish the logged song to services

# import the app
from log import app

# import system libraries
import base64
import urllib, urllib.parse, urllib.request, urllib.error

# import pylast for lastfm api calls
import pylast

# Icecast Info
ic_url = app.config['ICECAST_URL'] + "/admin/metadata"

# LastFM API Info
lastfm = pylast.LastFMNetwork(
        api_key       = app.config['LASTFM_API_KEY'],
        api_secret    = app.config['LASTFM_API_SECRET'],
        username      = app.config['LASTFM_USERNAME'],
        password_hash = pylast.md5(app.config['LASTFM_PASSWORD']))

# TuneIn API Info
ti_query = {
        'partnerId' : app.config['TUNEIN_PARTNER_ID'],
        'partnerKey': app.config['TUNEIN_PARTNER_KEY'],
        'id'        : app.config['TUNEIN_STATION_ID']}

# takes the played song and publishes it to various places
def scrobbleSong(timestamp, song):
    
    # push song to Icecast
    password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    server_url = app.config['ICECAST_URL']
    password_mgr.add_password(None, server_url, app.config['ICECAST_USERNAME'], app.config['ICECAST_PASSWORD'])
    handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
    opener = urllib.request.build_opener(handler)

    ic_query = {'mode': 'updinfo', 'song': song.artist + " | " + song.song}
    for m in app.config['ICECAST_MOUNTPOINT']:
        ic_query['mount'] = m
        ic_url_m = ic_url + '?' + urllib.parse.urlencode(ic_query)
        
        try:
            ic_request = urllib.request.Request(ic_url_m)
            opener.open(ic_request)
            urllib.request.install_opener(opener)
        
        except (Exception, urllib.error.URLError) as error :
            print ("URL Error! => ", error)

        except (Exception, urllib.error.HTTPError) as error :
            print ("HTTP Error! => ", error)

    # scrobble to last.fm
    lastfm.scrobble(
        title     = song.song, 
        artist    = song.artist, 
        album     = song.album, 
        timestamp = timestamp)

    # scrobble to TuneIn
    ti_query['title']   = song.song
    ti_query['artist']  = song.artist
    if song.album != "":
        ti_query['album'] = song.album
    
    ti_url = app.config['TUNEIN_API_URL'] + '?' + urllib.parse.urlencode(ti_query)

    try:
        ti_request = urllib.request.Request(ti_url)
        urllib.request.urlopen(ti_request)
    
    except (Exception, urllib.error.URLError) as error :
        print ("URL Error! => ", error)

    except (Exception, urllib.error.HTTPError) as error :
        print ("HTTP Error! => ", error)

    return True
