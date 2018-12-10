import argparse
import string
from typing import List

import nltk
from gensim.models import Doc2Vec
from gensim.models.doc2vec import TaggedDocument
from nltk.corpus import stopwords

from jobs.AbstractJob import AbstractJob


class TrainDoc2Vec(AbstractJob):

    def run(self, args: List[str]) -> None:
        corpus_location, out, clean = self.parse_arguments(args)
        self.train_doc2vec(corpus_location, out, clean)

    @staticmethod
    def train_doc2vec(corpus_filename, model_filename, clean):
        with open("../../corpora/" + corpus_filename, "r", encoding="utf8") as corpus:
            lines = [l.strip() for l in corpus.readlines()]
        if clean:
            sw = set(stopwords.words('english'))
            cleaned_lines = []
            stemmer = nltk.PorterStemmer()
            for line in lines:
                tokens = nltk.word_tokenize(line)
                cleaned_tokens = [stemmer.stem(token.lower()) for token in tokens if token.lower() not in sw
                                  and token not in string.punctuation]
                cleaned_line = " ".join(cleaned_tokens)
                cleaned_lines.append(cleaned_line)
            lines = cleaned_lines
        documents = [TaggedDocument(doc, [i]) for i, doc in enumerate(lines)]
        model = Doc2Vec(documents, vector_size=5, window=2, min_count=1, workers=4, epochs=10)
        model.save("../../models/" + model_filename)
        model.delete_temporary_training_data(keep_doctags_vectors=True, keep_inference=True)

    @staticmethod
    def parse_arguments(argv):
        parser = argparse.ArgumentParser(description="Train a doc2vec model.",
                                         prog=argv[0])
        parser.add_argument("--corpus", "-i", help="The name of the corpus file, located in /corpora.")
        parser.add_argument("--model", "-o",
                            help="The name of the file to save the model to, it will be located in /models.")
        parser.add_argument("--clean", "-c", type=bool, help="Whether or not to remove stopwords from the corpus.")
        args = parser.parse_args(argv[1:])
        return args.corpus, args.model, args.clean
