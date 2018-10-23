import time

import WikiAgent
from Heuristics import *


class HeuristicTester:
    @staticmethod
    def compare_heuristics(start, stop, *args):
        agent = WikiAgent.WikiAgent()
        for heuristic in args:
            print("testing heuristic {} with start {} and end {}"
                  .format(heuristic.__name__, start, stop))
            ts = time.time()
            path, expanded_count = agent.search(start, stop, heuristic)
            print("found path of length {} in {} seconds with {} expansions: {}"
                  .format(len(path), time.time() - ts, expanded_count, path if len(path) < 10 else "too long to show"))


if __name__ == "__main__":
    HeuristicTester.compare_heuristics(
        "Cattle",
        "France",
        bfs_heuristic,
        shortcut_null_heuristic,
        # null_heuristic  # takes a long time
    )
