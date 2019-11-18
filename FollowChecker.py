import MyTwitter, sys, json

# リレーションシップチェック
def check_friendship(twitter, target, source):
    try:
        target = MyTwitter.get_user_list(twitter, [target[0]])[0]
        relation = MyTwitter.check_friendship(twitter, target["id_str"], source)
        message = target["name"] + "\n"
        message += "@" + target["screen_name"] + "\n"
        # ブロックされている場合
        if relation["source"]["blocked_by"] == True:
            message += "ブロックされました"
            MyTwitter.direct_message(twitter, source, message)
        # ブロブロ解除された場合
        elif relation["source"]["following"] == False:
            message += "ブロブロ解除された可能性あり"
            MyTwitter.direct_message(twitter, source, message)
        # フォロー解除された場合
        elif relation["source"]["followed_by"] == False:
            message += "フォロー解除されました"
            MyTwitter.direct_message(twitter, source, message)
        # 原因不明の場合
        else:
            message += "失踪しました"
            MyTwitter.direct_message(twitter, source, message)
    except:
        message = target[2] + "\n"
        message += "@" + target[1] + "\n"
        message += "失踪しました"
        MyTwitter.direct_message(twitter, source, message)

def execute():
    twitter, user_id = MyTwitter.login()
    with open('data/follower.json', 'r') as f:
        friend_list = json.load(f)
    follower_list = MyTwitter.get_follower(twitter, user_id)
    if follower_list == []:
        print("Load Failed.")
        sys.exit()
    follower_ids = [user["id_str"] for user in follower_list]
    for target in friend_list:
        if target[0] not in follower_ids:
            check_friendship(twitter, target, user_id)
    follower_list = [[user["id_str"], user["screen_name"], user["name"]] for user in follower_list]
    with open('data/follower.json', 'w') as f:
        json.dump(follower_list, f, indent = 4)

if __name__ == '__main__':
    execute()
