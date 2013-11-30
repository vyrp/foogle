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
	def get(self):
		word=str(self.request.get('word'));
		uid=str(self.request.get('uid'));
		ocurrences = Comments.query(ndb.AND(Comments.uid==int(uid),Comments.word==word)) #ndb.gql("SELECT fbid FROM Comments WHERE uid=" + uid + " AND word=\'" + word + "\'" );
		response="";
		for ocurrence in ocurrences:
			response+=(str(ocurrence.fbid) + ",");
		self.response.write(response[0:-1]	);
		

class DummyPutCommentHandler(webapp2.RequestHandler):
	def get(self):
		comment = Comments();
		comment.fbid = int(self.request.get('fbid'));
		comment.word = str(self.request.get('word'));
		comment.uid = int(self.request.get('uid'));
		comment.put();
		self.response.write("Success");




app = webapp2.WSGIApplication([
    ('/putcomment', DummyPutCommentHandler),
    ('/comments', GetFromCommentsHandler)    
], debug=True)
