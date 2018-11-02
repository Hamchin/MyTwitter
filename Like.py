
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
        if tweet["favorited"] == True or MyTwitter.isTimeover(tweet["created_at"], 1) == True:
            break
        if include(tweet["text"]) == False and tweet["favorite_count"] > 0:
            niceTweetList.append(tweet)
    if niceTweetList == []:
        return None
    else:
        return max(niceTweetList, key = lambda tweet: tweet["favorite_count"])

def execute(user_id):
    twitter = MyTwitter.login()
    connection = sqlite3.connect("twitter.db")
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS favorite (id VARCHAR(255))")
    userList = []
    for data in cursor.execute("SELECT * FROM favorite"):
        userList.append(data[0])
    if userList == []:
        userList = getFollowingID(twitter, user_id, "")
    target = userList.pop(0)
    cursor.execute("DELETE FROM favorite")
    for data in userList:
        cursor.execute("INSERT INTO favorite (id) VALUES (?)", (data,))
    connection.commit()
    connection.close()
    tweetList = MyTwitter.getTweetList(twitter, target, 200)
    topTweet = getTopTweet(tweetList)
    friendship = MyTwitter.getFriendship(twitter, [target])[0]["connections"]
    if "following" in friendship and topTweet is not None:
        MyTwitter.postFavorite(twitter, topTweet["id_str"])

if __name__ == '__main__':
    try:
        user_id = sys.argv[1]
    except:
        print("Usage: python3 {0} [user_id]".format(sys.argv[0]))
        sys.exit()
    execute(user_id)

