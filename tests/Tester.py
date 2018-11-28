import csv

from apis import WikipediaApi
from src import HeuristicTester
from src.heuristics import Heuristics

test_file_path = "tests.txt"
results_file_path = "results.tsv"

heuristics = [Heuristics.BfsHeuristic, Heuristics.DfsHeuristic]


def run_tests():
    tests = []

    with open(test_file_path, "r") as test_file:
        for line in test_file:
            if not line.startswith("#"):
                parts = line.rstrip().split("|")
                tests.append((parts[0], parts[1]))

    with open('results.tsv', 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t',)
        writer.writerow(["start", "goal", "heuristic", "time_seconds", "nodes_expanded", "path_length", "path"])
        for test in tests:
            start, goal = test
            writer.writerows(run_one_test(start, goal))


def run_one_test(start, goal):
    res = HeuristicTester.HeuristicTester.compare_heuristics(start, goal, WikipediaApi.WikipediaApi, heuristics)
    ans_list = []
    for r in res:
        ans_list.append(
            [start, goal, r["heuristic"], str(r["time_seconds"]), str(r["nodes_expanded"]), str(r["path_length"]),
             str(r["path"])])
    return ans_list


if __name__ == "__main__":
    run_tests()
