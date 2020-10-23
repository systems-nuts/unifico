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
    # fig, axs = plt.subplots(8)
    df_list = []
    for csv_path in csv_path_list:
        df = pd.read_csv(csv_path, skiprows=start_line - 1, nrows=benchmark_num * iterations)
        df_list.append(df)

    df = pd.concat(df_list, ignore_index=True)
    print(df)
    for bench in set(df['Benchmark']):
        sns.boxplot(x='Base # Threads', y='Base Run Time', data=df[df['Benchmark'] == bench], palette='Set3')
        plt.title(bench)
        plt.show()

# for ax in axs.flat:
#     ax.set(ylabel='Run time')
    #
    # for ax in axs.flat:
    #     ax.label_outer()
    # plt.xticks(rotation=45)
    # plt.subplots_adjust(wspace=2, hspace=2)
    # plt.show()


if __name__ == '__main__':
    os.chdir('results')
    csv_list = ['CPU2017.077.intspeed.csv', 'CPU2017.078.intspeed.csv', 'CPU2017.079.intspeed.csv',
                'CPU2017.080.intspeed.csv', 'CPU2017.081.intspeed.csv', 'CPU2017.082.intspeed.csv',
                'CPU2017.083.intspeed.csv', 'CPU2017.084.intspeed.csv', 'CPU2017.085.intspeed.csv']
    extract_boxplots(csv_list, 10, 2, 7)
