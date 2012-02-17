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
import numpy

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

        classification, tweets = parse_training_corpus(corpus_file)

        reviews_positive = parse_imdb_corpus(
            '/media/python/workspace/sentiment-analyzer/data/positive')
        class_positive = len(reviews_positive) * ['positive']

        reviews_negative = parse_imdb_corpus(
            '/media/python/workspace/sentiment-analyzer/data/negative')
        class_negative = len(reviews_negative) * ['negative']

        self.data = tweets + reviews_positive + reviews_negative
        self.classification = (classification + class_positive +
            class_negative)

    def initial_fit(self):
        """Initializes the vectorizer by doing a fit and then a transform.
        """
        self.initialize_training_data()

        # We map the sentiments to the values specified in the SENTIMENT_MAP.
        # For any sentiment that is not part of the map we give a value 0.
        classification_vector = numpy.array(map(
            lambda s: self.SENTIMENT_MAP.get(s.lower(), 0),
                                             self.classification))

        feature_vector = self.vectorizer.fit_transform(self.data)

        return (classification_vector, feature_vector)

    def transform(self, test_data):
        """Performs the transform using the already initialized vectorizer.
        """
        feature_vector = self.vectorizer.transform(test_data)

    def score_func(self, true, predicted):
        """Score function for the validation.
        """
        return metrics.precision_recall_fscore_support(
            true, predicted, pos_label=None)

    def train_and_validate(self, mean=False):
        """Trains the SVC with the training data and validates with the test data.

        We do a K-Fold cross validation with K = 10.
        """
        classification_vector, feature_vector = self.initial_fit()

        self.classifier = svm.LinearSVC(loss='l2', penalty='l1', C=1000,
                                        dual=False, tol=1e-3)

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
                print "Class\t\t\tPrecision\tRecall\t\tF-Score"
                print "~~~~~\t\t\t~~~~~~~~~\t~~~~~~\t\t~~~~~~~"
                precision = score[0]
                recall = score[1]
                f_score = score[2]
                print "Positive:\t\t%f\t%f\t%f" % (precision[0], recall[0],
                                                   f_score[0])
                print "Negative:\t\t%f\t%f\t%f" % (precision[1], recall[1],
                                                   f_score[1])
                print "Neutral:\t\t%f\t%f\t%f" % (precision[2], recall[2],
                                                  f_score[2])

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
    scores = trainer.train_and_validate(mean=args.mean)

    if args.profile:
        if isinstance(args.profile, str):
            cProfile.run(
                'Trainer().train_and_validate()', args.profile)
            print 'Profile stored in %s' % args.profile
        else:
            cProfile.run(
                'Train().train_and_validate()', args.profile)
    else:
        if args.mean:
          trainer.build_ui(mean=True)
        if args.scores:
            trainer.build_ui()

        return scores


if __name__ == '__main__':
    scores = bootstrap()
