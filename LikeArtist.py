
# coding: utf-8

import MyTwitter
import sys

#テキストチェック
def checkText(text):
    wordList = ["アニメーター", "イラスト", "絵描き", "pixiv"]
    return True in [word in text for word in wordList]

#URLチェック
def checkURL(entities, word):
    try:
        if word in entities["url"]["urls"][0]["display_url"]: return True
    except:
        pass
    return True in [word in url["display_url"] for url in entities["description"]["urls"]]

def execute(list_id):
    twitter = MyTwitter.login()
    tweetList = []
    timeline = MyTwitter.getListTimeline(twitter, list_id, 1000)
    for tweet in timeline:
        if tweet.get("retweeted_status"): tweet = tweet["retweeted_status"]
        user = tweet["user"]
        if tweet["entities"].get("media") \
        and MyTwitter.isTimeover(tweet["created_at"], 7) == False \
        and tweet["favorite_count"] > 1000 \
        and MyTwitter.isFavorited(twitter, tweet["id_str"]) == False \
        and user["followers_count"] > 2 * user["friends_count"] \
        and user["followers_count"] > 1000 \
        and tweet["favorite_count"] > 2 * tweet["retweet_count"] \
        and (checkText(user["description"]) \
        or checkURL(user["entities"], "pixiv")):
            tweetList.append(tweet)
    if tweetList == []: return
    tweet = max(tweetList, key = lambda tweet: tweet["favorite_count"])
    MyTwitter.postFavorite(twitter, tweet["id_str"])
    MyTwitter.addUser(twitter, list_id, tweet["user"]["id_str"])

if __name__ == '__main__':
    try:
        list_id = sys.argv[1]
    except:
        print("Usage: python3 {0} [list_id]".format(sys.argv[0]))
        sys.exit()
    execute(list_id)

