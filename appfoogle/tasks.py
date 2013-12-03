import json
import logging
import urllib
import webapp2
from google.appengine.api import urlfetch
from google.appengine.runtime import DeadlineExceededError
from models import *
from preprocess import preprocess


class FacebookError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def FQL(query, access_token):
    params = {
        'q': query,
        'access_token': access_token
    }

    response = urlfetch.fetch('https://graph.facebook.com/fql?' + urllib.urlencode(params))
    if response.status_code == 200:
        response = json.loads(response.content)
        if 'error' in response:
            logging.error('Facebook error: ' + str(response['error']) + '\nQuery: ' + query)
        elif 'data' not in response:
            logging.error('Facebook unknown error: ' + str(response) + '\nQuery: ' + query)
        return response
    else:
        raise FacebookError('Facebook FQL Error: ' + str(response.status_code) + ' (' + query + ')')


def FQL_multi(access_token, queries):
    params = {
        'q': json.dumps(queries),
        'access_token': access_token
    }

    response = urlfetch.fetch('https://graph.facebook.com/fql?' + urllib.urlencode(params))
    if response.status_code == 200:
        response = json.loads(response.content)
        if 'error' in response:
            logging.error('Facebook error: ' + str(response['error']) + '\nQuery: ' + str(queries))
        elif 'data' not in response:
            logging.error('Facebook unknown error: ' + str(response) + '\nQuery: ' + str(queries))
        return response
    else:
        raise RuntimeError('Facebook FQL Error: ' + str(response.status_code) + ' (' + str(queries) + ')')


def FQL_batch(access_token, queries):
    params = {
        'access_token': access_token,
        'batch': [
            {
                'method': 'POST',
                'relative_url': 'method/fql.query?' + urllib.urlencode({'query': 'SELECT uid, name FROM user WHERE uid=me()'})  # queries aqui
            }
        ]
    }
    response = urlfetch.fetch(url='https://graph.facebook.com', payload=urllib.urlencode(params), method=urlfetch.POST)
    if response.status_code == 200:
        response = json.loads(response.content)
        return response
    else:
        raise RuntimeError('Facebook FQL Error: ' + str(response.status_code) + ' (' + str('TEST') + ')')


def populate(access_token, oldest_msg_ts=0, oldest_pst_ts=0, oldest_cmt_ts=0):
    logging.debug('<<<<<< Deferred: populate')

    response = FQL('SELECT uid FROM user WHERE uid=me()', access_token)
    uid = str(response['data'][0]['uid'])
    user = User.find_or_create(uid)
    user.access_token = access_token

    if user.is_populating:
        user.put()
        return

    user.is_populating = True
    user.put()

    try:
        # response = FQL('SELECT body, message_id, thread_id, created_time FROM message WHERE thread_id IN (SELECT thread_id FROM thread WHERE folder_id=0 LIMIT 50) ORDER BY created_time DESC LIMIT 1500', access_token)
        # logging.debug('Facebook response: data: ' + str(len(response['data']) if 'data' in response else None))

        # queries = {
            # 'threads': 'SELECT thread_id FROM thread WHERE folder_id=0 LIMIT 50',
            # 'messages': 'SELECT body, message_id FROM message WHERE thread_id IN (SELECT thread_id FROM #threads) ORDER BY created_time DESC LIMIT 1500'
        # }
        # response = FQL_multi(access_token, queries)
        # logging.debug('Facebook response:\n' + str(response))

        response = FQL_batch(access_token, 'TEST')
        logging.debug('Facebook response:\n' + str(response))
        
        # if 'data' in response:
            # logging.debug("response['data']: " + str(response['data']))
        # elif 'error' in response:
            # logging.warning('Facebook error: ' + str(response['error']))
        # else:
            # logging.warning('Unknown facebook error: ' + str(response))

    except DeadlineExceededError as e:
        logging.exception('Task: time limit exceeded')
        raise e

    except Exception as e:
        logging.exception(e)
        raise e

    finally:
        user = User.find_or_create(uid)
        user.is_populating = False
        user.put()

        logging.debug('Deferred: populate >>>>>>')
