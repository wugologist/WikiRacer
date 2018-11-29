import argparse
import logging

from apis import LocalApi, WikipediaApi
from jobs.AbstractJob import AbstractJob

log = logging.getLogger(__name__)


class CalculateBranchingFactor(AbstractJob):
    apis = {"web": WikipediaApi.WikipediaApi,
            "local": LocalApi.LocalWikipediaApi}

    def run(self, args):
        parsed = self.parse_args(args)
        self.determine_branching_factor(parsed.samples, self.apis[parsed.api])

    def parse_args(self, args):
        parser = argparse.ArgumentParser(description="Calculate the average branching factor of Wikipedia"
                                                     " through random sampling",
                                         prog=args[0])
        parser.add_argument("samples", type=int, help="How many articles to sample", default=1000)
        parser.add_argument("api", help="Whether to use the web or local Wikipedia API", choices=self.apis.keys())

        return parser.parse_args(args[1:])

    @staticmethod
    def determine_branching_factor(num_samples, api):
        """
        Determine the branching factor of Wikipedia articles through random sampling
        :param num_samples: The number of random articles to sample
        :param api: The API class to use (online or local)
        :return: The average number of links per article sampled
        """
        wiki_api = api()
        link_total = 0
        log.info("Calculating branching factor with {} samples".format(num_samples))
        for i in range(num_samples):
            links = len(wiki_api.get_random_text_and_links()[1])
            link_total += links
        avg = link_total / num_samples
        log.info("Average branching factor is {}".format(avg))
