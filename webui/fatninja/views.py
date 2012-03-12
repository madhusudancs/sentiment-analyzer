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

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template import loader

import datasettings

from fatninja.models import MetaData

from analyzer.twitter_api import Fetcher


def index(request):
    """View that renders the main search page and results.
    """
    context = {}

    if request.method == 'POST':
        post_data = request.POST
        
        query = post_data.get('query', None)
        if query:
            meta_object = MetaData.objects.create(
                search_key = query, search_stamp=datetime.datetime.now())
            meta_object.save()
            return redirect('%s?%s' % (reverse('fatninja.views.index'),
                                       urllib.urlencode({'q': query})))
    elif request.method == 'GET':
        get_data = request.GET
        query = get_data.get('q')
        if not query:
            return render_to_response(
                'fatninja/hero.html', RequestContext(request, context))

        context['query'] = query

        fetcher = Fetcher()
        results = fetcher.fetch(query, start_page=1, num_pages=10)

        fetched_tweets = []
        tweets_date = []
        tweets_user = []
        for result in results:
            for tweet in result['results']:
                fetched_tweets.append(tweet['text'])
                tweets_date.append(datetime.datetime(
                    *email.utils.parsedate_tz(tweet['created_at'])[:7]))
                tweets_user.append(tweet['from_user'])

        classifiers_file = open(os.path.join(datasettings.DATA_DIRECTORY,
                                            'classifiers.pickle'))
        classifiers = cPickle.load(classifiers_file)
        vectorizer_file = open(os.path.join(datasettings.DATA_DIRECTORY,
                                            'vectorizer.pickle'))
        vectorizer = cPickle.load(vectorizer_file)
        tweets_vector = vectorizer.transform(fetched_tweets)
        classified1 = list(classifiers[0].predict(tweets_vector))
        classified2 = list(classifiers[1].predict(tweets_vector))
        classified3 = list(classifiers[2].predict(tweets_vector))

        
        classified = []
     #   for predictions in list(classified1): #zip(classified1, classified2, classified3):
     #           neutral_count = predictions.count(0)
     #           positive_count = predictions.count(1)
     ##           negative_count = predictions.count(-1)
     #           if (neutral_count == negative_count and
     ##               negative_count == positive_count):
      #              classified.append(predictions[0])
      #          elif (neutral_count > positive_count and
      #              neutral_count > negative_count):
      ##              classified.append(0)
       #         elif (positive_count > neutral_count and
     #               positive_count > negative_count):
     #               classified.append(1)
     #           elif (negative_count > neutral_count and
     #               negative_count > positive_count):
     #               classified.append(-1)

        #classified = numpy.array(classified)
        context['tweets_classified'] = len(classified3)
        context['positive_count'] = classified2.count(1)
        context['negative_count'] = classified2.count(-1)
        context['neutral_count'] = classified2.count(0)
        
        context['classified_information'] = []
        for tweet, user, date, classification in zip(
          fetched_tweets, tweets_user, tweets_date, classified1):
            context['classified_information'].append(
                (tweet, user, date, classification))

    return render_to_response(
        'fatninja/hero.html', RequestContext(request, context))
