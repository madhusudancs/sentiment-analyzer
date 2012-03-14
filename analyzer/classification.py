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


import argparse
import cPickle
import os

from disco.core import Job
from disco.core import Params

import datasettings

from map_reduce import mapper
from map_reduce import reducer


class Classifier(object):
    """Class that abstracts the classification of tweets.
    """

    def __init__(self, query, num_pages):
        """Constructs the classifier object.

        Args:
            query: The query term for tweets.
            num_pages: The number of pages to be fetched.
        """
        self.query = query
        self.num_pages = num_pages

        vectorizer_file = open(os.path.join(datasettings.DATA_DIRECTORY,
                                            'vectorizer.pickle'))
        classifier_file = open(os.path.join(datasettings.DATA_DIRECTORY,
                                            'classifier.pickle'))

        self.vectorizer = cPickle.load(vectorizer_file)

        self.classifier = cPickle.load(classifier_file)

        # The feature vector for all the tweets fetched from the twitter API.
        self.feature_vector = None

        # Stores the list of predictions on the given query.
        self.prediction = None

    def start(self):
        """Starts the entire process of querying twitter and classification.

        This method is responsible for running MapReduce for feature
        extraction.
        """
        def range_reader(stream, size, url):
           page_num = stream.getvalue()
           # Map readers should return a list of values, so page_num is
           # explicitly converted to an integer and then wrapped into a
           # list. By doing this each mapper instance will get exactly
           # one page number
           # If we don't do this, the mapper API just reads the numbers
           # character by character and we end up fetching the same 10
           # pages: digits 0, 9 all through since each character of a number
           # should be one of these 10 digits.
           return [int(page_num)]

        job = Job()

        inputs = [('raw://%d' % (i)) for i in range(1, self.num_pages)]

        job.run(input=inputs, map=mapper, reduce=reducer,
                map_reader=range_reader, params=Params(
                    query=self.query,
                    trained_vectorizer=self.vectorizer
                    ),
                required_modules=[('vectorizer',
                                   os.path.join(datasettings.PROJECT_ROOT,
                                                'analyzer',
                                                'vectorizer.py'),)])

        self.feature_vector = self.vectorizer.build_feature_matrix(job)
        print self.feature_vector.shape
        self.classify()

    def classify(self):
        """Calls the classifier and returns the prediction.
        """
        feature_vector = self.feature_vector.tocsr() 
        self.prediction = self.classifier.predict(feature_vector)


def bootstrap():
  parser = argparse.ArgumentParser(description='Compiler arguments.')
  parser.add_argument('-q', '--query', metavar="Query", type=str,
                      nargs=1,
                      help='The query that must be used to search for tweets.')
  parser.add_argument('-p', '--pages', metavar="Pages", type=int,
                      nargs='?', const=True, default=100,
                      help='Number of pages of tweets to fetch. One page is '
                           'approximately 100 tweets.')
  args = parser.parse_args()

  query = args.query
  num_pages = args.pages

  classifier = Classifier(query, num_pages)
  classifier.start()

  return classifier

if __name__ == '__main__':
    classifier = bootstrap()
