import json
import re
import requests
from disco.core import Job, result_iterator

def map(page,params):
    DEFAULT_TOKEN_PATTERN = ur"\b\w\w+\b"
    stop_words = []
    token_pattern = DEFAULT_TOKEN_PATTERN   
    try:
        r = requests.get("http://search.twitter.com/search.json",params={'q': "Apple", 'rpp': 100, 'page': "1"})
        page_of_tweets = json.loads(r.text.encode("utf-8"))
        min_n = 1     

        for itr in page_of_tweets['results']:
            tweet_text = itr['text'] 
            tweet_id   = itr['id']
            compiled   = re.compile(token_pattern, re.UNICODE)
            tokens     = compiled.findall(tweet_text)
            max_n      = len(tokens) 
            # handle token n-grams
            if min_n != 1 or max_n != 1:
               original_tokens = tokens
               tokens = []
               n_original_tokens = len(original_tokens)
               for n in xrange(min_n,
                               min(max_n + 1, n_original_tokens + 1)):
                  for i in xrange(n_original_tokens - n + 1):
                      # handle stop words
                      if stop_words is not None:
                         tokens = [w for w in tokens if w not in stop_words]
                      yield (original_tokens[i: i + n],1)
  
    except requests.ConnectionError:
        pass
    
def reduce(iter, params):
    from disco.util import kvgroup
    for word, counts in kvgroup(sorted(iter)):
        yield word, sum(counts)
        
        
if __name__ == '__main__':
    job = Job().run(input=["file:///home/mask/python/cs221/sentiment-analyzer/analyzer/buckets.txt"],
                    map=map,
                    reduce=reduce)

