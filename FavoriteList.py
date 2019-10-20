import MyTwitter, sys, json

def execute(name, list_name):
    twitter, user_id = MyTwitter.login(name)
    tweets = MyTwitter.get_tweet_list(twitter, user_id, 200)
    id_list = [tweet["id_str"] for tweet in tweets if not MyTwitter.is_timeover(tweet['created_at'], 2)]
    friend_list = MyTwitter.get_following_id(twitter, user_id)
    with open('data/favored.json', 'r') as f:
        favored = json.load(f)
    for tweet_id in id_list:
        fav_list = MyTwitter.get_fav_user_id_list(tweet_id, [user_id])
        favored[tweet_id] = list(set(favored.get(tweet_id, []) + fav_list))
    favored = {k: v for k, v in favored.items() if k in id_list}
    user_list = list(set([user for k, v in favored.items() for user in v if user in friend_list]))
    list_id = MyTwitter.get_list_id(list_name)
    member_list = [user["id_str"] for user in MyTwitter.get_list_member(twitter, list_id)]
    for user_id in [user_id for user_id in member_list if user_id not in user_list]:
        MyTwitter.delete_user(twitter, list_id, user_id)
    for user_id in [user_id for user_id in user_list if user_id not in member_list]:
        MyTwitter.add_user(twitter, list_id, user_id)
    with open('data/favored.json', 'w') as f:
        json.dump(favored, f, indent = 4)

if __name__ == '__main__':
    try:
        execute(sys.argv[1], sys.argv[2])
    except:
        print("Usage: python3 {0} [user_type] [list_name]".format(sys.argv[0]))
        sys.exit()