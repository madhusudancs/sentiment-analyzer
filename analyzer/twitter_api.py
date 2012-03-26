# -*- coding: utf-8 -*-

import cPickle
import json
import sys
import threading
import time

import requests
import webbrowser


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
                             params={'q': query, 'rpp': 100, 'page': page,
                                     'lang': 'en'})
            results = json.loads(r.text)
            if results:
                self.thread_lock.acquire()
                self.data.extend(results['results'])
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
            time.sleep(1)

        return self.data


    def userworker(self, query, page):
        try:
            r = requests.get('https://api.twitter.com/1/statuses/user_timeline.json', 
                             params={'include_entities' : True, 'include_rts' : True, 
                                     'screen_name' : query, 'page' : page, 'count' : 200})
            if r.status_code == 200:
                results = json.loads(r.text)
                if results:
                    self.thread_lock.acquire()
                    self.data.extend(results)
                    self.thread_lock.release()
        
        except requests.ConnectionError:
            pass

    def userfetch(self, query, start_page=1, num_pages=16):
        threads = []
        for page in range(start_page, num_pages+1):
            t = threading.Thread(target=self.userworker, args=(query, page))
            threads.append(t)
            t.start()

        while threading.active_count() > 3:
            time.sleep(1)
 
        return self.data 
             
def main():
    threads = []
    for i in range(100):
        t = threading.Thread(target=fetch, args=(i + 1 + 1270, 'fail'))
        time.sleep(1)
        threads.append(t)
        t.start()
    return

