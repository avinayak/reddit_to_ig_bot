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
    desired_size = 1000

    im = Image.open(im_pth)
    old_size = im.size 
    ratio = float(desired_size)/max(old_size)
    new_size = tuple([int(x*ratio) for x in old_size])

    im = im.resize(new_size, Image.ANTIALIAS)
    new_im = Image.new("RGB", (desired_size, desired_size), (255, 255, 255))
    new_im.paste(im, ((desired_size-new_size[0])//2,
                        (desired_size-new_size[1])//2))
    new_im.save(im_pth)

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
