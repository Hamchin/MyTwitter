import MyTwitter
import sys

def execute(user_name, list_name):
    twitter, user_id = MyTwitter.login(user_name)
    idList = [tweet["id_str"] for tweet in MyTwitter.getTweetList(twitter, user_id, 200)]
    userList = []
    for tweet_id in idList[:10]:
        userList.extend(MyTwitter.getFavUserIDList(tweet_id, [user_id]))
    userList = list(set(userList))
    list_id = MyTwitter.getID(list_name)
    memberList = [user["id_str"] for user in MyTwitter.getListMember(twitter, list_id)]
    for user_id in [user_id for user_id in memberList if user_id not in userList]:
        MyTwitter.deleteUser(twitter, list_id, user_id)
    for user_id in [user_id for user_id in userList if user_id not in memberList]:
        MyTwitter.addUser(twitter, list_id, user_id)

if __name__ == '__main__':
    try:
        execute(sys.argv[1], sys.argv[2])
    except:
        print("Usage: python3 {0} [name] [list_name]".format(sys.argv[0]))
        sys.exit()

