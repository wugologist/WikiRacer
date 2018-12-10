import logging
from queue import PriorityQueue

from heuristics.Heuristics import AbstractHeuristic

log = logging.getLogger(__name__)


class Search:
    def __init__(self, api, heuristic: AbstractHeuristic):
        self.api = api
        self.heuristic = heuristic

    def a_star(self, start, goal):
        return self.generic_search(start, goal, True)

    def greedy(self, start, goal):
        return self.generic_search(start, goal, False)

    def generic_search(self, start, goal, use_cost):
        nodes_expanded = 0
        priority_queue = PriorityQueue()
        visited = set()
        # set up heuristic
        self.heuristic.setup(self.api, start, goal)
        # items in the queue are (cost, path, node) tuples
        priority_queue.put((0, [start], start))
        while not priority_queue.empty():
            cost, path, node = priority_queue.get()
            if node in visited:
                continue
            visited.add(node)
            if api.is_same_node(node, goal):
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
                    weight = cost + heuristic_value if use_cost else heuristic_value
                    priority_queue.put((weight, path + [neighbor], neighbor))
        log.warning("No path found between {}  and {}!".format(start, goal))
        return [], nodes_expanded  # no path found
