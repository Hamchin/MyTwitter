import json
import sys
from src import check_followers
from src import check_notices
from src import customize
from src import delete_tweets
from src import recommend
from src.twitter import Twitter

if __name__ == '__main__':
    config = json.load(open('config/config.json', 'r'))

    twitter = Twitter(
        config['consumer_key'],
        config['consumer_secret'],
        config['access_token'],
        config['access_secret']
    )

    mode = sys.argv[1] if len(sys.argv) >= 2 else ''
    if mode == 'check_followers':
        check_followers.main(twitter)
    elif mode == 'check_notices':
        check_notices.main(twitter, config['notice_api_url'])
    elif mode == 'customize':
        customize.main(twitter, config['notice_api_url'], **config['customize'])
    elif mode == 'delete_tweets':
        delete_tweets.main(twitter)
    elif mode == 'recommend':
        recommend.main(twitter)
