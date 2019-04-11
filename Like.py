
# coding: utf-8

import MyTwitter
import sqlite3
import sys

#ワードチェック
def include(text):
    wordList = {
        "定期", "募集", "いいね", "ふぁぼ", "スマホRPG",
        "#なうぷれ", "#nowplaying", "#NowPlaying", "#PS4share"
    }
    return True in [word in text for word in wordList]

#フォローユーザー取得
def getFollowingID(twitter, user_id, list_id):
    userList = MyTwitter.getFollowingID(twitter, user_id)
    friendList = MyTwitter.getListMember(twitter, list_id)
    friendList = [friend["id_str"] for friend in friendList]
    userList = [user for user in userList if user not in friendList]
    return list(reversed(userList))

#トップツイート取得
def getTopTweet(tweetList):
    niceTweetList = []
    for tweet in tweetList:
        if tweet["favorited"] or MyTwitter.isTimeover(tweet["created_at"], 2):
            break
        elif MyTwitter.isTimeover(tweet["created_at"], 1) and niceTweetList != []:
            break
        elif not include(tweet["text"]) and tweet["favorite_count"] > 0:
            niceTweetList.append(tweet)
    if niceTweetList == []:
        return None
    else:
        return max(niceTweetList, key = lambda tweet: tweet["favorite_count"])

def execute(name, list_name = None):
    twitter, user_id = MyTwitter.login(name)
    connection = sqlite3.connect("twitter.db")
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS favorite (type, id)")
    userList = []
    for data in cursor.execute("SELECT id FROM favorite WHERE type = ?", (name,)):
        userList.append(data[0])
    if userList == []:
        list_id = MyTwitter.getID(list_name) if list_name else ""
        userList = getFollowingID(twitter, user_id, list_id)
    target = userList.pop(0)
    cursor.execute("DELETE FROM favorite WHERE type = ?", (name,))
    for data in userList:
        cursor.execute("INSERT INTO favorite (type, id) VALUES (?, ?)", (name, data))
    connection.commit()
    connection.close()
    tweetList = MyTwitter.getTweetList(twitter, target, 200)
    topTweet = getTopTweet(tweetList)
    friendship = MyTwitter.getFriendship(twitter, [target])[0]["connections"]
    if "following" in friendship and topTweet is not None:
        MyTwitter.postFavorite(twitter, topTweet["id_str"])

if __name__ == '__main__':
    if len(sys.argv) == 3:
        execute(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 2:
        execute(sys.argv[1])
    else:
        print("Usage: python3 {0} [name] (list_name)".format(sys.argv[0]))
        sys.exit()
