from requests_oauthlib import OAuth1Session
from dotenv import load_dotenv
import os, json, time, math, datetime, re

load_dotenv()

# ログイン
def login():
    CK = os.getenv('CONSUMER_KEY')
    CS = os.getenv('CONSUMER_SECRET')
    AT = os.getenv('ACCESS_TOKEN')
    AS = os.getenv('ACCESS_SECRET')
    user_id = os.getenv('USER_ID')
    twitter = OAuth1Session(CK, CS, AT, AS)
    return twitter, user_id

# フォロー中のユーザーリストを取得する
def get_friends(twitter, user_id):
    url = "https://api.twitter.com/1.1/friends/list.json"
    params = {
        'user_id': user_id,
        'count': 200
    }
    users = []
    while True:
        res = twitter.get(url, params = params)
        if res.status_code != 200: break
        for user in json.loads(res.text)['users']:
            users.append(user)
        params['cursor'] = json.loads(res.text)['next_cursor_str']
        if params['cursor'] == '0': break
    return users

# フォロワーのユーザーリストを取得する
def get_followers(twitter, user_id):
    url = "https://api.twitter.com/1.1/followers/list.json"
    params = {
        'user_id': user_id,
        'count': 200
    }
    users = []
    while True:
        res = twitter.get(url, params = params)
        if res.status_code != 200: break
        for user in json.loads(res.text)['users']:
            users.append(user)
        params['cursor'] = json.loads(res.text)['next_cursor_str']
        if params['cursor'] == '0': break
    return users

# フォロー中のユーザーIDリストを取得する
def get_friend_ids(twitter, user_id):
    url = "https://api.twitter.com/1.1/friends/ids.json"
    params = {
        'user_id': user_id,
        'stringify_ids': True,
        'count': 1500
    }
    res = twitter.get(url, params = params)
    if res.status_code != 200: return []
    return json.loads(res.text)['ids']

# フォロワーのユーザーIDリストを取得する
def get_follower_ids(twitter, user_id):
    url = "https://api.twitter.com/1.1/followers/ids.json"
    params = {
        'user_id': user_id,
        'stringify_ids': True,
        'count': 1500
    }
    res = twitter.get(url, params = params)
    if res.status_code != 200: return []
    return json.loads(res.text)['ids']

# リストのメンバーリストを取得する
def get_list_members(twitter, list_id):
    url = "https://api.twitter.com/1.1/lists/members.json"
    params = {
        'list_id': list_id,
        'include_entities': False,
        'skip_status': True,
        'count': 5000
    }
    res = twitter.get(url, params = params)
    if res.status_code != 200: return []
    return json.loads(res.text)['users']

# IDまたはスクリーンネームからユーザーを取得する
def get_user(twitter, user_id = '', screen_name = ''):
    url = "https://api.twitter.com/1.1/users/show.json"
    key = 'user_id' if user_id else 'screen_name'
    value = user_id if user_id else screen_name
    params = {
        key: value,
        'include_entities': False
    }
    res = twitter.get(url, params = params, timeout = 10)
    if res.status_code != 200: return None
    return json.loads(res.text)

# IDリストまたはスクリーンネームリストからユーザーリストを取得する
def get_users(twitter, user_ids = [], screen_names = []):
    url = "https://api.twitter.com/1.1/users/lookup.json"
    key = 'user_id' if user_ids else 'screen_name'
    values = user_ids if user_ids else screen_names
    users = []
    for i in range(math.ceil(len(values)/100)):
        params = {
            key: ','.join(values[i*100:(i+1)*100]),
            'include_entities': False
        }
        res = twitter.get(url, params = params, timeout = 10)
        if res.status_code != 200: continue
        users.extend(json.loads(res.text))
    return users

# 複数のツイートを取得する
def get_tweets(twitter, tweet_ids):
    url = "https://api.twitter.com/1.1/statuses/lookup.json"
    tweets = []
    for i in range(math.ceil(len(tweet_ids)/100)):
        params = {
            'id': ','.join(tweet_ids[i*100:(i+1)*100]),
            'include_entities': False,
            'trim_user': True
        }
        res = twitter.get(url, params = params, timeout = 10)
        if res.status_code != 200: continue
        tweets.extend(json.loads(res.text))
    return tweets

# ユーザータイムラインを取得する
def get_user_timeline(twitter, user_id, count):
    url = "https://api.twitter.com/1.1/statuses/user_timeline.json"
    params = {
        'user_id': user_id,
        'exclude_replies': True,
        'include_rts': False,
        'count': 200
    }
    tweets = []
    for i in range(count//200):
        res = twitter.get(url, params = params)
        if res.status_code != 200: break
        tweets.extend(json.loads(res.text))
        params['max_id'] = tweets[-1]['id_str']
    return tweets

# ホームタイムラインを取得する
def get_home_timeline(twitter, count):
    url = "https://api.twitter.com/1.1/statuses/home_timeline.json"
    params = {
        'exclude_replies': True,
        'include_rts': True,
        'count': 200
    }
    tweets = []
    for i in range(count//200):
        res = twitter.get(url, params = params)
        if res.status_code != 200: break
        tweets.extend(json.loads(res.text))
        params['max_id'] = tweets[-1]['id_str']
    return tweets

# 対象ユーザーのリスト一覧を取得する
def get_list(twitter, user_id):
    url = "https://api.twitter.com/1.1/lists/list.json"
    params = {'user_id': user_id}
    res = twitter.get(url, params = params)
    if res.status_code != 200: return []
    return json.loads(res.text)

# リストのタイムラインを取得する
def get_list_timeline(twitter, list_id, count):
    url = "https://api.twitter.com/1.1/lists/statuses.json"
    params = {
        'list_id': list_id,
        'exclude_replies': True,
        'include_rts': True,
        'count': 200
    }
    tweets = []
    for i in range(count//200):
        res = twitter.get(url, params = params)
        if res.status_code != 200: break
        tweets.extend(json.loads(res.text))
        params['max_id'] = tweets[-1]['id_str']
    return tweets

# 対象ユーザーがいいねしたツイートリストを取得する
def get_like_tweets(twitter, user_id, count, target = '', loop = False, day = 0):
    url = "https://api.twitter.com/1.1/favorites/list.json"
    params = {
        'user_id': user_id,
        'count': 200,
        'exclude_replies': True
    }
    tweets, proceed = [], 0
    while proceed < count:
        res = twitter.get(url, params = params)
        if res.status_code == 200:
            proceed += 200
            for tweet in json.loads(res.text):
                tweets.append(tweet)
                if tweet['user']['id_str'] == target:
                    return tweets
            try:
                params['max_id'] = tweets[-1]['id_str']
            except:
                return tweets
            if day and is_timeover(tweets[-1]['created_at'], day):
                return tweets
        elif loop:
            time.sleep(60)
    return tweets

# ユーザーリストとの関係を取得する
def get_friendship(twitter, user_ids):
    url = "https://api.twitter.com/1.1/friendships/lookup.json"
    users = []
    lines = []
    for i, user in enumerate(user_ids):
        if i%100 == 0:
            lines.append(user + ',')
        else:
            lines[i//100] += user + ','
    for line in lines:
        line = line[:-1]
        params = {'user_id': line}
        res = twitter.get(url, params = params)
        if res.status_code != 200: return None
        users.extend(json.loads(res.text))
    return users

# ユーザー間の関係を取得する
def check_friendship(twitter, target, source):
    url = "https://api.twitter.com/1.1/friendships/show.json"
    params = {
        'source_id': source,
        'target_id': target
    }
    res = twitter.get(url, params = params)
    if res.status_code != 200: return None
    return json.loads(res.text)['relationship']

# 文字列から日付を取得する
def get_date(date):
    try:
        return datetime.datetime.strptime(date, "%a %b %d %H:%M:%S +0000 %Y")
    except:
        pass
    try:
        return datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    except:
        pass
    return None

# タイムオーバーをチェックする
def is_timeover(date, day):
    date = get_date(date)
    date = date + datetime.timedelta(hours = 9)
    standard = datetime.datetime.now()
    standard = standard - datetime.timedelta(days = day)
    return standard > date

# 対象ツイートがいいね済みかチェックする
def is_liked(twitter, tweet_id):
    url = "https://api.twitter.com/1.1/statuses/lookup.json"
    params = {
        'id': tweet_id,
        'trim_user': True,
        'include_entities': False
    }
    res = twitter.get(url, params = params)
    if res.status_code != 200: return None
    tweet = json.loads(res.text)[0]
    return tweet['favorited']

# ダイレクトメッセージを送信する
def direct_message(twitter, target, message):
    url = "https://api.twitter.com/1.1/direct_messages/events/new.json"
    data = {
        'event': {
            'type': 'message_create',
            'message_create': {
                'target': { 'recipient_id': target },
                'message_data': { 'text': message }
            }
        }
    }
    res = twitter.post(url, data = json.dumps(data))
    return res

# 対象ツイートにいいねを付ける
def like(twitter, tweet_id):
    url = "https://api.twitter.com/1.1/favorites/create.json"
    res = twitter.post(url, params = {'id': tweet_id})
    return res

# 対象ツイートのいいねを取り消す
def dislike(twitter, tweet_id):
    url = "https://api.twitter.com/1.1/favorites/destroy.json"
    res = twitter.post(url, params = {'id': tweet_id})
    return res

# リストへユーザーを追加する
def add_user(twitter, list_id, user_id = '', screen_name = ''):
    url = "https://api.twitter.com/1.1/lists/members/create.json"
    key = 'user_id' if user_id else 'screen_name'
    value = user_id if user_id else screen_name
    params = {
        'list_id': list_id,
        key: value
    }
    res = twitter.post(url, params = params)
    return res

# リストからユーザーを削除する
def delete_user(twitter, list_id, user_id = '', screen_name = ''):
    url = "https://api.twitter.com/1.1/lists/members/destroy.json"
    key = 'user_id' if user_id else 'screen_name'
    value = user_id if user_id else screen_name
    params = {
        'list_id': list_id,
        key: value
    }
    res = twitter.post(url, params = params)
    return res

# ツイートする
def tweet(twitter, tweet, media = None):
    url_text = "https://api.twitter.com/1.1/statuses/update.json"
    url_media = "https://upload.twitter.com/1.1/media/upload.json"
    if media:
        files = {'media' : media}
        res = twitter.post(url_media, files = files)
        media_id = json.loads(res.text)['media_id']
        params = {'status': tweet, 'media_ids': [media_id]}
        res = twitter.post(url_text, params = params)
    else:
        params = {'status': tweet}
        res = twitter.post(url_text, params = params)
    return res

# ツイートを削除する
def delete_tweet(twitter, tweet_id):
    url = f"https://api.twitter.com/1.1/statuses/destroy/{tweet_id}.json"
    res = twitter.post(url, params = {'id': tweet_id})
    return res
