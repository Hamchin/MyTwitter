import MyTwitter, NoticeDB, sys, requests, json

# 通知取得
def get_notices(size = 10):
    url = NoticeDB.NOTICE_API['ENDPOINT'] + NoticeDB.NOTICE_API['GET_NOTICES_URI']
    params = {'size': size}
    res = requests.get(url, params = params)
    notices = json.loads(res.text)
    return notices

# リストネームからリストメンバー取得
def get_list_members(twitter, list_name):
    if list_name == '': return []
    list_id = MyTwitter.get_list_id(list_name)
    members = MyTwitter.get_list_members(twitter, list_id)
    return members

# リストへユーザー追加
def add_users(twitter, list_name, target_ids, member_ids, trim_ids):
    list_id = MyTwitter.get_list_id(list_name)
    for target_id in target_ids:
        if target_id in trim_ids: continue
        if target_id in member_ids: continue
        target = MyTwitter.get_user(twitter, user_id = target_id)
        if target is None: continue
        if not target['following']: continue
        MyTwitter.add_user(twitter, list_id, user_id = target_id)

# リストからユーザー削除
def delete_users(twitter, list_name, target_ids, member_ids, trim_ids):
    list_id = MyTwitter.get_list_id(list_name)
    for member_id in member_ids:
        if member_id not in target_ids or member_id in trim_ids:
            MyTwitter.delete_user(twitter, list_id, user_id = member_id)

# いいねリスト更新
def execute(list_name, trim_list_name = ''):
    twitter, self_id = MyTwitter.login()
    notices = get_notices(size = 100)
    notices = [notice for notice in notices if notice['receiver_id'] == self_id]
    member_ids = [user['id_str'] for user in get_list_members(twitter, list_name)]
    trim_ids = [user['id_str'] for user in get_list_members(twitter, trim_list_name)]
    sender_ids = list(set([notice['sender_id'] for notice in notices]))
    add_users(twitter, list_name, sender_ids, member_ids, trim_ids)
    delete_users(twitter, list_name, sender_ids, member_ids, trim_ids)

if __name__ == '__main__':
    if len(sys.argv) == 3:
        execute(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 2:
        execute(sys.argv[1])
    else:
        print("Usage: python3 {0} [LIST_NAME] (EXCLUDED_LIST_NAME)".format(sys.argv[0]))
        sys.exit()
