# -*- coding: utf-8 -*-

import json
import re
import urllib
import urllib2
import webapp2
from models import *
from preprocess import preprocess


def FQL(query, access_token):
    params = {
        'q': query,
        'access_token': access_token
    }
    
    response = urllib2.urlopen('https://graph.facebook.com/fql?' + urllib.urlencode(params))
    response_json = json.loads(response.read())
    response.close()
    return response_json


class JsonRequestHandler(webapp2.RequestHandler):
    def parseJson(self):
        try:
            body = json.loads(self.request.body)
        except:
            self.error(400)
            self.response.write('400 invalid json in request body')
            return None
        return body


class SearchHandler(JsonRequestHandler):
    def getSearchParameters(self, body):
        offset = None
        if 'offset' in body:
            offset = body['offset']
            if not isinstance(offset, int):
                offset = None
        if not offset:
            offset = 0

        limit = None
        if 'limit' in body:
            limit = body['limit']
            if not isinstance(limit, int):
                limit=None
        if not limit:
            limit = 20 

        if 'uid' in body:
            uid = body['uid']
            if not isinstance(uid, int):
                self.error(400)
                self.response.write('400 non integer id')
                return None
        else:
            self.error(400)
            self.response.write('400 missing uid')
            return None

        return {"offset": offset, "limit": limit, "uid": uid}

    def getWord(self, body):
        if 'word' in body:
            word = body['word']
        else:
            self.error(400)
            self.response.write('400 missing word')
            return None
        return word

    def queryOcurrences(self, uid, word, offset, limit, cls):
        try:
            gqlOcurrences = cls.query(ndb.AND(cls.uid==int(uid), cls.word==word)).order(cls.timestamp)
            ocurrences = gqlOcurrences.fetch(offset=offset,limit=limit)
        except:
            self.error(500)
            self.response.write('500 error querying database')
            return None
        return ocurrences

    def processOcurrences(self, ocurrences):
        fbids = [0] * len(ocurrences);
        for i,ocurrence in enumerate(ocurrences):
            fbids[i] = {'fbid': ocurrence.fbid, 'timestamp': ocurrence.timestamp}
        return fbids

    def search(self, cls, body=None, word=None):
        if body == None:
            body = self.parseJson()
            if body == None:
                return None

        parameters = self.getSearchParameters(body)
        if parameters == None:
            return None
        offset = parameters['offset'];
        limit = parameters['limit'];
        uid = parameters['uid'];

        if word == None:
            word = self.getWord(body);
            if word == None:
                return None
        
        ocurrences = self.queryOcurrences(uid=uid, word=word, offset=offset, limit=limit, cls=cls)
        if ocurrences == None:
            return None
        fbids = self.processOcurrences(ocurrences)
        fbids = [dict(y) for y in set(tuple(x.items()) for x in fbids)]
        if fbids == None:
            return None

        response = {'data': fbids}
        return response


class PutCommentHandler(webapp2.RequestHandler):
    def post(self):
        try:
            body = json.loads(self.request.body)
        except:
            self.error(400)
            self.response.write('400 invalid json in request body')
            return
        comment = Comments(uid=body['uid'], fbid=body['fbid'], word=body['word']);
        comment.put()
        response = {'status': 'success'}
        self.response.write(json.dumps(response));


class PutMessageHandler(webapp2.RequestHandler):
    def post(self):
        try:
            body = json.loads(self.request.body)
        except:
            self.error(400)
            self.response.write('400 invalid json in request body')
            return
        message = Messages(uid=body['uid'], fbid=body['fbid'], word=body['word']);
        message.put()
        response = {'status': 'success'}
        self.response.write(json.dumps(response));


class MultiSearchHandler(SearchHandler):
    def getSentence(self, body):
        if 'sentence' in body:
            sentence = body['sentence']
        else:
            self.error(400)
            self.response.write('400 missing sentence')
            return None
        return sentence
    
    def createFbidHash(self, el):
        if not 'fbid' in el:
            return None
        if not 'timestamp' in el:
            return None
        if not 'type' in el:
            el['type']='u'

        return el['fbid'] + "!" + str(el['fbid']) + "!" + el['type']

    def getRate(self, el):
        if not 'rate' in el:
            return 1
        return el['rate']

    def getObjectFromHash(self, key):
        keys = key.split('!')

        if len(keys) >= 3:
            fbid = keys[0]
            timestamp = keys[1]
            t=keys[2]
        elif len(keys)>=2:
            fbid = keys[0]
            timestamp = keys[1]
            t='u'
        else:
            fbid = keys
            timestamp = 0
            t='u'

        return {'fbid': fbid, 'timestamp': int(timestamp),'type':t}

    def mergeResults(self, results):
        allOcurrences = {}
        for result in results:
            if not 'data' in result:
                continue
            data = result['data']
            for el in data:
                fbid = self.createFbidHash(el)
                if fbid == None:
                    continue
                if not fbid in allOcurrences:
                    allOcurrences[fbid] = 0

                allOcurrences[fbid] += self.getRate(el)

        sortedKeys = sorted(allOcurrences, key=allOcurrences.get, reverse=True)
        
        fbids = [{}] * len(sortedKeys); # Possivel fonte de BUG!!!!

        for i, key in enumerate(sortedKeys):
            fbids[i] = self.getObjectFromHash(key);
            fbids[i]['rate'] = allOcurrences[key];

        return fbids

    def multi_search(self, cls,body=None):
        if body==None:
            body = self.parseJson()
        if body == None:
            return
        sentence = self.getSentence(body)
        if sentence == None:
            return
        words = [preprocess(word) for word in re.split(r"\s", sentence)]
        
        results = []
        for word in words:
            if word == "":
                continue
            result = self.search(cls, body, word)
            if result:
                results.append(result)
        
        fbids = self.mergeResults(results)
        response = {'data': fbids}
        return response




class GetFromAllHandler(MultiSearchHandler):

    def setType(self,result,t):
        if 'data' in result:
            for fbid in result['data']:
                fbid['type']=t;

    def post(self):
        body=self.parseJson();
        if body==None:
            return
        results = []
        filt='cmp'
        if 'filter' in body:
            filt=body['filter']
        
        if 'p' in filt:
            result = self.multi_search(Posts)
            if result:
                self.setType(result,'p')
                results.append(result)

        if 'm' in filt:
            result = self.multi_search(Messages)
            if result:
                self.setType(result,'m')
                results.append(result)

        if 'c' in filt:
            result = self.multi_search(Comments)
            if result:
                self.setType(result,'c')
                results.append(result)
        
        fbids = self.mergeResults(results)
        response = {'data': fbids}    
        self.response.write(json.dumps(response))


class DummyCreateTimestamps(webapp2.RequestHandler):
    def get(self):
        comments = Comments.gql("WHERE uid>0");
        for i, comment in enumerate(comments):
            comment.timestamp = i
            comment.put()
        messages = Messages.gql("WHERE uid>0");
        for i, message in enumerate(messages):
            message.timestamp = i
            message.put()


class PopulateHandler(webapp2.RequestHandler):
    def post(self):
        status = 'success'
        
        try:
            access_token = self.request.get('access_token')
            response = FQL('SELECT uid FROM user WHERE uid=me()', access_token)
            
            if 'data' in response:
                uid = response['data'][0]['uid']
                user = User.find_or_create(str(uid))
                user.access_token = access_token
                user.put()
            elif 'error' in response:
                status = 'error'
            
        except:
            status = 'error'
        
        self.response.write(json.dumps({
            'status': status
        }))
