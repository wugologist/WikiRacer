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
        stemmer = PorterStemmer()
        stems = []
        for item in tokens:
            stems.append(stemmer.stem(item))
        return stems

    def get_transform(self, document):
        return self.model.transform([document])

    def extract_top_terms(self, transform, limit=None):
        feature_names = self.model.get_feature_names()
        terms = [(feature_names[term], transform[0, term]) for term in transform.nonzero()[1]]
        sorted_terms = sorted(terms, key=lambda t: t[1], reverse=True)
        return sorted_terms[:limit + 1] if limit is not None else sorted_terms

    def compare_transforms(self, node_transform, goal_transform, max_terms=5):
        """
        Calculate the similarity between two transform matrices
        """
        goal_terms = self.extract_top_terms(goal_transform, max_terms)
        feature_names = self.model.get_feature_names()
        node_features = {feature_names[term]: node_transform[0, term] for term in node_transform.nonzero()[1]}
        node_words = {feature_names[term] for term in node_transform.nonzero()[1]}

        difference = 0
        for i, term in enumerate(goal_terms):
            difference += abs((goal_terms[i][1] - node_features[term[0]]) / (i + 1)) \
                if term[0] in node_words \
                else goal_terms[i][1]

        return difference


class TfidfHeuristic(AbstractHeuristic):
    def __init__(self, corpus_filename, keyword_limit=5):
        self.api = None
        self.tfidf = None
        self.goal_transform = None
        self.corpus_filename = corpus_filename
        self.keyword_limit = keyword_limit
        self.summaries = dict()

    def setup(self, api, start, goal):
        log.info("Initializing TFIDF heuristic")
        self.api = api
        self.tfidf = Tfidf()
        self.tfidf.setup(self.corpus_filename)
        # goal_text = self.api.get_text_and_links(goal)[0]
        goal_text = self.api.get_summaries([goal])[goal]
        self.goal_transform = self.tfidf.get_transform(goal_text)
        log.info("Top {} keywords for goal article {}: {}".format(self.keyword_limit,
                                                                  goal,
                                                                  self.tfidf.extract_top_terms(self.goal_transform,
                                                                                               self.keyword_limit)))

    def preprocess_neighbors(self, neighbors):
        self.summaries.update(self.api.get_summaries(neighbors))

    def calculate_heuristic(self, node):
        # node_text = self.api.get_text_and_links(node)[0]
        node_text = self.summaries[node]
        node_transform = self.tfidf.get_transform(node_text)
        return self.tfidf.compare_transforms(node_transform, self.goal_transform)
