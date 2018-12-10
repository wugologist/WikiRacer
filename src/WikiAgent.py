import Search


class WikiAgent:
    def __init__(self, api):
        self.api = api

    def search(self, start, end, heuristic, greedy):
        search = Search.Search(self.api,
                               heuristic)
        return search.greedy(start, end) if greedy else search.a_star(start, end)
