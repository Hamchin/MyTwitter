import MyTwitter, sys, json

#リレーションシップチェック
def check_friendship(twitter, target, source):
    try:
        target = MyTwitter.get_user_list(twitter, [target])[0]
        relation = MyTwitter.check_friendship(twitter, target["id_str"], source)
        message = target["name"] + "\n"
        message += "@" + target["screen_name"] + "\n"
        #ブロックされている場合
        if relation["source"]["blocked_by"] == True:
            message += "ブロックされたゾ"
            MyTwitter.direct_message(twitter, source, message)
        #ブロブロ解除された場合
        elif relation["source"]["following"] == False:
            message += "ブロブロ解除されたゾ"
            MyTwitter.direct_message(twitter, source, message)
        #フォロー解除された場合
        elif relation["source"]["followed_by"] == False:
            message += "フォロー解除されたゾ"
            MyTwitter.direct_message(twitter, source, message)
        #原因不明の場合
        else:
            message += "失踪したゾ"
            MyTwitter.direct_message(twitter, source, message)
    except:
        message = target + "\n" + "失踪したゾ"
        MyTwitter.direct_message(twitter, source, message)

def execute(name):
    twitter, user_id = MyTwitter.login(name)
    with open('data/follower.json', 'r') as f:
        friend_list = json.load(f)
    follower_list = MyTwitter.get_follower_id(twitter, user_id)
    for target in friend_list[name]:
        if target not in follower_list:
            check_friendship(twitter, target, user_id)
    friend_list[name] = MyTwitter.get_follower_id(twitter, user_id)
    with open('data/follower.json', 'w') as f:
        json.dump(friend_list, f, indent = 4)

if __name__ == '__main__':
    if len(sys.argv) != 1:
        name_list = sys.argv[1:]
    else:
        print("Usage: python3 {0} [user_type]".format(sys.argv[0]))
        sys.exit()
    for name in name_list:
        execute(name)