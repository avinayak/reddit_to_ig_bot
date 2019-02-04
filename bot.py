#!/usr/bin/env python
# -*- coding: utf-8 -*-

from InstagramAPI import InstagramAPI
from celery import Celery
from celery.task import periodic_task
from datetime import timedelta
from os import environ
import urllib.request
import json
import re

url = 'https://www.reddit.com/r/%s.json'%environ.get('IGBOT_SUBREDDIT', 'pics')
username = os.environ['IGBOT_USERNAME'] environ.get('IGBOT_USERNAME', '')
password = os.environ['IGBOT_PASSWORD'] environ.get('IGBOT_PASSWORD', '')
hashtags = os.environ['IGBOT_HASHTAGS'] environ.get('IGBOT_HASHTAGS', '#reddit')
REDISCLOUD_URL = environ.get('REDIS_URL', 'redis://localhost')
DELAY = int(environ.get('IGBOT_DELAY', 60*60*4))

def retrive(url):
    req = urllib.request.Request(
    url, 
    data=None, 
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        }
    )
    f = urllib.request.urlopen(req)
    return f
    
celery = Celery('tasks', broker=REDISCLOUD_URL)

@periodic_task(run_every=timedelta(seconds=DELAY))
def post_ig():
    reddit_out = json.loads((retrive(url)).read().decode('utf-8'))

    with open('posted_imgs.txt','r+') as log:
        loglines = [i.strip() for i in log.readlines()]
        for post in reddit_out['data']['children']:
            imageurl = post['data']['url']
            title = post['data']['title']
            if imageurl not in loglines:
                break
        
        title = re.sub('\[[^\]]+\]', '', title).strip()
        print(imageurl,title)
        
        with open('art.jpg','wb') as imfile:
            imfile.write(retrive(imageurl).read())
        log.write(imageurl+"\n")
        
        InstagramAPI = InstagramAPI(username, password)
        InstagramAPI.login()  # login
        
        photo_path = './art.jpg'
        InstagramAPI.uploadPhoto(photo_path, caption='%s\n%s'%(title,hashtags))
