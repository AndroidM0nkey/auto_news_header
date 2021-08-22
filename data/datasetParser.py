import json
import re
from string import punctuation

from nltk import sent_tokenize


def converter(obj):
	obj['text'] = restructureText(obj['text'])
	return obj

def restructureText(text):
	sentences = []
	for sentence in sent_tokenize(text.lower()):
		sentences.append(re.sub(r' +', ' ', sentence.translate(str.maketrans('', '', punctuation))))

	return sentences

with open('dataset.json', 'r', encoding='utf-8') as inputFile:
	data = json.loads(inputFile.read())[:3]
	data = list(map(converter, data))
