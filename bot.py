#!/usr/bin/env python
# -*- coding: utf-8 -*-

from InstagramAPI import InstagramAPI
from celery import Celery
from PIL import Image, ImageOps
from celery.task import periodic_task
from datetime import timedelta
from os import environ
import urllib.request
import redis
import json
import re

print("Initializing worker..")
url = 'https://www.reddit.com/r/%s.json'%environ.get('IGBOT_SUBREDDIT', 'pics')
username = environ.get('IGBOT_USERNAME', '')
password = environ.get('IGBOT_PASSWORD', '')
hashtags = environ.get('IGBOT_HASHTAGS', '#reddit')
REDISCLOUD_URL = environ.get('REDIS_URL', 'redis://localhost')
DELAY = int(environ.get('IGBOT_DELAY', 60*60*4))
print("ENV VARS INITIALIZED")



def pad_image(im_pth):
    image  = Image.open(im_pth)
    width  = image.size[0]
    height = image.size[1]

    aspect = width / float(height)

    ideal_width = 1000
    ideal_height = 525

    ideal_aspect = ideal_width / float(ideal_height)

    if aspect > ideal_aspect:
        # Then crop the left and right edges:
        new_width = int(ideal_aspect * height)
        offset = (width - new_width) / 2
        resize = (offset, 0, width - offset, height)
    else:
        # ... crop the top and bottom:
        new_height = int(width / ideal_aspect)
        offset = (height - new_height) / 2
        resize = (0, offset, width, height - offset)

    thumb = image.crop(resize).resize((ideal_width, ideal_height), Image.ANTIALIAS)
    thumb.save(im_pth)

def retrive(url):
    print("RETRIVE",url)
    req = urllib.request.Request(
    url, 
    data=None, 
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        }
    )
    f = urllib.request.urlopen(req)
    print("RETRIVE_SUCCESS",url)
    return f
    
celery = Celery('tasks', broker=REDISCLOUD_URL)

@periodic_task(run_every=timedelta(seconds=DELAY))
def post_ig():
    print("TASK_START")
    reddit_out = json.loads((retrive(url)).read().decode('utf-8'))
    r = redis.Redis.from_url(REDISCLOUD_URL)
    for post in reddit_out['data']['children']:
        imageurl = post['data']['url']
        title = post['data']['title']
        if not r.exists(imageurl):
            break
        
    title = re.sub('\[[^\]]+\]', '', title).strip()
    print(imageurl,title)
        
    with open('art.jpg','wb') as imfile:
        imfile.write(retrive(imageurl).read())
    pad_image('art.jpg')
        
    print("POSTING",imageurl,title)
    ig_api = InstagramAPI(username, password)
    ig_api.login()  # login
        
    photo_path = './art.jpg'
    ig_api.uploadPhoto(photo_path, caption='%s\n%s'%(title,hashtags))
    r.set(imageurl,"1",ex=10*24*60*60)
    print("TASK_END")
