import json
import logging
import urllib
import webapp2
from google.appengine.api import urlfetch
from google.appengine.ext import deferred
from models import *
from preprocess import preprocess


def FQL(query, access_token):
    params = {
        'q': query,
        'access_token': access_token
    }

    response = urlfetch.fetch('https://graph.facebook.com/fql?' + urllib.urlencode(params))
    if response.status_code == 200:
        return json.loads(response.content)
    else:
        raise RuntimeError('Facebook FQL Error: ' + str(response.status_code))


def _populate(uid, access_token, oldest_msg_ts=0, oldest_pst_ts=0, oldest_cmt_ts=0):
    logging.info('>>>>>> Deferred: populate')

    # Messages
    response = FQL("SELECT body, message_id FROM message WHERE thread_id IN (SELECT thread_id FROM thread WHERE folder_id=0) ORDER BY created_time DESC", access_token)
    if 'data' in response:
        pass  # OK
    else:
        pass  # Error

    # Posts
    response = FQL("SELECT post_id, message FROM stream WHERE source_id=me() ORDER BY created_time DESC", access_token)
    if 'data' in response:
        pass  # OK
    else:
        pass  # Error

    response = FQL("SELECT post_id, message FROM stream WHERE source_id IN (SELECT gid FROM group_member WHERE uid=me()) ORDER BY created_time DESC", access_token)
    if 'data' in response:
        pass  # OK
    else:
        pass  # Error

    response = FQL("SELECT post_id, message FROM stream WHERE filter_key IN(SELECT filter_key FROM stream_filter WHERE type = 'newsfeed' AND uid=me()) AND is_hidden=0 ORDER BY created_time DESC", access_token)
    if 'data' in response:
        pass  # OK
    else:
        pass  # Error

    # Comments
    response = FQL("SELECT text, id FROM comment WHERE post_id IN (SELECT post_id FROM stream WHERE source_id IN (SELECT gid FROM group_member WHERE uid=me())) ORDER BY time DESC", access_token)
    if 'data' in response:
        pass  # OK
    else:
        pass  # Error

    user = User.find_or_create(uid)
    user.is_populating = False
    user.put()

    logging.info('Deferred: populate >>>>>>')


def start_populate_task(uid, access_token):
    user = User.find_or_create(uid)
    user.is_populating = True
    user.put()
    deferred.defer(_populate, uid, access_token, _queue='populate')
