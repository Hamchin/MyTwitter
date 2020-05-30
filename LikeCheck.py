import MyTwitter, requests, json, datetime

NOTICE_API = json.load(open('data/reference.json', 'r'))

class LikeChecker():
    twitter = None
    user_id = None
    excluded_list = None # {'name': LIST_NAME, 'id': LIST_ID}
    target_type = None
    display_type = None
    target_types = [
        'Following',
        'Followers',
        'Follow / Followed',
        'Follow / Not Followed',
        'Not Follow / Followed'
    ]
    display_types = ['Like Count', 'Last Date']

    # 初期化
    def __init__(self, excluded_list = None, target_type = None, display_type = None):
        self.twitter, self.user_id = MyTwitter.login()
        self.excluded_list = excluded_list
        self.target_type = target_type
        self.display_type = display_type

    # 全項目について質問する
    def ask_all(self):
        self.ask_excluded_list()
        self.ask_target_type()
        self.ask_display_type()

    # 除外するリストを質問する
    def ask_excluded_list(self):
        excluded_list = {'name': None, 'id': None}
        lists = self.get_lists()
        print()
        for i, item in enumerate(lists):
            print(f"{i+1}: {item['name']}")
        in_str = input('\n' + "? Excluded List (Number): ")
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
        in_str = input('\n' + "? Target Users (Number): ")
        index = self.get_number(in_str)
        assert(1 <= index <= len(self.target_types))
        target_type = self.target_types[index - 1]
        self.target_type = target_type

    # 表示タイプを質問する
    def ask_display_type(self):
        print()
        for i, display_type in enumerate(self.display_types):
            print(f"{i+1}: {display_type}")
        in_str = input('\n' + "? Display Mode (Number): ")
        index = self.get_number(in_str)
        assert(1 <= index <= len(self.display_types))
        display_type = self.display_types[index - 1]
        self.display_type = display_type

    # リストの情報を取得する
    def get_lists(self):
        lists = json.load(open('data/lists.json', 'r'))
        lists = [{'name': name, 'id': ID} for name, ID in lists.items()]
        return lists

    # 文字列を整数へ変換する
    def get_number(self, string):
        assert(string.isdecimal())
        return int(string)

    # いいねチェック
    def check(self):
        targets = self.get_targets()
        notices = self.get_notices()
        if self.display_type == 'Like Count':
            self.check_like_count(targets, notices)
        elif self.display_type == 'Last Date':
            self.check_last_date(targets, notices)
        else:
            raise Exception("Invalid Display Type")

    # 対象ユーザーを取得する
    def get_targets(self):
        # フォロー
        if self.target_type == 'Following':
            targets = MyTwitter.get_friends(self.twitter, self.user_id)
        # フォロワー
        elif self.target_type == 'Followers':
            targets = MyTwitter.get_followers(self.twitter, self.user_id)
        # 相互フォロー
        elif self.target_type == 'Follow / Followed':
            friends = MyTwitter.get_friends(self.twitter, self.user_id)
            follower_ids = MyTwitter.get_follower_ids(self.twitter, self.user_id)
            targets = [user for user in friends if user['id_str'] in follower_ids]
        # 片思い
        elif self.target_type == 'Follow / Not Followed':
            friends = MyTwitter.get_friends(self.twitter, self.user_id)
            follower_ids = MyTwitter.get_follower_ids(self.twitter, self.user_id)
            targets = [user for user in friends if user['id_str'] not in follower_ids]
        # 片思われ
        elif self.target_type == 'Not Follow / Followed':
            followers = MyTwitter.get_followers(self.twitter, self.user_id)
            friend_ids = MyTwitter.get_friend_ids(self.twitter, self.user_id)
            targets = [user for user in followers if user['id_str'] not in friend_ids]
        else:
            raise Exception("Invalid Target Type")
        if self.excluded_list['id']:
            excluded_users = MyTwitter.get_list_members(self.twitter, self.excluded_list['id'])
            excluded_user_ids = [user['id_str'] for user in excluded_users]
            targets = [target for target in targets if target['id_str'] not in excluded_user_ids]
        return targets

    # 通知を取得する
    def get_notices(self):
        url = NOTICE_API['ENDPOINT'] + NOTICE_API['GET_NOTICES_URI']
        params = {'size': 100000}
        res = requests.get(url, params = params)
        notices = json.loads(res.text)
        notices = [notice for notice in notices if notice['receiver_id'] == self.user_id]
        return notices

    # いいね数の降順に表示する
    def check_like_count(self, targets, notices):
        target_dict = {target['id_str']: target for target in targets}
        counter = {target['id_str']: 0 for target in targets}
        for notice in notices:
            sender_id = notice['sender_id']
            if target_dict.get(sender_id):
                counter[sender_id] += 1
        sorted_counter = sorted(counter.items(), key = lambda item: -item[1])
        print()
        for user_id, count in sorted_counter:
            user = target_dict[user_id]
            print(f"{user['name']} : {count}")
            print(f"https://twitter.com/{user['screen_name']}\n")

    # いいねした最終日時の新しい順に表示する
    def check_last_date(self, targets, notices):
        target_dict = {target['id_str']: target for target in targets}
        history = {target['id_str']: 0 for target in targets}
        for notice in notices:
            sender_id = notice['sender_id']
            if target_dict.get(sender_id):
                history[sender_id] = max(history[sender_id], notice['timestamp'])
        sorted_history = sorted(history.items(), key = lambda item: -item[1])
        print()
        for user_id, timestamp in sorted_history:
            user = target_dict[user_id]
            if timestamp == 0:
                date = None
            else:
                date = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
            print(f"{user['name']} : {date}")
            print(f"https://twitter.com/{user['screen_name']}\n")

if __name__ == '__main__':
    checker = LikeChecker()
    checker.ask_all()
    checker.check()
