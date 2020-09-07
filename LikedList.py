import MyTwitter, sys, os, json, requests, datetime
from dotenv import load_dotenv

load_dotenv()
NOTICE_API_URL = os.environ['NOTICE_API_URL']

class List():
    id = ''
    user_ids = []
    def __init__(self, twitter, list_id):
        if list_id is None: return
        self.id = list_id
        users = MyTwitter.get_list_members(twitter, self.id)
        self.user_ids = [user['id_str'] for user in users]

# 通知を取得する
def get_notices(twitter, user_id):
    params = {'size': 1000}
    res = requests.get(NOTICE_API_URL, params = params)
    notices = json.loads(res.text)
    notices = [notice for notice in notices if notice['receiver_id'] == user_id]
    # メディアツイートのみに対する通知に絞る
    tweet_ids = list(set([notice['tweet_id'] for notice in notices]))
    tweets = MyTwitter.get_tweets(twitter, tweet_ids)
    media_tweet_ids = [tweet['id_str'] for tweet in tweets if 'extended_entities' in tweet]
    notices = [notice for notice in notices if notice['tweet_id'] in media_tweet_ids]
    return notices

# 通知の送信ユーザーを取得する
def get_sender_ids(notices, twitter, user_id):
    sender_ids = []
    # 最新1日分の通知を取得する
    date = datetime.datetime.now() - datetime.timedelta(days = 1)
    timestamp = int(date.timestamp())
    sender_ids = sender_ids + [notice['sender_id'] for notice in notices if notice['timestamp'] > timestamp]
    # 最新1件のメディアツイートの通知を取得する
    tweets = MyTwitter.get_user_timeline(twitter, user_id, 200, exclude_replies = True, include_rts = False)
    media_tweet_ids = [tweet['id_str'] for tweet in tweets if 'extended_entities' in tweet]
    media_tweet_id = media_tweet_ids[0] if media_tweet_ids != [] else ''
    sender_ids = sender_ids + [notice['sender_id'] for notice in notices if notice['tweet_id'] == media_tweet_id]
    sender_ids = list(set(sender_ids))
    return sender_ids

# リストへユーザーを追加する
def add_users(twitter, target_list, target_ids):
    for target_id in target_ids:
        if target_id in target_list.user_ids: continue
        MyTwitter.add_user(twitter, target_list.id, user_id = target_id)

# リストからユーザーを削除する
def delete_users(twitter, target_list, target_ids):
    for member_id in target_list.user_ids:
        if member_id in target_ids: continue
        MyTwitter.delete_user(twitter, target_list.id, user_id = member_id)

# リストを更新する
def update(target_list_id, excluded_list_id = None):
    twitter, user_id = MyTwitter.login()
    target_list = List(twitter, target_list_id)
    excluded_list = List(twitter, excluded_list_id)
    notices = get_notices(twitter, user_id)
    sender_ids = get_sender_ids(notices, twitter, user_id)
    sender_ids = [id for id in sender_ids if id not in excluded_list.user_ids]
    add_users(twitter, target_list, sender_ids)
    delete_users(twitter, target_list, sender_ids)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        update(sys.argv[1])
    elif len(sys.argv) == 3:
        update(sys.argv[1], sys.argv[2])
    else:
        print(f"Usage: python3 {sys.argv[0]} [TARGET_LIST_ID] [EXCLUDED_LIST_ID]")
