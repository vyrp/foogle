FACEBOOK_APP_ID = "394904207304456"
FACEBOOK_APP_SECRET = "e1651b27b530f8d441f92eca6407c147"

import facebook
import jinja2
import os
import urllib2
import webapp2

from google.appengine.ext import db
from webapp2_extras import sessions


class User(db.Model):
    id = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    access_token = db.StringProperty(required=True)
    
    @classmethod
    def find_or_create(cls, key_name, access_token):
        user = cls.get_by_key_name(key_name)
        
        if not user:
            profile = facebook.GraphAPI(access_token).get_object("me")
            user = User(key_name=str(profile["id"]), id=str(profile["id"]), access_token=access_token)
            user.put()
        elif user.access_token != access_token:
            user.access_token = access_token
            user.put()
            
        return user


class BaseHandler(webapp2.RequestHandler):
    @property
    def current_user(self):
        if self.session.get("user"):
            return self.session.get("user")
        
        cookie = facebook.get_user_from_cookie(self.request.cookies, FACEBOOK_APP_ID, FACEBOOK_APP_SECRET)
        if cookie:
            user = User.find_or_create(cookie["uid"], cookie["access_token"])
            self.session["user"] = {
                'id': user.id,
                'access_token': user.access_token
            }
            return self.session["user"]
            
        return None

    def dispatch(self):
        self.session_store = sessions.get_store(request=self.request)
        try:
            webapp2.RequestHandler.dispatch(self)
        finally:
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        return self.session_store.get_session()
        
    def render(self, template, values):
        self.response.write(jinja_environment.get_template(template).render(values))


class HomeHandler(BaseHandler):
    def get(self):
        user = self.current_user
        response = 'X'
        if user:
            graph = facebook.GraphAPI(self.current_user['access_token'])
            response = graph.fql('SELECT body, message_id FROM message WHERE thread_id IN (SELECT thread_id FROM thread WHERE folder_id=0) ORDER BY created_time DESC')
        
        values = {
            'facebook_app_id': FACEBOOK_APP_ID,
            'current_user': user,
            'response': response
        }
        self.render('templates/requests.html', values)


class LogoutHandler(BaseHandler):
    def get(self):
        if self.current_user is not None:
            self.session['user'] = None

        self.redirect('/requests/login')

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__))
)

app = webapp2.WSGIApplication(
    [
        ('/requests/login', HomeHandler),
        ('/requests/logout', LogoutHandler)
    ],
    config={'webapp2_extras.sessions': {'secret_key': 'poweokNsd98134knsadk&83'}},
    debug=True
)