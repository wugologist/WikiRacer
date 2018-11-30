import logging
import os
import pickle
import string

import nltk
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer

from heuristics.Heuristics import AbstractHeuristic

log = logging.getLogger(__name__)


class Tfidf:
    def __init__(self):
        self.model = None

    def setup(self, corpus_filename):
        self.model = self.load_or_create_model(corpus_filename)

    @staticmethod
    def load_or_create_model(corpus_filename):
        model_filename = "{}.model".format(os.path.basename(corpus_filename))
        path = "../../models/"
        model_path = path + model_filename
        if not os.path.isdir(path):
            log.info("Creating directory {}".format(path))
            os.makedirs(path)

        if os.path.isfile(model_path):
            log.info("Loading existing model {}".format(model_path))
            with open(model_path, "rb") as file:
                return pickle.load(file)
        else:
            log.info("Creating new model {}".format(model_path))
            with open(corpus_filename, "r", encoding="utf-8") as corpus_file:
                corpus = [l.lower().translate(str.maketrans('', '', string.punctuation))
                          for l in corpus_file.readlines()]
                model = TfidfVectorizer(tokenizer=Tfidf.tokenize, stop_words='english')
                model.fit_transform(corpus)
                with open(model_path, "wb") as file:
                    pickle.dump(model, file)
                    return model

    @staticmethod
    def tokenize(text):
        tokens = nltk.word_tokenize(text)
        stems = []
        for item in tokens:
            stems.append(PorterStemmer().stem(item))
        return stems

    def get_transform(self, document):
        return self.model.transform([document])

    def extract_top_terms(self, transform, limit=None):
        # transform = self.get_transform(document)
        feature_names = self.model.get_feature_names()
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


class TfidfHeuristic(AbstractHeuristic):
    def __init__(self):
        self.api = None
        self.tfidf = None
        self.goal_transform = None
        self.corpus_filename = "../../corpera/1000.txt"  # TODO don't hard code this

    def setup(self, api, start, goal):
        self.api = api
        self.tfidf = Tfidf()
        self.tfidf.setup(self.corpus_filename)
        goal_text = self.api.get_text_and_links(goal)[0]
        self.goal_transform = self.tfidf.get_transform(goal_text)

    # TODO this doesn't really work
    def calculate_heuristic(self, node):
        node_text = self.api.get_text_and_links(node)[0]
        node_transform = self.tfidf.get_transform(node_text)
        return self.tfidf.compare_transforms(node_transform, self.goal_transform)


def test():
    tfidf = Tfidf()
    tfidf.setup("../../corpera/100.txt")
    print("stuff:")
    t1 = tfidf.get_transform("test document is a test")
    t2 = tfidf.get_transform("other document is a text")
    print(tfidf.compare_transforms(t1, t2))
    print(tfidf.compare_transforms(t1, t1))
    print(tfidf.compare_transforms(t2, t1))
    print(tfidf.compare_transforms(t2, t2))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test()
