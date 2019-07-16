from requests_oauthlib import OAuth1Session
import urllib.request, datetime, pickle
import json, math, time, sys, os, re

# ログイン
def login(name):
    with open('data/account.pickle', 'rb') as f:
        account = pickle.load(f)
    CK = account[name]['CK']
    CS = account[name]['CS']
    AT = account[name]['AT']
    AS = account[name]['AS']
    user_id = account[name]['id']
    twitter = OAuth1Session(CK, CS, AT, AS)
    return twitter, user_id

# ID取得
def get_list_id(name):
    with open('data/lists.pickle', 'rb') as f:
        lists = pickle.load(f)
    list_id = lists.get(name, None)
    return list_id

# フォロー中のユーザーリスト取得
def get_following(twitter, user_id):
    url = "https://api.twitter.com/1.1/friends/list.json"
    user_list = []
    params = {
            "user_id": user_id,
            "count": 200
            }
    while True:
        res = twitter.get(url, params = params)
        if res.status_code == 200:
            for user in json.loads(res.text)["users"]:
                user_list.append(user)
            params["cursor"] = json.loads(res.text)["next_cursor_str"]
        else:
            break
        if params["cursor"] == "0":
            break
    return user_list

# フォロー中のユーザーIDリスト取得
def get_following_id(twitter, user_id):
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
def get_follower_id(twitter, user_id):
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
def get_list_member(twitter, list_id):
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

# IDリストからユーザーリスト取得
def get_user_list(twitter, id_list):
    url = "https://api.twitter.com/1.1/users/lookup.json"
    user_list = []
    for i in range(math.ceil(len(id_list)/100)):
        params = {
                "user_id": ",".join(id_list[i*100:(i+1)*100]),
                "include_entities": False
                }
        res = twitter.get(url, params = params, timeout = 10)
        if res.status_code == 200:
            user_list.extend(json.loads(res.text))
    return user_list

# ユーザーのツイートリスト取得
def get_tweet_list(twitter, user_id, count):
    url = "https://api.twitter.com/1.1/statuses/user_timeline.json"
    tweet_list = []
    params = {
            "user_id": user_id,
            "exclude_replies": True,
            "include_rts": False,
            "count": 200
            }
    for i in range(count//200):
        res = twitter.get(url, params = params)
        if res.status_code == 200:
            tweet_list.extend(json.loads(res.text))
            params["max_id"] = tweet_list[-1]["id_str"]
    return tweet_list

# ホームのタイムライン取得
def get_timeline(twitter, count):
    url = "https://api.twitter.com/1.1/statuses/home_timeline.json"
    tweet_list = []
    params = {
            "exclude_replies": True,
            "include_rts": True,
            "count": 200
            }
    for i in range(count//200):
        res = twitter.get(url, params = params)
        if res.status_code == 200:
            tweet_list.extend(json.loads(res.text))
            params["max_id"] = tweet_list[-1]["id_str"]
    return tweet_list

# リストのタイムライン取得
def get_list_timeline(twitter, list_id, count):
    url = "https://api.twitter.com/1.1/lists/statuses.json"
    tweet_list = []
    params = {
            "list_id": list_id,
            "exclude_replies": True,
            "include_rts": True,
            "count": 200
            }
    for i in range(count//200):
        res = twitter.get(url, params = params)
        if res.status_code == 200:
            tweet_list.extend(json.loads(res.text))
            params["max_id"] = tweet_list[-1]["id_str"]
    return tweet_list

# お気に入り登録したツイートリスト取得
def get_fav_tweet_list(twitter, user_id, count, target = "", loop = False, day = 0):
    url = "https://api.twitter.com/1.1/favorites/list.json"
    tweet_list, proceed = [], 0
    params = {
            "user_id": user_id,
            "count": 200,
            "exclude_replies": True
            }
    while proceed < count:
        res = twitter.get(url, params = params)
        proceed += 200
        if res.status_code == 200:
            tweets = json.loads(res.text)
            for tweet in tweets:
                tweet_list.append(tweet)
                if tweet["user"]["id_str"] == target:
                    return tweet_list
            try:
                params["max_id"] = tweets[-1]["id_str"]
            except:
                return tweet_list
            if day and is_timeover(tweets[-1]["created_at"], day):
                return tweet_list
        elif loop:
            time.sleep(60)
            proceed -= 200
    return tweet_list

# お気に入り登録したユーザーIDリスト取得
def get_fav_user_id_list(tweet_id, exclude_list = []):
    try:
        url = "https://twitter.com/i/activity/favorited_popup?id=" + tweet_id
        json_data = urllib.request.urlopen(url).read()
        found_id_list = re.findall(r'data-user-id=\\"+\d+', json_data.decode('utf-8'))
        unique_id_list = list(set([re.findall(r'\d+', match)[0] for match in found_id_list]))
        user_id_list = [user_id for user_id in unique_id_list if user_id not in exclude_list]
        return user_id_list
    except:
        return []

# ユーザーリストとの関係取得
def get_friendship(twitter, user_id_list):
    url = "https://api.twitter.com/1.1/friendships/lookup.json"
    user_list = []
    line_list = []
    for i, user in enumerate(user_id_list):
        if i%100 == 0:
            line_list.append(user + ",")
        else:
            line_list[i//100] += user + ","
    for line in line_list:
        line = line[:-1]
        params = { "user_id": line }
        res = twitter.get(url, params = params)
        if res.status_code == 200:
            user_list.extend(json.loads(res.text))
        else:
            sys.exit()
    return user_list

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
def is_favorited(twitter, tweet_id):
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
def post_favorite(twitter, tweet_id):
    url = "https://api.twitter.com/1.1/favorites/create.json"
    res = twitter.post(url, params = {"id": tweet_id})
    return res

# お気に入り登録解除
def destroy_favorite(twitter, tweet_id):
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