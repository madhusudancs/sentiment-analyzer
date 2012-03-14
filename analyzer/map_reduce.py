import cPickle
import json
import os
import re
import requests

from disco.core import Params
from disco.func import chain_reader

import datasettings
from disco.core import Job, result_iterator
from sklearn.feature_extraction.text import CountVectorizer


class Tokenizer(CountVectorizer):
      
     def transform(self,tweet):
         analyze = self.build_analyzer()
         return analyze(tweet)
      
def map(page,params):
    et = emitTokens() 
    try:
        r = requests.get("http://search.twitter.com/search.json",params={'q': "Apple", 'rpp': 100, 'page': '1'})
        page_of_tweets = json.loads(r.text.decode(charset, charset_error))

        for itr in page_of_tweets['results']:
            tweet_text = itr['text'] 
            tweet_id   = itr['id']
            tokens = et.transform(tweet_text) 
            for token in tokens:
                yield  (u" ".join(token),(tweet_id,1))

    except requests.ConnectionError:
        pass
    
def reduce(iter, params):
    from disco.util import kvgroup

    vectorizer = params.vectorizer

    for token, count_tuple_list in kvgroup(sorted(iter)):
        j = vectorizer.vocabulary_.get(token)
        if j is not None:
            new_dict = {}
            for doc_id, count in count_tuple_list:
                if doc_id not in new_dict:
                    new_dict[doc_id] = count
                else:
                    new_dict[doc_id] += count
            yield j, new_dict
        else:
            yield None, None
        
        
if __name__ == '__main__':
    from sklearn.feature_extraction.text import *
    path = os.path.join(datasettings.DATA_DIRECTORY, 'buckets.txt')
    vectorizer_file = open(os.path.join(datasettings.DATA_DIRECTORY, 'vectorizer.pickle'))
    vectorizer = cPickle.load(vectorizer_file)
    job = Job().run(input=['tag://data:bigtxt'],
                    map=map,
                    reduce=reduce,
                    mapreader=chain_reader,
                    params=Params(vectorizer=vectorizer))

count = 0
numCols = 0
docsDict = {}
rowsList = []
colsList = []
dataList = []
for word, dict in result_iterator(job.wait(show=True)):
    numCols += 1
    for docID, tfidf in dict:
        if docID not in docsDict:
            docsDict[docID] = count
            count += 1
        dataList.append(tfidf)
        rowsList.append(docsDict[docID])
        colsList.append(word)

classifier_file = open(os.path.join(datasettings.DATA_DIRECTORY, 'classifier.pickle'))
classifier = cPickle.load(classifier_file) 

feature_vector = scipy.sparse.coo_matrix(
            (dataList, (rowsList, colsList)), shape=(count, numCols))
feature_vector = feature_vector.tocsr() 
prediction = classifier.predict(feature_vector)
