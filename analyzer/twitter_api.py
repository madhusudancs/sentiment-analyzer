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
    for i in range(100):
        t = threading.Thread(target=fetch, args=(i + 1 + 1270, 'fail'))
        time.sleep(1)
        threads.append(t)
        t.start()
    return

