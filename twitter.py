from requests_oauthlib import OAuth1Session
import json

class Twitter:
    user_id = ''
    session = None

    def __init__(self, consumer_key = '', consumer_secret = '', access_token = '', access_secret = ''):
        self.user_id = access_token.split('-')[0]
        self.session = OAuth1Session(consumer_key, consumer_secret, access_token, access_secret)

    # フォローしているユーザーをオブジェクトの一覧で取得する
    def get_friends(self, user_id = None, screen_name = None):
        url = 'https://api.twitter.com/1.1/friends/list.json'
        params = {
            'user_id': user_id,
            'screen_name': screen_name,
            'skip_status': True,
            'include_user_entities': False,
            'count': 200
        }
        users = []
        while True:
            res = self.session.get(url, params = params)
            if res.status_code != 200: break
            data = res.json()
            users += data['users']
            params['cursor'] = data['next_cursor_str']
            if params['cursor'] == '0': break
        return users

    # フォロワーをオブジェクトの一覧で取得する
    def get_followers(self, user_id = None, screen_name = None):
        url = 'https://api.twitter.com/1.1/followers/list.json'
        params = {
            'user_id': user_id,
            'screen_name': screen_name,
            'skip_status': True,
            'include_user_entities': False,
            'count': 200
        }
        users = []
        while True:
            res = self.session.get(url, params = params)
            if res.status_code != 200: break
            data = res.json()
            users += data['users']
            params['cursor'] = data['next_cursor_str']
            if params['cursor'] == '0': break
        return users

    # フォローしているユーザーをIDの一覧で取得する
    def get_friend_ids(self, user_id = None, screen_name = None):
        url = 'https://api.twitter.com/1.1/friends/ids.json'
        params = {
            'user_id': user_id,
            'screen_name': screen_name,
            'stringify_ids': True,
            'count': 5000
        }
        res = self.session.get(url, params = params)
        if res.status_code != 200: return []
        user_ids = res.json()['ids']
        return user_ids

    # フォロワーをIDの一覧で取得する
    def get_follower_ids(self, user_id = None, screen_name = None):
        url = 'https://api.twitter.com/1.1/followers/ids.json'
        params = {
            'user_id': user_id,
            'screen_name': screen_name,
            'stringify_ids': True,
            'count': 5000
        }
        res = self.session.get(url, params = params)
        if res.status_code != 200: return []
        user_ids = res.json()['ids']
        return user_ids

    # リストのメンバーを取得する
    def get_list_members(self, list_id = None, slug = None, owner_id = None, owner_screen_name = None):
        url = 'https://api.twitter.com/1.1/lists/members.json'
        params = {
            'list_id': list_id,
            'slug': slug,
            'owner_id': owner_id,
            'owner_screen_name': owner_screen_name,
            'skip_status': True,
            'include_user_entities': False,
            'count': 5000
        }
        res = self.session.get(url, params = params)
        if res.status_code != 200: return []
        users = res.json()['users']
        return users

    # ユーザーを取得する
    def get_user(self, user_id = None, screen_name = None):
        url = 'https://api.twitter.com/1.1/users/show.json'
        params = {
            'user_id': user_id,
            'screen_name': screen_name,
            'skip_status': True,
            'include_user_entities': False
        }
        res = self.session.get(url, params = params)
        if res.status_code != 200: return None
        user = res.json()
        return user

    # 複数のユーザーを取得する
    def get_users(self, user_ids = [], screen_names = []):
        url = 'https://api.twitter.com/1.1/users/lookup.json'
        if user_ids != []:
            user_key = 'user_id'
            user_values = user_ids
        else:
            user_key = 'screen_name'
            user_values = screen_names
        users = []
        while True:
            if user_values == []: break
            target_values, user_values = user_values[:100], user_values[100:]
            params = {
                user_key: ','.join(target_values),
                'skip_status': True,
                'include_user_entities': False
            }
            res = self.session.get(url, params = params)
            if res.status_code != 200: break
            users += res.json()
        return users

    # 複数のツイートを取得する
    def get_tweets(self, tweet_ids = [], trim_user = True):
        url = 'https://api.twitter.com/1.1/statuses/lookup.json'
        tweets = []
        while True:
            if tweet_ids == []: break
            target_ids, tweet_ids = tweet_ids[:100], tweet_ids[100:]
            params = {
                'id': ','.join(target_ids),
                'trim_user': trim_user,
                'include_entities': False
            }
            res = self.session.get(url, params = params)
            if res.status_code != 200: break
            tweets += res.json()
        return tweets

    # ユーザータイムラインを取得する
    def get_user_timeline(self, user_id = None, screen_name = None, count = 200, exclude_replies = True, include_rts = False, trim_user = True):
        url = 'https://api.twitter.com/1.1/statuses/user_timeline.json'
        params = {
            'user_id': user_id,
            'screen_name': screen_name,
            'exclude_replies': exclude_replies,
            'include_rts': include_rts,
            'trim_user': trim_user,
            'include_entities': False,
            'count': 200
        }
        tweets = []
        for i in range(count // 200):
            res = self.session.get(url, params = params)
            if res.status_code != 200: break
            tweets += res.json()
            params['max_id'] = tweets[-1]['id_str']
        return tweets

    # ホームタイムラインを取得する
    def get_home_timeline(self, count = 200, exclude_replies = True, include_rts = False, trim_user = True):
        url = 'https://api.twitter.com/1.1/statuses/home_timeline.json'
        params = {
            'exclude_replies': exclude_replies,
            'include_rts': include_rts,
            'trim_user': trim_user,
            'include_entities': False,
            'count': 200
        }
        tweets = []
        for i in range(count // 200):
            res = self.session.get(url, params = params)
            if res.status_code != 200: break
            tweets += res.json()
            params['max_id'] = tweets[-1]['id_str']
        return tweets

    # リストの一覧を取得する
    def get_lists(self, user_id = None, screen_name = None):
        url = 'https://api.twitter.com/1.1/lists/list.json'
        params = {
            'user_id': user_id,
            'screen_name': screen_name
        }
        res = self.session.get(url, params = params)
        if res.status_code != 200: return []
        lists = res.json()
        return lists

    # リストのタイムラインを取得する
    def get_list_timeline(self, list_id = None, slug = None, owner_id = None, owner_screen_name = None, count = 200, exclude_replies = True, include_rts = False, trim_user = True):
        url = 'https://api.twitter.com/1.1/lists/statuses.json'
        params = {
            'list_id': list_id,
            'slug': slug,
            'owner_id': owner_id,
            'owner_screen_name': owner_screen_name,
            'exclude_replies': exclude_replies,
            'include_rts': include_rts,
            'trim_user': trim_user,
            'include_entities': False,
            'count': 200
        }
        tweets = []
        for i in range(count // 200):
            res = self.session.get(url, params = params)
            if res.status_code != 200: break
            tweets += res.json()
            params['max_id'] = tweets[-1]['id_str']
        return tweets

    # 自分と対象ユーザーの関係を調べる
    def get_friendships(self, user_ids = [], screen_names = []):
        url = 'https://api.twitter.com/1.1/friendships/lookup.json'
        if user_ids != []:
            user_key = 'user_id'
            user_values = user_ids
        else:
            user_key = 'screen_name'
            user_values = screen_names
        relations = []
        while True:
            if user_values == []: break
            target_values, user_values = user_values[:100], user_values[100:]
            params = {user_key: ','.join(target_values)}
            res = self.session.get(url, params = params)
            if res.status_code != 200: break
            relations += res.json()
        return relations

    # 2人のユーザーの関係を取得する
    def get_friendship(self, source_id = None, target_id = None, source_screen_name = None, target_screen_name = None):
        url = 'https://api.twitter.com/1.1/friendships/show.json'
        params = {
            'source_id': source_id,
            'target_id': target_id,
            'source_screen_name': source_screen_name,
            'target_screen_name': target_screen_name
        }
        res = self.session.get(url, params = params)
        if res.status_code != 200: return None
        relation = res.json()['relationship']
        return relation

    # ダイレクトメッセージを送信する
    def direct_message(self, target_id, text):
        url = 'https://api.twitter.com/1.1/direct_messages/events/new.json'
        data = {
            'event': {
                'type': 'message_create',
                'message_create': {
                    'target': {'recipient_id': target_id},
                    'message_data': {'text': text}
                }
            }
        }
        res = self.session.post(url, data = json.dumps(data))
        return res

    # いいねを付ける
    def like(self, tweet_id):
        url = 'https://api.twitter.com/1.1/favorites/create.json'
        params = {
            'id': tweet_id,
            'trim_user': True,
            'include_entities': False
        }
        res = self.session.post(url, params = params)
        return res

    # いいねを取り消す
    def delete_like(self, tweet_id):
        url = 'https://api.twitter.com/1.1/favorites/destroy.json'
        params = {
            'id': tweet_id,
            'trim_user': True,
            'include_entities': False
        }
        res = self.session.post(url, params = params)
        return res

    # リツイートを実行する
    def retweet(self, tweet_id):
        url = f'https://api.twitter.com/1.1/statuses/retweet/{tweet_id}.json'
        params = {
            'trim_user': True,
            'include_entities': False
        }
        res = self.session.post(url, params = params)
        return res

    # リツイートを取り消す
    def delete_retweet(self, tweet_id):
        url = f'https://api.twitter.com/1.1/statuses/unretweet/{tweet_id}.json'
        params = {
            'trim_user': True,
            'include_entities': False
        }
        res = self.session.post(url, params = params)
        return res

    # ツイートを投稿する
    def tweet(self, text = '', media = None):
        url_text = 'https://api.twitter.com/1.1/statuses/update.json'
        url_media = 'https://upload.twitter.com/1.1/media/upload.json'
        if media:
            files = {'media': media}
            res = self.session.post(url_media, files = files)
            media_id = res.json()['media_id']
            params = {'status': text, 'media_ids': [media_id]}
            res = self.session.post(url_text, params = params)
        else:
            params = {
                'status': text,
                'trim_user': True,
                'include_entities': False
            }
            res = self.session.post(url_text, params = params)
        return res

    # ツイートを削除する
    def delete_tweet(self, tweet_id):
        url = f'https://api.twitter.com/1.1/statuses/destroy/{tweet_id}.json'
        params = {
            'id': tweet_id,
            'trim_user': True,
            'include_entities': False
        }
        res = self.session.post(url, params = params)
        return res

    # リストにメンバーを追加する
    def add_user(self, list_id = None, slug = None, owner_id = None, owner_screen_name = None, user_id = None, screen_name = None):
        url = 'https://api.twitter.com/1.1/lists/members/create.json'
        params = {
            'list_id': list_id,
            'slug': slug,
            'owner_id': owner_id,
            'owner_screen_name': owner_screen_name,
            'user_id': user_id,
            'screen_name': screen_name
        }
        res = self.session.post(url, params = params)
        return res

    # リストからメンバーを削除する
    def delete_user(self, list_id = None, slug = None, owner_id = None, owner_screen_name = None, user_id = None, screen_name = None):
        url = 'https://api.twitter.com/1.1/lists/members/destroy.json'
        params = {
            'list_id': list_id,
            'slug': slug,
            'owner_id': owner_id,
            'owner_screen_name': owner_screen_name,
            'user_id': user_id,
            'screen_name': screen_name
        }
        res = self.session.post(url, params = params)
        return res
