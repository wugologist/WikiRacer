import datetime

from src import HeuristicTester
from src.heuristics import Heuristics

test_file_path = "tests.txt"
results_file_path = "results.txt"

heuristics = [Heuristics.BfsHeuristic, Heuristics.DfsHeuristic]


def run_tests():
    tests = []

    with open(test_file_path, "r") as test_file:
        for line in test_file:
            if not line.startswith("#"):
                parts = line.rstrip().split("|")
                tests.append((parts[0], parts[1]))

    with open(results_file_path, "w") as results_file:
        results_file.write(str(datetime.datetime.now()) + "\n\n")

        for test in tests:
            start, goal = test
            results_file.write("Start: " + start + ", Goal: " + goal + "\n")
            results_file.writelines(run_one_test(start, goal))
            results_file.write("\n")
    pass


def run_one_test(start, goal):
    res = HeuristicTester.HeuristicTester.compare_heuristics(start, goal, heuristics)
    ans_list = []
    for r in res:
        line = "Heuristic: {}, Time(in seconds): {}, Nodes expanded: {}, Path length: {}, Path: {}\n" \
            .format(r["heuristic"], r["time_seconds"], r["nodes_expanded"], r["path_length"], r["path"])
        ans_list.append(line)
    return ans_list


if __name__ == "__main__":
    run_tests()
