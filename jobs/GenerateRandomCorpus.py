import argparse
import logging
import os
import sys
import time

from src import WikipediaApi

log = logging.getLogger(__name__)


def generate_random_corpus(count, filename):
    """
    Create a text file of random Wikipedia summaries
    """
    corpera_path = "../corpera/"
    if filename is None:
        if not os.path.isdir(corpera_path):
            os.makedirs(corpera_path)
        f = corpera_path + str(count)
        if not os.path.isfile(f + ".txt"):
            filename = f + ".txt"
        else:
            i = 1
            test_filename = f + "_{}.txt"
            while os.path.isfile(test_filename.format(i)):
                i += 1
            filename = test_filename.format(i)
        log.info("No path specified, using " + filename)

    wiki = WikipediaApi.WikipediaApi()
    text = []
    log.info("Generating corpus of {} random articles".format(count))
    ts = time.time()
    for i in range(count):
        text.append(wiki.get_random_text_and_links()[0].replace("\n", " "))

    with open(filename, "w", encoding="utf-8") as file:
        file.write("\n".join(text))
    log.info("Generated {} in {} seconds".format(filename, time.time() - ts))


def parse_arguments(argv):
    parser = argparse.ArgumentParser(description="Create a text file of random Wikipedia pages' text.",
                                     prog=argv[0])
    parser.add_argument("count", type=int, help="How many articles to include")
    parser.add_argument("--filename", "-f", help="Name of file to save corpus to")
    args = parser.parse_args(argv[1:])
    return args.count, args.filename


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    count, filename = parse_arguments(sys.argv)
    generate_random_corpus(count, filename)
