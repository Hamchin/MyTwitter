import twitter

RED, END = '\033[31m', '\033[0m'

# 不要なツイートを全て削除する
def delete():
    count = input('\nTweet Count >> ')
    count = 2000 if count == '' else int(count)
    # メディアツイート以外のツイートおよびリツイートを取得する
    tweets = twitter.get_user_timeline(count = count, exclude_replies = False, include_rts = True)
    is_media = lambda tweet: 'extended_entities' in tweet
    is_retweet = lambda tweet: 'retweeted_status' in tweet
    tweets = [tweet for tweet in tweets if not is_media(tweet) or is_retweet(tweet)]
    if tweets == []: return
    print()
    # ツイートを表示する
    for tweet in tweets:
        print(tweet['created_at'])
        print(tweet['text'], end = '\n\n')
    input('Enter to Delete >> ')
    print()
    # ツイートを削除する
    for i, tweet in enumerate(tweets):
        tweet_id = tweet['id_str']
        delete_tweet = lambda: twitter.delete_tweet(tweet_id)
        delete_retweet = lambda: twitter.delete_retweet(tweet_id)
        res = delete_retweet() if is_retweet(tweet) else delete_tweet()
        message = f'({i+1} / {len(tweets)})\t{tweet_id}\t{res.status_code}'
        if res.status_code != 200: message = RED + message + END
        print(message)

if __name__ == '__main__':
    delete()
