# -*- coding: utf-8 -*-

import sys
import tweepy
import webbrowser

# Query terms
Q = sys.argv[1:]

# Got these keys for my account
CONSUMER_KEY = 'aOdeHWvJLhU8eXNHC6Zhw'
CONSUMER_SECRET = '5J9IkSSMp7TuKPRbGrb9YSkHFUhKvTBR43l6Iee5M'

ACCESS_TOKEN = '222822849-YAPQ6rO6rH9GYNnkBkaqW2mFAgc1tOU1cRdPfOnN'
ACCESS_TOKEN_SECRET = 'KSK8oJ2Ob2R3WpuEz71NezR9Sh0jpXcKfyglLLEc'

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)


class CustomStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        try:
            print "%s" % (status.text)
        except Exception, e:
            print >> sys.stderr, 'Encountered Exception:', e
            pass


    def on_error(self, status_code):
        print >> sys.stderr, 'Encountered error with status code:', status_code
        return True # Don't kill the stream


    def on_timeout(self):
        print >> sys.stderr, 'Timeout...'
        return True # Don't kill the stream


# Create a streaming API and set a timeout value of 60 seconds.
streaming_api = tweepy.streaming.Stream(auth, CustomStreamListener(), timeout=60)

print >> sys.stderr, 'Filtering the public timeline for "%s"' % (' '.join(sys.argv[1:]),)

streaming_api.filter(follow=None, track=Q)

