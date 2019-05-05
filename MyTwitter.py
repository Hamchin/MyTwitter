
# coding: utf-8

from requests_oauthlib import OAuth1Session
import urllib.request, datetime, sqlite3
import json, math, time, sys, os, re

# ログイン
def login(name):
    connection = sqlite3.connect("twitter.db")
    cursor = connection.cursor()
    sql = "SELECT id FROM info WHERE name = ? AND type = ?"
    cursor.execute(sql, (name, "CK"))
    CK = cursor.fetchone()[0]
    cursor.execute(sql, (name, "CS"))
    CS = cursor.fetchone()[0]
    cursor.execute(sql, (name, "AT"))
    AT = cursor.fetchone()[0]
    cursor.execute(sql, (name, "AS"))
    AS = cursor.fetchone()[0]
    cursor.execute(sql, (name, "id"))
    user_id = cursor.fetchone()[0]
    connection.close()
    twitter = OAuth1Session(CK, CS, AT, AS)
    return twitter, user_id

# ID取得
def getID(name):
    connection = sqlite3.connect("twitter.db")
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM info WHERE name = ?", (name,))
    result = cursor.fetchone()
    connection.close()
    list_id = result[0] if result != [] else None
    return list_id

# フォロー中のユーザーリスト取得
def getFollowing(twitter, user_id):
    url = "https://api.twitter.com/1.1/friends/list.json"
    userList = []
    params = {
            "user_id": user_id,
            "count": 200
            }
    while True:
        req = twitter.get(url, params = params)
        if req.status_code == 200:
            for user in json.loads(req.text)["users"]:
                userList.append(user)
            params["cursor"] = json.loads(req.text)["next_cursor_str"]
        else:
            break
        if params["cursor"] == "0":
            break
    return userList

# フォロー中のユーザーIDリスト取得
def getFollowingID(twitter, user_id):
    url = "https://api.twitter.com/1.1/friends/ids.json"
    params = {
            "user_id": user_id,
            "stringify_ids": True,
            "count": 1500
            }
    req = twitter.get(url, params = params)
    if req.status_code == 200:
        return json.loads(req.text)["ids"]
    else:
        return []

# フォロワーのユーザーIDリスト取得
def getFollowerID(twitter, user_id):
    url = "https://api.twitter.com/1.1/followers/ids.json"
    params = {
            "user_id": user_id,
            "stringify_ids": True,
            "count": 1500
            }
    req = twitter.get(url, params = params)
    if req.status_code == 200:
        return json.loads(req.text)["ids"]
    else:
        return []

# リストのメンバーリスト取得
def getListMember(twitter, list_id):
    url = "https://api.twitter.com/1.1/lists/members.json"
    params = {
            "list_id": list_id,
            "include_entities": False,
            "skip_status": True,
            "count": 5000
            }
    req = twitter.get(url, params = params)
    if req.status_code == 200:
        return json.loads(req.text)["users"]
    else:
        return []

# IDリストからユーザーリスト取得
def getUserList(twitter, idList, user_id = True):
    url = "https://api.twitter.com/1.1/users/lookup.json"
    key = "user_id" if user_id else "screen_name"
    userList = []
    for i in range(math.ceil(len(idList)/100)):
        params = {
                key: ",".join(idList[i*100:(i+1)*100]),
                "include_entities": False
                }
        req = twitter.get(url, params = params)
        if req.status_code == 200:
            userList.extend(json.loads(req.text))
    return userList

# ユーザーのツイートリスト取得
def getTweetList(twitter, user_id, count):
    url = "https://api.twitter.com/1.1/statuses/user_timeline.json"
    tweetList = []
    params = {
            "user_id": user_id,
            "exclude_replies": True,
            "include_rts": False,
            "count": 200
            }
    for i in range(count//200):
        req = twitter.get(url, params = params)
        if req.status_code == 200:
            tweetList.extend(json.loads(req.text))
            params["max_id"] = tweetList[-1]["id_str"]
    return tweetList

# ホームのタイムライン取得
def getTimeline(twitter, count):
    url = "https://api.twitter.com/1.1/statuses/home_timeline.json"
    tweetList = []
    params = {
            "exclude_replies": True,
            "include_rts": True,
            "count": 200
            }
    for i in range(count//200):
        req = twitter.get(url, params = params)
        if req.status_code == 200:
            tweetList.extend(json.loads(req.text))
            params["max_id"] = tweetList[-1]["id_str"]
    return tweetList

# リストのタイムライン取得
def getListTimeline(twitter, list_id, count):
    url = "https://api.twitter.com/1.1/lists/statuses.json"
    tweetList = []
    params = {
            "list_id": list_id,
            "exclude_replies": True,
            "include_rts": True,
            "count": 200
            }
    for i in range(count//200):
        req = twitter.get(url, params = params)
        if req.status_code == 200:
            tweetList.extend(json.loads(req.text))
            params["max_id"] = tweetList[-1]["id_str"]
    return tweetList

# お気に入り登録したツイートリスト取得
def getFavTweetList(twitter, user_id, count, target = "", loop = False, verbose = False, day = 0):
    url = "https://api.twitter.com/1.1/favorites/list.json"
    tweetList, proceed = [], 0
    params = {
            "user_id": user_id,
            "count": 200,
            "exclude_replies": True
            }
    while proceed < count:
        req = twitter.get(url, params = params)
        proceed += 200
        if req.status_code == 200:
            tweets = json.loads(req.text)
            for tweet in tweets:
                tweetList.append(tweet)
                if tweet["user"]["id_str"] == target:
                    if verbose: print()
                    return tweetList
            try:
                params["max_id"] = tweets[-1]["id_str"]
            except:
                if verbose: print()
                return tweetList
            if verbose:
                sys.stdout.write("\rCOUNT: {0}".format(proceed))
                sys.stdout.flush()
            if day and isTimeover(tweets[-1]["created_at"], day):
                if verbose: print()
                return tweetList
        elif loop:
            time.sleep(60)
            proceed -= 200
    if verbose: print()
    return tweetList

# お気に入り登録したユーザーIDリスト取得
def getFavUserIDList(tweet_id, excList = []):
    try:
        url = "https://twitter.com/i/activity/favorited_popup?id=" + tweet_id
        jsonData = urllib.request.urlopen(url).read()
        foundIDList = re.findall(r'data-user-id=\\"+\d+', jsonData.decode('utf-8'))
        uniqueIDList = list(set([re.findall(r'\d+', match)[0] for match in foundIDList]))
        userIDList = [user_id for user_id in uniqueIDList if user_id not in excList]
        return userIDList
    except:
        return []

# ユーザーリストとの関係取得
def getFriendship(twitter, userIDList):
    url = "https://api.twitter.com/1.1/friendships/lookup.json"
    userList = []
    lineList = []
    for i, user in enumerate(userIDList):
        if i%100 == 0:
            lineList.append(user + ",")
        else:
            lineList[i//100] += user + ","
    for line in lineList:
        line = line[:-1]
        params = { "user_id": line }
        req = twitter.get(url, params = params)
        if req.status_code == 200:
            userList.extend(json.loads(req.text))
        else:
            sys.exit()
    return userList

# ユーザーとの関係チェック
def checkFriendship(twitter, target, source):
    url = "https://api.twitter.com/1.1/friendships/show.json"
    params = {
            "source_id": source,
            "target_id": target
            }
    req = twitter.get(url, params = params)
    if req.status_code == 200:
        return json.loads(req.text)["relationship"]
    else:
        sys.exit()

# 日付取得
def getDate(date):
    try:
        date = datetime.datetime.strptime(date, "%a %b %d %H:%M:%S +0000 %Y")
    except:
        date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    return date

# タイムオーバーチェック
def isTimeover(date, day):
    date = getDate(date)
    date = date + datetime.timedelta(hours = 9)
    standard = datetime.datetime.now()
    standard = standard - datetime.timedelta(days = day)
    return standard > date

# お気に入りチェック
def isFavorited(twitter, tweet_id):
    url = "https://api.twitter.com/1.1/statuses/lookup.json"
    params = {
            "id": tweet_id,
            "trim_user": True,
            "include_entities": False
            }
    req = twitter.get(url, params = params)
    if req.status_code == 200:
        tweet = json.loads(req.text)[0]
        return tweet["favorited"]

# ダイレクトメッセージ
def directMessage(twitter, target, message):
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
    req = twitter.post(url, data = json.dumps(data))
    return req

# お気に入り登録
def postFavorite(twitter, tweet_id):
    url = "https://api.twitter.com/1.1/favorites/create.json"
    req = twitter.post(url, params = {"id": tweet_id})
    return req

# お気に入り登録解除
def destroyFavorite(twitter, tweet_id):
    url = "https://api.twitter.com/1.1/favorites/destroy.json"
    req = twitter.post(url, params = {"id": tweet_id})
    return req

# リストへユーザー追加
def addUser(twitter, list_id, user_id):
    url = "https://api.twitter.com/1.1/lists/members/create.json"
    params = {
            "list_id": list_id,
            "user_id": user_id
            }
    req = twitter.post(url, params = params)
    return req

# リストからユーザー削除
def deleteUser(twitter, list_id, user_id):
    url = "https://api.twitter.com/1.1/lists/members/destroy.json"
    params = {
            "list_id": list_id,
            "user_id": user_id
            }
    req = twitter.post(url, params = params)
    return req

# ツイート
def tweet(twitter, tweet, media = None):
    url_text = "https://api.twitter.com/1.1/statuses/update.json"
    url_media = "https://upload.twitter.com/1.1/media/upload.json"
    if media:
        files = {"media" : media}
        req = twitter.post(url_media, files = files)
        media_id = json.loads(req.text)['media_id']
        params = {'status': tweet, "media_ids": [media_id]}
        req = twitter.post(url_text, params = params)
    else:
        params = {"status": tweet}
        req = twitter.post(url_text, params = params)
    return req

# ツイート削除
def deleteTweet(twitter, tweet_id):
    url = f"https://api.twitter.com/1.1/statuses/destroy/{tweet_id}.json"
    req = twitter.post(url, params = {"id": tweet_id})
    return req
