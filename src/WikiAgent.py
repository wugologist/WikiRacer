import Search


class WikiAgent:
    def __init__(self, api):
        self.api = api

    def search(self, start, end, heuristic):
        search = Search.Search(self.api,
                               heuristic)
        return search.a_star(start, end)
