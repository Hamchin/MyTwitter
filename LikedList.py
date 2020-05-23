import MyTwitter, NoticeDB, sys, requests, json

class List():
    name = ''
    id = ''
    member_ids = []
    trim_friends = False # フォローしているユーザーを除外するかどうか
    trim_not_friends = False # フォローしていないユーザーを除外するかどうか

    def __init__(self, name, trim_friends = False, trim_not_friends = False):
        self.name = name
        self.id = MyTwitter.get_list_id(self.name)
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
    list_instances = []
    trim_list_instance = None

    def __init__(self, list_instances, trim_list_instance):
        self.twitter, self.user_id = MyTwitter.login()
        self.list_instances = list_instances
        self.trim_list_instance = trim_list_instance
        self.notices = self.get_notices(100)
        self.sender_ids = list(set([notice['sender_id'] for notice in self.notices]))
        self.friend_ids = MyTwitter.get_friend_ids(self.twitter, self.user_id)

    # 通知取得
    def get_notices(self, size):
        url = NoticeDB.NOTICE_API['ENDPOINT'] + NoticeDB.NOTICE_API['GET_NOTICES_URI']
        params = {'size': size}
        res = requests.get(url, params = params)
        notices = json.loads(res.text)
        notices = [notice for notice in notices if notice['receiver_id'] == self.user_id]
        return notices

    # リストへユーザー追加
    def add_users(self, list_instance, target_ids):
        for target_id in target_ids:
            if target_id in list_instance.member_ids: continue
            MyTwitter.add_user(self.twitter, list_instance.id, user_id = target_id)

    # リストからユーザー削除
    def delete_users(self, list_instance, target_ids):
        for member_id in list_instance.member_ids:
            if member_id in target_ids: continue
            MyTwitter.delete_user(self.twitter, list_instance.id, user_id = member_id)

    # リスト更新
    def update(self):
        for list_instance in list_instances:
            target_ids = self.sender_ids
            if self.trim_list_instance:
                trim_ids = self.trim_list_instance.member_ids
                target_ids = [id for id in target_ids if id not in trim_ids]
            if list_instance.trim_friends:
                target_ids = [id for id in target_ids if id not in self.friend_ids]
            if list_instance.trim_not_friends:
                target_ids = [id for id in target_ids if id in self.friend_ids]
            self.add_users(list_instance, target_ids)
            self.delete_users(list_instance, target_ids)

if __name__ == '__main__':
    expected_args = ['[FIRST_LIST_NAME]', '[SECOND_LIST_NAME]', '[EXCLUDED_LIST_NAME]']
    if len(sys.argv) != len(expected_args) + 1:
        print(f"Usage: python3 {sys.argv[0]} {' '.join(expected_args)}")
        sys.exit()
    list_instances = [
        List(sys.argv[1], trim_not_friends = True),
        List(sys.argv[2], trim_friends = True)
    ]
    trim_list_instance = List(sys.argv[3])
    updater = ListUpdater(list_instances, trim_list_instance)
    updater.update()
