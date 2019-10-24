import MyTwitter, sys, json

#ワードチェック
def include(text):
    word_list = {
        "定期", "募集", "いいね", "ふぁぼ", "スマホRPG",
        "#なうぷれ", "#nowplaying", "#NowPlaying", "#PS4share"
    }
    return True in [word in text for word in word_list]

#フォローユーザー取得
def get_following_id(twitter, user_id, list_id):
    user_list = MyTwitter.get_following_id(twitter, user_id)
    friend_list = MyTwitter.get_list_member(twitter, list_id)
    friend_list = [friend["id_str"] for friend in friend_list]
    user_list = [user for user in user_list if user not in friend_list]
    return list(reversed(user_list))

#トップツイート取得
def get_top_tweet(tweet_list):
    good_tweet_list = []
    for tweet in tweet_list:
        if tweet["favorited"] or MyTwitter.is_timeover(tweet["created_at"], 2):
            break
        elif MyTwitter.is_timeover(tweet["created_at"], 1) and good_tweet_list != []:
            break
        elif not include(tweet["text"]) and tweet["favorite_count"] > 0:
            good_tweet_list.append(tweet)
    if good_tweet_list == []:
        return None
    else:
        return max(good_tweet_list, key = lambda tweet: tweet["favorite_count"])

def execute(name, list_name = None):
    twitter, user_id = MyTwitter.login(name)
    with open('data/favorite.json', 'r') as f:
        user_list = json.load(f)
    if user_list[name] == []:
        list_id = MyTwitter.get_list_id(list_name) if list_name else ""
        user_list[name] = get_following_id(twitter, user_id, list_id)
    target = user_list[name].pop(0)
    with open('data/favorite.json', 'w') as f:
        json.dump(user_list, f, indent = 4)
    tweet_list = MyTwitter.get_tweet_list(twitter, target, 200)
    top_tweet = get_top_tweet(tweet_list)
    friendship = MyTwitter.get_friendship(twitter, [target])[0]["connections"]
    if "following" in friendship and top_tweet is not None:
        MyTwitter.post_favorite(twitter, top_tweet["id_str"])

if __name__ == '__main__':
    if len(sys.argv) == 3:
        execute(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 2:
        execute(sys.argv[1])
    else:
        print("Usage: python3 {0} [user_type] (exception_list_name)".format(sys.argv[0]))
        sys.exit()