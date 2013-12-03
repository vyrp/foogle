import json
import logging
import urllib
import webapp2
from google.appengine.api import urlfetch
from google.appengine.ext import deferred
from google.appengine.runtime import DeadlineExceededError
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

        
def FQL_multi(access_token, *queries):
    params = {
        'access_token': access_token,
        'batch': [{}]
    }

    response = urlfetch.fetch('https://graph.facebook.com/fql?' + urllib.urlencode(params))
    if response.status_code == 200:
        return json.loads(response.content)
    else:
        raise RuntimeError('Facebook FQL Error: ' + str(response.status_code))


def _populate(access_token, oldest_msg_ts=0, oldest_pst_ts=0, oldest_cmt_ts=0):
    try:
        logging.debug('>>>>>> Deferred: populate')

        response = FQL('SELECT body, message_id, thread_id, created_time FROM message WHERE thread_id IN (SELECT thread_id FROM thread WHERE folder_id=0 LIMIT 50) ORDER BY created_time DESC LIMIT 1500', access_token)
        logging.debug('Facebook response: data: ' + str('data' in response))
        
        # queries = {
            # 'threads': 'SELECT thread_id FROM thread WHERE folder_id=0 LIMIT 50',
            # 'messages': 'SELECT body, message_id FROM message WHERE thread_id IN #threads LIMIT 50 ORDER BY created_time DESC'
        # }
        # response = FQL_multi(access_token, queries)
        # logging.debug('Facebook response:\n ' + str(response))
        
        # if 'data' in response:
            # logging.debug("response['data']: " + str(response['data']))
        # elif 'error' in response:
            # logging.warning('Facebook error: ' + str(response['error']))
        # else:
            # logging.warning('Unknown facebook error: ' + str(response))

    except DeadlineExceededError as e:
        logging.exception('Task: time limit exceeded')

    except Exception as e:
        logging.exception(e)

    finally:
        user = User.find_or_create(uid)
        user.is_populating = False
        user.put()

        logging.debug('Deferred: populate >>>>>>')


def start_populate_task(uid, access_token):
    user = User.find_or_create(uid)
    if not user.is_populating:
        user.is_populating = True
        user.put()
        deferred.defer(_populate, access_token, _queue='populate')
