import time

from bs4 import BeautifulSoup
from requests import get


def process(links):
    data = []
    for url in links:
        try:
            r = get(url.strip())
            r.encoding = r.apparent_encoding
            markup = BeautifulSoup(r.text, 'html.parser')

            article_body = markup.select('article[itemprop="articleBody"]')
            text = ''

            if len(article_body):
                for paragraph in article_body[0].select('p:not([itemprop])'):
                    text += paragraph.text + '\n'

            tags_body = markup.select('.textMTags')
            tags = []

            if len(tags_body):
                for tag in tags_body[0].find_all('a'):
                    tags.append(tag.text)

            data.append(
                {
                    'headline': markup.find('h1').text,
                    'body': text,
                    'date': markup.find('time')['datetime'],
                    'tags': tags
                }
            )
            time.sleep(0.1)
        except:
            print("went wrong")
            return []
    return data
    # algo.gogogo(data)