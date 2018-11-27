import abc
from typing import List


class AbstractJob(abc.ABC):
    @abc.abstractmethod
    def run(self, args: List[str]) -> None:
        """
        Run the job
        :param args: List of string arguments, passed in from the command line. Needs to be parsed by the job.
        """
        pass
