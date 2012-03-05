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
