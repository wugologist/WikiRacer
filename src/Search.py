import logging
from queue import PriorityQueue

from heuristics.Heuristics import AbstractHeuristic

log = logging.getLogger(__name__)


class Search:
    def __init__(self, api, heuristic: AbstractHeuristic):
        self.api = api
        self.heuristic = heuristic

    def a_star(self, start, goal):
        nodes_expanded = 0
        priority_queue = PriorityQueue()
        visited = set()
        # set up heuristic
        self.heuristic.setup(self.api, start, goal)
        # items in the queue are (cost, path, data) tuples
        priority_queue.put((0, [start], start))
        while not priority_queue.empty():
            cost, path, node = priority_queue.get()
            if node in visited:
                continue
            visited.add(node)
            if node == goal:
                return path, nodes_expanded
            if not self.api.is_valid_article(node):
                continue
            content, neighbors = self.api.get_text_and_links(node)
            nodes_expanded += 1
            log.debug("Got {} neighbors for {}: {}".format(len(neighbors),
                                                           node,
                                                           path if len(path) < 10 else path[0:5] + ["..."] + path[-5:]))
            # do any bulk preprocessing of neighbor nodes
            self.heuristic.preprocess_neighbors(neighbors)
            for neighbor in neighbors:
                if neighbor not in visited:
                    heuristic_value = self.heuristic.calculate_heuristic(neighbor)
                    priority_queue.put((cost + heuristic_value, path + [neighbor], neighbor))
        log.warning("No path found between {}  and {}!".format(start, goal))
        return [], nodes_expanded  # no path found
