# python utility to scrape twitter for #wmturequest tweets
# tweets are then added to the requests log api

# import system libraries
import os, json, sys, getopt, configparser, ast
import urllib, urllib.parse, urllib.request
from time import sleep

# requires twitter-python to be installed with pip
import twitter

class TwitterAPI:
    def __init__(self, consumer_key, consumer_secret, access_token_key, access_token_secret):

        self.api = twitter.Api(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token_key=access_token_key,
            access_token_secret=access_token_secret)

# main function
if __name__ == "__main__":
    # fetch info from the config file
    try:
        opts, args = getopt.getopt(sys.argv[1:], "", ["config="])

    except (Exception, getopt.GetoptError):
        print("Specify a config file with --config=<file name>")
        sys.exit(1)

    if len(opts) < 1:
        print("Specify a file with --config=<file name>")
        sys.exit(1)

    config_file = None

    for o, a in opts:
        if o == "--config":
            config_file = a

    config = configparser.ConfigParser()
    config.read(config_file)
    pid_path = config['GENERAL']['pid_path']

    # write out a pid file
    # note that this will overwrite an existing pid file
    try:
        pid_file = open(pid_path, 'w')
        pid_file.write(str(os.getpid()) + "\n")
        pid_file.close()
        
    except (Exception, IOError) as e:
        print("IO Error => ", e)

    twitter_api = TwitterAPI(
        config['TWITTER']['consumer_key'],
        config['TWITTER']['consumer_secret'],
        config['TWITTER']['access_token_key'],
        config['TWITTER']['access_token_secret'])

    sys.exit(0)
