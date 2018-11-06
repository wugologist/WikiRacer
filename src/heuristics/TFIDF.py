import string

import nltk
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer

from src import WikipediaApi


class Tfidf:
    def __init__(self, corpus_filename):
        with open(corpus_filename, "r", encoding="utf-8") as f:
            self.corpus = [l.lower().translate(str.maketrans('', '', string.punctuation)) for l in f.readlines()]
        self.tfidf = TfidfVectorizer(tokenizer=Tfidf.tokenize, stop_words='english')
        self.tfs = self.tfidf.fit_transform(self.corpus)

    @staticmethod
    def tokenize(text):
        tokens = nltk.word_tokenize(text)
        stems = []
        for item in tokens:
            stems.append(PorterStemmer().stem(item))
        return stems

    def get_transform(self, document):
        return self.tfidf.transform([document])

    def extract_top_n_terms(self, document, n=None):
        transform = self.get_transform(document)
        feature_names = self.tfidf.get_feature_names()
        terms = [(feature_names[term], transform[0, term]) for term in transform.nonzero()[1]]
        sorted_terms = sorted(terms, key=lambda t: t[1], reverse=True)
        return sorted_terms[:n + 1] if n is not None else sorted_terms


if __name__ == "__main__":
    tfidf = Tfidf("../../corpera/1000.txt")
    print("stuff:")
    response = tfidf.get_transform("This is a random string, whatever, blue, purple, portmanteau")
    print(tfidf.extract_top_n_terms("this is a super important document fdsfdsa the in a", 5))
    api = WikipediaApi.WikipediaApi()
    text = api.get_random_text_and_links()[0]
    print(tfidf.extract_top_n_terms(text, 10))
