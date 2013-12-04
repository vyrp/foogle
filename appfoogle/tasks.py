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


def FQL_batch(access_token, queries):
    params = {
        'access_token': access_token,
        'batch': [{
            'method': 'POST',
            'relative_url': 'method/fql.query?' + urllib.urlencode({'query': query})
        } for query in queries]
    }
    response = urlfetch.fetch(url='https://graph.facebook.com', payload=urllib.urlencode(params), method=urlfetch.POST)
    if response.status_code == 200:
        response = json.loads(response.content)
        return response
    else:
        raise FacebookError('Facebook FQL Error: ' + str(response.status_code))
 
 
def flatten(multilist):
    result = []
    for sublist in multilist:
        result.extend(sublist)
    return result


def bundle(flat_list, max_size):
    N = len(flat_list) / max_size
    multilist = [flat_list[i * max_size: (i + 1) * max_size] for i in xrange(0, N)]
    if flat_list[N * max_size:]:
        multilist.append(flat_list[N * max_size:])
    return multilist
    

def getAllMessages(access_token, user, now, year_ago, important_friends):
    queries = {
        'threads0': 'SELECT thread_id, updated_time, message_count, recipients FROM thread WHERE folder_id=0 ORDER BY updated_time DESC LIMIT 50 OFFSET 0',
        # 'threads50': 'SELECT thread_id, updated_time, message_count, recipients FROM thread WHERE folder_id=0 ORDER BY updated_time DESC LIMIT 50 OFFSET 50',
        # 'threads100': 'SELECT thread_id, updated_time, message_count, recipients FROM thread WHERE folder_id=0 ORDER BY updated_time DESC LIMIT 50 OFFSET 100',
        # 'threads150': 'SELECT thread_id, updated_time, message_count, recipients FROM thread WHERE folder_id=0 ORDER BY updated_time DESC LIMIT 50 OFFSET 150'
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
        
        queries = ['SELECT body, message_id, thread_id, created_time FROM message WHERE thread_id IN (' + str(small_list)[1:-1] + ') AND created_time < ' + str(now) + ' ORDER BY created_time DESC LIMIT 6000 OFFSET ' + str(offset) for small_list in bundle(map(str, active_threads), 20)]
        response = FQL_batch(access_token, queries)
        
        messages = flatten([json.loads(answer['body']) for answer in response])
        logging.debug("Number of messages: " + str(len(messages)))
        for msg in messages:
            threads[str(msg['thread_id'])] += 1
            sentencePutter.put(msg['body'], user.uid, str(msg['message_id']), int(msg['created_time']))
        
        if messages[0]['created_time'] < year_ago:
            break
        
        offset += 30
        active_threads = [thread_id for thread_id in threads.keys() if threads[thread_id] >= offset]
        _counter += 1

    sentencePutter.flush()


def getAllPosts(access_token, user, now, year_ago, important_friends, posts):
    response = FQL('SELECT gid FROM group_member WHERE uid=me()', access_token)
    groups = [str(item['gid']) for item in response['data']]
    logging.debug("Number of groups: " + str(len(groups)))
    
    queries = [
        'SELECT post_id, message, created_time, updated_time FROM stream WHERE source_id IN (' + str(important_friends)[5:-2] + ') AND created_time < ' + str(now) + ' ORDER BY created_time DESC LIMIT 100 OFFSET 0',
        # 'SELECT post_id, message, created_time, updated_time FROM stream WHERE source_id IN (' + str(important_friends)[5:-2] + ') AND created_time < ' + str(now) + ' ORDER BY created_time DESC LIMIT 100 OFFSET 100',
        # 'SELECT post_id, message, created_time, updated_time FROM stream WHERE source_id IN (' + str(important_friends)[5:-2] + ') AND created_time < ' + str(now) + ' ORDER BY created_time DESC LIMIT 100 OFFSET 200',
        # 'SELECT post_id, message, created_time, updated_time FROM stream WHERE source_id IN (' + str(important_friends)[5:-2] + ') AND created_time < ' + str(now) + ' ORDER BY created_time DESC LIMIT 100 OFFSET 300',
        'SELECT post_id, message, created_time, updated_time FROM stream WHERE source_id IN (' + str(groups)[1:-1] + ') AND created_time < ' + str(now) + ' ORDER BY created_time DESC LIMIT 100 OFFSET 0',
        # 'SELECT post_id, message, created_time, updated_time FROM stream WHERE source_id IN (' + str(groups)[1:-1] + ') AND created_time < ' + str(now) + ' ORDER BY created_time DESC LIMIT 100 OFFSET 100',
        # 'g_posts200': 'SELECT post_id, message, created_time, updated_time FROM stream WHERE source_id IN (' + str(groups)[1:-1] + ') AND created_time < ' + str(now) + ' ORDER BY created_time DESC LIMIT 100 OFFSET 200',
        # 'g_posts300': 'SELECT post_id, message, created_time, updated_time FROM stream WHERE source_id IN (' + str(groups)[1:-1] + ') AND created_time < ' + str(now) + ' ORDER BY created_time DESC LIMIT 100 OFFSET 300',
    ]
    response = FQL_batch(access_token, queries)
    data = flatten([json.loads(answer['body']) for answer in response])
    
    logging.debug("Number of posts: " + str(len(data)))

    posts_to_put = []
    posts.extend([post for post in data if (int(post['updated_time']) > user.last_timestamp and int(post['created_time']) > year_ago)])
    posts_to_put.extend([post for post in data if (int(post['created_time']) > user.last_timestamp and int(post['created_time']) > year_ago)])

    if len(posts_to_put) == 0:
        logging.debug('Facebook: no new posts')
        return

    sentencePutter = SentencePutter(models.Posts)
    for post in posts_to_put:
        sentencePutter.put(post['message'], user.uid, str(post['post_id']), int(post['created_time']))
    sentencePutter.flush()
    
    
def getAllComments(access_token, user, now, year_ago, posts_ids):
    logging.debug('Beginning getAllComments')

    logging.debug("Number of posts with new comments: " + str(len(posts_ids)))
    
    response = FQL_batch(access_token, ['SELECT comments FROM stream WHERE post_id IN (' + str(small_list)[1:-1] + ')' for small_list in bundle(posts_ids, 20)])
    data = flatten([json.loads(answer['body']) for answer in response])
    
    logging.debug("Number of comments: " + str(len(data)))
    
    comments_lists = [comments['comments']['comment_list'] for comments in data]
    sentencePutter = SentencePutter(models.Comments)
    counter = 0
    
    comments_lists = sorted(flatten(comments_lists), key=lambda comment: int(comment['time']), reverse=True)
    for comment in comments_lists:
        if int(comment['time']) > user.last_timestamp and int(comment['time']) > year_ago:
            sentencePutter.put(comment['text'], user.uid, str(comment['id']), int(comment['time']))
            counter += 1
    
    logging.debug("Number of putted comments: " + str(counter))


def populate(access_token):
    start = time.clock()
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
        getAllComments(access_token, user, now, year_ago, [str(post['post_id']) for post in posts])

    except FacebookError as e:
        logging.exception('Facebook Error ocurred.')

    except DeadlineExceededError as e:
        logging.exception('Task => Time Limit Exceeded')

    except Exception as e:
        logging.exception('Some error ocurred...')

    finally:
        user.is_populating = False
        user.last_timestamp = now
        user.put()

        logging.debug('Populate >>>>>>')
        delta = time.clock() - start
        logging.debug('TIME = ' + str(delta) + 's = ' + str(delta/60) + 'min')
