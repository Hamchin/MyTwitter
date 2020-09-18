from loader import twitter
import datetime, time

def is_timeover(created_at, days):
    date = datetime.datetime.strptime(created_at, '%a %b %d %H:%M:%S +0000 %Y')
    date = date + datetime.timedelta(hours = 9)
    standard = datetime.datetime.now()
    standard = standard - datetime.timedelta(days = days)
    return standard > date

def get_like_data(tweets, days):
    likes_after = [tweet for tweet in tweets if not is_timeover(tweet['created_at'], days)]
    likes_before = [tweet['id_str'] for tweet in tweets if not is_timeover(tweet['created_at'], days - 1)]
    likes = [tweet for tweet in likes_after if tweet['id_str'] not in likes_before]
    like_users = [tweet['user']['id_str'] for tweet in likes]
    like_users = list(set(like_users))
    return len(likes), len(like_users)

def get_like_tweets(user_id):
    url = 'https://api.twitter.com/1.1/favorites/list.json'
    params = {
        'user_id': user_id,
        'count': 200,
        'exclude_replies': True
    }
    tweets, proceed = [], 0
    while proceed < 1000:
        res = twitter.session.get(url, params = params)
        if res.status_code == 200:
            proceed += 200
            tweets += res.json()
            try:
                params['max_id'] = tweets[-1]['id_str']
            except:
                return tweets
            if is_timeover(tweets[-1]['created_at'], 5):
                return tweets
        else:
            time.sleep(60)
    return tweets

def preprocess(users):
    items = []
    print('Number of User:')
    print(f'Before:\t{len(users)}', end = '\t')
    users = [user for user in users if user['followers_count'] < user['friends_count'] < 800]
    user_ids = [user['id_str'] for user in users]
    relations = twitter.get_friendships(user_ids = user_ids)
    users = [user for user, relation in zip(users, relations) if 'following' not in relation['connections']]
    likes_per_tweet = lambda user: user['favourites_count'] / (user['statuses_count'] or 1)
    users = sorted(users, key = likes_per_tweet, reverse = True)
    print(f'After:\t{len(users)}\n')
    print('Number of Like Tweets:')
    users = users[:20]
    for i, user in enumerate(users):
        if user['protected']: continue
        print(f'({i+1} / {len(users)})', end = '\t')
        tweets = get_like_tweets(user['id_str'])
        print(f'Before: {len(tweets)}', end = '\t')
        tweets = [tweet for tweet in tweets if tweet['retweet_count'] < 20 and tweet['favorite_count'] < 50]
        print(f'After: {len(tweets)}')
        item = {
            'id_str': user['id_str'],
            'name': user['name'],
            'screen_name': user['screen_name'],
            'friends_count': user['friends_count'],
            'followers_count': user['followers_count'],
            'statuses_count': user['statuses_count'],
            'like_count': user['favourites_count']
        }
        item['likes_1day'], item['like_users_1day'] = get_like_data(tweets, 1)
        item['likes_2day'], item['like_users_2day'] = get_like_data(tweets, 2)
        item['likes_3day'], item['like_users_3day'] = get_like_data(tweets, 3)
        item['likes_4day'], item['like_users_4day'] = get_like_data(tweets, 4)
        item['likes_5day'], item['like_users_5day'] = get_like_data(tweets, 5)
        items.append(item)
    return items

def get_items(screen_name):
    users = twitter.get_friends(screen_name = screen_name)
    items = preprocess(users)
    return items

def show_items(items):
    total = lambda item: sum([item[f'like_users_{i+1}day'] for i in range(5)])
    items = sorted(items, key = lambda item: total(item), reverse = True)
    for item in items:
        for key, value in item.items():
            print(f'{key}\t{value}')
        print(f"link: https://twitter.com/{item['screen_name']}\n")

if __name__ == '__main__':
    screen_name = input('\nScreen Name of Based User: ')
    print('\n', '=' * 50, '\n', sep = '')
    items = get_items(screen_name)
    print('\n', '=' * 50, '\n', sep = '')
    show_items(items)
