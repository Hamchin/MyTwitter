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
| Timeout | 10 seconds |

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
$ zip -r function.zip src/lambda_function.py src/twitter.py
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

| Method | Endpoint | Description |
| - | - | - |
| POST | /friends/list | Get user objects for friends. |
| POST | /friends/ids | Get user IDs for friends. |
| POST | /followers/list | Get user objects for followers. |
| POST | /followers/ids | Get user IDs for followers. |
| POST | /users/show | Get one user object. |
| POST | /users/lookup | Get multiple user objects. |
| POST | /statuses/show | Get one tweet object. |
| POST | /statuses/lookup | Get multiple tweet objects. |
| POST | /statuses/user_timeline | Get tweets for the user. |
| POST | /statuses/home_timeline | Get tweets for friends. |
| POST | /lists/list | Get all lists of the user. |
| POST | /lists/statuses | Get tweets for list members. |
| POST | /lists/members | Get user objects for list members. |
| POST | /lists/members/create | Add the member to the list. |
| POST | /lists/members/destroy | Remove the member from the list. |
| POST | /friendships/show | Get the relationship between two users. |
| POST | /friendships/lookup | Get relationships to multiple users. |
| POST | /statuses/update | Post the tweet. |
| POST | /statuses/destroy | Delete the tweet. |
| POST | /statuses/retweet | Retweet the tweet. |
| POST | /statuses/unretweet | Un-retweet the tweet. |
| POST | /favorites/create | Like the tweet. |
| POST | /favorites/destroy | Un-like the tweet. |
| POST | /direct_messages/new | Send a direct message. |
