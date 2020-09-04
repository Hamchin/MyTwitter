import MyTwitter

RED, END = '\033[31m', '\033[0m'

# 不要なツイートを全て削除する
def delete():
    twitter, user_id = MyTwitter.login()
    count = input("\nTweet Count >> ")
    count = 2000 if count == '' else int(count)
    # メディアツイート以外のツイートを取得する
    tweets = MyTwitter.get_user_timeline(twitter, user_id, count, exclude_replies = False, include_rts = True)
    tweets = [tweet for tweet in tweets if 'extended_entities' not in tweet]
    if tweets == []: return
    print()
    # ツイートを表示する
    for tweet in tweets:
        print(tweet['created_at'])
        print(tweet['text'], end = '\n\n')
    input("Enter to Delete >> ")
    print()
    # ツイートを削除する
    for i, tweet in enumerate(tweets):
        res = MyTwitter.delete_tweet(twitter, tweet['id_str'])
        message = f"({i+1} / {len(tweets)})\t{tweet['id_str']}\t{res.status_code}"
        if res.status_code != 200: message = RED + message + END
        print(message)

if __name__ == '__main__':
    delete()
