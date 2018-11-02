
# coding: utf-8

import MyTwitter
import json
import sys
import time

def getKeyword():
    keywordList = []
    tagList = [
        "All Tag",
        "#バイク乗りと繋がりたい",
        "#バイク好きと繋がりたい",
        "#YAMAHAが美しい",
        "#初心者ライダー",
        "#バイク初心者",
        "#バイク女子",
        "#ツーリング",
        "#ツーリング仲間募集",
        "#CBを晒すとRTが来るらしい",
        "#CBRを晒すとRTが来るらしい",
        "#YZFを晒すとRTが来るらしい",
        "#バイク乗りとして軽く自己紹介"
    ]
    for i, tag in enumerate(tagList):
        print("{0:>2}: {1}".format(i, tag))
    wordList = input('\nKeyword >> ')
    MAX = int(input('MAX >> '))
    wordList = wordList.split()
    for word in wordList:
        if word.isdigit():
            index = int(word)
            if index == 0:
                keywordList.extend(tagList[1:])
            elif index in range(len(tagList)):
                keywordList.append(tagList[index])
        else:
            keywordList.append(word)
    return [" OR ".join(keywordList), MAX]

def search(twitter, keyword, MAX):
    url = "https://api.twitter.com/1.1/search/tweets.json"
    params = {
        "q": keyword,
        "lang": "ja",
        "result_type": "recent",
        "count": 100
    }
    count = 0
    limit = 0
    while True:
        req = twitter.get(url, params = params)
        if req.status_code == 200:
            timeline = json.loads(req.text)
            for tweet in timeline["statuses"]:
                if count >= MAX: return
                if tweet["entities"]["user_mentions"] == [] \
                and tweet["entities"]["urls"] == [] \
                and tweet["entities"].get("media") \
                and tweet["user"]["favourites_count"] >= 1000 \
                and tweet["user"]["friends_count"] >= 100 \
                and tweet["user"]["followers_count"] >= 100 \
                and tweet["user"]["favourites_count"] >= tweet["user"]["statuses_count"] * 2:
                    req = MyTwitter.postFavorite(twitter, tweet["id_str"])
                    if req.status_code == 200:
                        print("\n{0}".format(tweet["text"]))
                        print("OK => {0}".format(count))
                        count += 1
                        limit = 0
                        time.sleep(1)
                    else:
                        print("Error: %d\n" % req.status_code)
                        limit += 1
                        if limit >= 5: return
            params["max_id"] = timeline["statuses"][-1]["id_str"]
        else:
            print("Error: %d\n" % req.status_code)
            sys.exit()

def execute():
    twitter = MyTwitter.login()
    keyword, MAX = getKeyword()
    search(twitter, keyword, MAX)

if __name__ == '__main__':
    execute()

