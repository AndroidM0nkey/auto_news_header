import json
import spacy

# Opening JSON file
import textrank

f = open('../data/dataset_public.json', )

data = json.load(f)
print(data)
# all_news = [it['news'] for it in data]
texts = [[new['body'] for new in it['news']] for it in data]
#
# nlp = spacy.load("ru_core_news_lg")
# my_header = headers[0][2]
# my_str = ""
# for it in headers[0]:
#     my_str += it + " "
# doc = nlp(my_header)

# for np in doc.noun_chunks:
#     print(np.text)

# print(my_header, [(X.text, X.label_) for X in doc.ents], sep='\n')
# my_header = ' '.join([token.lemma_ for token in doc])
# print(my_header)
# doc = nlp(my_header)
# print(my_header, [(X.text, X.label_) for X in doc.ents], sep='\n')
# for title in headers:
#     for header in title:

print(texts[0][0], textrank.textrank(texts[0][0]))
