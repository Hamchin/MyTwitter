from twitter import Twitter
from dotenv import load_dotenv
import os

load_dotenv()

CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
ACCESS_SECRET = os.environ['ACCESS_SECRET']
TARGET_LIST_ID = os.environ['TARGET_LIST_ID']
EXCLUDED_LIST_ID = os.environ['EXCLUDED_LIST_ID']
NOTICE_API_URL = os.environ['NOTICE_API_URL']

twitter = Twitter(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
