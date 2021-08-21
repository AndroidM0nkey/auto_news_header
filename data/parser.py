import json
import time
from datetime import datetime, timedelta

from bs4 import BeautifulSoup
from requests import get

BASE_URL = 'https://www.interfax.ru'
CURRENT_TIME = datetime.now()

# Парсинг ссылок на статьи
with open('links.txt', 'w') as outFile:
	links = []

	for i in range(25):
		date = CURRENT_TIME - timedelta(days=i)
		YEAR, MONTH, DAY = date.year, '{:02}'.format(date.month), date.day
		print(YEAR, MONTH, DAY)

		markup = BeautifulSoup(get(f'{BASE_URL}/{YEAR}/{MONTH}/{DAY}').text, 'html.parser')

		for link in markup.select('.an a'):
			links.append(link['href'])

	outFile.write('\n'.join(links))
	time.sleep(0.25)
	

# Парсинг статей
with open('links.txt', 'r') as inputFile:
	data = []
	urls = inputFile.readlines()
	i = 1

	for url in urls:
		print(f'{i} / {len(urls)}')
		if url.startswith("/"):
			url = BASE_URL + url

		r = get(url.strip())
		r.encoding = r.apparent_encoding
		markup = BeautifulSoup(r.text, 'html.parser')

		articleBody = markup.select('article[itemprop="articleBody"]')
		text = ''

		if len(articleBody):
			for paragraph in articleBody[0].select('p:not([itemprop])'):
				text += paragraph.text + '\n'

		tagsBody = markup.select('.textMTags')
		tags = []

		if len(tagsBody):
			for tag in tagsBody[0].find_all('a'):
				tags.append(tag.text)

		data.append(
			{
				'title': markup.find('h1').text,
				'text': text,
				'date': markup.find('time')['datetime'],
				'tags': tags
			}
		)

		time.sleep(0.1)
		i += 1

	outputFile = open('dataset.json', 'w', encoding='utf-8')
	outputFile.write(json.dumps(data, ensure_ascii=False))
