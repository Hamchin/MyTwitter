from loader import twitter, NOTICE_API_URL
import requests, datetime

class LikeChecker():
    notices = []
    excluded_list = None # {'name': LIST_NAME, 'id': LIST_ID}
    target_type = None
    target_types = [
        'Following',
        'Followers',
        'Follow / Followed',
        'Follow / Not Followed',
        'Not Follow / Followed'
    ]

    # 初期化
    def __init__(self, excluded_list = None, target_type = None):
        self.excluded_list = excluded_list
        self.target_type = target_type

    # リストの情報を取得する
    def get_lists(self):
        lists = twitter.get_lists()
        lists = [{'id': item['id_str'], 'name': item['name']} for item in lists]
        return lists

    # 文字列を整数へ変換する
    def get_number(self, string):
        assert(string.isdecimal())
        return int(string)

    # 除外するリストを質問する
    def ask_excluded_list(self):
        excluded_list = None
        lists = self.get_lists()
        print()
        for i, item in enumerate(lists):
            print(f"{i+1}: {item['name']}")
        in_str = input('\n' + '? Excluded List (Number): ')
        if in_str != '':
            index = self.get_number(in_str)
            assert(1 <= index <= len(lists))
            excluded_list = lists[index - 1]
        self.excluded_list = excluded_list

    # 対象ユーザーの種類を質問する
    def ask_target_type(self):
        print()
        for i, target_type in enumerate(self.target_types):
            print(f"{i+1}: {target_type}")
        in_str = input('\n' + '? Target Users (Number): ')
        index = self.get_number(in_str)
        assert(1 <= index <= len(self.target_types))
        target_type = self.target_types[index - 1]
        self.target_type = target_type

    # 対象ユーザーを取得する
    def get_targets(self):
        # フォロー
        if self.target_type == 'Following':
            targets = twitter.get_friends()
        # フォロワー
        elif self.target_type == 'Followers':
            targets = twitter.get_followers()
        # 相互フォロー
        elif self.target_type == 'Follow / Followed':
            friends = twitter.get_friends()
            follower_ids = twitter.get_follower_ids()
            targets = [user for user in friends if user['id_str'] in follower_ids]
        # 片思い
        elif self.target_type == 'Follow / Not Followed':
            friends = twitter.get_friends()
            follower_ids = twitter.get_follower_ids()
            targets = [user for user in friends if user['id_str'] not in follower_ids]
        # 片思われ
        elif self.target_type == 'Not Follow / Followed':
            followers = twitter.get_followers()
            friend_ids = twitter.get_friend_ids()
            targets = [user for user in followers if user['id_str'] not in friend_ids]
        else:
            raise Exception('Invalid Target Type')
        if self.excluded_list:
            excluded_users = twitter.get_list_members(list_id = self.excluded_list['id'])
            excluded_user_ids = [user['id_str'] for user in excluded_users]
            targets = [target for target in targets if target['id_str'] not in excluded_user_ids]
        return targets

    # 通知を取得する
    def get_notices(self):
        count = input('\n' + '? Number of Notices (Number): ')
        count = 1000 if count == '' else int(count)
        params = {'size': count}
        res = requests.get(NOTICE_API_URL + '/notices', params = params)
        notices = res.json()
        notices = [notice for notice in notices if notice['receiver_id'] == twitter.user_id]
        return notices

    # いいねチェック
    def check(self):
        targets = self.get_targets()
        if self.notices == []: self.notices = self.get_notices()
        target_dict = {target['id_str']: target for target in targets}
        notice_dict = {target['id_str']: {'timestamp': 0, 'count': 0} for target in targets}
        for notice in self.notices:
            sender_id = notice['sender_id']
            if target_dict.get(sender_id):
                timestamp = max(notice_dict[sender_id]['timestamp'], notice['timestamp'])
                notice_dict[sender_id]['timestamp'] = timestamp
                notice_dict[sender_id]['count'] += 1
        notice_list = sorted(notice_dict.items(), key = lambda item: -item[1]['timestamp'])
        def get_date(timestamp):
            return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
        print('\n', '=' * 60, '\n', sep = '')
        for user_id, notice in notice_list:
            user = target_dict[user_id]
            date = get_date(notice['timestamp']) if notice['timestamp'] else None
            print(f"Name: {user['name']}")
            print(f"Last Date: {date}")
            print(f"Like Count: {notice['count']}")
            print(f"https://twitter.com/{user['screen_name']}\n")
        print('=' * 60)

if __name__ == '__main__':
    checker = LikeChecker()
    while True:
        checker.ask_excluded_list()
        checker.ask_target_type()
        checker.check()
