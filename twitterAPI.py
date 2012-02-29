# -*- coding: utf-8 -*-

import cPickle
import json
import sys
import threading
import time

import tweepy
import requests
import webbrowser

# Query terms
Q = sys.argv[1:]

# Got these keys for my account
CONSUMER_KEY = 'aOdeHWvJLhU8eXNHC6Zhw'
CONSUMER_SECRET = '5J9IkSSMp7TuKPRbGrb9YSkHFUhKvTBR43l6Iee5M'

ACCESS_TOKEN = '222822849-YAPQ6rO6rH9GYNnkBkaqW2mFAgc1tOU1cRdPfOnN'
ACCESS_TOKEN_SECRET = 'KSK8oJ2Ob2R3WpuEz71NezR9Sh0jpXcKfyglLLEc'

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

data_dict = {}

class CustomStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        try:
             data_dict[status.id] = status.text
             if len(data_dict) > 10:
                 raise Exception
        except Exception, e:
            print >> sys.stderr, 'Encountered Exception:', e
            raise


    def on_error(self, status_code):
        print >> sys.stderr, 'Encountered error with status code:', status_code
        return False # Don't kill the stream


    def on_timeout(self):
        print >> sys.stderr, 'Timeout...'
        return True # Don't kill the stream


#def main():
    # Create a streaming API and set a timeout value of 60 seconds.
#    streaming_api = tweepy.streaming.Stream(auth, CustomStreamListener(), timeout=60)
#
#    print >> sys.stderr, 'Filtering the public timeline for "%s"' % (' '.join(sys.argv[1:]),)
#
#    streaming_api.filter(follow=None, track=Q)


def fetch(page, query):
    d = {}

    for i in range(page, 5000, 100):
        try:
            r = requests.get('http://search.twitter.com/search.json',
                             params={'q': query, 'rpp': 100, 'page': page})
            results = r.text
            if results:
                filename = 'data/fetched/%s/tweetsfetched_%s_%d' % (
                    query.lower(), query.lower(), i)
                with open(filename, 'wb+') as fetched_file:
                    fetched_file.write(results)

            time.sleep(100)
        except requests.ConnectionError:
            time.sleep(100)
            continue

    print threading.currentThread().getName(), 'Exiting'
    return

def main():
    threads = []
#    for i in range(25):
#        t = threading.Thread(target=fetch, args=(i + 1 + 1350,'Oscar'))
#        time.sleep(1)
#        threads.append(t)
#        t.start()
#    for i in range(25):
#        t = threading.Thread(target=fetch, args=(i + 1 + 1321, 'Apple'))
#        time.sleep(1)
#        threads.append(t)
#        t.start()
#    for i in range(25):
#        t = threading.Thread(target=fetch, args=(i + 1 + 1275, 'Microsoft'))
#        time.sleep(1)
#        threads.append(t)
#        t.start()
#    for i in range(25):
#        t = threading.Thread(target=fetch, args=(i + 1 + 1270, 'Google'))
#        time.sleep(1)
#        threads.append(t)
#        t.start()
    for i in range(100):
        t = threading.Thread(target=fetch, args=(i + 1 + 1270, 'fail'))
        time.sleep(1)
        threads.append(t)
        t.start()
    return
