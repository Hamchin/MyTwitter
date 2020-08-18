import MyTwitter, sys, os, json, requests, datetime
from dotenv import load_dotenv

load_dotenv()
NOTICE_API_URL = os.getenv('NOTICE_API_URL')

class List():
    id = ''
    member_ids = []
    # フォローしているユーザーを除外するかどうか
    trim_friends = False
    # フォローしていないユーザーを除外するかどうか
    trim_not_friends = False

    def __init__(self, list_id, trim_friends = False, trim_not_friends = False):
        self.id = list_id
        self.trim_friends = trim_friends
        self.trim_not_friends = trim_not_friends
        twitter, user_id = MyTwitter.login()
        members = MyTwitter.get_list_members(twitter, self.id)
        self.member_ids = [member['id_str'] for member in members]

class ListUpdater():
    twitter = None
    user_id = ''
    notices = []
    sender_ids = []
    friend_ids = []
    target_list = None
    excluded_list = None

    def __init__(self, target_list, excluded_list):
        self.twitter, self.user_id = MyTwitter.login()
        self.target_list = target_list
        self.excluded_list = excluded_list
        self.notices = self.get_notices()
        self.sender_ids = list(set([notice['sender_id'] for notice in self.notices]))
        self.friend_ids = MyTwitter.get_friend_ids(self.twitter, self.user_id)

    # 通知取得
    def get_notices(self):
        params = {'size': 1000}
        res = requests.get(NOTICE_API_URL, params = params)
        notices = json.loads(res.text)
        notices = [notice for notice in notices if notice['receiver_id'] == self.user_id]
        # 最新100件または1日以内の通知に絞る
        now = datetime.datetime.now()
        date = now - datetime.timedelta(days = 1)
        timestamp = int(date.timestamp())
        index = next(i for i, notice in enumerate(notices) if notice['timestamp'] < timestamp)
        size = max(100, index)
        notices = notices[:size]
        # メディアツイートのみに対する通知に絞る
        tweet_ids = list(set([notice['tweet_id'] for notice in notices]))
        tweets = MyTwitter.get_tweets(self.twitter, tweet_ids)
        tweet_ids = [tweet['id_str'] for tweet in tweets if 'extended_entities' in tweet]
        notices = [notice for notice in notices if notice['tweet_id'] in tweet_ids]
        return notices

    # リストへユーザー追加
    def add_users(self, target_list, target_ids):
        for target_id in target_ids:
            if target_id in target_list.member_ids: continue
            MyTwitter.add_user(self.twitter, target_list.id, user_id = target_id)

    # リストからユーザー削除
    def delete_users(self, target_list, target_ids):
        for member_id in target_list.member_ids:
            if member_id in target_ids: continue
            MyTwitter.delete_user(self.twitter, target_list.id, user_id = member_id)

    # リスト更新
    def update(self):
        target_ids = self.sender_ids
        if self.excluded_list:
            trim_ids = self.excluded_list.member_ids
            target_ids = [id for id in target_ids if id not in trim_ids]
        if self.target_list.trim_friends:
            target_ids = [id for id in target_ids if id not in self.friend_ids]
        if self.target_list.trim_not_friends:
            target_ids = [id for id in target_ids if id in self.friend_ids]
        self.add_users(self.target_list, target_ids)
        self.delete_users(self.target_list, target_ids)

if __name__ == '__main__':
    target_list = None
    excluded_list = None
    if len(sys.argv) == 2:
        target_list = List(sys.argv[1])
    elif len(sys.argv) == 3:
        target_list = List(sys.argv[1])
        excluded_list = List(sys.argv[2])
    else:
        print(f"Usage: python3 {sys.argv[0]} [TARGET_LIST_ID] [EXCLUDED_LIST_ID]")
        sys.exit()
    updater = ListUpdater(target_list, excluded_list)
    updater.update()
