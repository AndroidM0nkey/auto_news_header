import json
import re
from pprint import pprint
from string import punctuation

import numpy as np
from nltk import download, sent_tokenize, word_tokenize
from nltk.cluster.util import cosine_distance
from nltk.corpus import stopwords
from nltk.stem.snowball import RussianStemmer
from nltk.tokenize import RegexpTokenizer
from pymystem3 import Mystem
from summa.keywords import keywords

# Загрузка стопслов nltk
download("stopwords")

MULTIPLE_WHITESPACE_PATTERN = re.compile(r"\s+", re.UNICODE)

for char in ['-', '/']:
    punctuation = punctuation.replace(char, '')


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
        self.steps = 100  # iteration steps
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
                print(str(sorted_pr[index]) + " : " +
                      str(self.pr_vector[sorted_pr[index]]))
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

data = json.loads(open('../data/dataset_public.json', encoding='utf-8').read())


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


summarizedText = generateSummarizedText(texts)
# print(preprocessText(summarizedText))
print(keywords(preprocessText(summarizedText), language='russian', words=50))
