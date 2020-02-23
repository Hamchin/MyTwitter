import MyTwitter, sys, json

# リレーションシップチェック
def check_friendship(twitter, target, source):
    try:
        user = MyTwitter.get_user(twitter, target[0])
        relation = MyTwitter.check_friendship(twitter, user["id_str"], source)
        message = user["name"] + "\n"
        message += "@" + user["screen_name"] + "\n"
        # ブロックされている場合
        if relation["source"]["blocked_by"] == True:
            message += "ブロックされました"
        # ブロブロ解除された場合
        elif relation["source"]["following"] == False:
            message += "ブロブロ解除された可能性あり"
        # フォロー解除された場合
        elif relation["source"]["followed_by"] == False:
            message += "フォロー解除されました"
        # 原因不明の場合
        else:
            message += "失踪しました"
    except:
        message = target[2] + "\n"
        message += "@" + target[1] + "\n"
        message += "失踪しました"
    finally:
        res = MyTwitter.direct_message(twitter, source, message)
        if res.status_code != 200: sys.exit()

def execute():
    twitter, user_id = MyTwitter.login()
    with open('data/follower.json', 'r') as f:
        friends = json.load(f)
    followers = MyTwitter.get_followers(twitter, user_id)
    if followers == []:
        sys.exit()
    follower_ids = [user["id_str"] for user in followers]
    for target in friends:
        if target[0] not in follower_ids:
            check_friendship(twitter, target, user_id)
    followers = [[user["id_str"], user["screen_name"], user["name"]] for user in followers]
    with open('data/follower.json', 'w') as f:
        json.dump(followers, f, indent = 4)

if __name__ == '__main__':
    execute()
