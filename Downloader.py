#!/usr/bin/env python
import requests
from bs4 import BeautifulSoup
import numpy as np
from wordcloud import WordCloud
import json
import os
from tqdm import tqdm

JSON_FILE = 'NDSS21-links.json'
FONT = './Comic Sans MS.ttf'
BLOCK_SZ = 1024

urls = [
    'https://www.ndss-symposium.org/ndss-program/ndss-2021/', 
]

banner = '''
 _______  ________    _________ _________  _______________   ________  ____ 
 \      \ \______ \  /   _____//   _____/  \_____  \   _  \  \_____  \/_   |
 /   |   \ |    |  \ \_____  \ \_____  \    /  ____/  /_\  \  /  ____/ |   |
/    |    \|    `   \/        \/        \  /       \  \_/   \/       \ |   |
\____|__  /_______  /_______  /_______  /  \_______ \_____  /\_______ \|___|
        \/        \/        \/        \/           \/     \/         \/     
________                      .__                    .___                   
\______ \   ______  _  ______ |  |   _________     __| _/___________        
 |    |  \ /  _ \ \/ \/ /    \|  |  /  _ \__  \   / __ |/ __ \_  __ \       
 |    `   (  <_> )     /   |  \  |_(  <_> ) __ \_/ /_/ \  ___/|  | \/       
/_______  /\____/ \/\_/|___|  /____/\____(____  /\____ |\___  >__|          
        \/                  \/                \/      \/    \/              
                                                                        Author: B3ale
'''

papers = {}

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
        links = soup.find_all('div', attrs={'class':"btn-group-vertical"})
        assert len(titles) == len(abstracts)
        l = len(links)
        idx = 0
        for i in range(l):
            if links[i].a.get_text() == u'Paper':
                title = titles[idx].strong.a.get_text()
                papers[title] = links[i].a['href']
                idx += 1
            else:
                continue
    with open(JSON_FILE, 'wb') as f:
        f.write(json.dumps(papers))

#print papers

for title, link in papers.items():
    file_name = title + '.pdf'
    if os.path.exists(file_name):
        continue
    while True:
        try:
            print '[+] start downloading <' + file_name + '>'
            # https://stackoverflow.com/questions/37573483/progress-bar-while-download-file-over-http-with-requests
            r = requests.get(link, stream=True)
            total_size_in_bytes = int(r.headers.get('content-length', 0))
            progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
            with open(file_name, 'wb') as f:
                for data in r.iter_content(BLOCK_SZ):
                    progress_bar.update(len(data))
                    f.write(data)
            progress_bar.close()
            if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
                print '[!] file size error'
            else:
                print '[+] downloaded successfully'
            break
        except requests.exceptions.SSLError:
            print '[!] network error, try again'

'''
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

