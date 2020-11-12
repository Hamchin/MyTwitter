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
def get_notices(media_only = False):
    params = {'size': 1000}
    notices = requests.get(NOTICE_API_URL + '/notices', params = params).json()
    notices = [notice for notice in notices if notice['receiver_id'] == twitter.user_id]
    # メディアツイートのみに対する通知に絞る
    if media_only:
        tweet_ids = list(set([notice['tweet_id'] for notice in notices]))
        tweets = twitter.get_tweets(tweet_ids = tweet_ids, trim_user = True)
        media_tweet_ids = [tweet['id_str'] for tweet in tweets if 'extended_entities' in tweet]
        notices = [notice for notice in notices if notice['tweet_id'] in media_tweet_ids]
    return notices

# 通知の送信ユーザーを取得する
def get_sender_ids(notices, days = 1, include_latest_media = False):
    sender_ids = []
    # 直近指定日数分の通知を取得する
    date = datetime.datetime.now() - datetime.timedelta(days = days)
    timestamp = int(date.timestamp())
    sender_ids += [notice['sender_id'] for notice in notices if notice['timestamp'] > timestamp]
    sender_ids = list(set(sender_ids))
    # 直近のメディアツイートに対する通知を取得する
    if include_latest_media:
        params = {'exclude_replies': True, 'exclude_retweets': True, 'trim_user': True, 'count': 200}
        tweets = twitter.get_user_timeline(**params)
        media_tweet_ids = [tweet['id_str'] for tweet in tweets if 'extended_entities' in tweet]
        media_tweet_id = media_tweet_ids[0] if media_tweet_ids != [] else ''
        sender_ids += [notice['sender_id'] for notice in notices if notice['tweet_id'] == media_tweet_id]
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

# リストを更新する
def update():
    target_list = List(TARGET_LIST_ID)
    notices = get_notices(media_only = False)
    sender_ids = get_sender_ids(notices, days = 1, include_latest_media = False)
    add_users(target_list, sender_ids)
    delete_users(target_list, sender_ids)

if __name__ == '__main__':
    update()
