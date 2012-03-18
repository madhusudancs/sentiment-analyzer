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

"""This module contains the models for the sentiment analyzer.
"""


import datetime

from email import utils

import mongoengine


mongoengine.connect('sentiment-analyzer')


class GeoLocation(mongoengine.EmbeddedDocument):
    """Holds the geo-coordinates.
    """
    latitude = mongoengine.FloatField()
    longtitude = mongoengine.FloatField()


class Tweet(mongoengine.Document):
    """Holds the tweet related information.
    """
    def __init__(self, *args, **kwargs):
        """Construct the tweet object.
        """
        if ('created_at' in kwargs and not isinstance(
          kwargs['created_at'], datetime.datetime)):
            kwargs['created_at'] = datetime.datetime(*utils.parsedate_tz(
                kwargs['created_at'])[:7])

        super(Tweet, self).__init__(*args, **kwargs)
        self.id_str = str(self.id_str)

    created_at = mongoengine.DateTimeField()
    from_user = mongoengine.StringField()
    from_user_id = mongoengine.IntField()
    from_user_id_str = mongoengine.StringField()
    from_user_name = mongoengine.StringField()
    geo = mongoengine.DictField(required=False)
    id_str = mongoengine.StringField(primary_key=True)
    in_reply_to_status_id = mongoengine.IntField(required=False)
    in_reply_to_status_id_str = mongoengine.StringField(max_length=1024,
                                                        required=False)
    iso_language_code = mongoengine.StringField(max_length=10)
    metadata = mongoengine.DictField()
    profile_image_url = mongoengine.StringField()
    profile_image_url_https = mongoengine.StringField()
    source = mongoengine.StringField()
    text = mongoengine.StringField()
    to_user = mongoengine.StringField(required=False)
    mongoengine.StringField(max_length=140)
    to_user_id = mongoengine.IntField(required=False)
    to_user_id_str = mongoengine.StringField(required=False)
    to_user_name = mongoengine.StringField(required=False)

    # 1 is positive, -1 is negative and 0 is neutral
    sentiment = mongoengine.IntField()


class FetchMetaData(mongoengine.Document):
    query_data = mongoengine.DictField()
    searched_at = mongoengine.DateTimeField()
    tweets = mongoengine.ListField(mongoengine.ReferenceField(Tweet))

