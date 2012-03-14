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


from argparse import ArgumentParser


class Classifier(object):
    """Class that abstracts the classification of tweets.
    """

    def __init__(self, feature_vector):
        """Constructs the classifier object.

        Args:
            feature_vector: The feature vector that must be classified.
        """
        self.feature_vector = feature_vector

    def classify(self):
        """Calls the classifier and returns the prediction.
        """
        classifier_file = open(os.path.join(datasettings.DATA_DIRECTORY,
                                            'classifier.pickle'))
        classifier = cPickle.load(classifier_file) 


        feature_vector = self.feature_vector.tocsr() 
        return classifier.predict(feature_vector)


def bootstrap():
  parser = ArgumentParser(description='Compiler arguments.')
  parser.add_argument('-q', '--query', metavar="Query", type=str,
                      nargs=1, const=True,
                      help='The query that must be used to search for tweets.')
  parser.add_argument('-p', '--pages', metavar="Pages", type=int,
                      nargs='?', const=True, default=10
                      help='Number of pages of tweets to fetch. One page is '
                           'approximately 100 tweets.')
  args = parser.parse_args()

  query = args.query
  num_pages = args.num_pages


  return elf


if __name__ == '__main__':
    bootstrap()