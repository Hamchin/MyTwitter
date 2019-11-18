import MyTwitter, sys

# テキストチェック
def check_text(text):
    word_list = ["アニメーター", "イラスト", "絵描き", "pixiv"]
    return True in [word in text for word in word_list]

# URLチェック
def check_url(entities, word):
    try:
        if word in entities["url"]["urls"][0]["display_url"]: return True
    except:
        pass
    return True in [word in url["display_url"] for url in entities["description"]["urls"]]

def execute(list_name):
    twitter, user_id = MyTwitter.login()
    list_id = MyTwitter.get_list_id(list_name)
    tweet_list = []
    timeline = MyTwitter.get_list_timeline(twitter, list_id, 1000)
    for tweet in timeline:
        if tweet.get("retweeted_status"): tweet = tweet["retweeted_status"]
        user = tweet["user"]
        if tweet["entities"].get("media") \
        and MyTwitter.is_timeover(tweet["created_at"], 7) == False \
        and tweet["favorite_count"] > 1000 \
        and MyTwitter.is_favorited(twitter, tweet["id_str"]) == False \
        and user["followers_count"] > 2 * user["friends_count"] \
        and user["followers_count"] > 1000 \
        and tweet["favorite_count"] > 2 * tweet["retweet_count"] \
        and (check_text(user["description"]) \
        or check_url(user["entities"], "pixiv")):
            tweet_list.append(tweet)
    if tweet_list == []: return
    tweet = max(tweet_list, key = lambda tweet: tweet["favorite_count"])
    MyTwitter.post_favorite(twitter, tweet["id_str"])

if __name__ == '__main__':
    if len(sys.argv) == 2:
        execute(sys.argv[1])
    else:
        print("Usage: python3 {0} [list_name]".format(sys.argv[0]))
        sys.exit()
