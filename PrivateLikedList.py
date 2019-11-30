import MyTwitter, sys, json

def execute(list_name):
    twitter, myself = MyTwitter.login()
    list_id = MyTwitter.get_list_id(list_name)
    with open('data/protected.json', 'r') as f:
        protected_data = json.load(f)
        protected_users = [data[0] for data in protected_data]
    target = None
    for i, (user_id, checked) in enumerate(protected_data):
        if not checked:
            target = user_id
            protected_data[i][1] = True
            break
    if target is None:
        followers = MyTwitter.get_followers(twitter, myself)
        protected_users = [user['id_str'] for user in followers if user['protected']]
        protected_data = [[user_id, False] for user_id in protected_users]
        if protected_data:
            target = protected_data[0][0]
            protected_data[0][1] = True
    if target:
        tweets = MyTwitter.get_like_tweets(twitter, target, 1000, myself)
        if tweets:
            tweet = tweets[-1]
            if not MyTwitter.is_timeover(tweet['created_at'], 2):
                MyTwitter.add_user(twitter, list_id, target)
            else:
                MyTwitter.delete_user(twitter, list_id, target)
        else:
            MyTwitter.delete_user(twitter, list_id, target)
    with open('data/protected.json', 'w') as f:
        json.dump(protected_data, f, indent = 4)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        execute(sys.argv[1])
    else:
        print("Usage: python3 {0} [list_name]".format(sys.argv[0]))
        sys.exit()
