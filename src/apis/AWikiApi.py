import abc


class AWikiApi(abc.ABC):
    """
    Abstract Class for Wikipedia APIs
    """

    def load(self):
        """
        Does whatever loading the API need to do. This method is expected to potentially take some time.
        By default does nothing, but can be overridden if the subclass needs to do some set up.
        """
        pass

    def is_valid_article(self, title):
        """
        Return True IFF the page has a canonical name.
        
        TODO This should be memoized which would improve performance a ton.
        """
        try:
            self.get_canonical_name(title)
            return True
        except IOError:
            return False

    def get_random_page(self):
        """
        Return a random page
        """
        raise Error("Method not implemented")

    def get_summaries(self, titles):
        """
        Bulk fetch summaries for a list of titles

        Follows redirects

        :param titles: A list of article titles
        :return: A dict of titles to summary strings
        """
        raise Error("Method not implemented")

    def is_same_node(self, title1, title2):
        """
        Returns true IFF title1 and title2 refer to the same article.

        Default implementation compares them based on the canonical name.
        If an API can guarantee that it will always return the article titles
        in their canonical form, it can override this behavior with simple string equality.
        """
        return self.get_canonical_name(title1) == self.get_canonical_name(title2)

    @abc.abstractmethod
    def get_text_and_links(self, title):
        """
        Return a tuple of (article text, link targets)

        Follows redirects
        """
        raise Error("Method not implemented")

    @abc.abstractmethod
    def get_canonical_name(self, title):
        """
        Get the official name of an article. Useful because we just check string equality for the goal test,
        so we don't want to skip over the goal if e.g. the capitalization is off
        :return: The canonical name of the given page
        """
        raise Error("Method not implemented")