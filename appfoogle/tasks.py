import json
import logging
import models
import time
import urllib
from google.appengine.api import urlfetch
from google.appengine.runtime import DeadlineExceededError
from puthandlers import SentencePutter
from preprocess import preprocess


YEAR = 365 * 24 * 3600L


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
        raise FacebookError('Facebook FQL Error: ' + str(response.status_code) + ' (' + str(queries) + ')')


def getAllMessages(access_token, user, now, year_ago, important_friends):
    queries = {
        'threads0': 'SELECT thread_id, updated_time, message_count, recipients FROM thread WHERE folder_id=0 ORDER BY updated_time DESC LIMIT 50 OFFSET 0',
        'threads50': 'SELECT thread_id, updated_time, message_count, recipients FROM thread WHERE folder_id=0 ORDER BY updated_time DESC LIMIT 50 OFFSET 50',
        'threads100': 'SELECT thread_id, updated_time, message_count, recipients FROM thread WHERE folder_id=0 ORDER BY updated_time DESC LIMIT 50 OFFSET 100',
        'threads150': 'SELECT thread_id, updated_time, message_count, recipients FROM thread WHERE folder_id=0 ORDER BY updated_time DESC LIMIT 50 OFFSET 150'
    }
    response = FQL_multi(access_token, queries)

    # Begin Friends
    tmp = []
    for result_set in response['data']:
        tmp.extend([{'message_count': thread['message_count'], 'recipients': thread['recipients']} for thread in result_set['fql_result_set']])
    
    tmp = [item['recipients'] for item in sorted(tmp, key=lambda item: item['message_count'], reverse=True)[0:10]]
    for sublist in tmp:
        important_friends.extend(map(str, sublist))
    # End Friends
    
    threads_ids = []
    for result_set in response['data']:
        threads_ids.extend([str(thread['thread_id']) for thread in result_set['fql_result_set'] if int(thread['updated_time']) > user.last_timestamp])

    if len(threads_ids) == 0:
        logging.debug('Facebook: no new threads')
        return

    threads = dict(zip(threads_ids, [0] * len(threads_ids)))

    offset = 0
    active_threads = threads.keys()
    sentencePutter = SentencePutter(models.Messages)
    _counter = 0
    while len(active_threads) > 0 and _counter < 4:
        logging.debug("Active threads: " + str(len(active_threads)))
        response = FQL('SELECT body, message_id, thread_id, created_time FROM message WHERE thread_id IN (' + str(map(str, active_threads))[1:-1] + ') AND created_time < ' + str(now) + ' ORDER BY created_time DESC LIMIT 6000 OFFSET ' + str(offset), access_token)
        data = response['data']
        for msg in data:
            threads[str(msg['thread_id'])] += 1
            sentencePutter.put(msg['body'], user.uid, str(msg['message_id']), int(msg['created_time']))
        
        if data[0]['created_time'] < year_ago:
            break
        
        offset += 30
        active_threads = [thread_id for thread_id in threads.keys() if threads[thread_id] >= offset]
        _counter += 1

    sentencePutter.flush()


def getAllPosts(access_token, user, now, year_ago, important_friends, posts):
    response = FQL('SELECT gid FROM group_member WHERE uid=me()', access_token)
    groups = [str(item['gid']) for item in response['data']]
    
    important_friends = str(important_friends.union(groups))[5:-2]
    logging.debug('Facebook best friends + groups: ' + important_friends)
    
    queries = {
        'posts0': 'SELECT post_id, message, created_time FROM stream WHERE source_id IN (' + important_friends + ') ORDER BY created_time DESC LIMIT 100 OFFSET 0',
        'posts100': 'SELECT post_id, message, created_time FROM stream WHERE source_id IN (' + important_friends + ') ORDER BY created_time DESC LIMIT 100 OFFSET 100',
        'posts200': 'SELECT post_id, message, created_time FROM stream WHERE source_id IN (' + important_friends + ') ORDER BY created_time DESC LIMIT 100 OFFSET 200',
        'posts300': 'SELECT post_id, message, created_time FROM stream WHERE source_id IN (' + important_friends + ') ORDER BY created_time DESC LIMIT 100 OFFSET 300',
    }
    response = FQL_multi(access_token, queries)
    
    for result_set in response['data']:
        posts.extend([post for post in result_set['fql_result_set'] if int(post['created_time']) > user.last_timestamp])

    if len(posts) == 0:
        logging.debug('Facebook: no new posts')
        return

    sentencePutter = SentencePutter(models.Posts)
    for post in posts:
        sentencePutter.put(post['message'], user.uid, str(post['post_id']), int(msg['created_time']))
    sentencePutter.flush()
    
    
def getAllComments(access_token, user, now, year_ago, posts_ids):
    logging.debug('Beginning getAllComments')

    response = FQL('SELECT comments FROM stream WHERE post_id IN (' + str(map(str, posts_ids))[1:-1] + ')')
    comments_lists = [comments['comments']['comment_list'] for comments in response['data']]
    sentencePutter = SentencePutter(models.Comments)
    for sublist in comments_lists:
        for comment in sublist:
            if int(comment['time']) > user.last_timestamp:
                sentencePutter.put(comment['text'], user.uid, str(comment['id']), int(comment['time']))


def populate(access_token):
    logging.debug('<<<<<< Deferred: populate')

    response = FQL('SELECT uid FROM user WHERE uid=me()', access_token)
    uid = str(response['data'][0]['uid'])
    user = models.User.find_or_create(uid)

    if user.is_populating:
        return

    user.is_populating = True
    user.put()

    now = long(time.time())
    year_ago = now - YEAR

    try:
        important_friends = []
        getAllMessages(access_token, user, now, year_ago, important_friends)
        posts = []
        getAllPosts(access_token, user, now, year_ago, set(important_friends), posts)
        getAllComments(access_token, user, now, year_ago, [post['post_id'] for post in posts])

    except FacebookError as e:
        logging.exception('Facebook Error ocurred.')

    except DeadlineExceededError as e:
        logging.exception('Task => Time Limit Exceeded')

    except Exception as e:
        logging.exception(e)

    finally:
        user.is_populating = False
        user.last_timestamp = now
        user.put()

        logging.debug('Populate >>>>>>')
