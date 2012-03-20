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
import cProfile
import datetime
import numpy
import os
import scipy
import string

from sklearn import cross_validation
from sklearn import metrics
from sklearn import svm
from sklearn import naive_bayes
from sklearn.utils import check_arrays

import datasettings

from analyzer.parser import parse_imdb_corpus
from analyzer.parser import parse_training_corpus
from vectorizer import SENTIMENT_MAP
from vectorizer import Vectorizer


class Trainer(object):
    """Trains the classifier with training data and does the cross validation.
    """

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
        corpus_file = open(os.path.join(datasettings.DATA_DIRECTORY,
                                        'full-corpus.csv'))

        classification, tweets = parse_training_corpus(corpus_file)

        reviews_positive = parse_imdb_corpus(
            os.path.join(datasettings.DATA_DIRECTORY, 'positive'))

        num_postive_reviews = len(reviews_positive)
        class_positive = ['positive'] * num_postive_reviews

        reviews_negative = parse_imdb_corpus(
            os.path.join(datasettings.DATA_DIRECTORY, 'negative'))
        num_negative_reviews = len(reviews_negative)
        class_negative = ['negative'] * num_negative_reviews

        self.data = tweets
        self.classification = classification

        #self.date_time = date_time
        #self.retweet = retweets
        #self.favorited = favorited

    def initial_fit(self):
        """Initializes the vectorizer by doing a fit and then a transform.
        """
        # We map the sentiments to the values specified in the SENTIMENT_MAP.
        # For any sentiment that is not part of the map we give a value 0.
        classification_vector = numpy.array(map(
            lambda s: SENTIMENT_MAP.get(s.lower(), 0),
                                        self.classification))

        feature_vector = self.vectorizer.fit_transform(self.data)

        return (classification_vector, feature_vector)

    def build_word_dict(self):
        """ Build sentiment dictionary and build vector of 
            weights for tweets.
        """
        fileIn = open(os.path.join(datasettings.DATA_DIRECTORY,
                                   'AFINN-96.txt'))
        wordDict = {}
        line = fileIn.readline()
        while line != '':
            temp = string.split(line, '\t')
            wordDict[temp[0]] = int(temp[1])
            line = fileIn.readline()
        fileIn.close()

        fileIn = open(os.path.join(datasettings.DATA_DIRECTORY,
                                   'AFINN-111.txt'))
        line = fileIn.readline()
        while line != '':
            temp = string.split(line, '\t')
            wordDict[temp[0]] = int(temp[1])
            line = fileIn.readline()
        fileIn.close()

        word_dict_vector = []
        for tweet in self.data:
            word_list = tweet.split()
            sum = 0
            for word in word_list:
                if word in wordDict.keys():
                    sum += wordDict[word]    
            word_dict_vector.append(sum)

        return word_dict_vector

    def transform(self, test_data):
        """Performs the transform using the already initialized vectorizer.
        """
        feature_vector = self.vectorizer.transform(test_data)

    def score_func(self, true, predicted):
        """Score function for the validation.
        """
        return metrics.precision_recall_fscore_support(
            true, predicted,
            pos_label=[
                SENTIMENT_MAP['positive'],
                SENTIMENT_MAP['negative'],
                SENTIMENT_MAP['neutral'],
                ],
            average='macro')

    def cross_validate(self, k=10):
        """Performs a k-fold cross validation of our training data.

        Args:
            k: The number of folds for cross validation.
        """
        self.scores = []

        X, y = check_arrays(self.feature_vector,
                            self.classification_vector,
                            sparse_format='csr')
        cv = cross_validation.check_cv(
            k, self.feature_vector, self.classification_vector,
            classifier=True)

        for train, test in cv:
            self.classifier1.fit(self.feature_vector[train],
                          self.classification_vector[train])
            self.classifier2.fit(self.feature_vector[train],
                          self.classification_vector[train])
            self.classifier3.fit(self.feature_vector[train],
                          self.classification_vector[train])
            classification1 = self.classifier1.predict(
                self.feature_vector[test])
            classification2 = self.classifier2.predict(
                self.feature_vector[test])
            classification3 = self.classifier3.predict(
                self.feature_vector[test])

            classification = []
            for predictions in zip(classification1, classification2,
                                   classification3):
                neutral_count = predictions.count(0)
                positive_count = predictions.count(1)
                negative_count = predictions.count(-1)
                if (neutral_count == negative_count and
                    negative_count == positive_count):
                    classification.append(predictions[0])
                elif (neutral_count > positive_count and
                    neutral_count > negative_count):
                    classification.append(0)
                elif (positive_count > neutral_count and
                    positive_count > negative_count):
                    classification.append(1)
                elif (negative_count > neutral_count and
                    negative_count > positive_count):
                    classification.append(-1)
            classification = numpy.array(classification)

            self.scores.append(self.score_func(y[test], classification))

    def train_and_validate(self, cross_validate=False, mean=False,
                           serialize=False):
        """Trains the SVC with the training data and validates with the test data.

        We do a K-Fold cross validation with K = 10.
        """
        self.classification_vector, self.feature_vector = self.initial_fit()

        self.classifier1 = naive_bayes.MultinomialNB()
        self.classifier2 = naive_bayes.BernoulliNB()
        self.classifier3 = svm.LinearSVC(loss='l2', penalty='l1',
                                         C=1000,dual=False, tol=1e-3)

        if cross_validate:
            self.cross_validate(k=cross_validate)
        else:
            self.classifier1.fit(self.feature_vector,
                                 self.classification_vector)
            self.classifier2.fit(self.feature_vector,
                                 self.classification_vector)
            self.classifier3.fit(self.feature_vector,
                                 self.classification_vector)

        if serialize:
            classifiers_file = open(os.path.join(
                datasettings.DATA_DIRECTORY, 'classifiers.pickle'), 'wb')
            cPickle.dump([self.classifier1,
                          self.classifier2,
                          self.classifier3], classifiers_file)
            vectorizer_file = open(os.path.join(
                datasettings.DATA_DIRECTORY, 'vectorizer.pickle'), 'wb')
            cPickle.dump(self.vectorizer, vectorizer_file)

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
        '-s', '--scores', metavar = 'Scores', type=int, nargs='?',
        help='Prints the scores by doing the cross validation with the '
        'argument passed as the number of folds. Cannot be run with -p '
        'turned on.')
    parser.add_argument(
        '-m', '--mean', action='store_true',
        help='Prints the mean accuracies. Cannot be run with -p/-s turned on.')
    parser.add_argument(
        '--serialize', action='store_true',
        help='Serializes the classifier, feature vector and the '
             'classification vector into the data directory with the same '
             'names.')
    args = parser.parse_args()

    trainer = Trainer()
    trainer.initialize_training_data()

    if args.profile:
        if isinstance(args.profile, str):
            cProfile.runctx(
                'trainer.train_and_validate()',
                {'trainer': trainer, 'serialize': args.serialize},
                {}, args.profile)
            print 'Profile stored in %s' % args.profile
        else:
            cProfile.runctx(
                'trainer.train_and_validate()',
                {'trainer': trainer, 'serialize': args.serialize},
                {}, args.profile)
    else:
        scores = trainer.train_and_validate(cross_validate=args.scores,
                                            mean=args.mean,
                                            serialize=args.serialize)
        if args.mean:
          trainer.build_ui(mean=True)
        if args.scores:
            trainer.build_ui()

        return scores

if __name__ == '__main__':
    scores = bootstrap()

