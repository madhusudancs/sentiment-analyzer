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


import cPickle
import datetime
import email
import os
import urllib

import numpy

from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template import loader
from django.utils.datastructures import SortedDict

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
        get_data = request.GET
        query = get_data.get('q')
        if not query:
            context['no_header_search_box'] = True
            return render_to_response(
                'fatninja/home.html', RequestContext(request, context))

        context['query'] = query

        stripped_query = query.strip()
        if stripped_query.startswith('@'):
            fetcher = Fetcher()
            results = fetcher.userfetch(stripped_query[1:], start_page=1, num_pages=16)
        else:
            fetcher = Fetcher()
            results = fetcher.fetch(stripped_query, start_page=1, num_pages=10)

        tweets_to_classify = []

        predicted_tweets = SortedDict()

        tweets_to_classify_id_map = {}

        data_to_db = {}

        #for result in results:
        for tweet in results:
            tweet_id = tweet['id']
            cached_tweet = cache.get(tweet_id)

            # Check if tweet is cached.
            cached_tweet = None
            if cached_tweet:
                predicted_tweets[tweet_id] = cached_tweet
            else:
                created_at = datetime.datetime(
                        *email.utils.parsedate_tz(tweet['created_at'])[:7])

                predicted_tweets[tweet_id] = {
                    'text': tweet['text'],
                    'date': created_at,
                    'user': tweet.get('from_user', stripped_query[1:])
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

        if tweets_to_classify: 
            classifiers_file = open(os.path.join(datasettings.DATA_DIRECTORY,
                                            'classifiers.pickle'))
            classifiers = cPickle.load(classifiers_file)
            vectorizer_file = open(os.path.join(datasettings.DATA_DIRECTORY,
                                            'vectorizer.pickle'))
            vectorizer = cPickle.load(vectorizer_file)
        
            tweets_vector = vectorizer.transform(tweets_to_classify)
            classified = list(classifiers[2].predict(tweets_vector))
        else:
            classified = []


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
                'user': tweet.get('from_user', stripped_query[1:]),
                'sentiment': sentiment
                })

        context['tweets_classified'] = len(predicted_tweets)
        context['positive_count'] = 0
        context['negative_count'] = 0
        context['neutral_count'] = 0
        for key, value in predicted_tweets.iteritems():
            if value['sentiment'] == 1:
                context['positive_count'] += 1
            elif value['sentiment'] == 0:
                context['neutral_count'] += 1
            else:
                context['negative_count'] += 1

        context['classified_information'] = predicted_tweets

    return render_to_response(
        'fatninja/home.html', RequestContext(request, context))

