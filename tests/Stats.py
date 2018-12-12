from scipy.stats import ks_2samp
import logging

log = logging.getLogger(__name__)

"""
After running our tests for each search and heuristic, we obtained the following data. We want to test whether the
results are significantly different from the baseline of the BFS heuristic. We will use the Kolmogorov-Smirnov 2 sample
significance test, with a null hypothesis that the two distributions of node expansion count are identical. If
p < 0.05, we can reject the null hypothesis.

The data is from the following test cases, in order:
1. Color -> Color
2. Cattle -> France
3. Fraser_Canyon_Gold_Rush -> British_Empire
4. Martin_Chambiges -> Knights_Templar
5. Francisco_Marıa_Alvarado -> American_Community_Survey
6. The_Triumph_of_Time_(film) - Mediterranean_diet
7. Corilagin -> South_Asia
8. Gramalote -> Causeway
9. Double_Sunrise_Over_Neptune -> Pinyin

Output:
INFO:__main__:Running significance test on node expansion counts
INFO:__main__:a_star/doc2vec has value 0.2222222222222222 (p=0.9574745441329627)
INFO:__main__:a_star/wordnet has value 0.33333333333333337 (p=0.6030013612753801)
INFO:__main__:a_star/tfidf has value 0.11111111111111116 (p=0.9999999450421078)
INFO:__main__:greedy/dfs has value 0.6888888888888889 (p=0.010727457713541545)
INFO:__main__:greedy/doc2vec has value 0.2222222222222222 (p=0.9574745441329627)
INFO:__main__:greedy/wordnet has value 0.4444444444444444 (p=0.24999584817106832)
INFO:__main__:greedy/tdidf has value 0.33333333333333337 (p=0.6030013612753801)
"""

baseline = [0, 1, 8, 8, 53, 20, 105, 204, 81]

data = {
    "a_star": {
        "doc2vec": [0, 1, 19, 19, 63, 174, 63, 425, 428],
        "wordnet": [0, 1, 4, 88, 5, 11, 14, 88, 15],
        "tfidf": [0, 1, 2, 8, 81, 56, 66, 217, 35]
    },
    "greedy": {
        "dfs": [0, 1, 243, 1969, 118, 1969, 118, 939, 631, 613],
        "doc2vec": [0, 1, 40, 5, 8, 42, 16, 136, 136],
        "wordnet": [0, 1, 5, 23, 4, 5, 13, 80, 6],
        "tdidf": [0, 1, 2, 569, 11, 131, 5, 19, 4]
    }
}


def run_ks_test():
    log.info("Running significance test on node expansion counts")
    for search in data:
        for heuristic in data[search]:
            statistic, p = ks_2samp(baseline, data[search][heuristic])
            log.info("{}/{} has value {} (p={})".format(search, heuristic, statistic, p))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    run_ks_test()
