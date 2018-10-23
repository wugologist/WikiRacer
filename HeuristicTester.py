import pprint
import time

import WikiAgent
from Heuristics import *


class HeuristicTester:
    @staticmethod
    def compare_heuristics(start, stop, *args):
        agent = WikiAgent.WikiAgent()
        results = []
        for heuristic in args:
            print("testing heuristic {} with start {} and end {}"
                  .format(heuristic.__name__, start, stop))
            start_time = time.time()
            path, expanded_count = agent.search(start, stop, heuristic)
            search_time = time.time() - start_time
            print("found path of length {} in {} seconds with {} expansions: {}"
                  .format(len(path),
                          search_time,
                          expanded_count,
                          path if len(path) < 10 else path[0:5] + ["..."] + path[-5:]))
            results.append(
                {
                    "heuristic": heuristic.__name__,
                    "time_seconds": search_time,
                    "path_length": len(path),
                    "nodes_expanded": expanded_count,
                    "path": path if len(path) < 10 else path[0:5] + ["..."] + path[-5:]
                }
            )
        return results


if __name__ == "__main__":
    results = HeuristicTester.compare_heuristics(
        "Fraser_Canyon_Gold_Rush",
        "British_Empire",
        bfs_heuristic,
        shortcut_bfs_heuristic,
        # null_heuristic  # takes a long time
    )
    pprint.pprint(results)
