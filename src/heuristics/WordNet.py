import logging

from nltk.corpus import wordnet
import nltk
import itertools

from heuristics.Heuristics import AbstractHeuristic

log = logging.getLogger(__name__)

# Source: https://stackoverflow.com/a/20037408/1556343
def flatmap(func, *iterable):
    return itertools.chain.from_iterable(map(func, *iterable))

class WordNetHeuristic(AbstractHeuristic):
    def __init__(self):
        self.wordNet = None
        self.api = None
        self.goal = None
        self.goal_synsets = None

    def get_first_synset(self, word):
        word_synsets = wordnet.synsets(word)
        if not word_synsets:
            return []
        return [word_synsets[0]]

    def link_exists(self, from_title, to_title):
        """
        Using the API, check if a title exists from the from_title article to the to_title article
        """
        return to_title in self.api.get_text_and_links(from_title)[1]

    def get_synsets(self, word, allow_neighbors=False, require_symmetric=False):
        """
        Get synsets for a word.
        If the word has a WordNet node, return it's own synsets.
        If require_symmetric=True, then ensure that neighbors have a symmetric edge with the article.
        """
        word_synsets = wordnet.synsets(word)
        if word_synsets:
            return [word_synsets[0]]
        if allow_neighbors:
            neighbors = self.api.get_text_and_links(word)[1]
            if require_symmetric:
                neighbors = filter(lambda article: self.link_exists(article, self.goal), neighbors)
            return list(flatmap(self.get_first_synset, neighbors))
        return []

    def setup(self, api, start, goal):
        log.info("Initializing WordNet heuristic")
        # Ensure that we have the WordNet corpus
        # This will download the corpus on the first run, but not on subsequent runs
        nltk.download('wordnet')
        self.api = api
        self.goal = goal
        # require_symmetric=True because it's important for synsets that we target
        # to either be the goal or have a direct link to the goal
        self.goal_synsets = self.get_synsets(goal, allow_neighbors=True, require_symmetric=True)
        if not self.goal_synsets:
            log.error("Unable to get synsets for goal node! Node: {}".format(goal))
            raise OSError("Goal and all goal's neighbors are not WordNet compatible")

    def calculate_heuristic(self, node):
        if node == self.goal:
            return 0
        node_synsets = self.get_synsets(node)
        if not node_synsets:
            return float("inf")
        potential_pairs = list(itertools.product(self.goal_synsets, node_synsets))
        # We reserve the heuristic of 0 for the goal, all other heuristics must have a value of at least 0.1
        # This way, if the goal doesn't have a synset, but we're going to a neighbor of the goal,
        # that neighbor still has a non-zero value and the true goal is prioritized once we reach the neighbor.
        return 0.1 + min(map(lambda pair: 1 - (pair[0].path_similarity(pair[1]) or 0), potential_pairs))
