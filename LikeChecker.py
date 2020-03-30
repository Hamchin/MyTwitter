import MyTwitter, time, json, sys, datetime

class FavoriteChecker():

    def __init__(self, list_name = None):
        self.twitter, self.user_id = MyTwitter.login()
        self.list_id = MyTwitter.get_list_id(list_name) if list_name else ''
        self.friends = MyTwitter.get_list_members(self.twitter, self.list_id)
        self.friends = [friend['id_str'] for friend in self.friends] + [self.user_id]
        self.follows = MyTwitter.get_friends(self.twitter, self.user_id)
        self.follows = [user for user in self.follows if user['id_str'] not in self.friends]
        self.users = []
        self.get_date = lambda date: str(MyTwitter.get_date(date))

    def check_favorite(self, user, target):
        tweets = MyTwitter.get_like_tweets(self.twitter, user['id_str'], 1000, target, loop = True)
        if tweets == []: return None
        tweet = tweets[-1]
        if tweet['user']['id_str'] == target:
            date = self.get_date(tweet['created_at'])
            return date + '\n\n' + tweet['text']
        date = "{0} ({1})".format(self.get_date(tweet['created_at']), len(tweets))
        return date + '\n\n' + "Not Found"

    def setup(self, count = 2000):
        self.users = []
        tweets = MyTwitter.get_tweets(self.twitter, self.user_id, count)
        for i, tweet in enumerate(tweets):
            sys.stdout.write("\r{0}%".format(100*i//(len(tweets)-1)))
            sys.stdout.flush()
            date = self.get_date(tweet['created_at'])
            text = date + '\n\n' + tweet['text']
            fav_user_ids = MyTwitter.get_like_user_ids(tweet['id_str'], self.friends)
            user_ids = [user['id_str'] for user in self.users]
            self.users.extend([{'id_str': user_id, 'text': text} for user_id in fav_user_ids if user_id not in user_ids])
        follows = [friend['id_str'] for friend in self.follows]
        self.users = [user for user in self.users if user['id_str'] in follows]

    def show_fav_user(self):
        users = MyTwitter.get_users(self.twitter, user_ids = [user['id_str'] for user in self.users])
        for i, user in enumerate(self.users):
            message = "{0}: {1}\n".format(i+1, users[i]['name'])
            message += "https://twitter.com/{0}\n\n".format(users[i]['screen_name'])
            message += user['text']
            print('=' * 50 + '\n')
            print(message + '\n')

    def show_not_fav_user(self):
        print("↓ Not Favorite User ↓" + '\n')
        for friend in self.follows:
            if friend['id_str'] not in [user['id_str'] for user in self.users] and friend['protected'] == False:
                print(friend['name'])
                print("https://twitter.com/" + friend['screen_name'] + '\n')

    def show_protected_user(self):
        user_ids = [user['id_str'] for user in self.users]
        for i, friend in enumerate(self.follows):
            if friend['id_str'] not in user_ids and friend['protected'] == True:
                message = friend['name'] + '\n'
                message += "https://twitter.com/{0}".format(friend['screen_name'])
                print(message + '\n')
                response = self.check_favorite(friend, self.user_id)
                if response is not None: print(response + '\n')
                print('=' * 50 + '\n')

if __name__ == '__main__':
    if len(sys.argv) == 2:
        FavoriteChecker = FavoriteChecker(sys.argv[1])
    elif len(sys.argv) == 1:
        FavoriteChecker = FavoriteChecker()
    else:
        print("Usage: python3 {0} (EXCLUDED_LIST_NAME)".format(sys.argv[0]))
        sys.exit()
    FavoriteChecker.setup()
    input('\n')
    while True:
        try:
            FavoriteChecker.show_fav_user()
            break
        except:
            pass
    input('=' * 50 + '\n')
    FavoriteChecker.show_not_fav_user()
    input('=' * 50 + '\n')
    FavoriteChecker.show_protected_user()
