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


class GetFromCommentsHandler(webapp2.RequestHandler):

	def post(self):
		try:
			body=json.loads(self.request.body)
		except:
			self.error(400)
			self.response.write('400 invalid json in request body')
			return

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

		if 'word' in body:
			word=body['word']
		else:
			self.error(400)
			self.response.write('400 invalid word')
			return 

		if 'uid' in body:
			uid=body['uid']
			if not isinstance(uid,int):
				self.error(400)
				self.response.write('400 non integer id')
				return
		else:
			self.error(400)
			self.response.write('400 invalid uid')
			return

		try:
			gqlOcurrences = Comments.query(ndb.AND(Comments.uid==int(uid),Comments.word==word))
			ocurrences=gqlOcurrences.fetch(offset=offset,limit=limit)
		except:
			self.error(500)
			self.response.write('500 error querying database')
			return

		fbids=[0]*len(ocurrences);
		for i,ocurrence in enumerate(ocurrences):
			fbids[i]=(ocurrence.fbid);
		
		response={'data':fbids}
		self.response.write(json.dumps(response));
		

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

class DummyPutCommentHandler(webapp2.RequestHandler):
	def get(self):
		comment = Comments();
		comment.fbid = int(self.request.get('fbid'));
		comment.word = str(self.request.get('word'));
		comment.uid = int(self.request.get('uid'));
		comment.put();
		self.response.write("Success");



app = webapp2.WSGIApplication([
    ('/putcomment', PutCommentHandler),
    ('/comments', GetFromCommentsHandler)    
], debug=True)
