import MyTwitter, time, json, sys, datetime

class FavoriteChecker():

    def __init__(self, user_name, list_name = None):
        self.twitter, self.user_id = MyTwitter.login(user_name)
        self.list_id = MyTwitter.get_list_id(list_name) if list_name else ""
        self.friend_list = MyTwitter.get_list_member(self.twitter, self.list_id)
        self.friend_list = [friend["id_str"] for friend in self.friend_list] + [self.user_id]
        self.follow_list = MyTwitter.get_following(self.twitter, self.user_id)
        self.follow_list = [user for user in self.follow_list if user["id_str"] not in self.friend_list]
        self.user_list = []
        self.get_date = lambda date: str(MyTwitter.get_date(date))

    def check_favorite(self, user, target):
        tweet_list = MyTwitter.get_fav_tweet_list(self.twitter, user["id_str"], 1000, target, loop = True)
        if tweet_list == []: return None
        tweet = tweet_list[-1]
        if tweet["user"]["id_str"] == target:
            date = self.get_date(tweet["created_at"])
            return date + "\n\n" + tweet["text"]
        date = "{0} ({1})".format(self.get_date(tweet["created_at"]), len(tweet_list))
        return date + "\n\n" + "Not Found"

    def setup(self, count = 2000):
        self.user_list = []
        tweet_list = MyTwitter.get_tweet_list(self.twitter, self.user_id, count)
        for i, tweet in enumerate(tweet_list):
            sys.stdout.write("\r{0}%".format(100*i//(len(tweet_list)-1)))
            sys.stdout.flush()
            date = self.get_date(tweet["created_at"])
            text = date + "\n\n" + tweet["text"]
            fav_user_id_list = MyTwitter.get_fav_user_id_list(tweet["id_str"], self.friend_list)
            user_id_list = [user["id_str"] for user in self.user_list]
            self.user_list.extend([{"id_str": user_id, "text": text} for user_id in fav_user_id_list if user_id not in user_id_list])
        follow_list = [friend["id_str"] for friend in self.follow_list]
        self.user_list = [user for user in self.user_list if user["id_str"] in follow_list]

    def show_fav_user(self):
        name_list = MyTwitter.get_user_list(self.twitter, [user["id_str"] for user in self.user_list])
        for i, user in enumerate(self.user_list):
            message = "{0}: {1}\n".format(i+1, name_list[i]["name"])
            message += "https://twitter.com/{0}\n\n".format(name_list[i]["screen_name"])
            message += user["text"]
            print("=" * 50 + "\n")
            print(message + "\n")

    def show_not_fav_user(self):
        print("↓ Not Favorite User ↓" + "\n")
        for friend in self.follow_list:
            if friend["id_str"] not in [user["id_str"] for user in self.user_list] and friend["protected"] == False:
                print(friend["name"])
                print("https://twitter.com/" + friend["screen_name"] + "\n")

    def show_protected_user(self):
        for i, friend in enumerate(self.follow_list):
            while friend["id_str"] not in [user["id_str"] for user in self.user_list] and friend["protected"] == True:
                try:
                    response = self.check_favorite(friend, self.user_id)
                    if response is not None:
                        message = friend["name"] + "\n"
                        message += "https://twitter.com/{0}\n\n".format(friend["screen_name"])
                        message += response
                        print(message + "\n")
                        print("=" * 50 + "\n")
                    break
                except:
                    time.sleep(60)

if __name__ == '__main__':
    if len(sys.argv) == 3:
        FavoriteChecker = FavoriteChecker(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 2:
        FavoriteChecker = FavoriteChecker(sys.argv[1])
    else:
        print("Usage: python3 {0} [user_type] (exception_list_name)".format(sys.argv[0]))
        sys.exit()
    FavoriteChecker.setup()
    input("\n")
    while True:
        try:
            FavoriteChecker.show_fav_user()
            break
        except:
            pass
    input("=" * 50 + "\n")
    FavoriteChecker.show_not_fav_user()
    input("=" * 50 + "\n")
    FavoriteChecker.show_protected_user()