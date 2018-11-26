import logging
from queue import PriorityQueue

log = logging.getLogger(__name__)


class Search:
    def __init__(self, api, heuristic):
        self.api = api
        self.heuristic = heuristic

    def a_star(self, start, goal):
        nodes_expanded = 0
        priority_queue = PriorityQueue()
        visited = set()
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
            for neighbor in neighbors:
                if neighbor not in visited:
                    heuristic = self.heuristic(neighbor, start, goal, content, neighbors)
                    priority_queue.put((cost + heuristic, path + [neighbor], neighbor))
        log.warning("No path found!")
        return [], nodes_expanded  # no path found
