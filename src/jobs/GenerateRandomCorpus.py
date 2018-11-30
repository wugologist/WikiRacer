import argparse
import logging
import os
import time
from typing import List

from apis import AWikiApi, WikipediaApi, LocalApi
from jobs.AbstractJob import AbstractJob

log = logging.getLogger(__name__)


class GenerateRandomCorpus(AbstractJob):
    apis = {"web": WikipediaApi.WikipediaApi,
            "local": LocalApi.LocalWikipediaApi}

    def __init__(self):
        self.api: AWikiApi = None

    def run(self, args: List[str]) -> None:
        count, filename, api = self.parse_arguments(args)
        self.api = self.apis[api]()
        self.generate_random_corpus(count, filename)

    def generate_random_corpus(self, count, filename):
        """
        Create a text file of random Wikipedia summaries
        """
        corpora_path = "../../corpora/"
        if filename is None:
            if not os.path.isdir(corpora_path):
                os.makedirs(corpora_path)
            f = corpora_path + str(count)
            if not os.path.isfile(f + ".txt"):
                filename = f + ".txt"
            else:
                i = 1
                test_filename = f + "_{}.txt"
                while os.path.isfile(test_filename.format(i)):
                    i += 1
                filename = test_filename.format(i)
            log.info("No path specified, using " + filename)

        text = []
        log.info("Generating corpus of {} random articles".format(count))
        ts = time.time()
        for i in range(count):
            text.append(self.api.get_random_text_and_links()[0].replace("\n", " "))

        with open(filename, "w", encoding="utf-8") as file:
            file.write("\n".join(text))
        log.info("Generated {} in {} seconds".format(filename, time.time() - ts))

    def parse_arguments(self, argv):
        parser = argparse.ArgumentParser(description="Create a text file of random Wikipedia pages' text.",
                                         prog=argv[0])
        parser.add_argument("count", type=int, help="How many articles to include")
        parser.add_argument("api", help="Whether to use the web or local Wikipedia API", choices=self.apis.keys())
        parser.add_argument("--filename", "-f", help="Name of file to save corpus to")
        args = parser.parse_args(argv[1:])
        return args.count, args.filename, args.api
