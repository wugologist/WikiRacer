import logging
import sys
from typing import Dict

from jobs.AbstractJob import AbstractJob
from jobs.CalculateBranchingFactor import CalculateBranchingFactor
from jobs.GenerateRandomCorpus import GenerateRandomCorpus

log = logging.getLogger(__name__)

# Register all jobs here
jobs: Dict[str, AbstractJob] = {
    "CalculateBranchingFactor": CalculateBranchingFactor(),
    "GenerateRandomCorpus": GenerateRandomCorpus()
}


def run_job(argv):
    if len(argv) < 2:
        raise RuntimeError("Must specify a job name")
    job_name = argv[1]
    log.info("Running {}".format(job_name))
    jobs[job_name].run(argv[1:])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_job(sys.argv)
