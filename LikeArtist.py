
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

def execute(main_name, sub_name, list_name):
    main, user_id = MyTwitter.login(main_name)
    if sub_name: sub, user_id = MyTwitter.login(sub_name)
    list_id = MyTwitter.getID(list_name)
    tweetList = []
    timeline = MyTwitter.getListTimeline(main, list_id, 1000)
    for tweet in timeline:
        if tweet.get("retweeted_status"): tweet = tweet["retweeted_status"]
        user = tweet["user"]
        if tweet["entities"].get("media") \
        and MyTwitter.isTimeover(tweet["created_at"], 7) == False \
        and tweet["favorite_count"] > 1000 \
        and MyTwitter.isFavorited(main, tweet["id_str"]) == False \
        and user["followers_count"] > 2 * user["friends_count"] \
        and user["followers_count"] > 1000 \
        and tweet["favorite_count"] > 2 * tweet["retweet_count"] \
        and (checkText(user["description"]) \
        or checkURL(user["entities"], "pixiv")):
            tweetList.append(tweet)
    if tweetList == []: return
    tweet = max(tweetList, key = lambda tweet: tweet["favorite_count"])
    MyTwitter.postFavorite(main, tweet["id_str"])
    if sub_name: MyTwitter.postFavorite(sub, tweet["id_str"])
    #MyTwitter.addUser(main, list_id, tweet["user"]["id_str"])

if __name__ == '__main__':
    if len(sys.argv) == 4:
        execute(sys.argv[1], sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 3:
        execute(sys.argv[1], None, sys.argv[2])
    else:
        print("Usage: python3 {0} [name] (name) [list_name]".format(sys.argv[0]))
        sys.exit()

