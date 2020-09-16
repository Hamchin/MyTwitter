# MyTwitter

## crontab

```
MYTWITTER=/Users/$USER/MyTwitter
VIRTUALENV=virtualenv/bin/activate

0 * * * * cd $MYTWITTER; source $VIRTUALENV; python3 check_follower.py;
*/10 * * * * cd $MYTWITTER; source $VIRTUALENV; python3 customize.py;
```
