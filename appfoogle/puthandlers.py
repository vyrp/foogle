import webapp2
from models import *
from preprocess import preprocess
import re
from google.appengine.ext import ndb


def clamp(word):
    return word if len(word) < 500 else word[0:500]


class SentencePutter():

    def __init__(self, cls):
        self.modelList = set()
        self.cls = cls
        self.count = 0

    def put(self, sentence, uid, fbid, timestamp):
        wordList = re.split(r"\s", sentence)
        wordList = [preprocess(word) for word in wordList]
        modelList = [(uid, fbid, word, timestamp) for word in wordList if word != ""]
        self.modelList = self.modelList.union(modelList)
        if(len(self.modelList) >= 1000):
            self.flush()

    def flush(self):
        if self.count > 2000:
            return
        modelList = [self.cls(uid_word=x[0] + "_" + x[2], fbid=x[1], timestamp=x[3]) for x in self.modelList]
        ndb.put_multi(list(modelList))
        self.count += len(modelList)
        self.modelList = set()
