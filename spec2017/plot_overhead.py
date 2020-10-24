import pandas as pd
import os

import matplotlib.pyplot as plt

import seaborn as sns


def extract_boxplots(core_csv_list, thread_csv_list, benchmark_num, iterations, start_line):
    """
    Extract boxplot for the runtime of a SPEC report.
    :param core_csv_list: list of location of csvs for the cores execution
    :param thread_csv_list: list of location of csvs for the threads execution
    :param benchmark_num: number of benchmarks
    :param iterations: parameter of benchmark execution
    :param start_line: beginning of csv
    :return:
    """
    df_core_list = []
    for csv_path in core_csv_list:
        df = pd.read_csv(csv_path, skiprows=start_line - 1, nrows=benchmark_num * iterations)
        df_core_list.append(df)

    df_thread_list = []
    for csv_path in thread_csv_list:
        df = pd.read_csv(csv_path, skiprows=start_line - 1, nrows=benchmark_num * 1)
        df_thread_list.append(df)

    df_core = pd.concat(df_core_list, ignore_index=True)  # Results for the core experiment
    df_thread = pd.concat(df_thread_list, ignore_index=True)  # Results for the thread experiment

    for bench in set(df_core_list['Benchmark']):
        sns.boxplot(x='Base # Threads', y='Base Run Time', data=df_core[df_core['Benchmark'] == bench], palette='Set3')
        sns.boxplot(x='Base # Threads', y='Base Run Time', data=df_thread[df_thread['Benchmark'] == bench], palette='Set2')
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
    core_csv_list = ['CPU2017.077.intspeed.csv', 'CPU2017.078.intspeed.csv', 'CPU2017.079.intspeed.csv',
                     'CPU2017.080.intspeed.csv', 'CPU2017.085.intspeed.csv']
    thread_csv_list = ['CPU2017.125.intspeed.refspeed.csv', 'CPU2017.126.intspeed.refspeed.csv', 'CPU2017.127.intspeed.refspeed.csv',
                       'CPU2017.128.intspeed.refspeed.csv', 'CPU2017.129.intspeed.refspeed.csv', 'CPU2017.130.intspeed.refspeed.csv',
                       'CPU2017.131.intspeed.refspeed.csv', 'CPU2017.132.intspeed.refspeed.csv', 'CPU2017.133.intspeed.refspeed.csv']
    extract_boxplots(core_csv_list, thread_csv_list, 10, 2, 7)
