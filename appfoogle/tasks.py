import logging
import webapp2
from google.appengine.ext import deferred
from models import *


def _populate(uid, access_token, oldest_msg_ts=0, oldest_pst_ts=0, oldest_cmt_ts=0):
    logging.info("DEFERRED: _populate")

    comment = Comments(uid='007', fbid='12ab34', word='teste', timestamp=123456)
    comment.put()


def start_populate_task(uid, access_token):
    deferred.defer(_populate, uid, access_token, _queue='populate')
