import datetime
import requests

FOLLOWING = 'Following'
FOLLOWERS = 'Followers'
MUTUAL_FOLLOW = 'Follow / Followed'
ONLY_FOLLOW = 'Follow / Not Followed'
ONLY_FOLLOWED = 'Not Follow / Followed'

# 文字列を整数へ変換する
def get_number(string):
    assert(string.isdecimal())
    return int(string)

# 対象ユーザーの種類を取得する
def get_target_type():
    target_types = [FOLLOWING, FOLLOWERS, MUTUAL_FOLLOW, ONLY_FOLLOW, ONLY_FOLLOWED]
    print()
    for i, target_type in enumerate(target_types):
        print(f"{i+1}: {target_type}")
    string = input('\n' + '? Target Users (Number): ')
    index = get_number(string)
    assert(1 <= index <= len(target_types))
    return target_types[index - 1]

# 対象ユーザーを取得する
def get_targets(twitter, target_type):
    targets = []
    # フォロー
    if target_type == FOLLOWING:
        targets = twitter.get_friends()
    # フォロワー
    elif target_type == FOLLOWERS:
        targets = twitter.get_followers()
    # 相互フォロー
    elif target_type == MUTUAL_FOLLOW:
        friends = twitter.get_friends()
        follower_ids = twitter.get_follower_ids()
        targets = [user for user in friends if user['id_str'] in follower_ids]
    # 片思い
    elif target_type == ONLY_FOLLOW:
        friends = twitter.get_friends()
        follower_ids = twitter.get_follower_ids()
        targets = [user for user in friends if user['id_str'] not in follower_ids]
    # 片思われ
    elif target_type == ONLY_FOLLOWED:
        followers = twitter.get_followers()
        friend_ids = twitter.get_friend_ids()
        targets = [user for user in followers if user['id_str'] not in friend_ids]
    return targets

# 通知を取得する
def get_notices(twitter, notice_api_url):
    size = input('\n' + '? Number of Notices (Number): ')
    size = 1000 if size == '' else get_number(size)
    params = {'receiver_id': twitter.user_id, 'size': size}
    notices = requests.get(notice_api_url + '/notices', params = params).json()
    return notices

# タイムスタンプから日付文字列を取得する
def get_date_string(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')

# メイン関数
def main(twitter, notice_api_url, notices = []):
    notices = get_notices(twitter, notice_api_url) if notices == [] else notices
    target_type = get_target_type()
    targets = get_targets(twitter, target_type)
    target_dict = {target['id_str']: target for target in targets}
    notice_dict = {target['id_str']: {'timestamp': 0, 'count': 0} for target in targets}
    for notice in notices:
        sender_id = notice['sender_id']
        if target_dict.get(sender_id):
            timestamp = max(notice_dict[sender_id]['timestamp'], notice['timestamp'])
            notice_dict[sender_id]['timestamp'] = timestamp
            notice_dict[sender_id]['count'] += 1
    notice_list = sorted(notice_dict.items(), key = lambda item: -item[1]['timestamp'])
    print('\n', '=' * 60, '\n', sep = '')
    for user_id, notice in notice_list:
        user = target_dict[user_id]
        date = get_date_string(notice['timestamp']) if notice['timestamp'] else None
        print(f"Name: {user['name']}")
        print(f"Last Date: {date}")
        print(f"Like Count: {notice['count']}")
        print(f"https://twitter.com/{user['screen_name']}\n")
    print('=' * 60)
    main(twitter, notice_api_url, notices)
