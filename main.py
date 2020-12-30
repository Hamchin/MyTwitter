import sys, json
from src.twitter import Twitter
from src import check_follower, check_notice, customize, delete_tweet, recommend

config = json.load(open('config/config.json', 'r'))

consumer_key = config['consumer_key']
consumer_secret = config['consumer_secret']
access_token = config['access_token']
access_secret = config['access_secret']
notice_api_url = config['notice_api_url']

twitter = Twitter(consumer_key, consumer_secret, access_token, access_secret)

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) >= 2 else ''
    if mode == 'check_follower':
        check_follower.main(twitter)
    elif mode == 'check_notice':
        check_notice.main(twitter, notice_api_url)
    elif mode == 'customize':
        customize.main(twitter, notice_api_url, **config['customize'])
    elif mode == 'delete_tweet':
        delete_tweet.main(twitter)
    elif mode == 'recommend':
        recommend.main(twitter)
