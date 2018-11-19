import string

import nltk
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer


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

    def extract_top_terms(self, transform, limit=None):
        # transform = self.get_transform(document)
        feature_names = self.tfidf.get_feature_names()
        terms = [(feature_names[term], transform[0, term]) for term in transform.nonzero()[1]]
        sorted_terms = sorted(terms, key=lambda t: t[1], reverse=True)
        return sorted_terms[:limit + 1] if limit is not None else sorted_terms

    def compare_transforms(self, transform1, transform2):
        """
        Calculate the similarity between two transform matrices
        :param transform1:
        :param transform2:
        :return: A number in [0, 1] where 0 is a perfect match
        """
        t1_terms = {t[0] for t in self.extract_top_terms(transform1, 20)}
        t2_terms = {t[0] for t in self.extract_top_terms(transform2, 20)}

        return 1 - len((t1_terms.intersection(t2_terms))) / len(t1_terms)


if __name__ == "__main__":
    tfidf = Tfidf("../../corpera/1000.txt")
    print("stuff:")
    t1 = tfidf.get_transform("test document is a test")
    t2 = tfidf.get_transform("other document is a text")
    print(tfidf.compare_transforms(t1, t2))
    print(tfidf.compare_transforms(t1, t1))
    print(tfidf.compare_transforms(t2, t1))
    print(tfidf.compare_transforms(t2, t2))
