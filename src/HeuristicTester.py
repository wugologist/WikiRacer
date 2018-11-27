import logging
import pprint
import time

from src import WikiAgent
from typing import List
from src.heuristics.Heuristics import *

log = logging.getLogger(__name__)


class HeuristicTester:
    @staticmethod
    def compare_heuristics(start, stop, heuristics: List[AbstractHeuristic]):
        agent = WikiAgent.WikiAgent()
        results = []
        for heuristic in heuristics:
            log.info("Testing heuristic {} with start {} and end {}"
                     .format(type(heuristic).__name__, start, stop))
            start_time = time.time()
            path, expanded_count = agent.search(start, stop, heuristic)
            search_time = time.time() - start_time
            log.info("Found path of length {} in {} seconds with {} expansions: {}"
                     .format(len(path),
                             search_time,
                             expanded_count,
                             path if len(path) < 10 else path[0:5] + ["..."] + path[-5:]))
            results.append(
                {
                    "heuristic": type(heuristic).__name__,
                    "time_seconds": search_time,
                    "path_length": len(path),
                    "nodes_expanded": expanded_count,
                    "path": path if len(path) < 10 else path[0:5] + ["..."] + path[-5:]
                }
            )
            log.info(results)
        return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    results = HeuristicTester.compare_heuristics(
        "Fraser_Canyon_Gold_Rush",
        "British_Empire",
        [
            DfsHeuristic(),
            BfsHeuristic()
        ]
    )
    pprint.pprint(results)
