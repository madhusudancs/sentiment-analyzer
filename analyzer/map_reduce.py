#!/usr/bin/env python
#
# Copyright 2012 Ajay Narayan, Madhusudan C.S., Shobhit N.S.
#
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import cPickle
import os

import datasettings

from vectorizer import Vectorizer


def mapper(page, params):
    """The mapper function for the MapReduce which analyzes tweets.

    We do a word N-gram analysis after stripping accents, decoding to
    UTF-8 and then removing stop words.

    Args:
        page: The number of the twitter search page for the query that
           this mapper has to fetch and analyze.
        params: The parameter object that holds the map reduce
            initialization parameters. This contains the query string!
    """
    import datetime
    import json
    import requests

    from email import utils
    from mongoengine.base import ValidationError

    from models import Tweet
    from models import GeoLocation
    from models import FetchMetaData

    trained_vectorizer = params.trained_vectorizer

    try:
        fetch_meta_data = FetchMetaData(
            query_data={
                'query_terms': params.query,
                'page': page },
            searched_at=datetime.datetime.now(),
            tweets=[]
            )
        r = requests.get(
            'http://search.twitter.com/search.json',
            params={'q': params.query, 'rpp': 100, 'page': page,
                    'lang': 'en'})

        page_of_tweets = json.loads(
            r.text.decode(trained_vectorizer.charset,
                          trained_vectorizer.charset_error))
        tweets = page_of_tweets.get('results')

        if not tweets:
          print ('No tweets were fetched in this mapper with page '
              'number %s.' % (page))
          print 'HTTP status was: ', r.status_code
          return

        # List of tweet database object to write to metadata object.

        tweets_saved = []
        for tweet in tweets:
            tweet_text = tweet['text']
            tweet_id = tweet['id']

            # Save it in the database.
            try:
                tweet_inserted = Tweet(**tweet)
                tweet_inserted.save()
                fetch_meta_data.tweets.append(tweet_inserted)

                analyze = trained_vectorizer.build_analyzer()
                tokens = analyze(tweet_text)
                for token in tokens:
                    yield (token, (tweet_id, 1))
            except ValidationError, e:
                print e

        fetch_meta_data.save()

    except requests.ConnectionError:
        print "There was a connection error."


def reducer(klv, params):
    """Reducer of the MapReduce framework that builds the Counts matrix.

    This returns just the counts for each token, tweet id pair. We build
    the actual matrix after we get the results from the reducer.
    
    Args:
        klv: The key and the list of values given as input to the reducer.
        params: The parameters supplied while initializing the MapReduce.
    """
    from disco.util import kvgroup

    trained_vectorizer = params.trained_vectorizer

    for token, count_tuple_list in kvgroup(sorted(klv)):
        token = token.strip()
        j = trained_vectorizer.vocabulary_.get(''.join(token.split()))
        if j is not None:
            new_dict = {}
            for doc_id, count in count_tuple_list:
                if doc_id not in new_dict:
                    new_dict[doc_id] = count
                else:
                    new_dict[doc_id] += count
            yield j, new_dict

