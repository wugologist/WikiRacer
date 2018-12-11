import csv
import datetime
import logging
import os

from heuristics import TFIDF, Doc2Vec, WordNet

from apis import WikipediaApi
from src import HeuristicTester
from src.heuristics import Heuristics

log = logging.getLogger(__name__)

test_file_path = "tests.txt"

api = WikipediaApi.WikipediaApi()
heuristics = [
    Heuristics.BfsHeuristic(),
    Doc2Vec.Doc2VecHeuristic(True),
    WordNet.WordNetHeuristic(),
    TFIDF.TfidfHeuristic("../corpora/1000.txt", 10)
]


def run_tests():
    tests = []

    with open(test_file_path, "r") as test_file:
        log.info("Running test file {}".format(test_file_path))
        for line in test_file:
            if not line.startswith("#"):
                parts = line.rstrip().split("|")
                tests.append((parts[0], parts[1]))

    if not os.path.exists("../results/"):
        os.makedirs("../results/")
    results_file_path = "../results/{}.tsv".format(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    log.info("Results will be stored in {}".format(results_file_path))

    with open(results_file_path, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(
            ["start", "goal", "heuristic", "greedy", "time_seconds", "nodes_expanded", "path_length", "path"])
        for test in tests:
            start, goal = test
            for row in run_one_test(start, goal):
                writer.writerow(row)
                f.flush()

def run_one_test(start, goal):
    log.info("Testing {} -> {}".format(start, goal))
    ans_list = []
    for greedy in [True, False]:
        log.info("Running search test {} {} {} {} {}".format(start, goal, api, greedy,
                                                             list(map(lambda h: type(h).__name__, heuristics))))
        try:
            for r in HeuristicTester.HeuristicTester.compare_heuristics(start, goal, api, greedy, heuristics):
                row = map(str,
                          [start, goal, r["heuristic"], r["greedy"],
                           r["time_seconds"], r["nodes_expanded"], r["path_length"], r["path"]])
                yield row
        except e:
            log.error("Error when running test... Skipping to next test case.", e)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    run_tests()
