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
import cProfile
import datetime
import numpy
import scipy

from sklearn import cross_validation
from sklearn import metrics
from sklearn import svm
from sklearn import naive_bayes
from sklearn.feature_extraction.text import Vectorizer

from parser import parse_imdb_corpus
from parser import parse_training_corpus


class Trainer(object):
    """Trains the classifier with training data and does the cross validation.
    """

    SENTIMENT_MAP = {
        'positive': 1,
        'negative': -1,
        'neutral': 0,
        'irrelevant': 0,
        }

    def __init__(self):
        """Initializes the datastructures required.
        """
        # The actual text extraction object (does text to vector mapping).
        self.vectorizer = Vectorizer()

        # A list of already hand classified tweets to train our classifier.
        self.data = None

        # A list containing the classification to each individual tweet
        # in the tweets list.
        self.classification = None

        self.classifier = None
        self.scores = None

    def initialize_training_data(self):
        """Initializes all types of training data we have.
        """
        corpus_file = open(
            '/media/python/workspace/sentiment-analyzer/data/full-corpus.csv')

        classification, date_time, tweets, retweets, favorited = \
            parse_training_corpus(corpus_file)

        reviews_positive = parse_imdb_corpus(
            '/media/python/workspace/sentiment-analyzer/data/positive')
        num_postive_reviews = len(reviews_positive)
        class_positive = ['positive'] * num_postive_reviews

        reviews_negative = parse_imdb_corpus(
            '/media/python/workspace/sentiment-analyzer/data/negative')
        num_negative_reviews = len(reviews_negative)
        class_negative = ['negative'] * num_negative_reviews

        self.data = tweets + reviews_positive + reviews_negative
        self.classification = (classification + class_positive +
            class_negative)

        self.date_time = date_time
        self.retweet = retweets
        self.favorited = favorited

    def initial_fit(self):
        """Initializes the vectorizer by doing a fit and then a transform.
        """
        # We map the sentiments to the values specified in the SENTIMENT_MAP.
        # For any sentiment that is not part of the map we give a value 0.
        classification_vector = numpy.array(map(
            lambda s: self.SENTIMENT_MAP.get(s.lower(), 0),
                                             self.classification))

        time_vector = []
        late_night = datetime.time(0, 0, 0)
        morning = datetime.time(6, 0, 0)
        afternoon = datetime.time(12, 0, 0)
        evening = datetime.time(16, 0, 0)
        night = datetime.time(19, 0, 0)
        night_end = datetime.time(23, 59, 59)
        for dt in self.date_time:
            time = dt.time()
            if late_night <= time < morning:
                time_map = 0
            elif morning <= time < afternoon:
                time_map = 1
            elif afternoon <= time < evening:
                time_map = 2
            elif evening <= time < night:
                time_map = 3
            elif night <= time <= night_end:
                time_map = 4

            time_vector.append(time_map)


        feature_vector = self.vectorizer.fit_transform(self.data)

        # Extend the feature vector with time, retweet and favorited
        # information
        time_coo = scipy.sparse.coo_matrix([time_vector]).transpose()
        retweet_coo = scipy.sparse.coo_matrix([self.retweet]).transpose()
        favorited_coo = scipy.sparse.coo_matrix([self.favorited]).transpose()
        feature_vector_coo = feature_vector.tocoo()
        data = scipy.concatenate((feature_vector_coo.data, retweet_coo.data,
                                  favorited_coo.data, time_coo.data))
        rows = scipy.concatenate((feature_vector_coo.row, retweet_coo.row,
                                  favorited_coo.row, time_coo.row))
        # The + 1 for the column value for favorited because we extending the
        # matrix by 2 columns and this happens to be the second column of the
        # additions
        cols = scipy.concatenate((
            feature_vector_coo.col,
            retweet_coo.col+feature_vector_coo.shape[1],
            favorited_coo.col+(feature_vector_coo.shape[1] + 1),
            time_coo.col + (feature_vector_coo.shape[1] + 2)))

        # +2 is again for same reason, we are adding 2 columns.
        feature_vector = scipy.sparse.coo_matrix(
            (data, (rows, cols)), shape=(feature_vector_coo.shape[0],
            feature_vector_coo.shape[1]+3))

        # Convert it back to CSR for efficient computation on sparse matrices.
        feature_vector = feature_vector.tocsr()

        return (classification_vector, feature_vector)

    def transform(self, test_data):
        """Performs the transform using the already initialized vectorizer.
        """
        feature_vector = self.vectorizer.transform(test_data)

    def train_and_validate(self, mean=False):
        """Trains the SVC with the training data and validates with the test data.

        We do a K-Fold cross validation with K = 10.
        """
        classification_vector, feature_vector = self.initial_fit()

        self.classifier = naive_bayes.MultinomialNB()

        def score_func(true, predicted):
            """Score function for the validation.
            """
            return metrics.precision_recall_fscore_support(
                true, predicted, pos_label=None, average='macro')

        # The value for the keyword argument cv is the K value in the K-Fold cross
        # validation that will be used.
        self.scores = cross_validation.cross_val_score(
            self.classifier, feature_vector, classification_vector, cv=10,
            score_func=score_func if not mean else None)

        return self.scores

    def build_ui(self, mean=False):
        """Prints out all the scores calculated.
        """
        for i, score in enumerate(self.scores):
            print "Cross Validation: %d" % (i + 1)
            print "*" * 40
            if mean:
                print "Mean Accuracy: %f" % (score)
            else:
                print "Precision\tRecall\t\tF-Score"
                print "~~~~~~~~~\t~~~~~~\t\t~~~~~~~"
                precision = score[0]
                recall = score[1]
                f_score = score[2]
                print "%f\t%f\t%f" % (precision, recall, f_score)


            print


def bootstrap():
    """Bootstrap the entire training process.
    """
    parser = argparse.ArgumentParser(description='Trainer arguments.')
    parser.add_argument('-c', '--corpus-file', dest='corpus_file',
                        metavar='Corpus', type=file, nargs='?',
                        help='name of the input corpus file.')
    parser.add_argument('-p', '--profile', metavar='Profile', type=str,
                        nargs='?', help='Run the profiler.')
    parser.add_argument(
        '-s', '--scores', action='store_true',
        help='Prints the scores. Cannot be run with -p turned on.')
    parser.add_argument(
        '-m', '--mean', action='store_true',
        help='Prints the mean accuracies. Cannot be run with -p/-s turned on.')
    args = parser.parse_args()

    trainer = Trainer()
    trainer.initialize_training_data()

    if args.profile:
        if isinstance(args.profile, str):
            cProfile.runctx(
                'trainer.train_and_validate()',
                {'trainer': trainer}, {}, args.profile)
            print 'Profile stored in %s' % args.profile
        else:
            cProfile.runctx(
                'trainer.train_and_validate()',
                {'trainer': trainer}, {}, args.profile)
    else:
        scores = trainer.train_and_validate(mean=args.mean)
        if args.mean:
          trainer.build_ui(mean=True)
        if args.scores:
            trainer.build_ui()

        return scores


if __name__ == '__main__':
    scores = bootstrap()
