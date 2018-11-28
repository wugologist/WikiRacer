import csv
import datetime
import os

from apis import WikipediaApi
from src import HeuristicTester
from src.heuristics import Heuristics

test_file_path = "tests.txt"

api = WikipediaApi.WikipediaApi()
heuristics = [Heuristics.BfsHeuristic(), Heuristics.DfsHeuristic()]


def run_tests():
    tests = []

    with open(test_file_path, "r") as test_file:
        for line in test_file:
            if not line.startswith("#"):
                parts = line.rstrip().split("|")
                tests.append((parts[0], parts[1]))

    if not os.path.exists("../results/"):
        os.makedirs("../results/")
    results_file_path = "../results/{}.tsv".format(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))

    with open(results_file_path, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t',)
        writer.writerow(["start", "goal", "heuristic", "time_seconds", "nodes_expanded", "path_length", "path"])
        for test in tests:
            start, goal = test
            writer.writerows(run_one_test(start, goal))


def run_one_test(start, goal):
    res = HeuristicTester.HeuristicTester.compare_heuristics(start, goal, api, heuristics)
    ans_list = []
    for r in res:
        row = [start, goal, r["heuristic"], r["time_seconds"], r["nodes_expanded"], r["path_length"], r["path"]]
        row = map(str, row)
        ans_list.append(row)
    return ans_list


if __name__ == "__main__":
    run_tests()
