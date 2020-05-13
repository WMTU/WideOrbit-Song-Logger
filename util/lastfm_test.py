# testing pylast functions for lastfm api calls

# import helper libraries
import os, sys, getopt, configparser, ast, json
from datetime import datetime, date, time
import requests

# imports pylast for lastfm api calls
import pylast

# set up lastfm connection
def connectLFM(key, secret, username, password):

    print("Setting up LastFM connection...")
    
    lastfm = pylast.LastFMNetwork(
        api_key       = key,
        api_secret    = secret,
        username      = username,
        password_hash = pylast.md5(password))
    
    return lastfm

# fetch artwork url
def fetchArtwork(api, artist, album):

    print("Getting album artwork...")

    image = ""

    if album != "":
        try:
            lfm_album = api.get_album(artist, album)
            image = lfm_album.get_cover_image()
        
        except (Exception, pylast.WSError) as error :
            print ("Error fetching album artwork! => ", error)
    else:
        print("  => No album specified!")
    
    if image is not str:
        image = ""
        print("  => No album artwork found!")
    else:
        print("  => Album Artwork: " + image)

    return image

# scrobble song to lastfm
def scrobbleSong(api, title, artist, album, ts):

    print("Scrobbling song...")

    if title != '':
        # scrobble to last.fm
        api.scrobble(
            title     = title, 
            artist    = artist, 
            album     = album, 
            timestamp = datetime.strptime(ts, '%Y-%m-%d %H:%M:%S').strftime("%s"))

        print("  => Added to LastFM!")
    else:
        print("  => Not adding empty song!")

# fetch np info from log api
def fetchNP(url):

    print("Fetching song from log API...")

    song = {
        'title':    '',
        'artist':   '',
        'album':    '',
        'ts':       ''}

    response = requests.get(url)

    if response.status_code == 200:
        np = json.loads(response.content.decode('utf-8'))

        song['title']   = np[0]['song']
        song['artist']  = np[0]['artist']
        song['album']   = np[0]['album']
        song['ts']      = np[0]['timestamp']

        print("  => NP: " + song['title'] + " by " + song['artist'] + " from the album " + song['album'])
        print("  => Song Logged " + song['ts'])
    else:
        print("!!! Error fetching song from log API !!!")

    return song

#######################################################################

if __name__ == "__main__":
    # fetch info from the config file
    try:
        opts, args = getopt.getopt(sys.argv[1:], "", ["creds=", "api="])

    except (Exception, getopt.GetoptError):
        print("Specify a LastFM Credentials file with --creds=<file name>")
        print("Specify an API URL with --api=<url>")
        sys.exit(1)

    if len(opts) < 1:
        print("Specify a LastFM Credentials file with --creds=<file name>")
        print("Specify an API URL with --api=<url>")
        sys.exit(1)

    credentials = None
    api = None

    for o, a in opts:
        if o == "--creds":
            credentials = a
        elif o == "--api":
            api = a

    config = configparser.ConfigParser()
    config.read(credentials)

    lastfm = connectLFM(
        config['LASTFM']['api_key'], 
        config['LASTFM']['api_secret'], 
        config['LASTFM']['username'], 
        config['LASTFM']['password'])

    run = True

    while run == True:
        prompt = input("Fetch Song? (Y/N) => ")

        if prompt != "Y":
            run = False
        
        else:
            run = True

            np = fetchNP(api)
            fetchArtwork(lastfm, np['artist'], np['album'])
            scrobbleSong(lastfm, np['title'], np['artist'], np['album'], np['ts'])

    exit(0)

