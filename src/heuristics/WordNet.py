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

    def get_synsets(self, word):
        """
        Get synsets for a word.
        If the word has a WordNet node, return it's own synsets.
        If the word doesn't, return all the synsets of it's neighbors.
        """
        word_synsets = wordnet.synsets(word)
        if word_synsets:
            return [word_synsets[0]]
        try:
            neighbors = self.api.get_text_and_links(word)[1]
            return list(flatmap(self.get_first_synset, neighbors))
        except OSError:
            return []

    def setup(self, api, start, goal):
        log.info("Initializing WordNet heuristic")
        # Ensure that we have the WordNet corpus
        # This will download the corpus on the first run, but not on subsequent runs
        nltk.download('wordnet')
        self.api = api
        self.goal = goal
        self.goal_synsets = self.get_synsets(goal)
        if not self.goal_synsets:
            log.error("Unable to get synsets for goal node! Node: {}".format(goal))
            raise Error("Goal and all goal's neighbors are not WordNet compatible")

    def calculate_heuristic(self, node):
        # log.debug("Calculating heuristic for {}".format(node))
        node_synsets = self.get_synsets(node)
        if not node_synsets:
            # log.warn("Unable to get synsets for {}".format(node))
            return float("inf")
        potential_pairs = list(itertools.product(self.goal_synsets, node_synsets))
        return min(map(lambda pair: 1 - (pair[0].path_similarity(pair[1]) or 0), potential_pairs))
