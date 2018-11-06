import argparse
import sys

from src import WikipediaApi


def generate_random_corpus(count, filename):
    """
    Create a text file of random Wikipedia summaries
    """
    wiki = WikipediaApi.WikipediaApi()
    text = []
    for i in range(count):
        text.append(wiki.get_random_text_and_links()[0].replace("\n", " "))

    with open(filename, "w", encoding="utf-8") as file:
        file.write("\n".join(text))


def parse_arguments(argv):
    parser = argparse.ArgumentParser(description="Create a text file of random Wikipedia pages' text.",
                                     prog=argv[0])
    parser.add_argument("count", type=int, help="How many articles to include")
    parser.add_argument("filename", help="Name of file to save corpus to")
    args = parser.parse_args(argv[1:])
    return args.count, args.filename


if __name__ == "__main__":
    count, filename = parse_arguments(sys.argv)
    generate_random_corpus(count, filename)
