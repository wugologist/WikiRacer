import Search
import WikipediaApi


class WikiAgent:
    def __init__(self):
        self.wikipedia_api = WikipediaApi.WikipediaApi()

    def search(self, start, end, heuristic):
        search = Search.Search(self.wikipedia_api.get_text_and_links,
                               heuristic)
        return search.a_star(start, end)
