#!/usr/bin/env python
import requests
from bs4 import BeautifulSoup
import numpy as np
from wordcloud import WordCloud
import json
import os

JSON_FILE = 'NDSS21.json'
FONT = './Comic Sans MS.ttf'

urls = [
    'https://www.ndss-symposium.org/ndss-program/ndss-2021/', 
]

papers = {}

banner = '''
                                                                        Author: B3ale
'''

print banner

if os.path.exists(JSON_FILE):
    with open(JSON_FILE, 'rb') as f:
        papers = json.loads(f.read())
else:
    for url in urls:
        r = requests.get(url=url)
        soup = BeautifulSoup(r.text, 'html.parser')
        titles = soup.select('div[style="display: flex; align-items: center"]')[2:]
        abstracts = soup.select('div[class="collapse"]')
        assert len(titles) == len(abstracts)
        l = len(titles)
        for i in range(l):
            title = titles[i].strong.a.get_text()
            abstract = abstracts[i].p.get_text()
            papers[title] = abstract
    with open(JSON_FILE, 'wb') as f:
        f.write(json.dumps(papers))

#print papers

title_text = ''
abstract_text = ''
for title, abstract in papers.items():
    try:
        title_text += title.encode() + ' '
        abstract_text += abstract.encode() + ' '
    except UnicodeEncodeError:
        continue

x, y = np.ogrid[:300, :300]
mask = (x - 150) ** 2 + (y - 150) ** 2 > 130 ** 2
mask = 255 * mask.astype(int)

title_wc = WordCloud(background_color='white', repeat=True, mask=mask, font_path=FONT, width=2000, height=2000, scale=4)
title_wc.generate(title_text)
title_wc.to_file('./title_cloud.png')

abstract_wc = WordCloud(background_color='white', repeat=True, mask=mask, font_path=FONT, width=2000, height=2000, scale=4)
abstract_wc.generate(abstract_text)
abstract_wc.to_file('./abstract_cloud.png')

'''
def draw_section_cloud(section_name):
    text = ''
    for title, p in papers[section_name].items():
        try:
            text += title.encode() + ' '
            text += p.encode() + ' '
        except UnicodeEncodeError:
            continue
    wc = WordCloud(background_color='white', repeat=True, mask=mask, font_path=FONT, width=2000, height=2000, scale=4)
    wc.generate(text)
    section_name = section_name.replace(' ', '_').replace(':', '').replace(';', '').replace(',', '')
    wc.to_file(section_name + '_cloud.png')
'''

