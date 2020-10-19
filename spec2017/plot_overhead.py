import pandas as pd
import numpy as np


def extract_scores(csv_path, benchmark_num, iterations, start_line):
    """
    Extract statistics for the runtime of a SPEC report.
    :param csv_path: location of csv
    :param benchmark_num:
    :param iterations: parameter of benchmark execution
    :param start_line: beginning of csv
    :return:
    """
    df = pd.read_csv(csv_path, skiprows=start_line - 1, nrows=benchmark_num * iterations)
    benchmark_names = df['Benchmark']
    scores_series = df['Est. Base Run Time']
    scores = list(scores_series.apply(lambda x: float(x)))
    aggregated_scores = [scores[x:x + iterations] for x in range(0, len(scores), iterations)]

    aggregated_scores = np.array(aggregated_scores)
    average_scores = [np.average(x) for x in aggregated_scores]
    min_scores = [np.min(x) for x in aggregated_scores]
    max_scores = [np.max(x) for x in aggregated_scores]
    percentile_scores = [np.percentile(x, 95) for x in aggregated_scores]

    print(benchmark_names)
    print(average_scores)
    print(min_scores)
    print(max_scores)
    print(percentile_scores)


if __name__ == '__main__':

    extract_scores('results/test.csv', 10, 1, 7)