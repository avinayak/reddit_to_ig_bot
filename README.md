# generic_igbot

An instagram bot that reposts content from reddit to instagram(I know it's evil). Uses celery to run image posting task periodically. 

Fork and deploy this repo in a heroku instance. Set the following config variables:

* `IGBOT_DELAY` - Delay in seconds between posts
* `IGBOT_USERNAME` - Instagram account username
* `IGBOT_PASSWORD` - Instagram account password
* `IGBOT_SUBREDDIT` - The subreddit to repost content from
* `IGBOT_HASHTAGS` - list of hashtags to be appened to the post
* `REDIS_URL` - The URL of the redis server used by celery task runner. This is auto configured if you provision a Heroku Redis addon.
