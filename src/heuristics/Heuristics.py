from src import WikipediaApi
from src.heuristics import TFIDF


def null_heuristic(node, start, goal, content, neighbors):
    return 0


def bfs_heuristic(node, start, goal, content, neighbors):
    return 1


def shortcut_bfs_heuristic(node, start, goal, content, neighbors):
    return -float("inf") if node == goal else 1


def dfs_heuristic(node, start, goal, content, neighbors):
    return -1


def shortcut_dfs_heuristic(node, start, goal, content, neighbors):
    return -float("inf") if node == goal else -1


def tfidf_heuristic(node, start, goal, content, neighbors):
    return Tfidf.get_instance(goal, "corpera/1000.txt").get_heuristic_value(node)


class Tfidf:
    instance = None

    def __init__(self, goal, corpus_filename):
        self.tfidf = TFIDF.Tfidf(corpus_filename)
        goal_text = WikipediaApi.WikipediaApi().get_text_and_links(goal)[0]
        self.goal_transform = self.tfidf.get_transform(goal_text)

    @staticmethod
    def get_instance(goal, corpus_filename):
        if Tfidf.instance is None:
            instance = Tfidf(goal, corpus_filename)
        return instance

    def get_heuristic_value(self, node):
        node_text = WikipediaApi.WikipediaApi().get_text_and_links(node)[0]
        node_transform = self.tfidf.get_transform(node_text)
        return self.tfidf.compare_transforms(node_transform, self.goal_transform)
