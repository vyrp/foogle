import json
import urllib
import urllib2
import webapp2

from google.appengine.ext import ndb


def FQL(query, access_token):
    params = {
        'q': query,
        'access_token': access_token
    }
    
    response = urllib2.urlopen('https://graph.facebook.com/fql?' + urllib.urlencode(params))
    response_json = json.loads(response.read())
    response.close()
    return response_json


class User(ndb.Model):
    uid = ndb.StringProperty(required=True)
    access_token = ndb.StringProperty()
    
    @classmethod
    def find_or_create(cls, uid):
        user = cls.query(cls.uid == uid).get()
        if not user:
            user = User(uid=uid)
        return user


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


app = webapp2.WSGIApplication([
    ('/populate', PopulateHandler)
], debug=True)