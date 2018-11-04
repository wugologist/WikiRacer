import WikipediaApi


def determine_branching_factor(samples=1000):
    """
    Determine the branching factor of Wikipedia articles through random sampling
    :param samples: The number of random articles to sample
    :return: The average number of links per article sampled
    """
    wikiApi = WikipediaApi.WikipediaApi()
    link_total = 0
    for i in range(samples):
        page = wikiApi.get_random_page()
        title = page.url.split("/")[-1]
        print(title)
        links = len(wikiApi.get_text_and_links(title)[1])
        link_total += links
    return link_total / samples


if __name__ == "__main__":
    print(determine_branching_factor(1000))
