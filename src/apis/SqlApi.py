#!/usr/bin/env python3

import logging
import sqlalchemy
from sqlalchemy.sql import text
import mwparserfromhell
from titlecase import titlecase
from .AWikiApi import AWikiApi
import itertools
import functools

log = logging.getLogger(__name__)

class SqlWikipediaApi(AWikiApi):
    """
    An API for accessing Wikipedia articles from a SQL database.
    Default arguments will connect to localhost over IPv4 on the standard port and sign in with user wikiracers and password wikiracers.
    """

    def __init__(self, db_host="127.0.0.1", db_port=3306, db_username="wikiracers", db_password="wikiracers"):
        self.db_host = db_host
        self.db_port = db_port
        self.db_username = db_username
        self.db_password = db_password
        
    def load(self):
        """
        Loads the index file into memory.
        Will potentially block the main thread for a little under a minute.
        Must be called before using this API.
        """
        self.connection = sqlalchemy.create_engine('mysql://{}:{}@{}:{}/wiki?charset=utf8'.format(self.db_username, self.db_password, self.db_host, self.db_port))
        self.connection.execute('SET NAMES utf8;')
        self.connection.execute('SET CHARACTER SET utf8;')
        self.connection.execute('SET character_set_connection=utf8;')

    def get_page_wikitext(self, title):
        """
        Get the wikitext for a given page
        """
        title = title.replace(" ", "_")
        statement = text("""SELECT text.old_text
                              FROM text
                              JOIN revision ON revision.rev_text_id = text.old_id
                              JOIN page ON page.page_latest = revision.rev_id 
                              WHERE page.page_namespace = 0
                              AND page.page_title = :title""")
        response = self.connection.execute(statement, title=title).fetchone()
        return (response and response[0].decode("utf-8")) or ""

    def get_parsed_page(self, title):
        """
        Return the mwparserfromhell parsed page for the given title
        """
        return mwparserfromhell.parse(self.get_page_wikitext(title))

    def page_exists(self, title):
        """
        Return True IFF the page exists
        """
        return self.get_page_wikitext(title) != ""

    def is_redirect_page(self, title):
        """
        Returns True IFF the page is a redirect page

        From Wikipedia (https://en.wikipedia.org/wiki/Help:Redirect):
        A page is treated as a redirect page if its wikitext begins with #REDIRECT followed by a valid wikilink or interwikilink. 
        A space is usually left before the link. (Note that some alternative capitalizations of "REDIRECT" are possible.)
        """
        return "#redirect" in self.get_page_wikitext(title).lower()

    def get_redirect_target(self, title):
        """
        Returns the target of a wikipedia redirect page. This is the target of the first link on the page.

        From Wikipedia:
        A page is treated as a redirect page if its wikitext begins with #REDIRECT followed by a valid wikilink or interwikilink. 
        A space is usually left before the link. (Note that some alternative capitalizations of "REDIRECT" are possible.)
        """
        parsed = self.get_parsed_page(title)
        links = parsed.ifilter_wikilinks(recursive=False) # We don't need recursion here since the redirect must be the first thing on the page
        link = list(itertools.islice(links, 1))[0] # Weird syntax because links is a generator and it's not trivial to get the first element of a generator
        link_target = link.title.strip_code().split("#")[0]
        return link_target

    def get_random_page(self):
        """
        Return a random page
        """

        # ORDER BY RAND() is not a good way to do this, but there isn't anything else really quick to implement.
        # FIXME, This is slow, but we can fix it later if we really need it optimized.
        statement = text("""SELECT page.page_title
                              FROM page
                              WHERE page.page_namespace = 0
                              ORDER BY RAND()
                              LIMIT 1""")
        return self.connection.execute(statement).fetchone()[0]

    def get_summaries(self, titles):
        """
        Bulk fetch summaries for a list of titles
        :param titles: A list of article titles
        :return: A dict of titles to summary strings

        Follows redirects

        For now, the sql wikipedia api just returns the entire page. :bee: :change:
        """
        return {title: self.get_text_and_links(title)[0] for title in titles}

    def make_canonical(self, links):
        """
        For every link in links, if the link is valid, return it's canonical name, otherwise don't include it in the resultant set.
        """
        canonical_links = set()
        for link in links:
            canonical_name = self.get_canonical_name(link)
            if canonical_name:
                canonical_links.add(canonical_name)
        return canonical_links

    def get_text_and_links(self, title):
        """
        Return a tuple of (article text, link targets)

        Follows redirects
        """
        parsed = self.get_parsed_page(title)
        text = parsed.strip_code()
        # Exclude any links which would result in an empty target
        links = parsed.ifilter_wikilinks(recursive=True, matches=lambda node: node.title.strip_code().split("#")[0].strip() != "")
        unique_links = set([link.title.strip_code().split("#")[0] for link in links])
        return text, self.make_canonical(unique_links)

    def get_name_variants(self, title):
        """
        Get potential variants for a title

        Eg, on input: A joUrNey tO WonderLAND
        - capitalcase: A journey to wonderland
        - accurate titlecase: A Journey to Wonderland
        - naive titlecase: A Journey To Wonderland
        - lowercase: a journey to wonderland
        - uppercase: A JOURNEY TO WONDERLAND

        Returns a list of the variants
        """
        return [title.capitalize(), titlecase(title), title.title(), title.lower(), title.upper()]

    def get_canonical_name_helper(self, title, try_naming_variants=True, blacklist=[]):
        """
        Get the official name of an article. Useful because we just check string equality for the goal test,
        so we don't want to skip over the goal if e.g. the capitalization is off
        :return: The canonical name of the given page

        If try_naming_variants is true, attempt to try other capitalizations of the name.
        This should be on most times, but not when we recur during the process of autocapitalization.

        This is the uncached version because it needs to keep track of a blacklist (which can't be cached)

        Cases:
        - The article name is correct
            - Use the article title as is
        - The article is a redirection page
            - Recursively call get_canonical_name_helper on the redirect target
        - The article doesn't exist
            - Attempt to perform auto capitalization on the title to see if any of those pages exist, in which case recur on them
            - If all fails, return None
        """
        title = title.replace("_", " ")
        if title in blacklist:
            return None
        if self.page_exists(title):
            if self.is_redirect_page(title):
                return self.get_canonical_name_helper(self.get_redirect_target(title), blacklist=blacklist + [title])
            else:
                return title
        else:
            if try_naming_variants:
                for variant in self.get_name_variants(title):
                    variant_canonical_name = self.get_canonical_name_helper(variant, try_naming_variants=False, blacklist=blacklist + [title]);
                    if variant_canonical_name:
                        return variant_canonical_name
            return None

    @functools.lru_cache(maxsize=1024)
    def get_canonical_name(self, title):
        """
        A cacheable version of get_canonical_name_helper.
        Just defers to get_canonical_name_helper for cache misses.
        """
        return self.get_canonical_name_helper(title)

if __name__ == "__main__":
    api = SqlWikipediaApi();
    api.load();
    # print("Canonical name of \"programming language\" is:", api.get_canonical_name("programming language"))
    # print("Validness of \"Mona Singh\" is:", api.is_valid_article("Mona Singh"))
    # links = api.get_text_and_links("Mona Singh")[1]
    # print("Links of \"Mona Singh\" are:", links)
    # for link in links:
        # print("Validness of link \"{}\" is:".format(link), api.is_valid_article(link))
    # print("Canonical name of \"uK\" is:", api.get_canonical_name("uK"))
    print("Canonical name of \"bat\" is:", api.get_canonical_name("bat"))
    # print("Text and links of \"uK\" is:", api.get_text_and_links("uK"))
    print("Here are a few random page titles:")
    print(api.get_random_page())
    print(api.get_random_page())
    print(api.get_random_page())
    # print("Get summaries of [\"A\", \"B\", \"Water\"] returns:", api.get_summaries(["A", "B", "Water"]))