# -*- coding: utf-8 -*-

from flask import Flask, render_template
from flask import request, jsonify
import urllib.request
import MyTwitter
import datetime
import time
import json
import sys
import re

app = Flask(__name__)
image = None
tweetList = {
        "Timeline": [],
        "Kawaii": [],
        "MyList": [],
        "University": [],
        "Myself": [],
        "Favorited": []
        }

def getTweetList(name):
    if name == "Timeline": return getTimeline()
    elif name == "Kawaii": return getKawaii()
    elif name == "MyList": return getMyList()
    elif name == "University": return getUniversity()
    elif name == "Myself": return getMyself()

def getTimeline():
    twitter = MyTwitter.login()
    friendList = MyTwitter.getListMember(twitter, "")
    friendList = [friend["id_str"] for friend in friendList]
    List = MyTwitter.getTimeline(twitter, 200)
    List = [tweet for tweet in List if not tweet.get("retweeted_status")
            and tweet["user"]["id_str"] not in friendList
            and tweet["favorite_count"] > 1]
    return list(map(retouch, List))

def getKawaii():
    twitter = MyTwitter.login()
    List = MyTwitter.getListTimeline(twitter, "", 400)
    List = [tweet["retweeted_status"]
            if tweet.get("retweeted_status") else tweet for tweet in List]
    List = [tweet for tweet in List if tweet["entities"].get("media")
            and tweet["favorite_count"] > 100
            and not MyTwitter.isTimeover(tweet["created_at"], 7)]
    return list(map(retouch, List))

def getMyList():
    twitter = MyTwitter.login()
    List = MyTwitter.getListTimeline(twitter, "", 200)
    List = [tweet["retweeted_status"]
            if tweet.get("retweeted_status") else tweet for tweet in List]
    return list(map(retouch, List))

def getUniversity():
    twitter = MyTwitter.login()
    List = MyTwitter.getListTimeline(twitter, "", 200)
    List = [tweet for tweet in List if not tweet.get("retweeted_status")]
    return list(map(retouch, List))

def getMyself():
    twitter = MyTwitter.login()
    List = MyTwitter.getTweetList(twitter, "", 200)
    return list(map(retouch, List))

def getFavorited():
    twitter = MyTwitter.login()
    List = MyTwitter.getTweetList(twitter, "", 200)[:10]
    List = [MyTwitter.getFavUserIDList(tweet["id_str"], [""])
            for tweet in List]
    List = [user for userList in List for user in userList]
    List = sorted(set(List), key = List.index)
    List = [MyTwitter.getTweetList(twitter, user_id, 200) for user_id in List]
    List = [tweet for tweetList in List for tweet in tweetList]
    List = sorted(List, key = lambda tweet: time.mktime(
        time.strptime(tweet["created_at"], "%a %b %d %H:%M:%S +0000 %Y")
        ), reverse = True)
    return list(map(retouch, List))

def retouch(tweet):
    date = tweet["created_at"]
    date = datetime.datetime.strptime(
            tweet["created_at"], "%a %b %d %H:%M:%S +0000 %Y")
    time = datetime.datetime.now() - date - datetime.timedelta(hours = 9)
    if time.days != 0: tweet["time"] = f"{time.days}d"
    elif time.seconds//60 >= 60: tweet["time"] = f"{time.seconds//3600}h"
    else: tweet["time"] = f"{time.seconds//60}m"
    tweet["text"] = re.sub(r'https://[^ \t\n\r\f]+','',tweet["text"])
    tweet["text"] = re.sub(r'#([^ \t\n\r\f]+)', r'<a href="https://twitter.com/hashtag/\1?src=hash" target="_blank">#\1</a>', tweet["text"])
    return tweet

@app.route("/")
def index():
    global image
    global tweetList
    image = None
    tweetList = {
            "Timeline": [],
            "Kawaii": [],
            "MyList": [],
            "University": [],
            "Myself": [],
            "Favorited": []
            }
    return render_template("index.html")

@app.route("/tweet", methods = ["POST"])
def tweet():
    global image
    twitter = MyTwitter.login()
    tweet = request.json["tweet"]
    media = request.json["media"]
    if image:
        req = MyTwitter.tweet(twitter, tweet, image)
        image = None
    elif media != "":
        media = urllib.request.urlopen(media).read()
        req = MyTwitter.tweet(twitter, tweet, media)
    else:
        req = MyTwitter.tweet(twitter, tweet)
    return req.text, req.status_code

@app.route("/favorite", methods = ["POST"])
def favorite():
    twitter = MyTwitter.login()
    tweet_id = request.json["tweet_id"]
    req = MyTwitter.postFavorite(twitter, tweet_id)
    return req.text, req.status_code

@app.route("/delete", methods = ["POST"])
def delete():
    twitter = MyTwitter.login()
    tweet_id = request.json["tweet_id"]
    req = MyTwitter.deleteTweet(twitter, tweet_id)
    return req.text, req.status_code

@app.route("/update", methods = ["POST"])
def update():
    global tweetList
    name = request.json["name"]
    newList = List = getTweetList(name)
    idList = [tweet["id_str"] for tweet in tweetList[name]]
    List = [tweet for tweet in List if tweet["id_str"] not in idList]
    idList = [tweet["id_str"] for tweet in newList]
    tweetList[name] = [tweet for tweet in tweetList[name]
            if tweet["id_str"] not in idList]
    tweetList[name] = (newList + tweetList[name])[:200]
    html = "small.html" if name == "Myself" else "timeline.html"
    return jsonify(tweetList = json.dumps(tweetList[name]),
            html = render_template(html, tweetList = List))

@app.route("/upload", methods = ["POST"])
def upload():
    global image
    image = request.files["image"]
    name = image.filename
    image = image.stream.read()
    return name

@app.route("/getFavorite", methods = ["POST"])
def getFavorite():
    twitter = MyTwitter.login()
    tweet_id = request.json["tweet_id"]
    user_id = request.json["user_id"]
    List = MyTwitter.getFavUserIDList(tweet_id, [user_id])
    List = MyTwitter.getUserList(twitter, List)
    return jsonify(json.dumps(List))

if __name__ == "__main__":
    argv = sys.argv
    if len(argv) != 2: port = 8888
    else: port = int(argv[1])
    app.debug = True
    app.run(host = "localhost", port = port)

