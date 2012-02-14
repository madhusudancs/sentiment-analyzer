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
import numpy

from sklearn import cross_validation
from sklearn.feature_extraction.text import Vectorizer
from sklearn import metrics
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
SENTIMENT_MAP = {
    'positive': 1,
    'negative': -1,
    'neutral': 0,
    'irrelevant': 0,
    }


def vectorize(classification, tweets):
    """Maps the classification and tweets to numerical values for classifier.

    Args:
       classification: A list containing the classification to each individual
           tweet in the tweets list.
       tweets: A list of already hand classified tweets to train our classifier.

    """
    # We map the sentiments to the values specified in the SENTIMENT_MAP.
    # For any sentiment that is not part of the map we give a value 0.
    classification_vector = numpy.array(map(
        lambda s: SENTIMENT_MAP.get(s.lower(), 0), classification))

    vectorizer = Vectorizer()
    feature_vector = vectorizer.fit_transform(tweets)

    return (classification_vector, feature_vector)


def train_and_validate(classification, tweets):
    """Trains the SVC with the training data and validates with the test data.

    We do a K-Fold cross validation with K = 10.

    Args:
       classification: A list containing the classification to each individual
           tweet in the tweets list.
       tweets: A list of already hand classified tweets to train our classifier.
    """
    classification_vector, feature_vector = vectorize(classification, tweets)

    # classifier = LinearSVC(loss='l2', penalty='l1', C=1000,
    #                       dual=False, tol=1e-3)
    classifier = RandomForestClassifier(max_depth = None, min_split = 1, random_state = 0,n_jobs = -1)
    # The value for the keyword argument cv is the K value in the K-Fold cross
    # validation that will be used.
    #classifier.fit(feature_vector.toarray(), classification_vector)
    # scores = cross_validation.cross_val_score(
    #    classifier, feature_vector.toarray(), classification_vector, cv=10,
    #    score_func=metrics.precision_recall_fscore_support)

    #return scores
    classifier.fit(feature_vector.toarray(),classification_vector)


def bootstrap():
    """Bootstrap the entire training process.
    """
    from parser import parse_training_corpus

    #parser = argparse.ArgumentParser(description='Trainer arguments.')
    #parser.add_argument('-c', '--corpus-file', dest='corpus_file',
    #                    metavar='Corpus', type=file, nargs='?',
    #                    help='name of the input corpus file.')
    #args = parser.parse_args()

    corpus_file =open('data/full-corpus.csv')
    if not corpus_file:
        print (
            "If you are running this as a standalone program supply the "
            "corpus file for training data to option -c/--corpus-file. Use "
            "-h option for more help on usage.")
        return

    classification, tweets = parse_training_corpus(corpus_file)

    scores = train_and_validate(classification, tweets)
    return scores


def build_ui(scores):
    """Prints out all the scores calculated.
    """
    for i, score in enumerate(scores):
        print "Cross Validation: %d" % (i + 1)
        print "*" * 40
        print "Class\t\t\tPrecision\tRecall\t\tF-Score"
        print "~~~~~\t\t\t~~~~~~~~~\t~~~~~~\t\t~~~~~~~"
        precision = score[0]
        recall = score[1]
        f_score = score[2]
        print "Positive:\t\t%f\t%f\t%f" % (precision[0], recall[0], f_score[0])
        print "Negative:\t\t%f\t%f\t%f" % (precision[1], recall[1], f_score[1])
        print "Neutral:\t\t%f\t%f\t%f" % (precision[2], recall[2], f_score[2])

        print


if __name__ == '__main__':
    scores = bootstrap()
    # build_ui(scores)

