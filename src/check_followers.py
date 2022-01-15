import json
import os

DATA_PATH = 'data/followers/{{USER_ID}}.json'

# ユーザーとの関係をチェックする
def check_friendship(twitter, target):
    target_id, target_screen_name, target_name = target
    try:
        relation = twitter.get_friendship(target_id = target_id)
        target_user = twitter.get_user(target_id)
        message = target_user['name'] + '\n'
        message += '@' + target_user['screen_name'] + '\n'
        # ブロックされている場合
        if relation['source']['blocked_by'] == True:
            message += 'ブロックされました'
        # ブロブロ解除された場合
        elif relation['source']['following'] == False:
            message += 'ブロブロ解除されました'
        # フォロー解除された場合
        elif relation['source']['followed_by'] == False:
            message += 'フォロー解除されました'
        # 原因不明の場合
        else:
            message += '失踪しました'
    except:
        message = target_name + '\n'
        message += '@' + target_screen_name + '\n'
        message += '失踪しました'
    finally:
        res = twitter.direct_message(twitter.user_id, message)
        if res.status_code != 200: return False
    return True

# メイン関数
def main(twitter):
    data_path = DATA_PATH.replace('{{USER_ID}}', twitter.user_id)
    friends = json.load(open(data_path)) if os.path.exists(data_path) else []
    followers = twitter.get_followers()
    if followers == []: return
    follower_ids = [user['id_str'] for user in followers]
    for target in friends:
        if target[0] in follower_ids: continue
        status = check_friendship(twitter, target)
        if status == False: return
    followers = [[user['id_str'], user['screen_name'], user['name']] for user in followers]
    json.dump(followers, open(data_path, 'w'), indent = 4, ensure_ascii = False)
