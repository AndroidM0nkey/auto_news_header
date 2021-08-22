# -*- coding: utf-8 -*-
"""Untitled3.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1_JOOIIwQg_H_B0v--ke56xueMFW0--LL
"""

# !pip install nltk
# !python -m spacy download en
# !pip install summa
# !pip install spacy
# !pip install markovify
# !pip install -m spacy download en

import pandas as pd
import numpy as np
import markovify
import re
import json
from math import sqrt
import copy
import pymorphy2
from pymystem3 import Mystem
from string import punctuation
from nltk import download, sent_tokenize, word_tokenize
from nltk.cluster.util import cosine_distance
from nltk.corpus import stopwords
import gensim.downloader as download_api
import nltk

nltk.download('gutenberg')
nltk.download('stopwords')
nltk.download("punkt")
nltk.download('stopwords')
russian_model = download_api.load('word2vec-ruscorpora-300')

MULTIPLE_WHITESPACE_PATTERN = re.compile(r"\s+", re.UNICODE)

for char in ['-', '/']:
    punctuation = punctuation.replace(char, '')


def generate_header(event):
    headlines = '. '.join([clear(article["headline"]) for article in event if article["headline"] is not None])
    extracted = ". ".join([clear(article["body"]) for article in event])
    # extracted1 = ". ".join([clear(generateSummarizedText([article["body"]], 1)) for article in event])
    train = headlines * 5 + extracted
    generated = generate_samples(train)

    return sorted(
        list({(el[0], el[1][:-1].capitalize()) for el in return_top_k_phrases(generated, train, 1) if el is not None}))[
           -10:]


def normalizeWhitespace(text):
    return MULTIPLE_WHITESPACE_PATTERN.sub(replaceWhitespace, text)


def replaceWhitespace(match):
    text = match.group()

    if "\n" in text or "\r" in text:
        return "\n"
    else:
        return " "


def isBlank(string):
    return not string or string.isspace()


def getSymmetricMatrix(matrix):
    return matrix + matrix.T - np.diag(matrix.diagonal())


def coreCosineSimilarity(vector1, vector2):
    return 1 - cosine_distance(vector1, vector2)


class TextRank4Sentences():
    def __init__(self):
        self.damping = 0.85  # damping coefficient, usually is .85
        self.min_diff = 1e-5  # convergence threshold
        self.steps = 100  # iteraion steps
        self.text_str = None
        self.sentences = None
        self.pr_vector = None

    def sentenceSimilarity(self, sent1, sent2, stopwords=None):
        if stopwords is None:
            stopwords = []

        sent1 = [w.lower() for w in sent1]
        sent2 = [w.lower() for w in sent2]

        all_words = list(set(sent1 + sent2))

        vector1 = [0] * len(all_words)
        vector2 = [0] * len(all_words)

        # build the vector for the first sentence
        for w in sent1:
            if w in stopwords:
                continue
            vector1[all_words.index(w)] += 1

        # build the vector for the second sentence
        for w in sent2:
            if w in stopwords:
                continue
            vector2[all_words.index(w)] += 1

        return coreCosineSimilarity(vector1, vector2)

    def buildSimilarityMatrix(self, sentences, stopwords=None):
        # create an empty similarity matrix
        sm = np.zeros([len(sentences), len(sentences)])

        for idx1 in range(len(sentences)):
            for idx2 in range(len(sentences)):
                if idx1 == idx2 or len(sentences[idx1]) < 7 or len(sentences[idx2]) < 7:
                    continue

                sm[idx1][idx2] = self.sentenceSimilarity(
                    sentences[idx1], sentences[idx2], stopwords=stopwords)

        # Get Symmeric matrix
        sm = getSymmetricMatrix(sm)

        # Normalize matrix by column
        norm = np.sum(sm, axis=0)
        # this is to ignore the 0 element in norm
        sm_norm = np.divide(sm, norm, where=norm != 0)

        return sm_norm

    def runPageRank(self, similarity_matrix):

        pr_vector = np.array([1] * len(similarity_matrix))

        # Iteration
        previous_pr = 0
        for epoch in range(self.steps):
            pr_vector = (1 - self.damping) + self.damping * \
                        np.matmul(similarity_matrix, pr_vector)
            if abs(previous_pr - sum(pr_vector)) < self.min_diff:
                break
            else:
                previous_pr = sum(pr_vector)

        return pr_vector

    def getSentence(self, index):
        try:
            return self.sentences[index]
        except IndexError:
            return ""

    def getTopSentences(self, number=5):
        top_sentences = {}

        if self.pr_vector is not None:
            sorted_pr = np.argsort(self.pr_vector)
            sorted_pr = list(sorted_pr)
            sorted_pr.reverse()

            index = 0
            for epoch in range(number):
                # print(str(sorted_pr[index]) + " : " +
                # str(self.pr_vector[sorted_pr[index]]))
                sent = self.sentences[sorted_pr[index]]
                sent = normalizeWhitespace(sent)
                top_sentences[sent] = self.pr_vector[sorted_pr[index]]
                index += 1

        return top_sentences

    def analyze(self, text, stop_words=None):
        self.text_str = text
        self.sentences = sent_tokenize(self.text_str)

        tokenized_sentences = [word_tokenize(sent) for sent in self.sentences]

        similarity_matrix = self.buildSimilarityMatrix(
            tokenized_sentences, stop_words)

        self.pr_vector = self.runPageRank(similarity_matrix)
        print(self.pr_vector)


STOP_WORDS = open('stopWords.txt', 'r').readlines()

data = json.loads(open('data.json', encoding='utf-8').read())


def generateSummarizedText(texts, sentenceNumber=3, stopWords=STOP_WORDS):
    summarizedText = ''

    for text in texts:
        tr4sh = TextRank4Sentences()
        tr4sh.analyze(text, stopWords)
        summarizedText += '\n'.join(tr4sh.getTopSentences(sentenceNumber).keys())

    return summarizedText


texts = []
for entry in data[0]['news'][:10]:
    texts.append(entry['body'])

mystem = Mystem()
russian_stopwords = stopwords.words("russian")


def preprocessText(text):
    text = re.sub(
        r' +', ' ', text.translate(str.maketrans('', '', punctuation)))
    tokens = mystem.lemmatize(text.lower())
    tokens = [
        token for token in tokens if token not in russian_stopwords and token != ' ' and token not in punctuation]
    text = ' '.join(list(set(tokens)))

    return text


dataset = pd.read_json('data.json')
news = pd.concat(pd.Series.tolist(dataset['news'].apply(lambda row: pd.DataFrame.from_dict(row))))[["headline", "body"]]
news.fillna("", inplace=True)
# news

stop = {'интерфакс'}


def clear(cell):
    return ". ".join(
        [" ".join([word.lower() for word in word_tokenize(sent) if word.isalpha() and word.lower() not in stop]) for
         sent in sent_tokenize(cell)])


# dataset
#
# [article["headline"] for article in dataset.iloc[4].news]

for i in range(len(dataset)):
    a = '. '.join([article["headline"] for article in dataset.iloc[i].news if article["headline"] != None])

semen = []


def generate_samples(text):
    gen = markovify.Text(text, state_size=1)

    ans = []
    for i in range(100):
        generated = gen.make_short_sentence(max_chars=50)
        if generated is not None:
            ans.append(generated)
    return ans


for i in range(len(dataset)):
    event = dataset.iloc[i].news
    headlines = '. '.join([clear(article["headline"]) for article in event if article["headline"] is not None])
    extracted = ". ".join([clear(article["body"]) for article in event])

    # extracted1 = ". ".join([clear(generateSummarizedText([article["body"]], 1)) for article in event])

    train = headlines * 5 + extracted
    # train1 = headlines + extracted1

    generated = generate_samples(train)
    # generated.extend(generate_samples(train1))

    semen.append((train, generated))


# with open("generated.json", "w") as gen:
#    gen.write(json.dumps(semen))

def return_top_k_phrases(list_of_phrases, text, k):
    morph = pymorphy2.MorphAnalyzer(lang='ru')

    text = re.sub(
        r' +', ' ', text.translate(str.maketrans('', '', punctuation)))
    parsed_text = text.split()
    parsed_named_text = []
    for word in parsed_text:
        cur_mas = morph.parse(word)[0]
        cur_pos = cur_mas.tag.POS
        cur_pos = str(cur_mas.tag.POS)
        if cur_pos == 'ADJV':
            cur_pos = 'ADJ'
        if cur_pos == 'ADJS':
            cur_pos = 'ADJ'
        elif cur_pos != 'VERB' and cur_pos != 'NOUN':
            continue
        parsed_named_text.append(str(cur_mas.normal_form) + '_' + str(cur_pos))

    result_vec = []
    for phrase in list_of_phrases:
        r_phrase = copy.deepcopy(phrase)
        r_phrase = re.sub(
            r' +', ' ', r_phrase.translate(str.maketrans('', '', punctuation)))
        cur_points = 0.0
        words = r_phrase.split()
        size = len(words)
        for word in words:
            cur_mas = morph.parse(word)[0]
            cur_pos = str(cur_mas.tag.POS)
            if cur_pos == 'ADJV':
                cur_pos = 'ADJ'
            if cur_pos == 'ADJS':
                cur_pos = 'ADJ'
            if cur_pos == 'INFN':
                cur_pos = 'VERB'
            elif cur_pos != 'VERB' and cur_pos != 'NOUN':
                size -= 1
                continue
            parsed_word = str(cur_mas.normal_form) + '_' + str(cur_pos)
            cur_metric = 0.0
            for wordt in parsed_named_text:
                try:
                    cm = (russian_model.similarity(parsed_word, wordt))
                except:
                    cm = 0.1
                cur_metric += (cm) ** 2
            cur_points += (sqrt(cur_metric / len(parsed_named_text)))
        if size != 0:
            result_vec.append((cur_points / size, phrase))
        else:
            result_vec.append((0, phrase))
    result_vec.sort()
    print(result_vec)

# text = semen[2][0]
# phrases = semen[2][1]
# return_top_k_phrases(phrases, text, 1)