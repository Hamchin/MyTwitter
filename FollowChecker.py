
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

def execute(user_id):
    twitter = MyTwitter.login()
    connection = sqlite3.connect("twitter.db")
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS friend (id VARCHAR(255), type VARCHAR(255))")
    followList = []
    for data in cursor.execute("SELECT id FROM friend WHERE type = ?", (user_id,)):
        followList.append(data[0])
    followerList = MyTwitter.getFollowerID(twitter, user_id)
    for target in followList:
        if target not in followerList:
            checkFriendship(twitter, target, user_id)
    cursor.execute("DELETE FROM friend WHERE type = ?", (user_id,))
    followList = MyTwitter.getFollowingID(twitter, user_id)
    for data in followList:
        cursor.execute("INSERT INTO friend (id, type) VALUES (?, ?)", (data, user_id))
    connection.commit()
    connection.close()

if __name__ == '__main__':
    try:
        user_id = sys.argv[1]
    except:
        print("Usage: python3 {0} [user_id]".format(sys.argv[0]))
        sys.exit()
    execute(user_id)

