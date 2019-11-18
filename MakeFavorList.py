import MyTwitter, sys, json

def execute(list_name, exception_list_name = ''):
    twitter, user_id = MyTwitter.login()
    tweets = MyTwitter.get_tweets(twitter, user_id, 200)
    ids = [tweet["id_str"] for tweet in tweets if not MyTwitter.is_timeover(tweet['created_at'], 2)]
    friends = MyTwitter.get_friend_ids(twitter, user_id)
    with open('data/favored.json', 'r') as f:
        favored = json.load(f)
    for tweet_id in ids:
        favs = MyTwitter.get_like_user_ids(tweet_id, [user_id])
        favored[tweet_id] = list(set(favored.get(tweet_id, []) + favs))
    favored = {k: v for k, v in favored.items() if k in ids}
    users = list(set([user for k, v in favored.items() for user in v if user in friends]))
    list_id = MyTwitter.get_list_id(list_name)
    members = [user["id_str"] for user in MyTwitter.get_list_members(twitter, list_id)]
    exception_list_id = MyTwitter.get_list_id(exception_list_name) if exception_list_name else None
    exception_members = [user["id_str"] for user in MyTwitter.get_list_members(twitter, exception_list_id)] if exception_list_id else []
    for user_id in [user_id for user_id in members if user_id not in users or user_id in exception_members]:
        MyTwitter.delete_user(twitter, list_id, user_id)
    for user_id in [user_id for user_id in users if user_id not in members and user_id not in exception_members]:
        MyTwitter.add_user(twitter, list_id, user_id)
    with open('data/favored.json', 'w') as f:
        json.dump(favored, f, indent = 4)

if __name__ == '__main__':
    if len(sys.argv) == 3:
        execute(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 2:
        execute(sys.argv[1])
    else:
        print("Usage: python3 {0} [list_name] (exception_list_name)".format(sys.argv[0]))
        sys.exit()
