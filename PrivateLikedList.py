import MyTwitter, sys, json

def accept_user(twitter, user, trim_list_name):
    if user is None: return False
    if trim_list_name == '': return True
    trim_list_id = MyTwitter.get_list_id(trim_list_name)
    trim_members = [user['id_str'] for user in MyTwitter.get_list_members(twitter, trim_list_id)]
    if user in trim_members: return False
    return True

def accept_tweet(tweet):
    if tweet is None: return False
    if MyTwitter.is_timeover(tweet['created_at'], 2): return False
    return True

def execute(list_name, trim_list_name = ''):
    twitter, self_id = MyTwitter.login()
    list_id = MyTwitter.get_list_id(list_name)
    with open('data/protected.json', 'r') as f:
        protected_data = json.load(f)
        protected_users = [data[0] for data in protected_data]
    target, mytweet = None, None
    for i, (user_id, checked) in enumerate(protected_data):
        if not checked:
            target = user_id
            protected_data[i][1] = True
            break
    if target is None:
        followers = MyTwitter.get_followers(twitter, self_id)
        protected_users = [user['id_str'] for user in followers if user['protected']]
        protected_data = [[user_id, False] for user_id in protected_users]
        if protected_data:
            target = protected_data[0][0]
            protected_data[0][1] = True
    if accept_user(twitter, target, trim_list_name):
        url = "https://api.twitter.com/1.1/favorites/list.json"
        params = {'user_id': self_id, 'count': 200, 'exclude_replies': True}
        for _ in range(5):
            res = twitter.get(url, params = params)
            if res.status_code == 200: tweets = json.loads(res.text)
            else: sys.exit()
            for tweet in tweets:
                if self_id == tweet['user']['id_str']:
                    mytweet = tweet
                    break
            if mytweet or tweets == []: break
            else: params['max_id'] = tweets[-1]['id_str']
        if accept_tweet(mytweet): MyTwitter.add_user(twitter, list_id, user_id = target)
        else: MyTwitter.delete_user(twitter, list_id, user_id = target)
    with open('data/protected.json', 'w') as f:
        json.dump(protected_data, f, indent = 4)

if __name__ == '__main__':
    if len(sys.argv) == 3:
        execute(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 2:
        execute(sys.argv[1])
    else:
        print("Usage: python3 {0} [LIST_NAME] (EXCLUDED_LIST_NAME)".format(sys.argv[0]))
        sys.exit()
