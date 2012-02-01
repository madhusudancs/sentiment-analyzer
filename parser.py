#!/usr/bin/env python
#
# Copyright 2012 Ajay Narayan, Madhusudan C.S., Shobit N.S.
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


import json
import os


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

