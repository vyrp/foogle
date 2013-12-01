# -*- coding: utf-8 -*- 

#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import json
import re
from google.appengine.ext import ndb

commonWords=re.compile(ur"^(por|pel[oa]s?|ao?s?|d[aeo]s?|duma?s?|em|nas?|entre|com|sem|os?|ou|se|que|for|at|the|and|or|in|that|by)$")

def normalize(word):
    word=word.lower()
    word=re.sub(ur'[áâàãä]',r'a',word)
    word=re.sub(ur'[éêèë]',r'e',word)
    word=re.sub(ur'[íîìï]',r'i',word)
    word=re.sub(ur'[óôòõö]',r'o',word)
    word=re.sub(ur'[úûùü]',r'u',word)
    word=re.sub(ur'[ýÿ]',r'y',word)
    word=re.sub(ur'ç',r'c',word)
    word=re.sub(ur'ñ',r'n',word)
    word=re.sub(ur'^[^a-zA-Z0-9]+',r'',word)
    word=re.sub(ur'[^a-zA-Z0-9]+$',r'',word)
    word=re.sub(ur'[^a-zA-Z0-9]',r'',word)
    return word

def simplify(word):
    return word

def isCommon(word):
    if commonWords.match(word):
        return True
    return False

def preprocess(word):
    word=normalize(word)
    if isCommon(word):
        return ""
    return simplify(word)





class Comments(ndb.Model):
    uid = ndb.IntegerProperty();
    fbid = ndb.StringProperty();
    word = ndb.StringProperty();
    timestamp = ndb.IntegerProperty();
    

class Posts(ndb.Model):
    uid = ndb.IntegerProperty();
    fbid = ndb.StringProperty();
    word = ndb.StringProperty();
    timestamp = ndb.IntegerProperty();
    

class Messages(ndb.Model):
    uid = ndb.IntegerProperty();
    fbid = ndb.StringProperty();
    word = ndb.StringProperty();
    timestamp = ndb.IntegerProperty();

class SearchHandler(webapp2.RequestHandler):
    def parseJson(self):
        try:
            body=json.loads(self.request.body)
        except:
            self.error(400)
            self.response.write('400 invalid json in request body')
            return None
        return body

    def getSearchParameters(self,body):
        offset=None
        if 'offset' in body:
            offset=body['offset']
            if not isinstance(offset,int):
                offset=None
        if not offset:
            offset=0

        limit=None
        if 'limit' in body:
            limit=body['limit']
            if not isinstance(limit,int):
                limit=None
        if not limit:
            limit=20 

        if 'uid' in body:
            uid=body['uid']
            if not isinstance(uid,int):
                self.error(400)
                self.response.write('400 non integer id')
                return None
        else:
            self.error(400)
            self.response.write('400 missing uid')
            return None

        return {"offset":offset,"limit":limit,"uid":uid}

    def getWord(self,body):
        if 'word' in body:
            word=body['word']
        else:
            self.error(400)
            self.response.write('400 missing word')
            return None
        return word

    def queryOcurrences(self,uid,word,offset,limit,cls):
        try:
            gqlOcurrences = cls.query(ndb.AND(cls.uid==int(uid),cls.word==word)).order(cls.timestamp)
            ocurrences=gqlOcurrences.fetch(offset=offset,limit=limit)
        except:
            self.error(500)
            self.response.write('500 error querying database')
            return None
        return ocurrences

    def processOcurrences(self,ocurrences):
        fbids=[0]*len(ocurrences);
        for i,ocurrence in enumerate(ocurrences):
            fbids[i]={'fbid':ocurrence.fbid,'timestamp':ocurrence.timestamp}
        return fbids

    def search(self,cls,body=None,word=None):
        if body==None:
            body=self.parseJson()
            if body==None:
                return None

        parameters=self.getSearchParameters(body)
        if parameters==None:
            return None
        offset=parameters['offset'];
        limit=parameters['limit'];
        uid=parameters['uid'];

        if word==None:
            word=self.getWord(body);
            if word==None:
                return None
        
        ocurrences=self.queryOcurrences(uid=uid,word=word,offset=offset,limit=limit,cls=cls)
        if ocurrences==None:
            return None
        fbids=self.processOcurrences(ocurrences)
        fbids=[dict(y) for y in set(tuple(x.items()) for x in fbids)]
        if fbids==None:
            return None

        response={'data':fbids}
        return response
    


        

class PutCommentHandler(webapp2.RequestHandler):
    def post(self):
        try:
            body=json.loads(self.request.body)
        except:
            self.error(400)
            self.response.write('400 invalid json in request body')
            return
        comment= Comments(uid=body['uid'],fbid=body['fbid'],word=body['word']);
        comment.put()
        response={'status':'success'}
        self.response.write(json.dumps(response));


class PutMessageHandler(webapp2.RequestHandler):
    def post(self):
        try:
            body=json.loads(self.request.body)
        except:
            self.error(400)
            self.response.write('400 invalid json in request body')
            return
        message= Messages(uid=body['uid'],fbid=body['fbid'],word=body['word']);
        message.put()
        response={'status':'success'}
        self.response.write(json.dumps(response));


class MultiSearchHandler(SearchHandler):
    def getSentence(self,body):
        if 'sentence' in body:
            sentence=body['sentence']
        else:
            self.error(400)
            self.response.write('400 missing sentence')
            return None
        return sentence

    

    
    def createFbidHash(self,el):
        if not 'fbid' in el:
            return None
        if not 'timestamp' in el:
            return None
        return el['fbid']+"!"+str(el['fbid'])

    def getRate(self, el):
        if not 'rate' in el:
            return 1
        return el['rate']

    def getObjectFromHash(self,key):
        keys=key.split('!')
        if len(keys)>=2:
            fbid=keys[0]
            timestamp=keys[0]
        else:
            fbid=keys
            timestamp=0

        return {'fbid':fbid,'timestamp':timestamp}

    def mergeResults(self,results):
        allOcurrences={}
        for result in results:
            if not 'data' in result:
                continue
            data=result['data']
            for el in data:
                fbid=self.createFbidHash(el)
                if fbid==None:
                    continue
                if not fbid in allOcurrences:
                    allOcurrences[fbid]=0

                allOcurrences[fbid]+=self.getRate(el)

        sortedKeys=sorted(allOcurrences,key=allOcurrences.get,reverse=True)
        
        fbids=[{}]*len(sortedKeys);

        for i,key in enumerate(sortedKeys):
            fbids[i]=self.getObjectFromHash(key);
            fbids[i]['rate']=allOcurrences[key];

        return fbids

    def multi_search(self,cls):
        body=self.parseJson()
        if body==None:
            return
        sentence=self.getSentence(body)
        if sentence==None:
            return
        words=[preprocess(word) for word in re.split(r"\s",sentence)]
        
        results=[]
        for word in words:
            if word=="":
                continue
            result=self.search(cls,body,word)
            if result:
                results.append(result)
        
        fbids=self.mergeResults(results)
        response={'data':fbids}
        return response

class GetFromCommentsHandler(MultiSearchHandler):
    def post(self):
        response=self.multi_search(Comments)
        if response==None:
            return
        self.response.write(json.dumps(response))



class GetFromMessagesHandler(MultiSearchHandler):        
    def post(self):
        response=self.multi_search(Messages)
        if response==None:
            return
        self.response.write(json.dumps(response))

class GetFromPostsHandler(MultiSearchHandler):
    def post(self):
        response=self.multi_search(Posts)
        if response==None:
            return
        self.response.write(json.dumps(response))


class GetFromAllHandler(MultiSearchHandler):
    def post(self):
        results=[]
        result=self.multi_search(Posts)
        if result:
            results.append(result)

        result=self.multi_search(Messages)
        if result:
            results.append(result)

        result=self.multi_search(Comments)
        if result:
            results.append(result)
        if len(results)==0:
            return
        fbids=self.mergeResults(results)
        response={'data':fbids}    
        self.response.write(json.dumps(response))



class DummyCreateTimestamps(webapp2.RequestHandler):
    def get(self):
        comments=Comments.gql("WHERE uid>0");
        for i,comment in enumerate(comments):
            comment.timestamp=i
            comment.put()
        messages=Messages.gql("WHERE uid>0");
        for i,message in enumerate(messages):
            message.timestamp=i
            message.put()

app = webapp2.WSGIApplication([
    ('/putcomment', PutCommentHandler),
    ('/putmessage', PutMessageHandler),
    ('/comments', GetFromCommentsHandler),
    ('/messages', GetFromMessagesHandler),
    ('/posts', GetFromPostsHandler),
    ('/search', GetFromAllHandler) ,
    ('/timestamp', DummyCreateTimestamps)
], debug=True)
