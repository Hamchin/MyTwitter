import requests, datetime

# リストのデータを取得する
def get_list_data(twitter, list_id):
    users = twitter.get_list_members(list_id = list_id)
    user_ids = [user['id_str'] for user in users]
    return {'id': list_id, 'user_ids': user_ids}

# 通知を取得する
def get_notices(twitter, notice_api_url, size = 0, media_only = False):
    params = {'receiver_id': twitter.user_id, 'size': size}
    notices = requests.get(notice_api_url + '/notices', params = params).json()
    # メディアツイートのみに対する通知に絞る
    if media_only:
        tweet_ids = list(set([notice['tweet_id'] for notice in notices]))
        tweets = twitter.get_tweets(tweet_ids = tweet_ids, trim_user = True)
        media_tweet_ids = [tweet['id_str'] for tweet in tweets if 'extended_entities' in tweet]
        notices = [notice for notice in notices if notice['tweet_id'] in media_tweet_ids]
    return notices

# 直近のツイートを取得する
def get_latest_tweets(twitter, size = 0):
    if size == 0: return []
    params = {'exclude_replies': True, 'exclude_retweets': True, 'trim_user': True, 'count': 200}
    tweets = twitter.get_user_timeline(**params)
    return tweets[:size]

# 通知の送信ユーザーを取得する
def get_sender_ids(twitter, notices, latest_days = 0, latest_tweets = 0, min_senders = 0):
    sender_ids = []
    # 直近の通知から取得する
    date = datetime.datetime.now() - datetime.timedelta(days = latest_days)
    timestamp = int(date.timestamp())
    sender_ids += [notice['sender_id'] for notice in notices if notice['timestamp'] > timestamp]
    sender_ids = list(set(sender_ids))
    # 直近のツイートから取得する
    tweets = get_latest_tweets(twitter, size = latest_tweets)
    tweet_ids = [tweet['id_str'] for tweet in tweets]
    sender_ids += [notice['sender_id'] for notice in notices if notice['tweet_id'] in tweet_ids]
    sender_ids = list(set(sender_ids))
    # 最低人数に達するまで取得する
    for notice in notices:
        if len(sender_ids) >= min_senders: break
        if notice['sender_id'] in sender_ids: continue
        sender_ids.append(notice['sender_id'])
    return sender_ids

# リストへユーザーを追加する
def add_users(twitter, target_list, target_ids):
    for target_id in target_ids:
        if target_id in target_list['user_ids']: continue
        twitter.add_user(list_id = target_list['id'], user_id = target_id)

# リストからユーザーを削除する
def delete_users(twitter, target_list, target_ids):
    for member_id in target_list['user_ids']:
        if member_id in target_ids: continue
        twitter.delete_user(list_id = target_list['id'], user_id = member_id)

# メイン関数
def main(twitter, notice_api_url, target_list_id = '', media_only = False, notice_size = 0, latest_days = 0, latest_tweets = 0, min_senders = 0):
    target_list = get_list_data(twitter, target_list_id)
    notices = get_notices(twitter, notice_api_url, notice_size, media_only)
    sender_ids = get_sender_ids(twitter, notices, latest_days, latest_tweets, min_senders)
    add_users(twitter, target_list, sender_ids)
    delete_users(twitter, target_list, sender_ids)
