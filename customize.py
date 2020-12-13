from loader import twitter, TARGET_LIST_ID, NOTICE_API_URL
import requests, datetime

class List():
    id = ''
    user_ids = []
    def __init__(self, list_id):
        if list_id == '': return
        self.id = list_id
        users = twitter.get_list_members(list_id = self.id)
        self.user_ids = [user['id_str'] for user in users]

# 通知を取得する
def get_notices(size = 0, media_only = False):
    params = {'receiver_id': twitter.user_id, 'size': size}
    notices = requests.get(NOTICE_API_URL + '/notices', params = params).json()
    # メディアツイートのみに対する通知に絞る
    if media_only:
        tweet_ids = list(set([notice['tweet_id'] for notice in notices]))
        tweets = twitter.get_tweets(tweet_ids = tweet_ids, trim_user = True)
        media_tweet_ids = [tweet['id_str'] for tweet in tweets if 'extended_entities' in tweet]
        notices = [notice for notice in notices if notice['tweet_id'] in media_tweet_ids]
    return notices

# 直近のツイートを取得する
def get_latest_tweets(size = 0, media_only = False):
    if size == 0: return []
    params = {'exclude_replies': True, 'exclude_retweets': True, 'trim_user': True, 'count': 200}
    tweets = twitter.get_user_timeline(**params)
    if media_only: tweets = list(filter(lambda tweet: 'extended_entities' in tweet), tweets)
    return tweets[:size]

# 通知の送信ユーザーを取得する
def get_sender_ids(notices, days = 1, latest_tweets_option = {}):
    sender_ids = []
    # 直近の通知を取得する
    date = datetime.datetime.now() - datetime.timedelta(days = days)
    timestamp = int(date.timestamp())
    sender_ids += [notice['sender_id'] for notice in notices if notice['timestamp'] > timestamp]
    sender_ids = list(set(sender_ids))
    # 直近のツイートに対する通知を取得する
    tweets = get_latest_tweets(**latest_tweets_option)
    tweet_ids = [tweet['id_str'] for tweet in tweets]
    sender_ids += [notice['sender_id'] for notice in notices if notice['tweet_id'] in tweet_ids]
    sender_ids = list(set(sender_ids))
    return sender_ids

# リストへユーザーを追加する
def add_users(target_list, target_ids):
    for target_id in target_ids:
        if target_id in target_list.user_ids: continue
        twitter.add_user(list_id = target_list.id, user_id = target_id)

# リストからユーザーを削除する
def delete_users(target_list, target_ids):
    for member_id in target_list.user_ids:
        if member_id in target_ids: continue
        twitter.delete_user(list_id = target_list.id, user_id = member_id)

if __name__ == '__main__':
    target_list = List(TARGET_LIST_ID)
    notices = get_notices(size = 100, media_only = False)
    latest_tweets_option = {'size': 1, 'media_only': False}
    sender_ids = get_sender_ids(notices, days = 1, latest_tweets_option = latest_tweets_option)
    add_users(target_list, sender_ids)
    delete_users(target_list, sender_ids)
