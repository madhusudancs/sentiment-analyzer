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

"""The views module for the webui of sentiment analyzer.
"""


import collections
import cPickle
import datetime
import email
import os
import time
import urllib

import numpy

from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template import loader

import datasettings

from fatninja.models import FetchMetaData
from fatninja.models import Tweet

from analyzer.twitter_api import Fetcher


def index(request):
    """View that renders the main search page and results.
    """
    context = {}

    if request.method == 'POST':
        post_data = request.POST
        
        query = post_data.get('query', None)
        if query:
            meta_object = FetchMetaData.objects.create(
                search_key = query, search_stamp=datetime.datetime.now())
            meta_object.save()
            return redirect('%s?%s' % (reverse('fatninja.views.index'),
                                       urllib.urlencode({'q': query})))
    elif request.method == 'GET':
        start = time.time()
        get_data = request.GET
        query = get_data.get('q')
        if not query:
            return render_to_response(
                'fatninja/hero.html', RequestContext(request, context))

        context['query'] = query

        fetcher = Fetcher()
        results = fetcher.fetch(query, start_page=1, num_pages=10)

        tweets_to_classify = []

        predicted_tweets = collections.OrderedDict()

        tweets_to_classify_id_map = {}

        data_to_db = {}

        for result in results:
            for tweet in result['results']:
                tweet_id = tweet['id']
                cached_tweet = cache.get(tweet_id)

                # Check if tweet is cached.
                if cached_tweet:
                    predicted_tweets[tweet_id] = cached_tweet
                else:
                    created_at = datetime.datetime(
                            *email.utils.parsedate_tz(tweet['created_at'])[:7])

                    predicted_tweets[tweet_id] = {
                        'text': tweet['text'],
                        'date': created_at,
                        'user': tweet['from_user']
                        }

                    # If not go check the database
                    database_tweet = Tweet.objects.with_id(str(tweet_id))
                    if (database_tweet and
                        database_tweet.sentiment in [-1, 0, 1]):
                        predicted_tweets[tweet_id]['sentiment'] = \
                            database_tweet.sentiment
                        cache.add(tweet_id, predicted_tweets[tweet_id])
                    else:
                        # If it is not even in the database, you are screwed :P
                        # Go classify it.                       
                        tweets_to_classify_id_map[len(tweets_to_classify)] = \
                            tweet['id']
                        tweets_to_classify.append(tweet['text'])

                        tweet['created_at'] = created_at
                        data_to_db[tweet_id] = tweet


        classifiers_file = open(os.path.join(datasettings.DATA_DIRECTORY,
                                            'classifiers.pickle'))
        classifiers = cPickle.load(classifiers_file)
        vectorizer_file = open(os.path.join(datasettings.DATA_DIRECTORY,
                                            'vectorizer.pickle'))
        vectorizer = cPickle.load(vectorizer_file)
        tweets_vector = vectorizer.transform(tweets_to_classify)
        classified = list(classifiers[1].predict(tweets_vector))

        context['tweets_classified'] = len(classified)
        context['positive_count'] = classified.count(1)
        context['negative_count'] = classified.count(-1)
        context['neutral_count'] = classified.count(0)

        for pointer, tweet_id in tweets_to_classify_id_map.items():
            sentiment = classified[pointer]
            predicted_tweets[tweet_id]['sentiment'] = sentiment
            # Write it both to the disk and the cache
            tweet = data_to_db[tweet_id]
            tweet['sentiment'] = sentiment
            Tweet(**tweet).save()

            cache.add(tweet_id, {
                'text': tweet['text'],
                'date': tweet['created_at'],
                'user': tweet['from_user'],
                'sentiment': sentiment
                })

        context['classified_information'] = predicted_tweets
        end = time.time()
        print end - start

    return render_to_response(
        'fatninja/hero.html', RequestContext(request, context))

