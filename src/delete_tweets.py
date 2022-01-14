# ハイライトカラー
RED = '\033[31m'
END = '\033[0m'

# パラメータ
MEDIA_KEY = 'extended_entities'
REPLY_KEY = 'in_reply_to_user_id'
RETWEET_KEY = 'retweeted_status'

# テキストツイートかどうか判定する
def is_text_tweet(tweet):
    if tweet.get(MEDIA_KEY): return False
    if tweet.get(REPLY_KEY): return False
    if tweet.get(RETWEET_KEY): return False
    return True

# リプライかどうか判定する
def is_reply(tweet):
    if tweet.get(RETWEET_KEY): return False
    if tweet.get(REPLY_KEY): return True
    return False

# リツイートかどうか判定する
def is_retweet(tweet):
    if tweet.get(RETWEET_KEY): return True
    return False

# 削除処理を実行する
def take_delete_process(twitter, tweets, function = None, message = ''):
    # ツイートをフィルタリングする
    tweets = list(filter(function, tweets))
    if tweets == []: return
    print('\n' + '=' * 50)
    print(message)
    print('=' * 50 + '\n')
    # ツイートを表示する
    for tweet in tweets:
        print(tweet['created_at'])
        print(tweet['full_text'], end = '\n\n')
    res = input('Do you want to continue [Y/n]? ')
    if not (res == '' or res.upper() == 'Y'): return
    print()
    # ツイートを削除する
    for i, tweet in enumerate(tweets):
        tweet_id = tweet['id_str']
        if is_retweet(tweet): res = twitter.delete_retweet(tweet_id)
        else: res = twitter.delete_tweet(tweet_id)
        message = f"({i+1} / {len(tweets)})\t{tweet_id}\t{res.status_code}"
        if res.status_code != 200: message = RED + message + END
        print(message)

# メイン関数
def main(twitter):
    count = input('\n' + 'Tweet Count >> ')
    count = 200 if count == '' else int(count)
    params = {'exclude_replies': False, 'exclude_retweets': False, 'trim_user': True, 'count': count}
    tweets = twitter.get_user_timeline(**params)
    take_delete_process(twitter, tweets, function = is_text_tweet, message = 'Text Tweets')
    take_delete_process(twitter, tweets, function = is_reply, message = 'Reply Tweets')
    take_delete_process(twitter, tweets, function = is_retweet, message = 'Retweets')
