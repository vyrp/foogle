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
from google.appengine.ext import ndb


class Comments(ndb.Model):
	uid = ndb.IntegerProperty();
	fbid = ndb.IntegerProperty();
	word = ndb.StringProperty();
	

class Posts(ndb.Model):
	uid = ndb.IntegerProperty();
	fbidh = ndb.IntegerProperty();
	fbidl = ndb.IntegerProperty();
	word = ndb.StringProperty();
	

class Messages(ndb.Model):
	uid = ndb.IntegerProperty();
	fbid = ndb.IntegerProperty();
	word = ndb.StringProperty();


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
			gqlOcurrences = cls.query(ndb.AND(Comments.uid==int(uid),Comments.word==word))
			ocurrences=gqlOcurrences.fetch(offset=offset,limit=limit)
		except:
			self.error(500)
			self.response.write('500 error querying database')
			return None
		return ocurrences

	def processOcurrences(self):
		pass

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

		if 'words' in body:
			words=body['words']
			if not isinstance(words,list):
				self.error(400)
				self.response.write('400 words is not an array')
				return
		else:
			self.error(400)
			self.response.write('400 invalid words')
			return 

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

	def normalize(self,word):
		return word

	def createFbidHash(self,el):
		return None

	def multi_search(self,cls):
		body=self.parseJson()
		if body==None:
			return
		sentence=self.getSentence(body)
		if sentence==None:
			return
		words=[self.normalize(word) for word in sentence.split(" ")]
		
		results=[]
		for word in words:
			result=self.search(cls,body,word)
			if result:
				results.append(result)
		
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
				allOcurrences[fbid]+=1

		sortedKeys=sorted(allOcurrences,key=allOcurrences.get,reverse=True)
		
		fbids=[{}]*len(sortedKeys);

		for i,key in enumerate(sortedKeys):
			fbids[i]=self.getObjectFromHash(key);
			fbids[i]['rate']=allOcurrences[key];

		response={'data':fbids}
		return response

class GetFromCommentsHandler(MultiSearchHandler):
	def processOcurrences(self,ocurrences):
		fbids=[0]*len(ocurrences);
		for i,ocurrence in enumerate(ocurrences):
			fbids[i]={'fbid':ocurrence.fbid}
		return fbids

	def createFbidHash(self,el):
		if not 'fbid' in el:
			return None
		return el['fbid']

	def getObjectFromHash(self,key):
		return {'fbid':key}

	def post(self):
		response=self.multi_search(Comments)
		if response==None:
			return
		self.response.write(json.dumps(response))



class GetFromMessagesHandler(MultiSearchHandler):
	def processOcurrences(self,ocurrences):
		fbids=[0]*len(ocurrences);
		for i,ocurrence in enumerate(ocurrences):
			fbids[i]={'fbid':ocurrence.fbid}
		return fbids

	def createFbidHash(self,el):
		if not 'fbid' in el:
			return None
		return el['fbid']

	def getObjectFromHash(self,key):
		return {'fbid':key}
	
	def post(self):
		response=self.multi_search(Messages)
		if response==None:
			return
		self.response.write(json.dumps(response))

class GetFromPostsHandler(MultiSearchHandler):
	def processOcurrences(self,ocurrences):
		fbids=[0]*len(ocurrences);
		for i,ocurrence in enumerate(ocurrences):
			fbids[i]={'fbidl':ocurrence.fbidl,'fbidh':ocurrence.fbidh}
		return fbids

	def createFbidHash(self,el):
		if not 'fbidl' in el:
			return None
		if not 'fbidh' in el:
			return None
		return str(el['fbidl'])+'_'+str(el['fbidh'])

	def getObjectFromHash(self,key):
		return {'fbid':key}

	def post(self):
		response=self.multi_search(Posts)
		if response==None:
			return
		self.response.write(json.dumps(response))


app = webapp2.WSGIApplication([
    ('/putcomment', PutCommentHandler),
    ('/comments', GetFromCommentsHandler),
    ('/messages', GetFromMessagesHandler),
    ('/posts', GetFromPostsHandler)   
], debug=True)
