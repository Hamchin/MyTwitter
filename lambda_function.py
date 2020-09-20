from twitter import Twitter
import os, json

# Twitterオブジェクトを取得する
def get_twitter(data):
    consumer_key = os.environ['CONSUMER_KEY']
    consumer_secret = os.environ['CONSUMER_SECRET']
    access_token = data.get('access_token') or ''
    access_secret = data.get('access_secret') or ''
    twitter = Twitter(consumer_key, consumer_secret, access_token, access_secret)
    return twitter

# パラメータを抽出する
def get_params(data, keys):
    params = {key: value for key, value in data.items() if key in keys}
    return params

# レスポンスを生成する
def response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': json.dumps(body)
    }

def lambda_handler(event, context):
    path = event.get('path') or ''
    method = event.get('httpMethod') or ''
    body = event.get('body')
    body = json.loads(body) if body else {}
    twitter = get_twitter(body)
    # フォローしているユーザーをオブジェクトの一覧で取得する
    if path == '/friends/list' and method == 'POST':
        keys = ['user_id', 'screen_name']
        params = get_params(body, keys)
        users = twitter.get_friends(**params)
        return response(200, users)
    # フォローしているユーザーをIDの一覧で取得する
    elif path == '/friends/ids' and method == 'POST':
        keys = ['user_id', 'screen_name']
        params = get_params(body, keys)
        user_ids = twitter.get_friend_ids(**params)
        return response(200, user_ids)
    # フォロワーをオブジェクトの一覧で取得する
    elif path == '/followers/list' and method == 'POST':
        keys = ['user_id', 'screen_name']
        params = get_params(body, keys)
        users = twitter.get_followers(**params)
        return response(200, users)
    # フォロワーをIDの一覧で取得する
    elif path == '/followers/ids' and method == 'POST':
        keys = ['user_id', 'screen_name']
        params = get_params(body, keys)
        user_ids = twitter.get_follower_ids(**params)
        return response(200, user_ids)
    # ユーザーを取得する
    elif path == '/users/show' and method == 'POST':
        keys = ['user_id', 'screen_name']
        params = get_params(body, keys)
        user = twitter.get_user(**params)
        return response(200, user)
    # 複数のユーザーを取得する
    elif path == '/users/lookup' and method == 'POST':
        keys = ['user_ids', 'screen_names']
        params = get_params(body, keys)
        users = twitter.get_users(**params)
        return response(200, users)
    # 複数のツイートを取得する
    elif path == '/statuses/lookup' and method == 'POST':
        keys = ['tweet_ids', 'trim_user']
        params = get_params(body, keys)
        tweets = twitter.get_tweets(**params)
        return response(200, tweets)
    # ユーザータイムラインを取得する
    elif path == '/statuses/user_timeline' and method == 'POST':
        keys = ['user_id', 'screen_name', 'count', 'exclude_replies', 'include_rts', 'trim_user']
        params = get_params(body, keys)
        tweets = twitter.get_user_timeline(**params)
        return response(200, tweets)
    # ホームタイムラインを取得する
    elif path == '/statuses/home_timeline' and method == 'POST':
        keys = ['count', 'exclude_replies', 'include_rts', 'trim_user']
        params = get_params(body, keys)
        tweets = twitter.get_home_timeline(**params)
        return response(200, tweets)
    # リストの一覧を取得する
    elif path == '/lists/list' and method == 'POST':
        keys = ['user_id', 'screen_name']
        params = get_params(body, keys)
        lists = twitter.get_lists(**params)
        return response(200, lists)
    # リストのタイムラインを取得する
    elif path == '/lists/statuses' and method == 'POST':
        keys = ['list_id', 'slug', 'owner_id', 'owner_screen_name', 'count', 'exclude_replies', 'include_rts', 'trim_user']
        params = get_params(body, keys)
        tweets = twitter.get_list_timeline(**params)
        return response(200, tweets)
    # リストのメンバーを取得する
    elif path == '/lists/members' and method == 'POST':
        keys = ['list_id', 'slug', 'owner_id', 'owner_screen_name']
        params = get_params(body, keys)
        users = twitter.get_list_members(**params)
        return response(200, users)
    # リストにメンバーを追加する
    elif path == '/lists/members/create' and method == 'POST':
        keys = ['list_id', 'slug', 'owner_id', 'owner_screen_name', 'user_id', 'screen_name']
        params = get_params(body, keys)
        res = twitter.add_user(**params)
        return response(res.status_code, res.json())
    # リストからメンバーを削除する
    elif path == '/lists/members/destroy' and method == 'POST':
        keys = ['list_id', 'slug', 'owner_id', 'owner_screen_name', 'user_id', 'screen_name']
        params = get_params(body, keys)
        res = twitter.delete_user(**params)
        return response(res.status_code, res.json())
    # 2人のユーザーの関係を取得する
    elif path == '/friendships/show' and method == 'POST':
        keys = ['source_id', 'target_id', 'source_screen_name', 'target_screen_name']
        params = get_params(body, keys)
        relation = twitter.get_friendship(**params)
        return response(200, relation)
    # 自分と対象ユーザーの関係を調べる
    elif path == '/friendships/lookup' and method == 'POST':
        keys = ['user_ids', 'screen_names']
        params = get_params(body, keys)
        relations = twitter.get_friendships(**params)
        return response(200, relations)
    # ツイートを投稿する
    elif path == '/statuses/update' and method == 'POST':
        keys = ['text', 'media']
        params = get_params(body, keys)
        res = twitter.tweet(**params)
        return response(res.status_code, res.json())
    # ツイートを削除する
    elif path == '/statuses/destroy' and method == 'POST':
        keys = ['tweet_id']
        params = get_params(body, keys)
        res = twitter.delete_tweet(**params)
        return response(res.status_code, res.json())
    # リツイートを実行する
    elif path == '/statuses/retweet' and method == 'POST':
        keys = ['tweet_id']
        params = get_params(body, keys)
        res = twitter.retweet(**params)
        return response(res.status_code, res.json())
    # リツイートを取り消す
    elif path == '/statuses/unretweet' and method == 'POST':
        keys = ['tweet_id']
        params = get_params(body, keys)
        res = twitter.delete_retweet(**params)
        return response(res.status_code, res.json())
    # いいねを付ける
    elif path == '/favorites/create' and method == 'POST':
        keys = ['tweet_id']
        params = get_params(body, keys)
        res = twitter.like(**params)
        return response(res.status_code, res.json())
    # いいねを取り消す
    elif path == '/favorites/destroy' and method == 'POST':
        keys = ['tweet_id']
        params = get_params(body, keys)
        res = twitter.delete_like(**params)
        return response(res.status_code, res.json())
    # ダイレクトメッセージを送信する
    elif path == '/direct_messages/new' and method == 'POST':
        keys = ['target_id', 'text']
        params = get_params(body, keys)
        res = twitter.direct_message(**params)
        return response(res.status_code, res.json())
    return response(400, None)
