import abc


class AbstractHeuristic(abc.ABC):
    """
    An abstract heuristic class. All heuristic classes should inherit this class.
    """

    def setup(self, api, start, goal):
        """
        Called when the search is started. Put any preprocessing or setup here.
        """
        pass

    def preprocess_neighbors(self, neighbors):
        """
        Called when the neighbors of a node are found. Can do bulk/parallel processing here.
        :param neighbors: A list of neighbor nodes
        """
        pass

    @abc.abstractmethod
    def calculate_heuristic(self, node):
        """
        Calculate the heuristic value for a node
        :param node: The name of the node
        :param content: Any data for the node (e.g. text)
        :return: An integer. Lower heuristic values should be closer to the goal node.
        """
        pass


# Some trivial heuristics #


class NullHeuristic(AbstractHeuristic):
    def calculate_heuristic(self, node):
        return 0


class BfsHeuristic(AbstractHeuristic):
    def __init__(self):
        self.goal = None

    def setup(self, api, start, goal):
        self.goal = goal

    def calculate_heuristic(self, node):
        return -float("inf") if node == self.goal else 1


class DfsHeuristic(AbstractHeuristic):
    def __init__(self):
        self.goal = None

    def setup(self, api, start, goal):
        self.goal = goal

    def calculate_heuristic(self, node):
        return -float("inf") if node == self.goal else -1
