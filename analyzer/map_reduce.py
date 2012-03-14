import json
import re
import requests
from disco.core import Job, result_iterator
from sklearn.feature_extraction.text import CountVectorizer

class emitTokens(CountVectorizer):
      
     def transform(self,tweet):
         analyze = self.build_analyzer()
         return analyze(tweet)
      
    




def map(page,params):
    DEFAULT_TOKEN_PATTERN = ur"\b\w\w+\b"
    stop_words = []
    token_pattern = DEFAULT_TOKEN_PATTERN   
    et = emitTokens() 
    try:
        r = requests.get("http://search.twitter.com/search.json",params={'q': "Apple", 'rpp': 100, 'page': "1"})
        page_of_tweets = json.loads(r.text.encode("utf-8"))
        min_n = 1     

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

    vectorizer_file = open(os.path.join(datasettings.DATA_DIRECTORY, 'vectorizer.pickle'))
    vectorizer = cPickle.load(vectorizer_file)

    for word, counts in kvgroup(sorted(iter)):
        j = vectorizer.vocabulary.get(word)
        if j is not None:
            newDict = {}
            for docID, count in countTupleList:
                if docID not in newDict.keys():
                    newDict[docID] = count
                else:
                    newDict[docID] += count
            yield j, newDict
        else:
            yield None, None
        
        
if __name__ == '__main__':
    job = Job().run(input=["file:///home/mask/python/cs221/sentiment-analyzer/analyzer/buckets.txt"],
                    map=map,
                    reduce=reduce)

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
