import MyTwitter, requests, json

API_URL = "https://notice-database.herokuapp.com/notices"

class LikeChecker():
    twitter = None
    user_id = None
    targets = None
    excluded_list = None # {'name': LIST_NAME, 'id': LIST_ID}
    target_type = None # 'Following' or 'Followers'
    display_type = None # 'Like Count' or 'Last Date'
    target_types = ['Following', 'Followers']
    display_types = ['Like Count', 'Last Date']

    def __init__(self, excluded_list = None, target_type = None, display_type = None):
        self.twitter, self.user_id = MyTwitter.login()
        self.excluded_list = excluded_list if excluded_list else self.ask_excluded_list()
        self.target_type = target_type if target_type else self.ask_target_type()
        self.display_type = display_type if display_type else self.ask_display_type()
        self.targets = self.get_targets()

    def ask_excluded_list(self):
        excluded_list = {'name': None, 'id': None}
        lists = self.get_lists()
        print()
        for i, item in enumerate(lists):
            print(f"{i+1}: {item['name']}")
        in_str = input('\n' + "? Excluded List (Number): ")
        if in_str != '':
            index = self.get_number(in_str)
            assert(1 <= index <= len(lists))
            excluded_list = lists[index - 1]
        return excluded_list

    def ask_target_type(self):
        print()
        for i, target_type in enumerate(self.target_types):
            print(f"{i+1}: {target_type}")
        in_str = input('\n' + "? Target Users (Number): ")
        index = self.get_number(in_str)
        assert(1 <= index <= len(self.target_types))
        return self.target_types[index - 1]

    def ask_display_type(self):
        print()
        for i, display_type in enumerate(self.display_types):
            print(f"{i+1}: {display_type}")
        in_str = input('\n' + "? Display Mode (Number): ")
        index = self.get_number(in_str)
        assert(1 <= index <= len(self.display_types))
        return self.display_types[index - 1]

    def get_lists(self):
        with open('data/lists.json', 'r') as f:
            lists = json.load(f)
        lists = [{'name': name, 'id': ID} for name, ID in lists.items()]
        return lists

    def get_number(self, string):
        assert(string.isdecimal())
        return int(string)

    def get_targets(self):
        if self.target_type == 'Following':
            targets = MyTwitter.get_friends(self.twitter, self.user_id)
        elif self.target_type == 'Followers':
            targets = MyTwitter.get_followers(self.twitter, self.user_id)
        else:
            raise Exception("Invalid Target Type")
        if self.excluded_list['id']:
            excluded_users = MyTwitter.get_list_members(self.twitter, self.excluded_list['id'])
            excluded_user_ids = [user['id_str'] for user in excluded_users]
            targets = [target for target in targets if target['id_str'] not in excluded_user_ids]
        return targets

    def check(self):
        notices = self.get_notices(size = 10000)
        if self.display_type == 'Like Count':
            self.check_like_count(notices)
        elif self.display_type == 'Last Date':
            self.check_last_date(notices)
        else:
            raise Exception("Invalid Display Type")

    def get_notices(self, size = 10):
        params = {'size': size}
        res = requests.get(API_URL, params = params)
        notices = json.loads(res.text)
        notices = [notice for notice in notices if notice['receiver_id'] == self.user_id]
        return notices

    def check_like_count(self, notices):
        target_dict = {target['id_str']: target for target in self.targets}
        counter = {target['id_str']: 0 for target in self.targets}
        for notice in notices:
            sender_id = notice['sender_id']
            if target_dict.get(sender_id):
                counter[sender_id] += 1
        sorted_counter = sorted(counter.items(), key = lambda item: -item[1])
        print()
        for user_id, count in sorted_counter:
            user = target_dict[user_id]
            print(f"{user['name']} : {count}")
            print(f"https://twitter.com/{user['screen_name']}\n")

    def check_last_date(self, notices):
        pass

if __name__ == '__main__':
    checker = LikeChecker()
    checker.check()
