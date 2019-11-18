from requests_oauthlib import OAuth1Session
import urllib.request, datetime
import json, math, time, sys, os, re

# ログイン
def login():
    with open('data/account.json', 'r') as f:
        account = json.load(f)
    CK = account['CK']
    CS = account['CS']
    AT = account['AT']
    AS = account['AS']
    user_id = account['id']
    twitter = OAuth1Session(CK, CS, AT, AS)
    return twitter, user_id

# リストID取得
def get_list_id(name):
    with open('data/lists.json', 'r') as f:
        lists = json.load(f)
    list_id = lists.get(name, None)
    return list_id

# フォロー中のユーザーリスト取得
def get_friends(twitter, user_id):
    url = "https://api.twitter.com/1.1/friends/list.json"
    users = []
    params = {
            "user_id": user_id,
            "count": 200
            }
    while True:
        res = twitter.get(url, params = params)
        if res.status_code == 200:
            for user in json.loads(res.text)["users"]:
                users.append(user)
            params["cursor"] = json.loads(res.text)["next_cursor_str"]
        else:
            break
        if params["cursor"] == "0":
            break
    return users

# フォロワーのユーザーリスト取得
def get_followers(twitter, user_id):
    url = "https://api.twitter.com/1.1/followers/list.json"
    users = []
    params = {
            "user_id": user_id,
            "count": 200
            }
    while True:
        res = twitter.get(url, params = params)
        if res.status_code == 200:
            for user in json.loads(res.text)["users"]:
                users.append(user)
            params["cursor"] = json.loads(res.text)["next_cursor_str"]
        else:
            break
        if params["cursor"] == "0":
            break
    return users

# フォロー中のユーザーIDリスト取得
def get_friend_ids(twitter, user_id):
    url = "https://api.twitter.com/1.1/friends/ids.json"
    params = {
            "user_id": user_id,
            "stringify_ids": True,
            "count": 1500
            }
    res = twitter.get(url, params = params)
    if res.status_code == 200:
        return json.loads(res.text)["ids"]
    else:
        return []

# フォロワーのユーザーIDリスト取得
def get_follower_ids(twitter, user_id):
    url = "https://api.twitter.com/1.1/followers/ids.json"
    params = {
            "user_id": user_id,
            "stringify_ids": True,
            "count": 1500
            }
    res = twitter.get(url, params = params)
    if res.status_code == 200:
        return json.loads(res.text)["ids"]
    else:
        return []

# リストのメンバーリスト取得
def get_list_members(twitter, list_id):
    url = "https://api.twitter.com/1.1/lists/members.json"
    params = {
            "list_id": list_id,
            "include_entities": False,
            "skip_status": True,
            "count": 5000
            }
    res = twitter.get(url, params = params)
    if res.status_code == 200:
        return json.loads(res.text)["users"]
    else:
        return []

# IDまたはスクリーンネームからユーザー取得
def get_user(twitter, user_id = '', screen_name = ''):
    url = "https://api.twitter.com/1.1/users/show.json"
    key = "user_id" if user_id else "screen_name"
    value = user_id if user_id else screen_name
    params = {
            key: value,
            "include_entities": False
            }
    res = twitter.get(url, params = params, timeout = 10)
    if res.status_code == 200:
        return json.loads(res.text)
    return None

# IDリストからユーザーリスト取得
def get_users(twitter, ids):
    url = "https://api.twitter.com/1.1/users/lookup.json"
    users = []
    for i in range(math.ceil(len(ids)/100)):
        params = {
                "user_id": ",".join(ids[i*100:(i+1)*100]),
                "include_entities": False
                }
        res = twitter.get(url, params = params, timeout = 10)
        if res.status_code == 200:
            users.extend(json.loads(res.text))
    return users

# ユーザーのツイートリスト取得
def get_tweets(twitter, user_id, count):
    url = "https://api.twitter.com/1.1/statuses/user_timeline.json"
    tweets = []
    params = {
            "user_id": user_id,
            "exclude_replies": True,
            "include_rts": False,
            "count": 200
            }
    for i in range(count//200):
        res = twitter.get(url, params = params)
        if res.status_code == 200:
            tweets.extend(json.loads(res.text))
            params["max_id"] = tweets[-1]["id_str"]
    return tweets

# ホームのタイムライン取得
def get_timeline(twitter, count):
    url = "https://api.twitter.com/1.1/statuses/home_timeline.json"
    tweets = []
    params = {
            "exclude_replies": True,
            "include_rts": True,
            "count": 200
            }
    for i in range(count//200):
        res = twitter.get(url, params = params)
        if res.status_code == 200:
            tweets.extend(json.loads(res.text))
            params["max_id"] = tweets[-1]["id_str"]
    return tweets

# リストのタイムライン取得
def get_list_timeline(twitter, list_id, count):
    url = "https://api.twitter.com/1.1/lists/statuses.json"
    tweets = []
    params = {
            "list_id": list_id,
            "exclude_replies": True,
            "include_rts": True,
            "count": 200
            }
    for i in range(count//200):
        res = twitter.get(url, params = params)
        if res.status_code == 200:
            tweets.extend(json.loads(res.text))
            params["max_id"] = tweets[-1]["id_str"]
    return tweets

# お気に入り登録したツイートリスト取得
def get_like_tweets(twitter, user_id, count, target = "", loop = False, day = 0):
    url = "https://api.twitter.com/1.1/favorites/list.json"
    tweets, proceed = [], 0
    params = {
            "user_id": user_id,
            "count": 200,
            "exclude_replies": True
            }
    while proceed < count:
        res = twitter.get(url, params = params)
        if res.status_code == 200:
            proceed += 200
            for tweet in json.loads(res.text):
                tweets.append(tweet)
                if tweet["user"]["id_str"] == target:
                    return tweets
            try:
                params["max_id"] = tweets[-1]["id_str"]
            except:
                return tweets
            if day and is_timeover(tweets[-1]["created_at"], day):
                return tweets
        elif loop:
            time.sleep(60)
    return tweets

# お気に入り登録したユーザーIDリスト取得
def get_like_user_ids(tweet_id, excludes = []):
    try:
        url = "https://twitter.com/i/activity/favorited_popup?id=" + tweet_id
        json_data = urllib.request.urlopen(url).read()
        found_ids = re.findall(r'data-user-id=\\"+\d+', json_data.decode('utf-8'))
        unique_ids = list(set([re.findall(r'\d+', match)[0] for match in found_ids]))
        user_ids = [user_id for user_id in unique_ids if user_id not in excludes]
        return user_ids
    except:
        return []

# ユーザーリストとの関係取得
def get_friendship(twitter, user_ids):
    url = "https://api.twitter.com/1.1/friendships/lookup.json"
    users = []
    lines = []
    for i, user in enumerate(user_ids):
        if i%100 == 0:
            lines.append(user + ",")
        else:
            lines[i//100] += user + ","
    for line in lines:
        line = line[:-1]
        params = { "user_id": line }
        res = twitter.get(url, params = params)
        if res.status_code == 200:
            users.extend(json.loads(res.text))
        else:
            sys.exit()
    return users

# ユーザーとの関係チェック
def check_friendship(twitter, target, source):
    url = "https://api.twitter.com/1.1/friendships/show.json"
    params = {
            "source_id": source,
            "target_id": target
            }
    res = twitter.get(url, params = params)
    if res.status_code == 200:
        return json.loads(res.text)["relationship"]
    else:
        sys.exit()

# 日付取得
def get_date(date):
    try:
        date = datetime.datetime.strptime(date, "%a %b %d %H:%M:%S +0000 %Y")
    except:
        date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    return date

# タイムオーバーチェック
def is_timeover(date, day):
    date = get_date(date)
    date = date + datetime.timedelta(hours = 9)
    standard = datetime.datetime.now()
    standard = standard - datetime.timedelta(days = day)
    return standard > date

# お気に入りチェック
def is_liked(twitter, tweet_id):
    url = "https://api.twitter.com/1.1/statuses/lookup.json"
    params = {
            "id": tweet_id,
            "trim_user": True,
            "include_entities": False
            }
    res = twitter.get(url, params = params)
    if res.status_code == 200:
        tweet = json.loads(res.text)[0]
        return tweet["favorited"]

# ダイレクトメッセージ
def direct_message(twitter, target, message):
    url = "https://api.twitter.com/1.1/direct_messages/events/new.json"
    data = {
            "event": {
                "type": "message_create",
                "message_create": {
                    "target": { "recipient_id": target },
                    "message_data": { "text": message }
                    }
                }
            }
    res = twitter.post(url, data = json.dumps(data))
    return res

# お気に入り登録
def like(twitter, tweet_id):
    url = "https://api.twitter.com/1.1/favorites/create.json"
    res = twitter.post(url, params = {"id": tweet_id})
    return res

# お気に入り登録解除
def dislike(twitter, tweet_id):
    url = "https://api.twitter.com/1.1/favorites/destroy.json"
    res = twitter.post(url, params = {"id": tweet_id})
    return res

# リストへユーザー追加
def add_user(twitter, list_id, user_id):
    url = "https://api.twitter.com/1.1/lists/members/create.json"
    params = {
            "list_id": list_id,
            "user_id": user_id
            }
    res = twitter.post(url, params = params)
    return res

# リストからユーザー削除
def delete_user(twitter, list_id, user_id):
    url = "https://api.twitter.com/1.1/lists/members/destroy.json"
    params = {
            "list_id": list_id,
            "user_id": user_id
            }
    res = twitter.post(url, params = params)
    return res

# ツイート
def tweet(twitter, tweet, media = None):
    url_text = "https://api.twitter.com/1.1/statuses/update.json"
    url_media = "https://upload.twitter.com/1.1/media/upload.json"
    if media:
        files = {"media" : media}
        res = twitter.post(url_media, files = files)
        media_id = json.loads(res.text)['media_id']
        params = {'status': tweet, "media_ids": [media_id]}
        res = twitter.post(url_text, params = params)
    else:
        params = {"status": tweet}
        res = twitter.post(url_text, params = params)
    return res

# ツイート削除
def delete_tweet(twitter, tweet_id):
    url = f"https://api.twitter.com/1.1/statuses/destroy/{tweet_id}.json"
    res = twitter.post(url, params = {"id": tweet_id})
    return res
