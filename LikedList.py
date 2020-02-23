import MyTwitter, sys, requests, json

# 通知取得
def get_notices():
    res = requests.get("https://notice-database.herokuapp.com/notices")
    notices = json.loads(res.text)
    return notices

# 通知削除
def delete_notice(ID):
    url = "https://notice-database.herokuapp.com/notice"
    headers = {'content-type': 'application/json'}
    requests.delete(url, data = json.dumps({'id': ID}), headers = headers)

# 指定日数より過去の通知削除
def delete_timeover_notices(notices, day = 0):
    deleted_ids = []
    for notice in notices:
        if MyTwitter.is_timeover(notice['datetime'], day):
            delete_notice(notice['id'])
            deleted_ids.append(notice['id'])
    return deleted_ids

# リストネームからリストメンバー取得
def get_list_members(twitter, list_name):
    if list_name == '': return []
    list_id = MyTwitter.get_list_id(list_name)
    members = MyTwitter.get_list_members(twitter, list_id)
    return members

# 通知の送信ユーザー取得(カウント付き)
def get_notice_senders(notices):
    names = [notice['send_user'] for notice in notices]
    senders = {name: {'count': 0, 'time': 0} for name in list(set(names))}
    for notice in notices:
        name = notice['send_user']
        time = MyTwitter.get_date(notice['datetime']).timestamp()
        senders[name]['count'] += 1
        senders[name]['time'] = max(senders[name]['time'], int(time))
    senders = sorted(senders.items(), key = lambda sender: (-sender[1]['count'], -sender[1]['time']))
    return senders

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
    notices = get_notices()
    deleted_ids = delete_timeover_notices(notices, day = 7)
    notices = [notice for notice in notices if notice['id'] not in deleted_ids]
    notices = [notice for notice in notices if notice['receive_user'] == self_user['screen_name']]
    member_names = [user['screen_name'] for user in get_list_members(twitter, list_name)]
    trim_names = [user['screen_name'] for user in get_list_members(twitter, trim_list_name)]
    notice_senders = [sender[0] for sender in get_notice_senders(notices)]
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
