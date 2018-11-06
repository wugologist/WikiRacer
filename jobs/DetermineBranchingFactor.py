from src import WikipediaApi


def determine_branching_factor(samples):
    """
    Determine the branching factor of Wikipedia articles through random sampling
    :param samples: The number of random articles to sample
    :return: The average number of links per article sampled
    """
    wiki_api = WikipediaApi.WikipediaApi()
    link_total = 0
    for i in range(samples):
        links = len(wiki_api.get_random_text_and_links()[1])
        link_total += links
    return link_total / samples


if __name__ == "__main__":
    print(determine_branching_factor(10))
