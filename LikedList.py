import MyTwitter, sys, requests, json

# 通知取得
def get_notices(size = 10):
    params = {'size': size}
    res = requests.get("https://notice-database.herokuapp.com/api/notices", params = params)
    notices = json.loads(res.text)
    return notices

# リストネームからリストメンバー取得
def get_list_members(twitter, list_name):
    if list_name == '': return []
    list_id = MyTwitter.get_list_id(list_name)
    members = MyTwitter.get_list_members(twitter, list_id)
    return members

# リストへユーザー追加
def add_users(twitter, list_name, target_names, member_names, trim_names):
    list_id = MyTwitter.get_list_id(list_name)
    for target_name in target_names:
        if target_name in trim_names: continue
        if target_name in member_names: continue
        MyTwitter.add_user(twitter, list_id, screen_name = target_name)

# リストからユーザー削除
def delete_users(twitter, list_name, target_names, member_names, trim_names):
    list_id = MyTwitter.get_list_id(list_name)
    for member_name in member_names:
        if member_name not in target_names or member_name in trim_names:
            MyTwitter.delete_user(twitter, list_id, screen_name = member_name)

# いいねリスト更新
def execute(list_name, trim_list_name = ''):
    twitter, self_id = MyTwitter.login()
    self_user = MyTwitter.get_user(twitter, user_id = self_id)
    notices = get_notices(size = 100)
    notices = [notice for notice in notices if notice['receive_user'] == self_user['screen_name']]
    member_names = [user['screen_name'] for user in get_list_members(twitter, list_name)]
    trim_names = [user['screen_name'] for user in get_list_members(twitter, trim_list_name)]
    notice_senders = list(set([notice['send_user'] for notice in notices]))
    add_users(twitter, list_name, notice_senders, member_names, trim_names)
    delete_users(twitter, list_name, notice_senders, member_names, trim_names)

if __name__ == '__main__':
    if len(sys.argv) == 3:
        execute(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 2:
        execute(sys.argv[1])
    else:
        print("Usage: python3 {0} [list_name] (trim_list_name)".format(sys.argv[0]))
        sys.exit()
