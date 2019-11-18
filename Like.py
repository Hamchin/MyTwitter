import MyTwitter, sys, json

# ワードチェック
def include(text):
    words = {
        "定期", "募集", "いいね", "ふぁぼ", "スマホRPG",
        "#なうぷれ", "#nowplaying", "#NowPlaying", "#PS4share"
    }
    return True in [word in text for word in words]

# フォローユーザー取得
def get_friend_ids(twitter, user_id, list_id):
    users = MyTwitter.get_friend_ids(twitter, user_id)
    friends = MyTwitter.get_list_members(twitter, list_id)
    friends = [friend["id_str"] for friend in friends]
    users = [user for user in users if user not in friends]
    return list(reversed(users))

# トップツイート取得
def get_top_tweet(tweets):
    good_tweets = []
    for tweet in tweets:
        if tweet["favorited"] or MyTwitter.is_timeover(tweet["created_at"], 2):
            break
        elif MyTwitter.is_timeover(tweet["created_at"], 1) and good_tweets != []:
            break
        elif not include(tweet["text"]) and tweet["favorite_count"] > 0:
            good_tweets.append(tweet)
    if good_tweets == []:
        return None
    else:
        return max(good_tweets, key = lambda tweet: tweet["favorite_count"])

def execute(list_name = None):
    twitter, user_id = MyTwitter.login()
    with open('data/favorite.json', 'r') as f:
        users = json.load(f)
    if users == []:
        list_id = MyTwitter.get_list_id(list_name) if list_name else ""
        users = get_friend_ids(twitter, user_id, list_id)
    target = users.pop(0)
    with open('data/favorite.json', 'w') as f:
        json.dump(users, f, indent = 4)
    tweets = MyTwitter.get_tweets(twitter, target, 200)
    top_tweet = get_top_tweet(tweets)
    friendship = MyTwitter.get_friendship(twitter, [target])[0]["connections"]
    if "following" in friendship and top_tweet is not None:
        MyTwitter.like(twitter, top_tweet["id_str"])

if __name__ == '__main__':
    if len(sys.argv) == 2:
        execute(sys.argv[1])
    elif len(sys.argv) == 1:
        execute()
    else:
        print("Usage: python3 {0} (exception_list_name)".format(sys.argv[0]))
        sys.exit()
