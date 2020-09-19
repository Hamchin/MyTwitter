# MyTwitter

## crontab

```
MYTWITTER=/Users/$USER/MyTwitter
VIRTUALENV=virtualenv/bin/activate

0 * * * * cd $MYTWITTER; source $VIRTUALENV; python3 check_follower.py;
*/10 * * * * cd $MYTWITTER; source $VIRTUALENV; python3 customize.py;
```

## Lambda Function

| Attribute | Content |
| - | - |
| Name | MyTwitterAPI |
| Runtime | Python 3.8 |
| Memory | 128 MB |
| Timeout | 30 seconds |

### Role

| Attribute | Content |
| - | - |
| Name | LambdaAccess2CloudWatchLogs |
| Policy | CloudWatchLogsFullAccess |

### Environmental Variable

| Key |
| - |
| CONSUMER_KEY |
| CONSUMER_SECRET |

To create zip file:

```
$ zip -r function.zip lambda_function.py twitter.py
```

## Lambda Layer

| Attribute | Content |
| - | - |
| Name | OAuthLibrary |
| Runtime | Python 3.8 |

To create zip file:

```
$ pip3 install -t ./python requests_oauthlib
$ zip -r package.zip ./python
```

## API Gateway

- Use Lambda Proxy Integration.
- Enable CORS.

### GET /friends/list

Returns a list of user objects for every user the specified user is following.

### GET /friends/ids

Returns a list of user IDs for every user the specified user is following.

### GET /followers/list

Returns a list of user objects for users following the specified user.

### GET /followers/ids

Returns a list of user IDs for every user following the specified user.

### GET /users/show

Returns a user object specified by the required user_id or screen_name parameter.

### GET /users/lookup

Returns a list of user objects specified by the comma-separated list of user_ids or screen_names.

### GET /statuses/lookup

Returns a list of tweet objects specified by the comma-separated list of IDs.

### GET /statuses/user_timeline

Returns a list of the latest tweets posted by the user specified by the screen_name or user_id parameter.

### GET /statuses/home_timeline

Returns a list of the latest tweets posted by the authenticating user and the users they follow.

### GET /lists/statuses

Returns a list of the latest tweets posted by members of the specified list.

### GET /lists/list

Returns all lists the authenticating or specified user subscribes to, including their own.

### GET /lists/members

Returns a list of user objects for the members of the specified list.

### POST /lists/members/create

Adds the member to the list.

### POST /lists/members/destroy

Removes the member from the list.

### GET /friendships/show

Returns detailed information about the relationship between two arbitrary users.

### GET /friendships/lookup

Returns the relationships of the authenticating user to the comma-separated list of user_ids or screen_names provided.

### POST /statuses/update

Posts a tweet as the authenticating user.

### POST /statuses/destroy

Destroys the tweet specified by the required ID parameter.

### POST /statuses/retweet

Retweets the tweet specified by the required ID parameter.

### POST /statuses/unretweet

Revokes the retweeted status specified by the required ID parameter.

### POST /favorites/create

Likes the tweet specified by the required ID parameter.

### POST /favorites/destroy

Revokes the liked status specified by the required ID parameter.

### POST /direct_messages/new

Sends a direct message from the authenticating user to the specified user.
