
# coding: utf-8

import MyTwitter
import sqlite3
import sys

#リレーションシップチェック
def checkFriendship(twitter, target, source):
    try:
        target = MyTwitter.getUserList(twitter, [target])[0]
        relation = MyTwitter.checkFriendship(twitter, target["id_str"], source)
        message = target["name"] + "\n"
        message += "@" + target["screen_name"] + "\n"
        #ブロックされている場合
        if relation["source"]["blocked_by"] == True:
            message += "ブロックされたゾ"
            MyTwitter.directMessage(twitter, source, message)
        #ブロブロ解除された場合
        elif relation["source"]["following"] == False:
            message += "ブロブロ解除されたゾ"
            MyTwitter.directMessage(twitter, source, message)
        #フォロー解除された場合
        elif relation["source"]["followed_by"] == False:
            message += "フォロー解除されたゾ"
            MyTwitter.directMessage(twitter, source, message)
        #原因不明の場合
        else:
            message += "失踪したゾ"
            MyTwitter.directMessage(twitter, source, message)
    except:
        message = target + "\n" + "失踪したゾ"
        MyTwitter.directMessage(twitter, source, message)

def execute(name):
    twitter, user_id = MyTwitter.login(name)
    connection = sqlite3.connect("twitter.db")
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS friend (type, id)")
    friendList = [data[0] for data in cursor.execute("SELECT id FROM friend WHERE type = ?", (name,))]
    followerList = MyTwitter.getFollowerID(twitter, user_id)
    for target in friendList:
        if target not in followerList:
            checkFriendship(twitter, target, user_id)
    cursor.execute("DELETE FROM friend WHERE type = ?", (name,))
    friendList = MyTwitter.getFollowerID(twitter, user_id)
    for user_id in friendList:
        cursor.execute("INSERT INTO friend (type, id) VALUES (?, ?)", (name, user_id))
    connection.commit()
    connection.close()

if __name__ == '__main__':
    if len(sys.argv) != 1:
        nameList = sys.argv[1:]
    else:
        print("Usage: python3 {0} [user_type]".format(sys.argv[0]))
        sys.exit()
    for name in nameList:
        execute(name)
