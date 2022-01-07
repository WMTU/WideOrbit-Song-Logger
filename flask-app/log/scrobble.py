# module to publish the logged song to services

# import the app
from log import app

# import system libraries
import base64
import urllib, urllib.parse
import requests

# import telnet to communicate with DEVA RDS
from telnetlib import Telnet

# import pylast for lastfm api calls
import pylast

# DEVA RDS info
rds_ip      = app.config['RDS_IP']
rds_port    = app.config['RDS_PORT']

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

def updateRDS(song):

    # send to DEVA RDS
    # open up a new telnet connection
    with Telnet(rds_ip, rds_port) as tn:
        # format string for the RDS injector
        rdstext = "TEXT={} by {}\n\r".format(song.song, song.artist)

        # send the string to RDS injector
        # note: strings must be byte endoded, so use encode() when sending
        tn.write(rdstext.encode('ascii') + b"\n")

    return True

# takes the played song and publishes it to various places
def scrobbleSong(timestamp, song):

    # send to icecasts mounts
    ic_query = {'mode': 'updinfo', 'song': song.artist + " | " + song.song}
    for m in app.config['ICECAST_MOUNTPOINT']:
        ic_query['mount'] = m
        ic_url_m = ic_url + '?' + urllib.parse.urlencode(ic_query)
        
        try:
            r = requests.get(ic_url_m, auth=(app.config['ICECAST_USERNAME'], app.config['ICECAST_PASSWORD']))
        
        except (Exception, requests.RequestException) as error :
            print ("Icecast Connection Error! => ", error)

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
        r = requests.get(ti_url)
    
    except (Exception, requests.RequestException) as error :
        print ("TuneIn Connection Error! => ", error)

    return True
