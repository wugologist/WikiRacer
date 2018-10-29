import argparse
import datetime
import logging
import os
import sys

import Heuristics
import HeuristicTester

log = logging.getLogger(__name__)


def parse(argv):
    parser = argparse.ArgumentParser(description="Find a path between Wikipedia pages with the given heuristic",
                                     prog=argv[0])
    parser.add_argument("start", help="The starting article name")
    parser.add_argument("goal", help="The goal page name")
    parser.add_argument("--heuristic", help="The heuristic function to use (from Heuristics.py)")
    parser.add_argument("--quiet", "-q", help="Create fewer log messages", action="count")
    parser.add_argument("--nolog", "-n", help="Log to console instead of file", action="store_true")

    return parser.parse_args(argv[1:])


def initialize_logger(arguments):
    format = '%(asctime)-15s %(levelname)s %(name)s: %(message)s'
    levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR]
    level = levels[min(arguments.quiet, len(levels))] if arguments.quiet else 0

    if arguments.nolog:
        logging.basicConfig(
            format=format,
            level=level)
    else:
        if not os.path.exists("logs/"):
            os.makedirs("logs/")

        logging.basicConfig(
            format=format,
            level=level,
            filename="logs/{}.log".format(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")),
            filemode="a")


def run_search(arguments):
    heuristic = getattr(Heuristics, arguments.heuristic, None)
    if heuristic is None:
        log.error("{} is not a valid heuristic. Options: {}"
                  .format(arguments.heuristic,
                          list(filter(lambda x: x[0] != "_", dir(Heuristics)))))  # filter out dunder methods

    HeuristicTester.HeuristicTester.compare_heuristics(arguments.start, arguments.goal, heuristic)


if __name__ == "__main__":
    args = parse(sys.argv)
    initialize_logger(args)
    run_search(args)
