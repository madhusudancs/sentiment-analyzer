#!/usr/bin/env python
#
# Copyright 2012 Ajay Narayan, Madhusudan C.S., Shobhit N.S.
#
# This file contains sections of code copied from the Python's CSV
# module's (marked as "copied from CSV documentation") documentation at
#
# http://docs.python.org/library/csv.html
#
# The copyright of this code is attributed to the original authors of
# the code and the if the license exists for those snippets, those snippets
# of code is still under the same original license. Authors of this
# file are not responsible in any way for those snippets of code.
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


"""Contains the parser functions and classes required to parse a tweet stored
as JSON.
"""


import codecs
import csv
import json
import os


class UTF8Recoder:
    """Iterator that reads an encoded stream and reencodes the input to UTF-8

    "copied from CSV documentation"
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")


def parse_json_files(directory):
    """Function that walks through the directory of JSON files containing tweets
    """
    data_dir_params = list(os.walk(directory))
    base_dir = data_dir_params[0][0]
    json_files = data_dir_params[0][2]

    json_list = []
    for f in json_files:
        # Default encoding of UTF-8 is assumed for the Python's JSON library.
        tweet_json = json.load(open(os.path.join(base_dir, f)))
        json_list.append(tweet_json)


def parse_training_corpus(corpus_file):
    """Parses the corpus file containing the training data using UTF-8 encoding.

    "copied from CSV documentation"
    """
    encoded_corpus = UTF8Recoder(open(corpus_file), 'utf-8')
    reader = csv.reader(encoded_corpus)
    return reader

