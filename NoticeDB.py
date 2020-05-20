import sqlite3, requests, json

DATABASE_PATH = 'data/notices.db'
NOTICE_API = json.load(open('data/notice_api.json', 'r'))

# データベース操作用デコレーター
def database(func):
    def wrapper(*args, **kwargs):
        # データベース接続
        connection = sqlite3.connect(DATABASE_PATH)
        connection.row_factory = sqlite3.Row
        # カーソル作成
        cursor = connection.cursor()
        # テーブル作成
        cursor.execute("CREATE TABLE IF NOT EXISTS notices (id INTEGER PRIMARY KEY, receiver_id TEXT, sender_id TEXT, tweet_id TEXT, timestamp INTEGER)")
        # 処理の実行
        kwargs['cursor'] = cursor
        res = func(*args, **kwargs)
        # データベースの保存
        connection.commit()
        # データベースの接続を閉じる
        connection.close()
        return res
    return wrapper

# リモートから全通知を取得する
def get_remote_notices():
    url = NOTICE_API['ENDPOINT'] + NOTICE_API['GET_NOTICES_URI']
    params = {'size': 10000}
    res = requests.get(url, params = params)
    notices = json.loads(res.text)
    notices = sorted(notices, key = lambda notice: notice['id'])
    return notices

# ローカルから全通知を取得する
@database
def get_local_notices(cursor = None):
    cursor.execute('SELECT * FROM notices')
    notices = [dict(notice) for notice in cursor.fetchall()]
    return notices

# データベースに複数の通知を挿入する
@database
def insert_notices(notices, cursor = None):
    inserted_notices = []
    for notice in notices:
        try:
            cursor.execute("INSERT INTO notices VALUES (:id, :receiver_id, :sender_id, :tweet_id, :timestamp)", notice)
            inserted_notices.append(notice)
        except sqlite3.IntegrityError as e:
            print(f"IntegrityError: {e.args[0]} = {notice['id']}")
    return inserted_notices

# リモート上から複数の通知を削除する
def delete_remote_notices(notices):
    url = NOTICE_API['ENDPOINT'] + NOTICE_API['DELETE_NOTICE_URI']
    headers = {'content-type': 'application/json'}
    deleted_notices = []
    for notice in notices:
        data = {'id': notice['id'], 'password': NOTICE_API['PASSWORD']}
        res = requests.delete(url, headers = headers, data = json.dumps(data))
        res = json.loads(res.text)
        if res['status'] != 'SUCCESS':
            print(f"DeleteError: notice.id = {notice['id']}")
        else:
            deleted_notices.append(res['notice'])
    return deleted_notices

if __name__ == '__main__':
    in_str = input('\n' + "? Number of notices to transfer from remote to local: ")
    assert(in_str.isdecimal())
    size = int(in_str)
    notices = get_remote_notices()
    notices = notices[:size]
    inserted_notices = insert_notices(notices)
    print('\n' + f"Number of insert notices: {len(inserted_notices)}")
    input('\n' + "Press return to delete notices from remote: ")
    deleted_notices = delete_remote_notices(inserted_notices)
    print('\n' + f"Number of deleted notices: {len(deleted_notices)}" + '\n')
