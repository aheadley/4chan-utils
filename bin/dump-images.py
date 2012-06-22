#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
import sys
import os
import re

def tag_filter(tag):
    if tag.name == 'a' and 'href' in tag.attrs and 'class' not in tag.attrs:
        return re.match(r'//images\.4chan\.org/\w+/src/\d+\.(?:jpe?g|png|gif)',
            tag['href'])
    return False

response = requests.get(sys.argv[1])
if response.ok:
    page = BeautifulSoup(response.text)
    for tag in page.find_all(tag_filter):
        url = 'http:' + tag['href']
        name = tag.next_sibling.next_sibling['title']
        if not os.path.exists(name):
            mtime = int(url.split('/')[-1].rsplit('.', 1)[0])
            print '{url} -> {name}'.format(url=url, name=name, time=mtime)
            img_req = requests.get(url)
            if img_req.ok:
                with open(name, 'wb') as img:
                    img.write(img_req.content)
                os.utime(name, (mtime, mtime))
            else:
                print img_req
        else:
            print '{name} exists, skipping...'.format(name=name)
