# reddit_to_ig_bot

An instagram bot that rips content from reddit to instagram(I know it's cancerous💀).
Uses celery to run image posting task periodically. [see it in action](https://www.instagram.com/albumartcurator/)

## Instructions

1. Fork and deploy this repo in a heroku instance.
2. Attach a Heroku Redis addon to the dyno.
3. Set the following config variables:

* `IGBOT_USERNAME` - Instagram account username
* `IGBOT_PASSWORD` - Instagram account password
* `IGBOT_SUBREDDIT` - The subreddit to repost content from
* `IGBOT_DELAY` - Delay in seconds between posts
* `IGBOT_HASHTAGS` - list of hashtags to be appened to the post
* `REDIS_URL` - The URL of the redis server used by celery task runner (This is auto configured if you provision a Heroku Redis addon).
