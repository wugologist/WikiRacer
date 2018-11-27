from src import WikipediaApi


def determine_branching_factor(samples, api):
    """
    Determine the branching factor of Wikipedia articles through random sampling
    :param samples: The number of random articles to sample
    :param api: The API class to use (online or local)
    :return: The average number of links per article sampled
    """
    wiki_api = api()
    link_total = 0
    for i in range(samples):
        links = len(wiki_api.get_random_text_and_links()[1])
        link_total += links
    return link_total / samples


if __name__ == "__main__":
    print(determine_branching_factor(1000, WikipediaApi.WikipediaApi))
