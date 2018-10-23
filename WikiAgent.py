import Search
import WikipediaApi
from Heuristics import *


class WikiAgent:
    def __init__(self):
        self.wikipedia_api = WikipediaApi.WikipediaApi()

    def search(self, start, end, heuristic):
        search = Search.Search(self.wikipedia_api.get_text_and_links,
                               heuristic)
        return search.a_star(start, end)


if __name__ == "__main__":
    agent = WikiAgent()
    print(agent.search("cattle", "France", null_heuristic))
