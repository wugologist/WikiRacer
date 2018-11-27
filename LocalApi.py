#!/usr/bin/env python3

import random
import logging
import bz2
import pickle
import itertools
import xml.etree.ElementTree as xml
import mwparserfromhell
from titlecase import titlecase
from os.path import getsize
from IWikiApi import IWikiApi

log = logging.getLogger(__name__)

class WikipediaIndexFile:
    """
    A class to represent the index file provided with the data dump
    The index file is a sequence of lines, each of the form:
    BZ2_OFFSET:ARTICLE_ID:ARTICLE_TITLE

    When we read the index file, we want to keep track of the ARTICLE_TITLE and the BZ2_OFFSET.
    Articles are arranged in groups with the same BZ2_OFFSET,
    and we need to know the BZ2_OFFSET of the group and the BZ2_OFFSET of the group after.

    This allows us to take a clipping of the BZ2 file to decompress.
    """
    def __init__(self, index_file, xml_file_size):
        self.index_file = index_file
        self.xml_file_size = xml_file_size
        self.articles = {}
        self.article_titles = set()

    def manual_load(self):
        """
        Read through the index file and build up a map from article titles to tuples of the form (chunk_start, chunk_end).
        (chunk_start, chunk_end) are the bytes that you would need to extract from the xml.bz2 file to find the chunk
        containing a given page. Note that chunks may contain more than one article.

        Store the current chunk region and titles in a buffer, when we find a new chunk we know the beginning 
        and end of the previous chunk so we can add them to the dictionary.
        """
        buffer_region_start = 0
        buffer_titles = []
        with open(self.index_file, "r") as index_file:
            for line in index_file:
                [line_region_start, _id, *split_name] = line.split(":")
                line_article_name = ":".join(split_name).strip()
                if line_region_start != buffer_region_start:
                    for name in buffer_titles:
                        self.articles[name] = (int(buffer_region_start), int(line_region_start))
                    buffer_region_start = line_region_start
                    buffer_titles = []
                buffer_titles.append(line_article_name)
        for name in buffer_titles:
            self.articles[name] = (int(buffer_region_start), int(self.xml_file_size))

    def load(self):
        """
        Load the wikipedia index file into memory.
        If an articles.pickle.tmp exists, we simply load that (~12 seconds)
        If the pickle file doesn't exist, we manually load the index by parsing the text file (~43 seconds)
        """
        try:
            with open("articles.pickle.tmp", "rb") as articles_pickle_file:
                log.debug("Using pickled article file")
                self.articles = pickle.load(articles_pickle_file)
        except IOError:
            log.debug("Unable to use pickled articles, doing a manual load of the index file")
            self.manual_load()
            with open("articles.pickle.tmp", "wb") as articles_pickle_file:
                log.debug("Saving articles as a pickled dump to speed up future loads")
                pickle.dump(self.articles, articles_pickle_file)
        self.article_titles = set(self.articles.keys())

    def get_range(self, title):
        """
        Find the range of bytes for a given article based on the title.

        Returns (start, end) in bytes of the bzipped xml file
        """
        return self.articles[title]

    def page_exists(self, title):
        """
        Return True IFF the article exists in the dictionary
        """
        return title in self.article_titles

    def get_random_title(self):
        """
        Return a random title from the list of articles
        """
        return random.choice(list(self.article_titles))

class LocalWikipediaApi(IWikiApi):
    def __init__(self, index_file, bz_xml_file):
        self.index_file = WikipediaIndexFile(index_file, getsize(bz_xml_file))
        self.bz_xml_file = bz_xml_file

    def load(self):
        """
        Loads the index file into memory.
        Will potentially block the main thread for a little under a minute.
        Must be called before using this API.
        """
        self.index_file.load()

    def get_page_chunk(self, title):
        """
        Load the XML chunk from the bz_xml_file based on the indexes in the index file.
        Returns the text of the chunk.
        """
        start, end = self.index_file.get_range(title)
        length = end - start
        with open(self.bz_xml_file, "rb") as bz_xml_file:
            bz_xml_file.seek(start)
            chunk = bz_xml_file.read(length)
        xml = bz2.decompress(chunk)
        return xml

    def get_page_wikitext(self, title):
        """
        Get the wikitext for a given page
        """
        chunk = self.get_page_chunk(title)

        # Need to wrap the page fragments in a parent to make it valid xml
        chunk_xml = xml.fromstring("<pages>" + chunk.decode('utf-8') + "</pages>")

        # Find the correct page
        pages = chunk_xml.findall("page")
        for page in pages:
            if page.find("title").text == title:
                correctPage = page

        # Return the text of the correct page
        return correctPage.find("./revision/text").text

    def get_parsed_page(self, title):
        """
        Return the mwparserfromhell parsed page for the given title
        """
        parsed = mwparserfromhell.parse(self.get_page_wikitext(title))
        return parsed

    def page_exists(self, title):
        """
        Return True IFF the page exists
        """
        return self.index_file.page_exists(title)

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
        return self.index_file.get_random_title()

    def get_summaries(self, titles):
        """
        Bulk fetch summaries for a list of titles
        :param titles: A list of article titles
        :return: A dict of titles to summary strings

        Follows redirects

        For now, the local wikipedia api just returns the entire page. :bee: :change:
        """
        return {title: self.get_text_and_links(self.get_canonical_name(title))[0] for title in titles}

    def get_text_and_links(self, title):
        """
        Return a tuple of (article text, link targets)

        Follows redirects
        """
        parsed = self.get_parsed_page(self.get_canonical_name(title))
        text = parsed.strip_code()
        # Exclude any links which would result in an empty target
        links = parsed.ifilter_wikilinks(recursive=True, matches=lambda node: node.title.strip_code().split("#")[0].strip() != "")
        unique_links = set([link.title.strip_code().split("#")[0] for link in links])
        return text, unique_links

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

    def get_canonical_name(self, title, try_naming_variants=True, blacklist=[]):
        """
        Get the official name of an article. Useful because we just check string equality for the goal test,
        so we don't want to skip over the goal if e.g. the capitalization is off
        :return: The canonical name of the given page

        If try_naming_variants is true, attempt to try other capitalizations of the name.
        This should be on most times, but not when we recur during the process of autocapitalization.

        Cases:
        - The article name is correct
            - Use the article title as is
        - The article is a redirection page
            - Recursively call get_canonical_name on the redirect target
        - The article doesn't exist
            - Attempt to perform auto capitalization on the title to see if any of those pages exist, in which case recur on them
            - If all fails, raise IOError
        """
        title = title.replace("_", " ")
        if title in blacklist:
            raise IOError("{} not a valid page title (in the blacklist {})".format(title, blacklist))
        if self.page_exists(title):
            if self.is_redirect_page(title):
                return self.get_canonical_name(self.get_redirect_target(title), blacklist=blacklist + [title])
            else:
                return title
        else:
            if try_naming_variants:
                for variant in self.get_name_variants(title):
                    try:
                        return self.get_canonical_name(variant, try_naming_variants=False, blacklist=blacklist + [title])
                    except IOError:
                        continue
            raise IOError("{} not a valid page title".format(title))

if __name__ == "__main__":
    """
    For testing purposes, this file can be called with the arguments PATH_TO_INDEX and PATH_TO_XML_BZ2.
    This file will then run a short demo of the methods.
    """
    import sys
    path_to_index = sys.argv[1]
    path_to_xml_bz2 = sys.argv[2]
    api = LocalWikipediaApi(path_to_index, path_to_xml_bz2)
    print("Loading the index...")
    api.load()
    print("Done loading!")
    print("Canonical name of \"programming language\" is:", api.get_canonical_name("programming language"))
    print("Validness of \"Sybra_fuscotriangularis\" is:", api.is_valid_article("Sybra_fuscotriangularis"))
    links = api.get_text_and_links("programming language")[1]
    print("Links of \"programming language\" are:", links)
    for link in links:
        print("Validness of link \"{}\" is:".format(link), api.is_valid_article(link))
    print("Canonical name of \"uK\" is:", api.get_canonical_name("uK"))
    print("Canonical name of \"bat\" is:", api.get_canonical_name("bat"))
    print("Text and links of \"uK\" is:", api.get_text_and_links("uK"))
    print("Here are a few random page titles:", api.get_random_page(), api.get_random_page(), api.get_random_page())
    print("Get summaries of [\"A\", \"B\", \"Water\"] returns:", api.get_summaries(["A", "B", "Water"]))
    print("Testing to see if any articles contain a _ in their name:")
    for title in api.index_file.article_titles:
        if "_" in title:
            print("title contains underscore:", title)