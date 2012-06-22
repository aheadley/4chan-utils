#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
import sys
import os
import re

yt_re = re.compile(r'((?:http://)?(?:www\.)?youtu(?:be\.com/watch\?(?:\S*)v=|\.be/)[\w_-]+)')

response = requests.get(sys.argv[1])
if response.ok:
    page = BeautifulSoup(response.text)
    for tag in page.find_all('blockquote'):
        m = yt_re.search(tag.get_text())
        if m:
            print m.groups(1)[0]
