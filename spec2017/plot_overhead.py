import pandas as pd
import os

import matplotlib.pyplot as plt

import seaborn as sns


def extract_boxplots(csv_path_list, benchmark_num, iterations, start_line):
    """
    Extract boxplot for the runtime of a SPEC report.
    :param csv_path_list: list of location of csvs
    :param benchmark_num: number of benchmarks
    :param iterations: parameter of benchmark execution
    :param start_line: beginning of csv
    :return:
    """
    fig, axs = plt.subplots(8)
    for i in range(0, 8):
        df = pd.read_csv(csv_path_list[i], skiprows=start_line - 1, nrows=benchmark_num * iterations)
        sns.boxplot(x='Benchmark', y='Base Run Time', data=df, palette='Set3', ax=axs[i])

    for ax in axs.flat:
        ax.set(ylabel='Run time')

    for ax in axs.flat:
        ax.label_outer()
    plt.xticks(rotation=45)
    plt.subplots_adjust(wspace=2, hspace=2)
    plt.show()


if __name__ == '__main__':
    os.chdir('results')
    csv_list = ['CPU2017.077.intspeed.csv', 'CPU2017.078.intspeed.csv', 'CPU2017.079.intspeed.csv',
                'CPU2017.080.intspeed.csv', 'CPU2017.081.intspeed.csv', 'CPU2017.082.intspeed.csv',
                'CPU2017.083.intspeed.csv', 'CPU2017.084.intspeed.csv']
    extract_boxplots(csv_list, 10, 2, 7)
