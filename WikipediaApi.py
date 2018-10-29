import json
import logging
from queue import Queue
from threading import Thread
from time import time

import requests
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)  # Don't want these requests filling the logs


class WikipediaApi(object):
    def __init__(self):
        self.api_root = "https://en.wikipedia.org/api/rest_v1/"
        self.headers = {'User-Agent': 'wong.mich@husky.neu.edu'}  # Wikipedia asks to provide contact info in user agent
        self.cache = dict()  # cache page summaries to avoid duplicate requests
        self.worker_count = 8

    def get_page(self, title):
        url = self.api_root + "page/html/" + title
        return requests.get(url, headers=self.headers)

    def get_summaries(self, titles):
        """
        Bulk fetch summaries for a list of titles
        :param titles: A list of article titles
        :return: A dict of titles to summary strings
        """
        ts = time()
        queue = Queue()
        summaries = dict()
        for x in range(self.worker_count):
            worker = self.WikipediaSummaryWorker(queue, self.api_root, self.headers, summaries, self.cache)
            worker.daemon = True
            worker.start()
        for title in titles:
            queue.put(title)
        queue.join()
        log.debug("Took {} seconds to fetch {} summaries".format(time() - ts, len(titles)))
        return summaries

    def get_text_and_links(self, title):
        r = self.get_page(title)
        response = BeautifulSoup(r.text, 'html.parser')
        links = response.find_all('a')
        unique_links = set([link["href"].split("/")[-1].split("#")[0]
                            for link in links
                            if link.parent.name == "p" and link.class_ != "new"])
        return response.text, unique_links

    class WikipediaSummaryWorker(Thread):
        def __init__(self, queue, api_root, headers, results, cache):
            Thread.__init__(self)
            self.queue = queue
            self.api_root = api_root
            self.headers = headers
            self.results = results
            self.cache = cache

        def run(self):
            while True:
                title = self.queue.get()

                if title in self.cache:
                    self.results[title] = self.cache[title]
                    self.queue.task_done()
                else:
                    url = self.api_root + "page/summary/" + title
                    response = requests.get(url, headers=self.headers)
                    try:
                        if response.status_code == 200:
                            summary = json.loads(response.text)["extract"]
                            self.results[title] = summary
                            self.cache[title] = summary
                    finally:
                        self.queue.task_done()

