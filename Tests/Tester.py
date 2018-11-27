import datetime

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

    with open(results_file_path, "w") as results_file:
        results_file.write("start\tgoal\theuristic\ttime_seconds\tnodes_expanded\tpath_length\tpath\n")

        for test in tests:
            start, goal = test
            # results_file.write("Start: " + start + ", Goal: " + goal + "\n")
            results_file.writelines(run_one_test(start, goal))
            # results_file.write("\n")
        results_file.write(str(datetime.datetime.now()))  # do we want a timestamp? where should it go?




def run_one_test(start, goal):
    res = HeuristicTester.HeuristicTester.compare_heuristics(start, goal, heuristics)
    ans_list = []
    for r in res:
        line = [start, goal, r["heuristic"], str(r["time_seconds"]), str(r["nodes_expanded"]), str(r["path_length"]), str(r["path"])]
        ans_list.append("\t".join(line) + "\n")
    return ans_list


if __name__ == "__main__":
    run_tests()
