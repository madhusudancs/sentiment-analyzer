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

class Fetcher(object):
    """Abstracts the twitter API.
    """

    def __init__(self):
        """Constructs the twitter fetcher.
        """
        self.data = []
        self.thread_lock = threading.Lock()

    def worker(self, query, page):
        """Thread worker which actually fetches a page of tweets.

        Args:
            query: the search query term that must be used to fetch tweets.
            num_page: number of pages to fetch.
        """
        try:
            r = requests.get('http://search.twitter.com/search.json',
                             params={'q': query, 'rpp': 100, 'page': page})
            results = json.loads(r.text)
            if results:
                self.thread_lock.acquire()
                self.data.append(results)
                self.thread_lock.release()
        except requests.ConnectionError:
            pass

    def fetch(self, query, start_page=1, num_pages=10):
        """Method that performs the fetch of tweets asyncronously.

        This method is responsible for spawning threads for fetching tweets.

        Args:
            query: the search query term that must be used to fetch tweets.
            start_page: the starting page on twitter to fetch the tweets from.
            num_page: number of pages to fetch.
        """
        threads = []
        for page in range(start_page, num_pages):
            t = threading.Thread(target=self.worker, args=(query, page))
            threads.append(t)
            t.start()

        while threading.active_count() > 3:
            print threading.active_count()
            time.sleep(1)

        return self.data

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
