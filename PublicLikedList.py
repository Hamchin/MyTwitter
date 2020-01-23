import MyTwitter, sys, json

def execute(list_name, trim_list_name = ''):
    twitter, myself = MyTwitter.login()
    tweets = MyTwitter.get_tweets(twitter, myself, 200)
    ids = [tweet["id_str"] for tweet in tweets if not MyTwitter.is_timeover(tweet['created_at'], 2)]
    with open('data/follower.json', 'r') as f:
        followers = json.load(f)
        followers = [user[0] for user in followers]
    with open('data/protected.json', 'r') as f:
        protected_data = json.load(f)
        protected_users = [data[0] for data in protected_data]
    with open('data/liked.json', 'r') as f:
        liked = json.load(f)
    for tweet_id in ids:
        likes = MyTwitter.get_like_user_ids(tweet_id, [myself])
        liked[tweet_id] = list(set(liked.get(tweet_id, []) + likes))
    liked = {tweet_id: data for tweet_id, data in liked.items() if tweet_id in ids}
    users = list(set([user for tweet_id, data in liked.items() for user in data if user in followers]))
    list_id = MyTwitter.get_list_id(list_name)
    members = [user["id_str"] for user in MyTwitter.get_list_members(twitter, list_id)]
    members = [user_id for user_id in members if user_id not in protected_users]
    trim_list_id = MyTwitter.get_list_id(trim_list_name) if trim_list_name else None
    trim_members = [user["id_str"] for user in MyTwitter.get_list_members(twitter, trim_list_id)] if trim_list_id else []
    delete_ids = [user_id for user_id in members if user_id not in users or user_id in trim_members]
    for user_id in delete_ids:
        MyTwitter.delete_user(twitter, list_id, user_id)
    add_ids = [user_id for user_id in users if user_id not in members and user_id not in trim_members]
    for user_id in add_ids:
        MyTwitter.add_user(twitter, list_id, user_id)
    with open('data/liked.json', 'w') as f:
        json.dump(liked, f, indent = 4)

if __name__ == '__main__':
    if len(sys.argv) == 3:
        execute(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 2:
        execute(sys.argv[1])
    else:
        print("Usage: python3 {0} [list_name] (trim_list_name)".format(sys.argv[0]))
        sys.exit()
