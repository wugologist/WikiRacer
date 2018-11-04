import argparse
import datetime
import logging
import os
import sys

import HeuristicTester
import Heuristics
import WikipediaApi

log = logging.getLogger(__name__)


def parse(argv):
    parser = argparse.ArgumentParser(description="Find a path between Wikipedia pages with the given heuristic",
                                     prog=argv[0])
    parser.add_argument("start", help="The starting article name")
    parser.add_argument("goal", help="The goal page name")
    parser.add_argument("--heuristic", help="The heuristic function to use (from Heuristics.py)")
    parser.add_argument("--quiet", "-q", help="Create fewer log messages", action="count")
    parser.add_argument("--only-console", help="Log to only the console", action="store_true")
    parser.add_argument("--only-file", help="Log to only a file", action="store_true")

    return parser.parse_args(argv[1:])


def initialize_logger(arguments):
    format = '%(asctime)-15s %(levelname)s %(name)s: %(message)s'
    levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR]
    level = levels[min(arguments.quiet, len(levels))] if arguments.quiet else 0

    handlers = []

    if not arguments.only_console:
        filename = "logs/{}.log".format(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        handlers.append(logging.FileHandler(filename))

    if not arguments.only_console:
        handlers.append(logging.StreamHandler(sys.stdout))

    logging.basicConfig(
        format=format,
        level=level,
        handlers=handlers)


def run_search(arguments):
    heuristic = getattr(Heuristics, arguments.heuristic, None)
    if heuristic is None:
        log.error("{} is not a valid heuristic. Options: {}"
                  .format(arguments.heuristic,
                          list(filter(lambda x: x[0] != "_", dir(Heuristics)))))  # filter out dunder methods

    api = WikipediaApi.WikipediaApi()
    start = api.get_canonical_name(arguments.start)
    goal = api.get_canonical_name(arguments.goal)
    HeuristicTester.HeuristicTester.compare_heuristics(start, goal, heuristic)


if __name__ == "__main__":
    args = parse(sys.argv)
    initialize_logger(args)
    run_search(args)
