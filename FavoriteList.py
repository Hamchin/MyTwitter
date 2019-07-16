import MyTwitter, sys

def execute(user_name, list_name):
    twitter, user_id = MyTwitter.login(user_name)
    id_list = [tweet["id_str"] for tweet in MyTwitter.get_tweet_list(twitter, user_id, 200)]
    user_list = []
    friend_list = MyTwitter.get_following_id(twitter, user_id)
    for tweet_id in id_list[:10]:
        user_list.extend(MyTwitter.get_fav_user_id_list(tweet_id, [user_id]))
    user_list = [user for user in list(set(user_list)) if user in friend_list]
    list_id = MyTwitter.get_list_id(list_name)
    member_list = [user["id_str"] for user in MyTwitter.get_list_member(twitter, list_id)]
    for user_id in [user_id for user_id in member_list if user_id not in user_list]:
        MyTwitter.delete_user(twitter, list_id, user_id)
    for user_id in [user_id for user_id in user_list if user_id not in member_list]:
        MyTwitter.add_user(twitter, list_id, user_id)

if __name__ == '__main__':
    try:
        execute(sys.argv[1], sys.argv[2])
    except:
        print("Usage: python3 {0} [user_type] [list_name]".format(sys.argv[0]))
        sys.exit()