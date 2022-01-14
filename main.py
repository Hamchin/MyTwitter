import argparse
import json
from src import check_followers
from src import check_notices
from src import customize
from src import delete_tweets
from src import recommend
from src.twitter import Twitter

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', required = True, choices = [
        'check_followers',
        'check_notices',
        'customize',
        'delete_tweets',
        'recommend'
    ])
    args = parser.parse_args()

    config = json.load(open('config/config.json', 'r'))

    twitter = Twitter(
        config['consumer_key'],
        config['consumer_secret'],
        config['access_token'],
        config['access_secret']
    )

    if args.mode == 'check_followers':
        check_followers.main(twitter)
    elif args.mode == 'check_notices':
        check_notices.main(twitter, config['notice_api_url'])
    elif args.mode == 'customize':
        customize.main(twitter, config['notice_api_url'], **config['customize'])
    elif args.mode == 'delete_tweets':
        delete_tweets.main(twitter)
    elif args.mode == 'recommend':
        recommend.main(twitter)
