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


from django.db import models

# Create your models here.
#Tweet table : Holds the tweet text and meta data information.

class Tweet(models.Model):
      tweet_text  = models.CharField(max_length=140)
      tweet_stamp = models.DateTimeField('Tweet Stamp')
      def __unicode__(self):
          return self.tweet_text      

class MetaData(models.Model):
      search_key   = models.CharField(max_length = 30)
      search_stamp = models.DateTimeField('Query Stamp') 
      def __unicode__(self):
          return self.search_key
