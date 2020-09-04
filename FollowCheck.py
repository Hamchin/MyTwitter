import MyTwitter, json

# ユーザー間の関係をチェックする
def check_friendship(twitter, target, source):
    try:
        user = MyTwitter.get_user(twitter, target[0])
        relation = MyTwitter.check_friendship(twitter, user['id_str'], source)
        if relation is None: raise
        message = user['name'] + '\n'
        message += '@' + user['screen_name'] + '\n'
        # ブロックされている場合
        if relation['source']['blocked_by'] == True:
            message += "ブロックされました"
        # ブロブロ解除された場合
        elif relation['source']['following'] == False:
            message += "ブロブロ解除されました"
        # フォロー解除された場合
        elif relation['source']['followed_by'] == False:
            message += "フォロー解除されました"
        # 原因不明の場合
        else:
            message += "失踪しました"
    except:
        message = target[2] + '\n'
        message += '@' + target[1] + '\n'
        message += "失踪しました"
    finally:
        res = MyTwitter.direct_message(twitter, source, message)
        if res.status_code != 200: return False
    return True

# フォローチェック
def check():
    file = 'data/follower.json'
    twitter, user_id = MyTwitter.login()
    friends = json.load(open(file, 'r'))
    followers = MyTwitter.get_followers(twitter, user_id)
    if followers == []: return
    follower_ids = [user['id_str'] for user in followers]
    for target in friends:
        if target[0] not in follower_ids:
            status = check_friendship(twitter, target, user_id)
            if status == False: return
    followers = [[user['id_str'], user['screen_name'], user['name']] for user in followers]
    json.dump(followers, open(file, 'w'), indent = 4, ensure_ascii = False)

if __name__ == '__main__':
    check()
